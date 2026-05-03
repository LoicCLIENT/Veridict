"""Router for the v2 peritaje pipeline (encargo → informe estructurado + chat)."""

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agents.peritaje import generar_informe, responder_pregunta_perito
from agents.respuesta_editor import editar_respuesta
from agents import trace_store
from models import (
    Cita,
    EstadoCaso,
    InformePericial,
    MensajeChat,
    RespuestaPeritoInput,
    RespuestaPregunta,
)
from reports.pdf_informe import generar_pdf
from routers.casos import casos_db


class EditarRespuestaInput(BaseModel):
    """Edición manual del perito sobre una respuesta C_i del informe."""
    respuesta: str | None = None         # nuevo texto del párrafo
    confianza: float | None = None       # nueva confianza
    citas: list[Cita] | None = None      # nuevas citas (opcional, sobrescribe)


class IniciarRespuestaIncrementalOutput(BaseModel):
    """Resultado de marcar una pregunta como respondida e iniciar el proceso."""
    informe: InformePericial
    afecta_a: list[str]


class EditarPasoIncrementalInput(BaseModel):
    """Solicita reescribir UNA respuesta C_i ya iniciada."""
    info_id: str
    pregunta_id: str


router = APIRouter()


_PDF_DIR = Path(__file__).resolve().parent.parent / "uploads" / "_pdfs"
_PDF_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{caso_id}/informe", response_model=InformePericial)
async def generar_o_regenerar_informe(caso_id: str) -> InformePericial:
    """Genera (o regenera) el informe pericial v2 a partir del Caso."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]
    caso.estado = EstadoCaso.PROCESANDO
    casos_db[caso_id] = caso

    informe = await generar_informe(caso)
    caso.informe = informe
    caso.estado = EstadoCaso.COMPLETADO
    casos_db[caso_id] = caso
    return informe


@router.get("/{caso_id}/informe", response_model=InformePericial)
async def obtener_informe(caso_id: str) -> InformePericial:
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    return caso.informe


@router.post("/{caso_id}/simulacion", response_model=InformePericial)
async def regenerar_simulacion(caso_id: str) -> InformePericial:
    """Regenera SOLO la escena del SimulationAgent (LLM) reutilizando los datos
    que ya produjeron los specialists del Perito en la última generación.

    Mucho más rápido que `/informe` (una sola llamada al LLM) y útil cuando:
    - el informe ya existe pero el panel "Simulación" no tiene escena;
    - hay que iterar sobre la calidad de la reconstrucción sin re-correr todo.
    """
    from agents.specialists import escena_simulacion
    from models import EscenaSimulacionData, InformePericial, ToolCallLog

    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    # NO exigimos informe previo: si falta, creamos uno vacío para hospedar la
    # escena. El SimulationAgent puede trabajar solo con los datos del caso
    # (vehículos, hechos, lesiones) y los datos del trace_store si existen.
    if not caso.informe:
        caso.informe = InformePericial(resumen_caso="Escena reconstruida sin informe previo.")

    # Reconstruir datos_por_tool desde varias fuentes (en orden de preferencia):
    # 1) informe.trace persistido (último run guardado en BD),
    # 2) trace_store (último run en memoria del orquestador),
    # 3) tool_calls del informe (mínimo: solo inputs/resumen).
    datos_por_tool: dict = {}
    trace = (caso.informe.trace if caso.informe and caso.informe.trace else {}) or {}
    for d in trace.get("datos_completos") or []:
        if isinstance(d, dict) and "tool" in d and "datos" in d:
            datos_por_tool[d["tool"]] = d["datos"]
    if not datos_por_tool:
        try:
            store_trace = trace_store.get(caso_id) or {}
        except Exception:
            store_trace = {}
        for d in store_trace.get("datos_completos") or []:
            if isinstance(d, dict) and "tool" in d and "datos" in d:
                datos_por_tool[d["tool"]] = d["datos"]
    if not datos_por_tool and caso.informe.tool_calls:
        # Último recurso: aunque no tengamos los `datos` completos, pasamos
        # los inputs+resumen para que el LLM al menos sepa qué tools se han
        # llamado y use el caso original como evidencia.
        for tc in caso.informe.tool_calls:
            datos_por_tool[tc.agente or "unknown"] = {
                "pregunta": tc.pregunta,
                "inputs": tc.inputs,
                "resumen": tc.resultado_resumen,
                "fuentes": tc.fuentes_consultadas,
            }
    print(f"[regenerar_simulacion] caso={caso_id} datos_por_tool keys={list(datos_por_tool.keys())}", flush=True)

    contexto = {
        "caso_id": caso.id,
        "fotos": list(caso.fotos),
        "hechos_atestado": (
            caso.hechos_atestado.model_dump(mode="json")
            if caso.hechos_atestado else {}
        ),
        "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
    }

    sim_out = await escena_simulacion.reconstruir_escena(
        caso=caso,
        datos_por_tool=datos_por_tool,
        contexto=contexto,
    )

    sim_data = sim_out.get("datos")
    if sim_data:
        try:
            caso.informe.simulacion_escena = EscenaSimulacionData.model_validate(sim_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Escena inválida: {e}")

    sim_log = sim_out.get("_log")
    if isinstance(sim_log, ToolCallLog):
        # Sustituir el ToolCallLog anterior del SimulationAgent (si lo hay)
        caso.informe.tool_calls = [
            t for t in (caso.informe.tool_calls or []) if t.agente != "SimulationAgent"
        ] + [sim_log]

    casos_db[caso_id] = caso
    return caso.informe


def _ensamblar_turnos(razon: list[dict], datos_c: list[dict]) -> list[dict]:
    """Combina los turnos del perito con las respuestas de los specialists."""
    by_turn_tool: dict[tuple, list[dict]] = {}
    for d in datos_c:
        key = (d["turno"], d["tool"])
        by_turn_tool.setdefault(key, []).append(d)

    turnos: list[dict] = []
    for r in razon:
        turn_no = r["turno"]
        tools_pedidas = []
        for tp in r.get("tools_pedidas", []):
            name = tp["name"]
            args = tp.get("input", {})
            respuesta = None
            opciones = by_turn_tool.get((turn_no, name), [])
            for d in opciones:
                if d["inputs"] == args:
                    respuesta = d["datos"]
                    break
            if respuesta is None and opciones:
                respuesta = opciones[0]["datos"]
            tools_pedidas.append({
                "tool": name,
                "inputs": args,
                "respuesta_resumen": _resumir_respuesta(name, respuesta) if respuesta else None,
                "respuesta_completa": respuesta,
            })

        turnos.append({
            "turno": turn_no,
            "razonamiento": r.get("razonamiento") or "",
            "tools_pedidas": tools_pedidas,
            "stop_reason": r.get("stop_reason"),
        })
    return turnos


@router.get("/{caso_id}/razonamiento")
async def obtener_razonamiento(caso_id: str) -> dict:
    """Devuelve el trace turno a turno. Si la generación está en curso,
    devuelve el progreso parcial con su estado en directo."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    # 1. ¿Hay una generación en curso o terminada hace poco? Servir el trace en vivo.
    parcial = trace_store.get(caso_id)
    if parcial is not None:
        turnos = _ensamblar_turnos(
            parcial.get("razonamiento_perito") or [],
            parcial.get("datos_completos") or [],
        )
        return {
            "caso_id": caso_id,
            "estado": parcial.get("estado", "iniciando"),
            "mensaje": parcial.get("mensaje", ""),
            "error": parcial.get("error"),
            "started_at": parcial.get("started_at"),
            "updated_at": parcial.get("updated_at"),
            "n_turnos": len(turnos),
            "n_tool_calls": sum(len(t["tools_pedidas"]) for t in turnos),
            "turnos": turnos,
            "informe_borrador": parcial.get("informe_borrador"),
            "en_vivo": True,
        }

    # 2. Sin trace en curso → caer al trace persistido en el informe final.
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    trace = (caso.informe.trace if caso.informe.trace else {}) or {}
    turnos = _ensamblar_turnos(
        trace.get("razonamiento_perito") or [],
        trace.get("datos_completos") or [],
    )
    return {
        "caso_id": caso_id,
        "estado": "completado",
        "mensaje": "Informe pericial listo",
        "error": None,
        "started_at": None,
        "updated_at": None,
        "n_turnos": len(turnos),
        "n_tool_calls": sum(len(t["tools_pedidas"]) for t in turnos),
        "turnos": turnos,
        "informe_borrador": None,
        "en_vivo": False,
    }


def _resumir_respuesta(tool_name: str, datos: dict | None) -> str:
    """Devuelve un resumen humano de la respuesta de un specialist."""
    if not datos:
        return "—"
    if tool_name == "consultar_escena":
        via = (datos.get("via_principal") or {}).get("name") or (datos.get("via_principal") or {}).get("highway")
        pend = datos.get("pendiente_pct")
        pend_desc = datos.get("pendiente_descartada_pct")
        if pend is not None:
            pend_str = f"{pend}%"
        elif pend_desc is not None:
            pend_str = f"DEM={pend_desc}% (descartada, inverosímil)"
        else:
            pend_str = "—"
        vis = datos.get("visibilidad_efectiva_m")
        vis_str = f" · visibilidad {vis} m" if vis else ""
        return (
            f"📍 {datos.get('direccion_resuelta', '')[:60] or 'sin dirección'} · "
            f"vía={via or '—'} · pendiente={pend_str}{vis_str} · "
            f"{datos.get('imagenes_disponibles', 0)} imágenes Mapillary"
        )
    if tool_name == "consultar_meteo":
        return (
            f"🌤️ {datos.get('estado_tiempo', '—')} · {datos.get('temperatura_c')}°C · "
            f"calzada {datos.get('calzada_estimada')} · "
            f"{'día' if datos.get('es_dia') else 'noche'}"
        )
    if tool_name == "consultar_ficha_tecnica":
        tipo = datos.get("tipo_vehiculo")
        if tipo == "bicicleta":
            return (
                f"🚲 {datos.get('marca')} {datos.get('modelo')} (bicicleta) · "
                f"bici {datos.get('masa_kg')} kg · sillín {datos.get('altura_sillin_m')} m · "
                f"manillar {datos.get('anchura_manillar_m')} m · "
                f"ciclista est. {datos.get('masa_ciclista_estimada_kg')} kg"
            )
        return (
            f"🚗 {datos.get('marca')} {datos.get('modelo')} · "
            f"{datos.get('masa_kg')} kg · ancho {datos.get('ancho_m')} m · "
            f"{len(datos.get('sistemas_seguridad') or [])} sistemas seguridad"
        )
    if tool_name == "consultar_legal":
        n_norm = len(datos.get("normativa") or [])
        adv = datos.get("advertencia_temporal")
        s = f"⚖️ {n_norm} artículos seleccionados"
        if adv:
            s += f" · ⚠ {adv[:80]}"
        return s
    if tool_name in ("calcular_fisica", "simular_fisica"):
        return f"🧮 {datos.get('resumen', '')[:200]}"
    if tool_name == "verificar_atestado":
        return f"🔍 {datos.get('observacion', '')[:200]}"
    if tool_name == "analizar_conformidad_atestado":
        return (
            f"📋 valoración: {datos.get('valoracion_global', '—')} · "
            f"{len(datos.get('incongruencias') or [])} incongruencias · "
            f"{len(datos.get('elementos_omitidos') or [])} omisiones"
        )
    if tool_name in ("generar_frame_simulacion", "obtener_frame_simulacion"):
        return (
            f"🎬 frame {datos.get('evento')} · v_pre A={datos.get('v_pre_a_kmh')} km/h, "
            f"B={datos.get('v_pre_b_kmh')} km/h · Δv A={datos.get('delta_v_a_kmh')}, B={datos.get('delta_v_b_kmh')}"
        )
    if tool_name == "analizar_biomecanica":
        wad = datos.get("wad") or {}
        return (
            f"🩺 WAD {wad.get('zona_impacto', '—')} → "
            f"{wad.get('velocidad_min_kmh', '?')}-{wad.get('velocidad_max_kmh', '?')} km/h · "
            f"Ec={datos.get('energia_cinetica_kj')} kJ · "
            f"AIS3+={datos.get('probabilidad_ais3_pct')}% · "
            f"{len(datos.get('mecanismos_lesivos_compatibles') or [])} mecanismos lesivos"
        )
    if tool_name == "listar_biblioteca_fotos":
        return (
            f"📚 {datos.get('total', 0)} fotos en {len(datos.get('por_tipo', {}))} tipos: "
            + ", ".join(datos.get("tipos_disponibles") or [])[:200]
        )
    if tool_name == "buscar_foto_perito":
        match = datos.get("match")
        if not match:
            return f"📷 sin match · {(datos.get('falta_info') or '')[:150]}"
        return f"📷 match: {(match.get('descripcion') or '')[:160]}"
    if tool_name == "analizar_imagen_dano":
        d = datos.get("descripcion") or ""
        return f"👁️ {d[:200]}"
    return str(datos)[:200]


@router.get("/{caso_id}/trace.md")
async def descargar_trace_markdown(caso_id: str):
    """Vuelca el trace completo del orquestador y los specialists en Markdown,
    incluyendo comparativa con el informe IURGI/ITRASA oficial del caso Aulestia.
    """
    from fastapi.responses import PlainTextResponse
    from agents.peritaje import _build_trace_markdown  # type: ignore

    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    md = _build_trace_markdown(caso)
    return PlainTextResponse(md, media_type="text/markdown; charset=utf-8")


@router.get("/{caso_id}/informe.pdf")
async def descargar_pdf_informe(caso_id: str):
    """Genera y devuelve el PDF UNE-EN 16775 del informe."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    out = _PDF_DIR / f"informe_{caso_id}.pdf"
    generar_pdf(caso.informe, caso, out)
    return FileResponse(out, media_type="application/pdf", filename=f"informe_{caso_id[:8]}.pdf")


@router.post("/{caso_id}/responder", response_model=InformePericial)
async def responder_info_faltante(caso_id: str, body: RespuestaPeritoInput) -> InformePericial:
    """El perito responde a una pregunta de info faltante; se regenera el informe COMPLETO.

    Endpoint legacy. Para edición incremental (más rápida y barata) usar
    `/responder-incremental`.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    informe = await responder_pregunta_perito(caso, body.info_id, body.respuesta)
    caso.informe = informe
    casos_db[caso_id] = caso
    return informe


@router.post("/{caso_id}/responder-incremental", response_model=InformePericial)
async def responder_info_incremental(caso_id: str, body: RespuestaPeritoInput) -> InformePericial:
    """Edición INCREMENTAL.

    Cuando el perito aporta el dato pedido por una `info_faltante`, se
    reescriben SOLO las respuestas C_i listadas en `info_faltante.afecta_a`.
    El resto del informe (resumen, fichas, cálculos, normativa, biomecánica,
    conformidad, otras respuestas) queda intacto.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")

    target_info = next(
        (q for q in caso.informe.info_faltante if q.id == body.info_id), None
    )
    if target_info is None:
        raise HTTPException(status_code=404, detail=f"Info faltante {body.info_id} no encontrada")

    # 1) Marcar respondida y registrar en el chat
    target_info.respondida = True
    target_info.respuesta_perito = body.respuesta
    caso.informe.chat.append(MensajeChat(
        rol="claude", contenido=target_info.pregunta, referencia_info_id=body.info_id,
    ))
    caso.informe.chat.append(MensajeChat(
        rol="perito", contenido=body.respuesta, referencia_info_id=body.info_id,
    ))

    # 2) Reescribir solo las respuestas afectadas
    afecta = target_info.afecta_a or []
    if not afecta:
        # Si no hay scope, no editamos nada — solo registramos en el chat
        caso.informe.updated_at = datetime.utcnow().isoformat() if False else caso.informe.updated_at
        casos_db[caso_id] = caso
        return caso.informe

    nuevas: dict[str, RespuestaPregunta] = {}
    razon = (
        f"El perito aporta dato nuevo en respuesta a «{target_info.pregunta[:120]}»: "
        f"{body.respuesta[:300]}"
    )
    for pregunta_id in afecta:
        nueva = await editar_respuesta(caso, pregunta_id, body.respuesta, razon=razon)
        if nueva is not None:
            nuevas[pregunta_id] = nueva

    # 3) Sustituir las respuestas afectadas
    if nuevas:
        caso.informe.respuestas = [
            nuevas.get(r.pregunta_id, r) for r in caso.informe.respuestas
        ]

    casos_db[caso_id] = caso
    return caso.informe


@router.post(
    "/{caso_id}/responder-start",
    response_model=IniciarRespuestaIncrementalOutput,
)
async def iniciar_respuesta_incremental(
    caso_id: str, body: RespuestaPeritoInput
) -> IniciarRespuestaIncrementalOutput:
    """Paso 1 del flujo incremental con progreso visible.

    Marca la `info_faltante` como respondida, registra los mensajes en el chat
    y devuelve la lista de respuestas C_i que hay que reescribir, para que el
    frontend pueda iterar mostrando progreso real por cada paso.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")

    target_info = next(
        (q for q in caso.informe.info_faltante if q.id == body.info_id), None
    )
    if target_info is None:
        raise HTTPException(
            status_code=404, detail=f"Info faltante {body.info_id} no encontrada"
        )

    target_info.respondida = True
    target_info.respuesta_perito = body.respuesta
    caso.informe.chat.append(
        MensajeChat(
            rol="claude",
            contenido=target_info.pregunta,
            referencia_info_id=body.info_id,
        )
    )
    caso.informe.chat.append(
        MensajeChat(
            rol="perito",
            contenido=body.respuesta,
            referencia_info_id=body.info_id,
        )
    )

    casos_db[caso_id] = caso
    return IniciarRespuestaIncrementalOutput(
        informe=caso.informe,
        afecta_a=list(target_info.afecta_a or []),
    )


@router.post(
    "/{caso_id}/responder-edit-step",
    response_model=InformePericial,
)
async def editar_paso_incremental(
    caso_id: str, body: EditarPasoIncrementalInput
) -> InformePericial:
    """Paso 2 del flujo incremental: reescribe UNA respuesta C_i.

    Llama a `editar_respuesta` SOLO para la `pregunta_id` indicada y devuelve
    el informe actualizado. El frontend itera este endpoint una vez por cada
    C_i listado en `afecta_a` para visualizar el progreso paso a paso.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")

    target_info = next(
        (q for q in caso.informe.info_faltante if q.id == body.info_id), None
    )
    if target_info is None or not target_info.respondida:
        raise HTTPException(
            status_code=400,
            detail="La pregunta debe haberse iniciado con /responder-start",
        )

    razon = (
        f"El perito aporta dato nuevo en respuesta a «{target_info.pregunta[:120]}»: "
        f"{(target_info.respuesta_perito or '')[:300]}"
    )
    nueva = await editar_respuesta(
        caso, body.pregunta_id, target_info.respuesta_perito, razon=razon
    )
    if nueva is not None:
        caso.informe.respuestas = [
            nueva if r.pregunta_id == body.pregunta_id else r
            for r in caso.informe.respuestas
        ]

    casos_db[caso_id] = caso
    return caso.informe


@router.patch("/{caso_id}/informe/respuesta/{pregunta_id}", response_model=InformePericial)
async def editar_respuesta_manual(
    caso_id: str, pregunta_id: str, body: EditarRespuestaInput,
) -> InformePericial:
    """Edición MANUAL del perito sobre una respuesta C_i.

    Permite al perito firmante reescribir el texto, ajustar la confianza o
    sustituir las citas SIN pasar por el LLM. Cambios persisten en el caso.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")

    target = next(
        (r for r in caso.informe.respuestas if r.pregunta_id == pregunta_id), None
    )
    if target is None:
        raise HTTPException(status_code=404, detail=f"Respuesta {pregunta_id} no encontrada")

    if body.respuesta is not None:
        target.respuesta = body.respuesta
    if body.confianza is not None:
        target.confianza = max(0.0, min(1.0, float(body.confianza)))
    if body.citas is not None:
        target.citas = body.citas

    casos_db[caso_id] = caso
    return caso.informe

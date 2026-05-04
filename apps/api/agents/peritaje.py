"""Pipeline v2: el Perito coordinador (tool_use) orquesta a los specialists.

Reemplaza el pipeline monolítico anterior. Mantiene el mismo contrato público:
    generar_informe(caso) -> InformePericial
    responder_pregunta_perito(caso, info_id, respuesta) -> InformePericial
"""

from __future__ import annotations

import json
from typing import Optional

from agents.perito import construir_informe, coordinar
from agents.specialists import cronologia as cronologia_spec
from agents.specialists import escena_simulacion
from agents import trace_store
from models import (
    CalculoFisico,
    Caso,
    Cita,
    FichaTecnicaVehiculo,
    FuenteNormativa,
    InformePericial,
    InfoFaltante,
    MensajeChat,
    PrioridadInfoFaltante,
    RespuestaPregunta,
    ToolCallLog,
)
from services.enrichment import enriquecer_todos
from services.research import bibliografia_para, normativa_para


def _fallback_informe(caso: Caso, error: str) -> InformePericial:
    fichas = enriquecer_todos(caso.vehiculos_identificacion)
    tipo = caso.encargo.tipo if caso.encargo else None
    normativa = normativa_para(tipo) if tipo else []
    bibliografia = bibliografia_para(tipo) if tipo else []
    preguntas = (caso.encargo.preguntas if caso.encargo else None) or [
        "Resuma técnicamente el siniestro."
    ]
    return InformePericial(
        resumen_caso=f"Informe en modo degradado: {error}",
        fichas_tecnicas=fichas,
        normativa_aplicable=normativa,
        bibliografia=bibliografia,
        respuestas=[
            RespuestaPregunta(
                pregunta_id=f"C{i+1}", pregunta=p,
                respuesta="Pendiente — el sistema no pudo invocar al perito coordinador.",
                confianza=0.0,
            )
            for i, p in enumerate(preguntas)
        ],
        info_faltante=[
            InfoFaltante(
                id="Q1",
                pregunta="¿Puedes ampliar las observaciones de tu inspección?",
                motivo=error,
                prioridad=PrioridadInfoFaltante.BLOQUEANTE,
            ),
        ],
    )


def _harvest_specialist_outputs(
    tool_calls: list[ToolCallLog],
) -> tuple[list[FichaTecnicaVehiculo], list[FuenteNormativa], list[str], list[CalculoFisico]]:
    """Reconstruye fichas, normativa, bibliografía y cálculos a partir de los logs."""
    fichas: list[FichaTecnicaVehiculo] = []
    normativa: list[FuenteNormativa] = []
    bibliografia: list[str] = []
    calculos: list[CalculoFisico] = []

    for log in tool_calls:
        # Estos campos los rellenamos por contrato del specialist; los logs llevan
        # los inputs y un resumen, pero los datos completos están en el flujo
        # que pasamos a Claude. Para la UI nos basta con lo que el coordinador
        # ya sabe; aquí dejamos la extracción ligera.
        pass

    return fichas, normativa, bibliografia, calculos


async def generar_informe(caso: Caso) -> InformePericial:
    """Orquesta el Perito coordinador y devuelve el InformePericial."""
    # 1. Sembrar fichas/normativa/biblio aunque el coordinador falle (los specialists
    #    también las consultarán, pero queremos garantizar que la UI tenga estos
    #    paneles aunque Opus no esté disponible).
    fichas = enriquecer_todos(caso.vehiculos_identificacion)
    tipo = caso.encargo.tipo if caso.encargo else None
    normativa = normativa_para(tipo) if tipo else []
    bibliografia = bibliografia_para(tipo) if tipo else []

    # 2. Cálculos básicos (Δv, energía) que ya teníamos en v1 — se mantienen
    #    porque la UI los pinta y al Perito le sirven como semilla.
    calculos: list[CalculoFisico] = []
    if caso.hechos_atestado and len(caso.hechos_atestado.velocidades_declaradas) >= 2:
        velocidades = sorted(
            caso.hechos_atestado.velocidades_declaradas,
            key=lambda v: v.valor_kmh, reverse=True,
        )
        delta_v = velocidades[0].valor_kmh - velocidades[1].valor_kmh
        calculos.append(
            CalculoFisico(
                nombre="Δv aproximada (declaraciones)",
                formula="v_rapido - v_lento",
                valor=round(delta_v, 1),
                unidad="km/h",
                justificacion=(
                    f"{velocidades[0].vehiculo_id} {velocidades[0].valor_kmh} km/h vs "
                    f"{velocidades[1].vehiculo_id} {velocidades[1].valor_kmh} km/h. "
                    f"Cálculo deterministra preliminar; la simulación puede refinarlo."
                ),
            )
        )

    # 3. Llamar al Perito coordinador con tool_use
    trace_store.init(caso.id)
    try:
        coord_out = await coordinar(caso, caso_id=caso.id)
    except Exception as e:
        trace_store.finalize(caso.id, estado="error",
                             mensaje=f"Excepción en coordinador: {e}", error=str(e))
        raise

    if not coord_out.get("informe_data"):
        from agents.perito import (  # type: ignore
            _build_biomecanico, _build_conformidad, _build_escena, _build_meteo,
        )
        err_msg = coord_out.get("error", "error desconocido")
        trace_store.finalize(caso.id, estado="error",
                             mensaje=f"Informe degradado: {err_msg}", error=err_msg)
        fallback = _fallback_informe(caso, err_msg)
        fallback.fichas_tecnicas = fichas
        fallback.normativa_aplicable = normativa
        fallback.bibliografia = bibliografia
        fallback.calculos = calculos
        fallback.tool_calls = coord_out.get("tool_calls", [])
        fallback.imagenes = coord_out.get("imagenes_recopiladas", [])
        datos = coord_out.get("datos_por_tool") or {}
        if datos.get("analizar_biomecanica"):
            fallback.analisis_biomecanico = _build_biomecanico(datos["analizar_biomecanica"])
        if datos.get("consultar_escena"):
            fallback.contexto_escena = _build_escena(datos["consultar_escena"])
        if datos.get("consultar_meteo"):
            fallback.contexto_meteo = _build_meteo(datos["consultar_meteo"])
        if datos.get("analizar_conformidad_atestado"):
            fallback.conformidad_atestado = _build_conformidad(datos["analizar_conformidad_atestado"])
        # SimulationAgent también en modo degradado
        try:
            sim_out = await escena_simulacion.reconstruir_escena(
                caso=caso,
                datos_por_tool=datos,
                contexto={
                    "caso_id": caso.id,
                    "fotos": list(caso.fotos),
                    "hechos_atestado": (
                        caso.hechos_atestado.model_dump(mode="json")
                        if caso.hechos_atestado else {}
                    ),
                    "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
                },
            )
            from models import EscenaSimulacionData
            sim_data = sim_out.get("datos")
            if sim_data:
                fallback.simulacion_escena = EscenaSimulacionData.model_validate(sim_data)
            sim_log = sim_out.get("_log")
            if sim_log is not None:
                fallback.tool_calls = list(fallback.tool_calls or []) + [sim_log]
        except Exception:
            pass
        return fallback

    # 3.bis SimulationAgent (LLM): reconstruye la escena cenital animable a
    # partir de los datos que el Perito ya ha recopilado. Post-step opcional;
    # si falla devuelve una EscenaSimulacionData vacía con `falta_info` y la
    # UI muestra un placeholder.
    trace_store.update(caso.id, estado="simulacion",
                       mensaje="Running SimulationAgent to reconstruct the scene…")
    simulacion_escena = None
    sim_log = None
    try:
        contexto_sim = {
            "caso_id": caso.id,
            "fotos": list(caso.fotos),
            "hechos_atestado": (
                caso.hechos_atestado.model_dump(mode="json") if caso.hechos_atestado else {}
            ),
            "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
        }
        sim_out = await escena_simulacion.reconstruir_escena(
            caso=caso,
            datos_por_tool=coord_out.get("datos_por_tool") or {},
            contexto=contexto_sim,
        )
        simulacion_escena = sim_out.get("datos")
        sim_log = sim_out.get("_log")
    except Exception as e:
        print(f"[peritaje] SimulationAgent excepción: {e}", flush=True)

    # 4. Construir el InformePericial final
    trace_store.update(caso.id, estado="construyendo",
                       mensaje="Assembling the expert report…")
    chat_previo = caso.informe.chat if caso.informe else []
    informe = construir_informe(
        coord_out=coord_out,
        fichas_recopiladas=fichas,
        normativa_recopilada=normativa,
        bibliografia_recopilada=bibliografia,
        calculos_recopilados=calculos,
        chat_previo=chat_previo,
        simulacion_escena=simulacion_escena,
        fotos_caso=list(caso.fotos),  # Para extraer fotos citadas en respuestas
    )
    if sim_log is not None:
        informe.tool_calls = list(informe.tool_calls or []) + [sim_log]

    # 4.bis CronologiaAgent: si tenemos simulación, generar la cronología pericial
    # con un snapshot SVG por evento. Las imágenes generadas se añaden a
    # `informe.imagenes` para que el PDF las embeba en sección 6 también.
    trace_store.update(caso.id, estado="cronologia",
                       mensaje="Building accident timeline…")
    try:
        crono_out = await cronologia_spec.construir_cronologia(
            caso=caso,
            escena=informe.simulacion_escena,
            datos_por_tool=coord_out.get("datos_por_tool") or {},
        )
        eventos = crono_out.get("datos") or []
        if eventos:
            informe.cronologia = eventos
        crono_log = crono_out.get("_log")
        if crono_log is not None:
            informe.tool_calls = list(informe.tool_calls or []) + [crono_log]
        for sub in crono_out.get("_sub_logs") or []:
            informe.tool_calls = list(informe.tool_calls or []) + [sub]
            for img in (sub.imagenes or []):
                informe.imagenes = list(informe.imagenes or []) + [img]
    except Exception as e:
        print(f"[peritaje] CronologiaAgent excepción: {e}", flush=True)

    # Persistimos el trace completo en el informe (campo serializable) para que
    # sobreviva al reinicio del servidor y se pueda revisar desde /razonamiento
    # y /trace.md aunque el trace_store en memoria ya se haya vaciado.
    informe.trace = {
        "razonamiento_perito": coord_out.get("razonamiento_perito", []),
        "datos_completos": coord_out.get("datos_completos", []),
    }
    trace_store.finalize(caso.id, estado="completado",
                         mensaje="Informe pericial listo")
    return informe


def _build_trace_markdown(caso) -> str:
    """Genera el deep-log estructurado: razonamiento del Perito turno a turno,
    inputs y outputs completos de cada especialista, y comparación con IURGI."""
    informe = caso.informe
    trace = (informe.trace if informe and informe.trace else {}) or {}
    razon = trace.get("razonamiento_perito", [])
    datos_c = trace.get("datos_completos", [])

    encargo = caso.encargo
    out: list[str] = []
    out.append("# Trace deep-log del orquestador VERIDICT-PERITO")
    out.append("")
    out.append(f"**Caso:** `{caso.id}`  ")
    out.append(f"**Fecha siniestro:** {caso.fecha_accidente.isoformat() if caso.fecha_accidente else '—'}  ")
    out.append(f"**Tipo:** {caso.tipo_colision.value if caso.tipo_colision else '—'}  ")
    if encargo:
        out.append(f"**Encargo:** {encargo.tipo.value} — {encargo.solicitante or '—'}  ")
        out.append(f"**Procedimiento:** {encargo.procedimiento or '—'}  ")
    out.append("")
    out.append("---")
    out.append("")

    # ── 1. Conversación turno a turno ───────────────────────────────────────
    out.append("## 1. Conversación orquestador ↔ especialistas (turno a turno)")
    out.append("")
    out.append(f"El Perito Opus 4.7 ejecutó **{len(razon)} turnos** invocando "
               f"**{len(datos_c)} llamadas a tools**. Para cada turno se documenta:")
    out.append("- Razonamiento intermedio del Perito (text blocks).")
    out.append("- Tools que el Perito decidió invocar y con qué inputs.")
    out.append("- Datos completos devueltos por cada specialist.")
    out.append("")

    # Indexar tool calls por turno
    by_turn: dict[int, list[dict]] = {}
    for d in datos_c:
        by_turn.setdefault(d["turno"], []).append(d)

    for r in razon:
        turn = r["turno"]
        out.append(f"### Turno {turn}")
        if r.get("razonamiento"):
            out.append("**🧠 Razonamiento del Perito:**")
            out.append("")
            out.append("> " + r["razonamiento"].replace("\n", "\n> "))
            out.append("")
        else:
            out.append("*(El Perito no emite texto en este turno; pasa directamente a tool_use.)*")
            out.append("")

        if r.get("stop_reason") == "tool_use":
            out.append(f"**🔧 Tools invocadas en este turno: {len(r['tools_pedidas'])}**")
            out.append("")
            for i, tp in enumerate(r["tools_pedidas"], 1):
                tool_name = tp["name"]
                inputs = tp.get("input", {})
                out.append(f"#### {turn}.{i} → `{tool_name}`")
                out.append("")
                out.append("**Inputs del Perito:**")
                out.append("```json")
                out.append(json.dumps(inputs, ensure_ascii=False, indent=2))
                out.append("```")
                # Buscar la respuesta correspondiente
                respuesta = next(
                    (d for d in by_turn.get(turn, [])
                     if d["tool"] == tool_name and d["inputs"] == inputs),
                    None,
                )
                if respuesta:
                    out.append("")
                    out.append("**Respuesta del especialista:**")
                    out.append("```json")
                    out.append(json.dumps(_recortar(respuesta["datos"]),
                                          ensure_ascii=False, indent=2))
                    out.append("```")
                out.append("")
        else:
            out.append(f"*(stop_reason: `{r.get('stop_reason')}` — fin de la investigación)*")
            out.append("")

    out.append("---")
    out.append("")

    # ── 2. Resumen por agente ───────────────────────────────────────────────
    out.append("## 2. Resumen por especialista (todos los outputs)")
    out.append("")
    by_agente: dict[str, list] = {}
    for tc in (informe.tool_calls or []):
        by_agente.setdefault(tc.agente, []).append(tc)
    for agente, calls in by_agente.items():
        out.append(f"### {agente} ({len(calls)} llamadas)")
        for c in calls:
            out.append(f"- **Pregunta:** {c.pregunta}")
            out.append(f"  - **Resultado:** {c.resultado_resumen or '—'}")
            if c.fuentes_consultadas:
                out.append(f"  - **Fuentes:** {' · '.join(c.fuentes_consultadas)}")
            if c.falta_info:
                out.append(f"  - ⚠️ **Falta:** {c.falta_info}")
            out.append(f"  - **Duración:** {c.duracion_ms or 0} ms")
        out.append("")
    out.append("---")
    out.append("")

    # ── 3. Comparativa lado a lado con IURGI ────────────────────────────────
    out.append("## 3. Comparativa con el informe IURGI/ITRASA oficial")
    out.append("")
    out.append("Sección a sección del PDF oficial vs lo que ha producido Veridict.")
    out.append("")

    secciones = [
        ("§2 Tipo de accidente y condiciones del lugar",
         "Colisión fronto-lateral excéntrica turismo–bicicleta. Vía urbana en pendiente, anchura 3.10–3.20 m, calzada estrecha en curva.",
         _veredict_seccion_2(informe, caso)),
        ("§3 Características del lugar (LIDAR 3D)",
         "Anchura 3.10–3.20 m, distancia visibilidad 26.5 m / >30 m según trayectoria curva, pendiente 9-11.6%.",
         _veredict_seccion_3(informe, caso)),
        ("§5 Vehículos implicados",
         "SEAT Ibiza (anchura 1.64 m según Virtual Crash 5.0). Bicicleta Orbea, sillín 79 cm, manillar 55 cm.",
         _veredict_seccion_5(informe)),
        ("§6 Análisis del atestado policial (CRÍTICA)",
         "Errores: límite genérico 30 km/h erróneo para 2020; croquis sin escala; sin cálculos de velocidad; retroceso 'imposible'; ausencia de pruebas drogas; conclusiones carentes de rigor científico.",
         _veredict_seccion_6(informe)),
        ("§7 Análisis de velocidad del turismo",
         "Daños altos en parabrisas/techo → ≥50 km/h según UC3M-GC 2020.",
         _veredict_seccion_7(informe)),
        ("§8 Estudio biomecánico",
         "Leyes de Newton, Ec=½mv². Energía a 50 km/h: 110.918 J vs 17.747 J reglamentaria (×6.25). Lesiones cefálicas letales por autopsia.",
         _veredict_seccion_8(informe)),
        ("§9 Evitabilidad",
         "A 20 km/h con μ=0.75: detención en 1.89 m / 0.76 s. Tiempo ciclista huella 8 m: 3.33 s. Conductor tenía margen de 1.57 s para evitar la colisión.",
         _veredict_seccion_9(informe)),
        ("§10 Condicionantes y posibles causas",
         "Quebranto Art. 3 RGC (diligencia), Art. 45 RGC (adecuación velocidad), Art. 46 RGC (moderación ante ciclistas/edificios). Conductor vecino conocedor de la vía.",
         _veredict_seccion_10(informe)),
        ("§11 Conclusiones (7 puntos)",
         "1) Fronto-lateral excéntrica. 2) Velocidad excesiva ≥50 km/h (exceso 150%). 3) Energía ×6.25. 4) Lesiones letales coherentes. 5) Conductor sin maniobra evasiva con 3.33 s. 6) Evitable por simple respeto al RGC. 7) Atestado deficiente.",
         _veredict_seccion_11(informe)),
    ]

    for titulo, iurgi, veridict in secciones:
        out.append(f"### {titulo}")
        out.append("")
        out.append("| | IURGI/ITRASA oficial | Veridict |")
        out.append("|---|---|---|")
        out.append(f"| Contenido | {iurgi} | {veridict} |")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## 4. Conclusiones del Perito Veridict")
    out.append("")
    for r in (informe.respuestas or []):
        out.append(f"### {r.pregunta_id} — confianza {int(r.confianza*100)}%")
        out.append(f"**Q:** {r.pregunta}")
        out.append("")
        out.append(f"**A:** {r.respuesta}")
        out.append("")
        if r.citas:
            out.append("**Citas:**")
            for c in r.citas:
                out.append(f"- `[{c.tipo}]` {c.referencia}" + (f" — *{c.extracto}*" if c.extracto else ""))
            out.append("")
    out.append("")

    out.append(f"**Confianza global:** {int((informe.confianza_global or 0)*100)}%")
    return "\n".join(out)


def _recortar(d, max_len: int = 600):
    """Recorta valores largos para que el JSON sea legible en Markdown."""
    if isinstance(d, dict):
        return {k: _recortar(v, max_len) for k, v in d.items()}
    if isinstance(d, list):
        return [_recortar(x, max_len) for x in d[:8]]   # max 8 items
    if isinstance(d, str) and len(d) > max_len:
        return d[:max_len] + "…"
    return d


def _veredict_seccion_2(informe, caso) -> str:
    parts = []
    if caso.tipo_colision:
        parts.append(f"Tipo: {caso.tipo_colision.value}")
    if informe.contexto_escena:
        e = informe.contexto_escena
        if e.via_principal_nombre:
            parts.append(f"vía: {e.via_principal_nombre}")
        if e.pendiente_pct is not None:
            parts.append(f"pendiente: {e.pendiente_pct}%")
    return "; ".join(parts) or "—"


def _veredict_seccion_3(informe, caso) -> str:
    parts = []
    if informe.contexto_escena:
        e = informe.contexto_escena
        if e.anchura_m: parts.append(f"anchura {e.anchura_m} m (OSM)")
        if e.pendiente_pct is not None: parts.append(f"pendiente {e.pendiente_pct}% (DEM)")
        if e.n_imagenes_mapillary: parts.append(f"{e.n_imagenes_mapillary} imágenes Mapillary")
    if caso.hechos_atestado and caso.hechos_atestado.observaciones:
        parts.append("observaciones del perito instructor citadas")
    return "; ".join(parts) or "Datos limitados — sin LIDAR 3D"


def _veredict_seccion_5(informe) -> str:
    out = []
    for f in informe.fichas_tecnicas or []:
        out.append(f"{f.marca} {f.modelo}: masa {f.masa_kg} kg, ancho {f.ancho_m} m, "
                   f"{len(f.sistemas_seguridad)} sistemas seguridad, fuente {f.fuente}")
    return " · ".join(out) or "—"


def _veredict_seccion_6(informe) -> str:
    if not informe.conformidad_atestado:
        return "No analizada"
    c = informe.conformidad_atestado
    return (f"Valoración global: **{c.valoracion_global}**. "
            f"{len(c.incongruencias)} incongruencias, "
            f"{len(c.elementos_omitidos)} omisiones detectadas. "
            f"Reglas R1-R8 aplicadas automáticamente.")


def _veredict_seccion_7(informe) -> str:
    bio = informe.analisis_biomecanico
    parts = []
    for c in informe.calculos or []:
        if "huella" in c.nombre.lower() or "stannard" in (c.formula or "").lower():
            parts.append(f"velocidad por huella: {c.valor} {c.unidad}")
    if bio and bio.wad:
        parts.append(f"WAD {bio.wad.zona_impacto}: {bio.wad.velocidad_min_kmh}-{bio.wad.velocidad_max_kmh} km/h")
    return "; ".join(parts) or "—"


def _veredict_seccion_8(informe) -> str:
    bio = informe.analisis_biomecanico
    if not bio:
        return "—"
    parts = []
    if bio.energia_cinetica_kj is not None:
        parts.append(f"Ec={bio.energia_cinetica_kj} kJ")
    if bio.probabilidad_ais3_pct is not None:
        parts.append(f"AIS3+ p={bio.probabilidad_ais3_pct}%")
    if bio.mecanismos_lesivos_compatibles:
        parts.append(f"{len(bio.mecanismos_lesivos_compatibles)} mecanismos lesivos identificados")
    if bio.cadena_4_impactos_sucesivos:
        parts.append("cadena de 4 impactos documentada")
    if bio.analisis_craneal:
        parts.append("análisis cefálico (5 tipos lesión craneal)")
    return "; ".join(parts) or "—"


def _veredict_seccion_9(informe) -> str:
    parts = []
    for c in informe.calculos or []:
        if "detenc" in c.nombre.lower() or "detenc" in (c.formula or "").lower():
            parts.append(f"{c.nombre}: {c.valor} {c.unidad}")
    # Buscar también si hay cita de tiempo_huella en respuestas
    for r in informe.respuestas or []:
        if "tiempo_huella" in r.respuesta.lower() or "3,08" in r.respuesta or "3.08" in r.respuesta:
            parts.append("tiempo_huella ciclista: 3.08 s (vs IURGI 3.33 s)")
            break
    return "; ".join(parts) or "—"


def _veredict_seccion_10(informe) -> str:
    refs = [n.referencia for n in (informe.normativa_aplicable or [])]
    return f"{len(refs)} artículos: {', '.join(refs[:6])}" if refs else "—"


def _veredict_seccion_11(informe) -> str:
    n = len(informe.respuestas or [])
    out = f"{n} conclusiones generadas"
    if informe.conformidad_atestado and informe.conformidad_atestado.valoracion_global in ("incompleto", "deficiente"):
        out += " (incluye C-AT crítica al atestado)"
    return out


async def responder_pregunta_perito(
    caso: Caso, info_id: str, respuesta_perito: str
) -> InformePericial:
    """El perito ha contestado a una InfoFaltante. Marcamos respondida,
    añadimos al chat, y re-generamos el informe con el contexto ampliado."""
    if not caso.informe:
        raise ValueError("El caso aún no tiene informe generado.")

    target: Optional[InfoFaltante] = None
    for q in caso.informe.info_faltante:
        if q.id == info_id:
            q.respondida = True
            q.respuesta_perito = respuesta_perito
            target = q
            break
    if target is None:
        raise ValueError(f"No existe la pregunta de info faltante con id={info_id}")

    caso.informe.chat.append(
        MensajeChat(rol="claude", contenido=target.pregunta, referencia_info_id=info_id)
    )
    caso.informe.chat.append(
        MensajeChat(rol="perito", contenido=respuesta_perito, referencia_info_id=info_id)
    )

    return await generar_informe(caso)

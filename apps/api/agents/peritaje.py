"""Pipeline v2: el Perito coordinador (tool_use) orquesta a los specialists.

Reemplaza el pipeline monolítico anterior. Mantiene el mismo contrato público:
    generar_informe(caso) -> InformePericial
    responder_pregunta_perito(caso, info_id, respuesta) -> InformePericial
"""

from __future__ import annotations

from typing import Optional

from agents.perito import construir_informe, coordinar
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
    coord_out = await coordinar(caso)

    if not coord_out.get("informe_data"):
        from agents.perito import (  # type: ignore
            _build_biomecanico, _build_conformidad, _build_escena, _build_meteo,
        )
        fallback = _fallback_informe(caso, coord_out.get("error", "error desconocido"))
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
        return fallback

    # 4. Construir el InformePericial final
    chat_previo = caso.informe.chat if caso.informe else []
    informe = construir_informe(
        coord_out=coord_out,
        fichas_recopiladas=fichas,
        normativa_recopilada=normativa,
        bibliografia_recopilada=bibliografia,
        calculos_recopilados=calculos,
        chat_previo=chat_previo,
    )
    return informe


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

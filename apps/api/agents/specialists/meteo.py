"""MeteoAgent — meteorología histórica del momento del siniestro."""

from __future__ import annotations

import time

from models import ToolCallLog
from services.external.meteo import meteo_historica


async def consultar_meteo(lat: float, lon: float, fecha_iso: str) -> dict:
    t0 = time.time()
    data = await meteo_historica(lat, lon, fecha_iso)

    falta = None
    if data.get("error"):
        falta = f"No se pudo obtener meteo histórica: {data['error']}. Pregunta al perito si dispone del parte oficial AEMET."

    if data.get("estado_tiempo"):
        resumen = (
            f"{data['estado_tiempo']}, {data.get('temperatura_c')}°C, "
            f"precipitación {data.get('precipitacion_mm')} mm, "
            f"calzada {data.get('calzada_estimada')}, "
            f"{'día' if data.get('es_dia') else 'noche'}."
        )
    else:
        resumen = "Datos meteorológicos no disponibles."

    log = ToolCallLog(
        agente="MeteoAgent",
        pregunta=f"Meteo histórica en {lat},{lon} el {fecha_iso}",
        inputs={"lat": lat, "lon": lon, "fecha": fecha_iso},
        resultado_resumen=resumen,
        fuentes_consultadas=["Open-Meteo Archive (ECMWF ERA5)"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": data, "_log": log}

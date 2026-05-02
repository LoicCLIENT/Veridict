"""Open-Meteo historical-weather. Sin API key, datos hora a hora.

Devuelve precipitación, temperatura, viento, código de tiempo y la posición
del sol estimada para la fecha y ubicación dadas.
"""

from __future__ import annotations

from datetime import datetime, date

import httpx

from config import get_settings


WEATHER_CODES = {
    0: "despejado", 1: "mayoritariamente despejado", 2: "parcialmente nublado",
    3: "cubierto", 45: "niebla", 48: "niebla con escarcha",
    51: "llovizna ligera", 53: "llovizna moderada", 55: "llovizna densa",
    61: "lluvia ligera", 63: "lluvia moderada", 65: "lluvia intensa",
    71: "nieve ligera", 73: "nieve moderada", 75: "nieve intensa",
    80: "chubascos ligeros", 81: "chubascos moderados", 82: "chubascos violentos",
    95: "tormenta", 96: "tormenta con granizo ligero", 99: "tormenta con granizo intenso",
}


async def meteo_historica(lat: float, lon: float, fecha_iso: str) -> dict:
    """Devuelve meteo de la fecha (resolución horaria, hora del siniestro si viene en ISO)."""
    settings = get_settings()
    try:
        dt = datetime.fromisoformat(fecha_iso.replace("Z", ""))
    except ValueError:
        return {"error": "fecha inválida", "fuente": "Open-Meteo"}

    fecha_str = dt.date().isoformat()
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": fecha_str, "end_date": fecha_str,
        "hourly": "temperature_2m,precipitation,windspeed_10m,winddirection_10m,weathercode,visibility",
        "daily": "sunrise,sunset",
        "timezone": "Europe/Madrid",
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(settings.open_meteo_url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return {"error": str(e), "fuente": "Open-Meteo"}

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    target_hour = dt.hour
    idx = None
    for i, t in enumerate(times):
        try:
            if datetime.fromisoformat(t).hour == target_hour:
                idx = i
                break
        except ValueError:
            continue
    if idx is None and times:
        idx = 0

    if idx is None:
        return {"error": "sin datos horarios", "fuente": "Open-Meteo"}

    code = hourly.get("weathercode", [None])[idx]
    precipitacion = hourly.get("precipitation", [None])[idx]
    daily = data.get("daily", {})

    return {
        "temperatura_c": hourly.get("temperature_2m", [None])[idx],
        "precipitacion_mm": precipitacion,
        "viento_kmh": _to_kmh(hourly.get("windspeed_10m", [None])[idx]),
        "viento_direccion_deg": hourly.get("winddirection_10m", [None])[idx],
        "visibilidad_m": hourly.get("visibility", [None])[idx],
        "estado_tiempo": WEATHER_CODES.get(code, f"código {code}") if code is not None else None,
        "calzada_estimada": _estado_calzada(precipitacion),
        "amanecer": daily.get("sunrise", [None])[0] if daily.get("sunrise") else None,
        "atardecer": daily.get("sunset", [None])[0] if daily.get("sunset") else None,
        "es_dia": _es_dia(dt, daily) if daily else None,
        "fuente": "Open-Meteo Archive (ECMWF ERA5)",
    }


def _to_kmh(ms_or_kmh):
    """Open-Meteo devuelve ya km/h por defecto; parche por si vuelven m/s."""
    return ms_or_kmh


def _estado_calzada(prec_mm: float | None) -> str:
    if prec_mm is None:
        return "desconocido"
    if prec_mm < 0.1:
        return "seca"
    if prec_mm < 2.5:
        return "mojada"
    return "encharcada"


def _es_dia(dt: datetime, daily: dict) -> bool | None:
    try:
        sunrise = datetime.fromisoformat(daily["sunrise"][0])
        sunset = datetime.fromisoformat(daily["sunset"][0])
        return sunrise <= dt <= sunset
    except (KeyError, ValueError, IndexError):
        return None

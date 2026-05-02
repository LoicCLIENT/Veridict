"""
Datos meteorológicos históricos via Open-Meteo (ERA5).
Gratuito, sin API key, cobertura histórica mundial.
"""

from datetime import datetime
from typing import Optional

import httpx

from models import MeteoData

# WMO weather codes → descripción en español
WMO_CODES = {
    0: "despejado",
    1: "principalmente despejado", 2: "parcialmente nuboso", 3: "nublado",
    45: "niebla", 48: "niebla con escarcha",
    51: "llovizna ligera", 53: "llovizna moderada", 55: "llovizna densa",
    61: "lluvia ligera", 63: "lluvia moderada", 65: "lluvia intensa",
    71: "nieve ligera", 73: "nieve moderada", 75: "nieve intensa",
    80: "chubascos ligeros", 81: "chubascos moderados", 82: "chubascos violentos",
    95: "tormenta", 96: "tormenta con granizo", 99: "tormenta con granizo intenso",
}


async def get_weather_at(
    lat: float,
    lon: float,
    fecha: datetime,
) -> MeteoData:
    """
    Obtiene condiciones meteorológicas históricas para un lugar y momento dado.
    Usa Open-Meteo ERA5 reanalysis (datos cada hora, histórico desde 1940).
    """
    date_str = fecha.strftime("%Y-%m-%d")
    hour = fecha.hour

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "windspeed_10m",
            "winddirection_10m",
            "visibility",
            "weathercode",
            "cloudcover",
        ]),
        "timezone": "Europe/Madrid",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        # Encontrar el índice correspondiente a la hora del accidente
        target = f"{date_str}T{hour:02d}:00"
        idx = next((i for i, t in enumerate(times) if t == target), 0)

        def val(key):
            lst = hourly.get(key, [])
            return lst[idx] if idx < len(lst) else None

        temp = val("temperature_2m")
        humidity = val("relative_humidity_2m")
        precip = val("precipitation")
        wind_speed = val("windspeed_10m")
        wind_dir_deg = val("winddirection_10m")
        visibility_m = val("visibility")
        weather_code = val("weathercode") or 0
        cloudcover = val("cloudcover")

        # Convertir dirección de viento en grados a texto
        wind_dir_txt = _degrees_to_dir(wind_dir_deg) if wind_dir_deg is not None else None

        # Visibilidad: Open-Meteo devuelve metros (máx 24140 m = sin límite)
        if visibility_m is not None:
            if visibility_m >= 10000:
                visibilidad = "buena (>10 km)"
            elif visibility_m >= 4000:
                visibilidad = f"moderada ({visibility_m/1000:.1f} km)"
            elif visibility_m >= 1000:
                visibilidad = f"reducida ({visibility_m/1000:.1f} km)"
            else:
                visibilidad = f"muy reducida ({visibility_m:.0f} m)"
        else:
            visibilidad = None

        estado_tiempo = WMO_CODES.get(weather_code, f"código {weather_code}")

        return MeteoData(
            temperatura=round(temp, 1) if temp is not None else None,
            humedad=round(humidity) if humidity is not None else None,
            precipitacion=round(precip, 1) if precip is not None else None,
            viento_velocidad=round(wind_speed, 1) if wind_speed is not None else None,
            viento_direccion=wind_dir_txt,
            visibilidad=visibilidad,
            nubosidad=f"{cloudcover:.0f}%" if cloudcover is not None else None,
            estado_tiempo=estado_tiempo,
            fuente="Open-Meteo ERA5 reanalysis",
        )

    except Exception as e:
        print(f"Weather API error: {e}")
        return MeteoData(fuente="no disponible")


def _degrees_to_dir(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    idx = round(deg / 45) % 8
    return dirs[idx]

"""Open-Elevation API. Pendiente de la vía a partir de un perfil de puntos."""

from __future__ import annotations

import math

import httpx

from config import get_settings


async def perfil_y_pendiente(lat: float, lon: float, radio_m: int = 60) -> dict:
    """Muestrea elevación en 5 puntos alineados N-S y E-O y calcula pendiente máxima."""
    settings = get_settings()
    deg = radio_m / 111_111.0
    puntos = [
        (lat, lon),
        (lat + deg, lon),
        (lat - deg, lon),
        (lat, lon + deg),
        (lat, lon - deg),
    ]
    body = {"locations": [{"latitude": la, "longitude": lo} for la, lo in puntos]}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(settings.open_elevation_url, json=body)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return {"elevacion_m": None, "pendiente_pct": None,
                "fuente": "Open-Elevation", "error": str(e)}

    elevs = [item["elevation"] for item in data.get("results", []) if "elevation" in item]
    if not elevs:
        return {"elevacion_m": None, "pendiente_pct": None,
                "fuente": "Open-Elevation", "error": "sin datos"}

    centro = elevs[0]
    pendientes = []
    for e in elevs[1:]:
        dh = abs(e - centro)
        pendientes.append(100 * dh / radio_m)

    return {
        "elevacion_m": round(centro, 1),
        "pendiente_pct": round(max(pendientes) if pendientes else 0, 1),
        "pendiente_media_pct": round(sum(pendientes) / max(1, len(pendientes)), 1),
        "fuente": "Open-Elevation (DEM SRTM)",
    }

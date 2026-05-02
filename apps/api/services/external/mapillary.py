"""Mapillary API client — imágenes ground-level georreferenciadas.

Si no hay token configurado, devuelve [] sin error para que el agente lo sepa.
"""

from __future__ import annotations

from typing import Any

import httpx

from config import get_settings


async def imagenes_cerca(lat: float, lon: float, radio_m: int = 30, max_n: int = 6) -> list[dict[str, Any]]:
    """Devuelve [{id, url, thumb_url, captured_at, compass_angle, lat, lon}]."""
    settings = get_settings()
    if not settings.mapillary_access_token:
        return []

    deg = radio_m / 111_111.0
    bbox = f"{lon - deg},{lat - deg},{lon + deg},{lat + deg}"
    params = {
        "access_token": settings.mapillary_access_token,
        "fields": "id,thumb_2048_url,thumb_1024_url,captured_at,compass_angle,geometry",
        "bbox": bbox,
        "limit": max_n,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get("https://graph.mapillary.com/images", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    out = []
    for img in data.get("data", []):
        geom = img.get("geometry", {}).get("coordinates", [None, None])
        out.append({
            "id": img["id"],
            "url": img.get("thumb_2048_url"),
            "thumb_url": img.get("thumb_1024_url"),
            "captured_at": img.get("captured_at"),
            "compass_angle": img.get("compass_angle"),
            "lat": geom[1],
            "lon": geom[0],
            "fuente": "Mapillary",
        })
    return out

"""Cliente Nominatim (OpenStreetMap) — geocoding directo y reverso.

Sin API key. Política de uso: 1 req/s y User-Agent identificativo.
"""

from __future__ import annotations

from typing import Optional

import httpx


HEADERS = {"User-Agent": "Veridict-AI/0.1 (forensic accident assistant)"}


async def geocode(direccion: str) -> Optional[dict]:
    """Devuelve {lat, lon, display_name} para una dirección textual."""
    if not direccion:
        return None
    params = {"q": direccion, "format": "jsonv2", "limit": 1, "addressdetails": 1}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get("https://nominatim.openstreetmap.org/search",
                            params=params, headers=HEADERS)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None
    if not data:
        return None
    item = data[0]
    try:
        return {
            "lat": float(item["lat"]),
            "lon": float(item["lon"]),
            "display_name": item.get("display_name"),
            "type": item.get("type"),
            "importance": item.get("importance"),
        }
    except (KeyError, ValueError):
        return None


async def reverse(lat: float, lon: float) -> Optional[dict]:
    """Devuelve {display_name, address{...}} para unas coordenadas."""
    params = {"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1, "zoom": 18}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get("https://nominatim.openstreetmap.org/reverse",
                            params=params, headers=HEADERS)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None
    if not data:
        return None
    return {"display_name": data.get("display_name"), "address": data.get("address", {})}

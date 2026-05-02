"""OpenStreetMap Overpass API client.

Devuelve datos de la vía (anchura, carriles, velocidad máxima), señales y
elementos de tráfico cerca de un punto.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from config import get_settings


async def consultar_via(lat: float, lon: float, radio_m: int = 50) -> dict[str, Any]:
    """Devuelve datos de la vía + señales en `radio_m` alrededor del punto.

    Resultado:
        {
          "vias": [{"id": int, "highway": str, "name": str?, "maxspeed": str?,
                    "lanes": int?, "width": float?, "surface": str?, "oneway": bool?}],
          "senales": [{"id": int, "tipo": str, "texto": str?, "lat": ..., "lon": ...}],
          "cycleway": bool, "crossings": int,
          "fuente": "OpenStreetMap Overpass"
        }
    """
    settings = get_settings()
    query = f"""
    [out:json][timeout:25];
    (
      way(around:{radio_m},{lat},{lon})[highway];
      node(around:{radio_m},{lat},{lon})[traffic_sign];
      node(around:{radio_m},{lat},{lon})[highway=stop];
      node(around:{radio_m},{lat},{lon})[highway=give_way];
      node(around:{radio_m},{lat},{lon})[highway=traffic_signals];
      node(around:{radio_m},{lat},{lon})[highway=crossing];
      way(around:{radio_m},{lat},{lon})[cycleway];
    );
    out tags geom 50;
    """
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(settings.overpass_url, data={"data": query})
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return {"vias": [], "senales": [], "cycleway": False, "crossings": 0,
                "fuente": "OpenStreetMap Overpass", "error": str(e)}

    vias: list[dict[str, Any]] = []
    senales: list[dict[str, Any]] = []
    cycleway = False
    crossings = 0

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        if el["type"] == "way" and "highway" in tags:
            vias.append({
                "id": el["id"],
                "highway": tags.get("highway"),
                "name": tags.get("name"),
                "ref": tags.get("ref"),
                "maxspeed": tags.get("maxspeed"),
                "lanes": _safe_int(tags.get("lanes")),
                "width": _safe_float(tags.get("width")),
                "surface": tags.get("surface"),
                "oneway": tags.get("oneway") in ("yes", "true", "1"),
                "lit": tags.get("lit"),
                "smoothness": tags.get("smoothness"),
            })
            if tags.get("cycleway") and tags.get("cycleway") != "no":
                cycleway = True
        elif el["type"] == "node":
            tag = tags.get("traffic_sign") or tags.get("highway")
            if tag in ("crossing",):
                crossings += 1
            elif tag:
                senales.append({
                    "id": el["id"],
                    "tipo": tag,
                    "texto": tags.get("traffic_sign:text") or tags.get("name"),
                    "lat": el.get("lat"),
                    "lon": el.get("lon"),
                })

    return {
        "vias": vias,
        "senales": senales,
        "cycleway": cycleway,
        "crossings": crossings,
        "fuente": "OpenStreetMap Overpass",
    }


def _safe_int(v: Any) -> int | None:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _safe_float(v: Any) -> float | None:
    try:
        return float(str(v).replace("m", "").strip()) if v is not None else None
    except (TypeError, ValueError):
        return None

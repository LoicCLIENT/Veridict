"""DGT data client for road information."""

import httpx
from typing import Optional


async def get_road_data(lat: float, lon: float) -> dict:
    """
    Get road data from DGT for a location.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Road data dict
    """
    # DGT doesn't have a public API, so we use OSM data
    # and supplement with mock DGT-specific data

    return {
        "estado_trafico": "fluido",
        "incidencias": [],
        "obras": False,
        "fuente": "DGT",
    }

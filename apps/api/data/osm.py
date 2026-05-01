"""OpenStreetMap Overpass API client for road data."""

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


async def get_osm_data(lat: float, lon: float, radius: float = 50) -> dict:
    """
    Get road data from OpenStreetMap.

    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters

    Returns:
        Road data dict
    """
    try:
        query = f"""
        [out:json];
        way(around:{radius},{lat},{lon})["highway"];
        out body;
        """

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(OVERPASS_URL, data={"data": query})
            response.raise_for_status()
            data = response.json()

            if data.get("elements"):
                way = data["elements"][0]
                tags = way.get("tags", {})

                return {
                    "tipo_via": _map_highway_type(tags.get("highway", "")),
                    "nombre_via": tags.get("name", ""),
                    "velocidad_maxima": _extract_speed_limit(tags),
                    "num_carriles": int(tags.get("lanes", 2)),
                    "superficie": tags.get("surface", "asfalto"),
                    "iluminacion": "si" if tags.get("lit") == "yes" else "no",
                    "fuente": "OpenStreetMap",
                }

    except Exception as e:
        print(f"OSM API error: {e}")

    return _get_mock_osm_data()


def _map_highway_type(highway: str) -> str:
    """Map OSM highway type to Spanish road type."""
    mapping = {
        "motorway": "autopista",
        "trunk": "autovia",
        "primary": "carretera_nacional",
        "secondary": "carretera_comarcal",
        "tertiary": "carretera_local",
        "residential": "via_urbana",
        "living_street": "zona_residencial",
        "service": "via_servicio",
    }
    return mapping.get(highway, "via_urbana")


def _extract_speed_limit(tags: dict) -> int:
    """Extract speed limit from OSM tags."""
    maxspeed = tags.get("maxspeed", "")

    if maxspeed.isdigit():
        return int(maxspeed)

    # Handle special values
    if maxspeed == "walk":
        return 20
    elif "zone:30" in str(tags):
        return 30

    # Default based on highway type
    highway = tags.get("highway", "")
    defaults = {
        "motorway": 120,
        "trunk": 100,
        "primary": 90,
        "secondary": 70,
        "residential": 30,
    }
    return defaults.get(highway, 50)


def _get_mock_osm_data() -> dict:
    """Return mock OSM data."""
    return {
        "tipo_via": "via_urbana",
        "nombre_via": "Calle Principal",
        "velocidad_maxima": 50,
        "num_carriles": 2,
        "superficie": "asfalto",
        "iluminacion": "si",
        "fuente": "mock",
    }

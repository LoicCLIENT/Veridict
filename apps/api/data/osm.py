"""
OpenStreetMap Overpass API — datos de la vía en el lugar del accidente.

Selecciona la carretera de mayor categoría dentro del radio de búsqueda,
lo que es correcto en intersecciones donde hay varias opciones.
"""

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Prioridad: valor menor = vía más importante
_HIGHWAY_PRIORITY = {
    "motorway": 1, "motorway_link": 1,
    "trunk": 2, "trunk_link": 2,
    "primary": 3, "primary_link": 3,
    "secondary": 4, "secondary_link": 4,
    "tertiary": 5, "tertiary_link": 5,
    "unclassified": 6,
    "residential": 7,
    "living_street": 8,
    "service": 9,
}


async def get_osm_data(lat: float, lon: float, radius: float = 50) -> dict:
    """
    Obtiene datos de la vía desde OpenStreetMap Overpass.

    Devuelve la carretera de mayor categoría en el radio dado.
    En caso de error retorna datos de fallback (fuente: "no disponible").
    """
    query = f"""
    [out:json][timeout:10];
    way(around:{radius},{lat},{lon})["highway"];
    out body;
    """
    headers = {"User-Agent": "Veridict-AI/1.0 (forensic accident reconstruction)"}

    try:
        async with httpx.AsyncClient(timeout=12, headers=headers) as client:
            response = await client.post(OVERPASS_URL, data={"data": query})
            response.raise_for_status()
            data = response.json()

        elements = data.get("elements", [])
        if not elements:
            return _fallback_data()

        # Elegir la vía de mayor categoría
        best = min(
            elements,
            key=lambda e: _HIGHWAY_PRIORITY.get(e.get("tags", {}).get("highway", ""), 99),
        )
        tags = best.get("tags", {})

        return {
            "tipo_via": _map_highway_type(tags.get("highway", "")),
            "nombre_via": tags.get("name") or tags.get("ref") or "",
            "velocidad_maxima": _extract_speed(tags),
            "num_carriles": _extract_lanes(tags),
            "superficie": tags.get("surface") or "asfalto",
            "iluminacion": "sí" if tags.get("lit") == "yes" else "no",
            "fuente": "OpenStreetMap",
        }

    except Exception as e:
        print(f"OSM Overpass error: {e}")
        return _fallback_data()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _map_highway_type(highway: str) -> str:
    return {
        "motorway": "autopista",
        "motorway_link": "enlace_autopista",
        "trunk": "autovía",
        "trunk_link": "enlace_autovía",
        "primary": "carretera_nacional",
        "primary_link": "enlace_nacional",
        "secondary": "carretera_comarcal",
        "secondary_link": "enlace_comarcal",
        "tertiary": "carretera_local",
        "tertiary_link": "enlace_local",
        "unclassified": "vía_sin_clasificar",
        "residential": "vía_urbana",
        "living_street": "zona_residencial",
        "service": "vía_de_servicio",
    }.get(highway, "vía_urbana")


def _extract_speed(tags: dict) -> int:
    """Extrae el límite de velocidad. Maneja 'ES:urban', 'walk', números y rangos."""
    maxspeed = str(tags.get("maxspeed", "")).strip().lower()

    # Valores numéricos directos
    if maxspeed.isdigit():
        return int(maxspeed)

    # Valores especiales
    special = {
        "walk": 10,
        "es:living_street": 10,
        "es:urban": 50,
        "es:rural": 90,
        "es:motorway": 120,
        "none": 120,
    }
    if maxspeed in special:
        return special[maxspeed]

    # "60 mph" o similares con unidad
    parts = maxspeed.split()
    if parts and parts[0].isdigit():
        v = int(parts[0])
        if len(parts) > 1 and parts[1] == "mph":
            v = round(v * 1.60934)
        return v

    # Fallback por tipo de vía
    return {
        "motorway": 120,
        "trunk": 100,
        "primary": 90,
        "secondary": 70,
        "tertiary": 60,
        "residential": 30,
        "living_street": 10,
        "service": 20,
    }.get(tags.get("highway", ""), 50)


def _extract_lanes(tags: dict) -> int:
    """Extrae número de carriles. Tolera '2;3', '2|1', textos, etc."""
    raw = str(tags.get("lanes", "")).strip()
    if not raw:
        return _default_lanes(tags.get("highway", ""))
    # Tomar el primer token numérico
    for token in raw.replace("|", ";").split(";"):
        token = token.strip()
        if token.isdigit():
            return max(1, int(token))
    return _default_lanes(tags.get("highway", ""))


def _default_lanes(highway: str) -> int:
    return {
        "motorway": 3,
        "trunk": 2,
        "primary": 2,
        "secondary": 2,
        "tertiary": 1,
        "residential": 1,
        "living_street": 1,
    }.get(highway, 2)


def _fallback_data() -> dict:
    return {
        "tipo_via": "vía_urbana",
        "nombre_via": "",
        "velocidad_maxima": 50,
        "num_carriles": 2,
        "superficie": "asfalto",
        "iluminacion": "desconocida",
        "fuente": "no disponible",
    }

"""
Geocodificación inversa via Nominatim (OpenStreetMap).
Gratuito, sin API key. Convierte lat/lon en dirección postal.
"""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "Veridict-AI/1.0 (forensic accident reconstruction)"}


async def get_address(lat: float, lon: float) -> dict:
    """
    Obtiene la dirección postal y nombre de vía a partir de coordenadas GPS.

    Returns:
        dict con 'direccion_completa', 'via', 'numero', 'municipio', 'provincia'
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                NOMINATIM_URL,
                params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
                headers=HEADERS,
            )
            r.raise_for_status()
            data = r.json()

        addr = data.get("address", {})

        # Extraer componentes relevantes
        via = (
            addr.get("road")
            or addr.get("pedestrian")
            or addr.get("highway")
            or addr.get("footway")
            or "Vía desconocida"
        )
        numero = addr.get("house_number", "s/n")
        municipio = addr.get("city") or addr.get("town") or addr.get("village") or ""
        provincia = addr.get("county") or addr.get("state_district") or ""
        comunidad = addr.get("state") or ""
        cp = addr.get("postcode") or ""

        partes = [via]
        if numero and numero != "s/n":
            partes[0] = f"{via}, {numero}"
        if cp and municipio:
            partes.append(f"{cp} {municipio}")
        elif municipio:
            partes.append(municipio)
        if provincia and provincia != municipio:
            partes.append(provincia)

        direccion_completa = " — ".join(partes)

        return {
            "direccion_completa": direccion_completa,
            "via": via,
            "numero": numero,
            "municipio": municipio,
            "provincia": provincia,
            "comunidad": comunidad,
            "codigo_postal": cp,
            "display_name": data.get("display_name", ""),
        }

    except Exception as e:
        print(f"Nominatim error: {e}")
        return {
            "direccion_completa": f"Coordenadas: {lat:.5f}, {lon:.5f}",
            "via": "",
            "municipio": "",
            "provincia": "",
        }

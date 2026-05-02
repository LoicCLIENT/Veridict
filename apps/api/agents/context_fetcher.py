"""
Context Fetcher — obtiene en paralelo todos los datos externos del lugar del accidente:
  • Dirección exacta (Nominatim)
  • Meteorología histórica (Open-Meteo ERA5)
  • Datos de la vía (OpenStreetMap Overpass)
  • Posición solar (cálculo astronómico local)
"""

import asyncio

from models import Caso, Contexto, MeteoData, ViaData, SolData


async def fetch_full_context(caso: Caso) -> Contexto:
    """
    Lanza las 4 consultas externas en paralelo y devuelve el Contexto completo.
    Nunca lanza excepción — si algo falla devuelve datos parciales.
    """
    lat = caso.ubicacion.lat
    lon = caso.ubicacion.lon
    fecha = caso.fecha_accidente

    address_task = _fetch_address(lat, lon)
    meteo_task = _fetch_meteo(lat, lon, fecha)
    via_task = _fetch_via(lat, lon)
    sol_task = _fetch_sol(lat, lon, fecha)

    address, meteo, via, sol = await asyncio.gather(
        address_task, meteo_task, via_task, sol_task,
        return_exceptions=True,
    )

    ctx = Contexto()

    nominatim_via = ""
    if isinstance(address, dict):
        ctx.direccion = address.get("direccion_completa")
        ctx.municipio = address.get("municipio")
        ctx.provincia = address.get("provincia")
        nominatim_via = address.get("via", "")

    if isinstance(meteo, MeteoData):
        ctx.meteo = meteo

    if isinstance(via, ViaData):
        # Si OSM no devuelve nombre de vía, usar el de Nominatim como respaldo
        if not via.nombre_via and nominatim_via:
            via.nombre_via = nominatim_via
        ctx.via = via

    if isinstance(sol, SolData):
        ctx.sol = sol

    return ctx


async def _fetch_address(lat: float, lon: float) -> dict:
    from data.nominatim import get_address
    return await get_address(lat, lon)


async def _fetch_meteo(lat: float, lon: float, fecha) -> MeteoData:
    from data.weather import get_weather_at
    return await get_weather_at(lat, lon, fecha)


async def _fetch_via(lat: float, lon: float) -> ViaData:
    try:
        from data.osm import get_osm_data
        raw = await get_osm_data(lat, lon)
        return ViaData(
            tipo_via=raw.get("tipo_via"),
            nombre_via=raw.get("nombre_via"),
            velocidad_maxima=raw.get("velocidad_maxima"),
            num_carriles=raw.get("num_carriles"),
            superficie=raw.get("superficie"),
            iluminacion=raw.get("iluminacion"),
            fuente="OpenStreetMap",
        )
    except Exception as e:
        print(f"OSM error: {e}")
        return ViaData(fuente="no disponible")


async def _fetch_sol(lat: float, lon: float, fecha) -> SolData:
    try:
        from data.suncalc import get_sun_position
        raw = await get_sun_position(lat, lon, fecha.isoformat())
        return SolData(
            azimuth=raw.get("azimuth"),
            altitude=raw.get("altitude"),
            es_dia=raw.get("es_dia"),
            hora_amanecer=raw.get("hora_amanecer"),
            hora_atardecer=raw.get("hora_atardecer"),
            deslumbramiento_posible=raw.get("deslumbramiento_posible"),
        )
    except Exception as e:
        print(f"SunCalc error: {e}")
        return SolData()

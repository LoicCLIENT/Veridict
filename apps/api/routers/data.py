"""Router for external data APIs."""

from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/meteo")
async def get_meteo(
    lat: float = Query(...), lon: float = Query(...), t: Optional[str] = Query(None)
) -> dict:
    """Get weather data from AEMET."""
    from data.aemet import get_weather_data

    try:
        data = await get_weather_data(lat, lon, t)
        return data
    except Exception as e:
        return {
            "error": str(e),
            "mock_data": {
                "temperatura": 18.5,
                "humedad": 65,
                "precipitacion": 2.5,
                "viento_velocidad": 15,
                "viento_direccion": "NE",
                "visibilidad": "buena",
            },
        }


@router.get("/via")
async def get_via(lat: float = Query(...), lon: float = Query(...)) -> dict:
    """Get road data from DGT and OSM."""
    from data.dgt import get_road_data
    from data.osm import get_osm_data

    try:
        dgt_data = await get_road_data(lat, lon)
        osm_data = await get_osm_data(lat, lon)
        return {**dgt_data, **osm_data}
    except Exception as e:
        return {
            "error": str(e),
            "mock_data": {
                "tipo_via": "autovia",
                "velocidad_maxima": 120,
                "num_carriles": 3,
                "estado_pavimento": "bueno",
                "iluminacion": "artificial",
            },
        }


@router.get("/sol")
async def get_sol(
    lat: float = Query(...), lon: float = Query(...), t: Optional[str] = Query(None)
) -> dict:
    """Get sun position data."""
    from data.suncalc import get_sun_position

    try:
        data = await get_sun_position(lat, lon, t)
        return data
    except Exception as e:
        return {
            "error": str(e),
            "mock_data": {
                "azimuth": 180.5,
                "altitude": 45.2,
                "es_dia": True,
            },
        }


@router.get("/vehiculo")
async def get_vehiculo(modelo: str = Query(...)) -> dict:
    """Get vehicle coefficients from NHTSA database."""
    from physics.coefficients import get_vehicle_coefficients

    try:
        data = get_vehicle_coefficients(modelo)
        return data
    except Exception as e:
        return {
            "error": str(e),
            "mock_data": {
                "modelo": modelo,
                "coef_a": 45.2,
                "coef_b": 0.15,
                "masa_curb_kg": 1350,
                "categoria": "passenger_car",
            },
        }

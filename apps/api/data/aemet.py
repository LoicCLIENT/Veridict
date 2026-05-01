"""AEMET OpenData API client for weather data."""

import httpx
from typing import Optional
from config import get_settings


async def get_weather_data(
    lat: float, lon: float, timestamp: Optional[str] = None
) -> dict:
    """
    Get weather data from AEMET for a location and time.

    Args:
        lat: Latitude
        lon: Longitude
        timestamp: ISO timestamp (defaults to current)

    Returns:
        Weather data dict
    """
    settings = get_settings()

    if not settings.aemet_api_key:
        return _get_mock_weather()

    try:
        async with httpx.AsyncClient() as client:
            # First, get the municipality code
            # AEMET API requires municipality code, not coordinates
            # In production, would need to reverse geocode first

            # For now, return mock data
            return _get_mock_weather()

    except Exception as e:
        print(f"AEMET API error: {e}")
        return _get_mock_weather()


def _get_mock_weather() -> dict:
    """Return mock weather data for testing."""
    return {
        "temperatura": 18.5,
        "humedad": 65,
        "precipitacion": 0.0,
        "viento_velocidad": 12,
        "viento_direccion": "NE",
        "visibilidad": "buena",
        "presion": 1015,
        "nubosidad": "parcialmente nublado",
        "fuente": "mock",
    }

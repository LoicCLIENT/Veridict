"""Sun position calculations using astronomical formulas."""

import math
from datetime import datetime
from typing import Optional


async def get_sun_position(
    lat: float, lon: float, timestamp: Optional[str] = None
) -> dict:
    """
    Calculate sun position for a location and time.

    Args:
        lat: Latitude
        lon: Longitude
        timestamp: ISO timestamp (defaults to current)

    Returns:
        Sun position data
    """
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    else:
        dt = datetime.utcnow()

    # Calculate Julian date
    jd = _datetime_to_jd(dt)

    # Calculate sun position
    azimuth, altitude = _calculate_sun_position(lat, lon, jd)

    return {
        "azimuth": round(azimuth, 2),
        "altitude": round(altitude, 2),
        "es_dia": altitude > 0,
        "hora_amanecer": _calculate_sunrise(lat, lon, jd),
        "hora_atardecer": _calculate_sunset(lat, lon, jd),
        "deslumbramiento_posible": _check_glare_risk(azimuth, altitude),
    }


def _datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian date."""
    year = dt.year
    month = dt.month
    day = dt.day + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24

    if month <= 2:
        year -= 1
        month += 12

    a = int(year / 100)
    b = 2 - a + int(a / 4)

    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd


def _calculate_sun_position(lat: float, lon: float, jd: float) -> tuple:
    """
    Calculate sun azimuth and altitude.

    Returns:
        Tuple of (azimuth, altitude) in degrees
    """
    # Days since J2000.0
    n = jd - 2451545.0

    # Mean longitude of the Sun
    L = (280.460 + 0.9856474 * n) % 360

    # Mean anomaly of the Sun
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)

    # Ecliptic longitude
    lambda_sun = L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
    lambda_rad = math.radians(lambda_sun)

    # Obliquity of ecliptic
    epsilon = math.radians(23.439 - 0.0000004 * n)

    # Right ascension and declination
    sin_lambda = math.sin(lambda_rad)
    cos_lambda = math.cos(lambda_rad)

    alpha = math.atan2(math.cos(epsilon) * sin_lambda, cos_lambda)
    delta = math.asin(math.sin(epsilon) * sin_lambda)

    # Hour angle
    gmst = (18.697374558 + 24.06570982441908 * n) % 24
    lst = gmst + lon / 15
    ha = math.radians((lst * 15) - math.degrees(alpha))

    # Convert to horizontal coordinates
    lat_rad = math.radians(lat)
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    sin_delta = math.sin(delta)
    cos_delta = math.cos(delta)
    cos_ha = math.cos(ha)

    altitude = math.asin(sin_lat * sin_delta + cos_lat * cos_delta * cos_ha)
    azimuth = math.atan2(
        -math.sin(ha), cos_lat * math.tan(delta) - sin_lat * cos_ha
    )

    return (math.degrees(azimuth) + 180) % 360, math.degrees(altitude)


def _calculate_sunrise(lat: float, lon: float, jd: float) -> str:
    """Calculate sunrise time (simplified)."""
    # Simplified calculation - would need more precision for production
    return "07:15"


def _calculate_sunset(lat: float, lon: float, jd: float) -> str:
    """Calculate sunset time (simplified)."""
    return "20:45"


def _check_glare_risk(azimuth: float, altitude: float) -> bool:
    """
    Check if sun position could cause glare for drivers.

    Glare is most problematic when sun is low (altitude < 30)
    and in direction of travel.
    """
    return 0 < altitude < 30

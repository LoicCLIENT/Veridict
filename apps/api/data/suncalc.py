"""
Posición solar — cálculo astronómico puro (sin dependencias externas).

Implementa:
  • Azimuth y altitud del sol para la hora exacta del accidente
  • Amanecer/atardecer reales usando ángulo horario en el horizonte (NOAA)
  • Corrección automática UTC ↔ hora local española (CET/CEST)
  • Riesgo de deslumbramiento para conductores
"""

import calendar
import math
from datetime import datetime, timedelta
from typing import Optional


# ── Timezone helpers ──────────────────────────────────────────────────────────

def _spain_utc_offset(dt: datetime) -> int:
    """Devuelve el offset UTC de España para la fecha dada (+1 CET, +2 CEST)."""
    year = dt.year

    def last_sunday(y: int, month: int) -> datetime:
        last_day = calendar.monthrange(y, month)[1]
        d = datetime(y, month, last_day)
        while d.weekday() != 6:  # 6 = Sunday
            d -= timedelta(days=1)
        return d

    # CEST: último domingo de marzo 02:00 → último domingo de octubre 03:00
    cest_start = last_sunday(year, 3).replace(hour=2)
    cest_end = last_sunday(year, 10).replace(hour=3)
    return 2 if cest_start <= dt.replace(tzinfo=None) < cest_end else 1


# ── Julian date ───────────────────────────────────────────────────────────────

def _to_jd(dt: datetime) -> float:
    """Convierte datetime (UTC) a fecha juliana."""
    year, month = dt.year, dt.month
    day = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    a = int(year / 100)
    b = 2 - a + int(a / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5


# ── Sun position ──────────────────────────────────────────────────────────────

def _sun_position(lat: float, lon: float, jd: float) -> tuple[float, float]:
    """
    Calcula azimuth y altitud del sol (grados) para un instante dado (JD UTC).
    Algoritmo: aproximación de baja precisión USNO (~0.01° error).
    """
    n = jd - 2451545.0  # días desde J2000.0

    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    epsilon = math.radians(23.439 - 0.0000004 * n)

    sin_l, cos_l = math.sin(lambda_sun), math.cos(lambda_sun)
    alpha = math.atan2(math.cos(epsilon) * sin_l, cos_l)
    delta = math.asin(math.sin(epsilon) * sin_l)

    gmst = (18.697374558 + 24.06570982441908 * n) % 24
    lst = gmst + lon / 15.0
    ha = math.radians(lst * 15.0 - math.degrees(alpha))

    lat_r = math.radians(lat)
    sin_lat, cos_lat = math.sin(lat_r), math.cos(lat_r)
    sin_d, cos_d, cos_ha = math.sin(delta), math.cos(delta), math.cos(ha)

    altitude = math.degrees(math.asin(sin_lat * sin_d + cos_lat * cos_d * cos_ha))
    # Formula NOAA: A=atan2(sin H, cos H·sin φ − tan δ·cos φ) + 180°
    azimuth = math.degrees(math.atan2(
        math.sin(ha),
        cos_ha * sin_lat - math.tan(delta) * cos_lat,
    ))
    return (azimuth + 180) % 360, altitude


# ── Sunrise / sunset ──────────────────────────────────────────────────────────

def _sunrise_sunset(lat: float, lon: float, jd_noon_utc: float, tz_offset: int) -> tuple[str, str]:
    """
    Calcula amanecer y atardecer para el día dado.

    jd_noon_utc: fecha juliana para las 12:00 UTC del día del accidente.
    Devuelve strings "HH:MM" en hora local española.
    """
    n = jd_noon_utc - 2451545.0

    # Declinación solar
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    L = (280.460 + 0.9856474 * n) % 360
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    epsilon = math.radians(23.439 - 0.0000004 * n)
    delta = math.asin(math.sin(epsilon) * math.sin(lambda_sun))

    # Corrección ecuación del tiempo (minutos)
    B = math.radians(360.0 / 365.0 * (n - 81))
    eot_min = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    # Mediodía solar en UTC
    solar_noon_utc = 12.0 - lon / 15.0 - eot_min / 60.0

    # Ángulo horario en el horizonte (cénit 90.833° = refracción + radio solar)
    cos_H = (
        (math.sin(math.radians(-0.833)) - math.sin(math.radians(lat)) * math.sin(delta))
        / (math.cos(math.radians(lat)) * math.cos(delta))
    )

    if cos_H < -1:
        return "sol continuo", "sol continuo"
    if cos_H > 1:
        return "noche polar", "noche polar"

    H_hours = math.degrees(math.acos(cos_H)) / 15.0
    sunrise = (solar_noon_utc - H_hours + tz_offset) % 24
    sunset = (solar_noon_utc + H_hours + tz_offset) % 24

    def fmt(h: float) -> str:
        hh, mm = divmod(round(h * 60), 60)
        return f"{hh:02d}:{mm:02d}"

    return fmt(sunrise), fmt(sunset)


# ── Public API ────────────────────────────────────────────────────────────────

async def get_sun_position(
    lat: float,
    lon: float,
    timestamp: Optional[str] = None,
) -> dict:
    """
    Calcula posición solar para un lugar y hora del accidente.

    timestamp: ISO string en hora local española (naive). Si es None usa UTC actual.
    """
    if timestamp:
        dt_local = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if dt_local.tzinfo is not None:
            dt_local = dt_local.replace(tzinfo=None)
    else:
        dt_local = datetime.utcnow()

    tz_offset = _spain_utc_offset(dt_local)
    # Convertir hora local España → UTC para los cálculos astronómicos
    dt_utc = dt_local - timedelta(hours=tz_offset)

    jd = _to_jd(dt_utc)
    azimuth, altitude = _sun_position(lat, lon, jd)

    # Amanecer/atardecer: usar mediodía UTC del mismo día
    dt_noon_utc = dt_utc.replace(hour=12, minute=0, second=0, microsecond=0)
    jd_noon = _to_jd(dt_noon_utc)
    sunrise, sunset = _sunrise_sunset(lat, lon, jd_noon, tz_offset)

    return {
        "azimuth": round(azimuth, 2),
        "altitude": round(altitude, 2),
        "es_dia": altitude > 0,
        "hora_amanecer": sunrise,
        "hora_atardecer": sunset,
        "deslumbramiento_posible": _check_glare_risk(azimuth, altitude),
    }


def _check_glare_risk(azimuth: float, altitude: float) -> bool:
    """
    Riesgo de deslumbramiento: sol bajo (altitud 0-25°) en dirección de conducción.
    El intervalo peligroso es cuando el sol está sobre el horizonte pero no ha subido
    lo suficiente para quedar fuera del ángulo visual del conductor.
    """
    return 0 < altitude < 25

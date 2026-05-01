"""
Stannard Baker Method Implementation.

Calculates pre-braking speed from skid mark length.
Standard method in traffic accident reconstruction.
"""

import math


# Friction coefficients for different surfaces and conditions
FRICTION_COEFFICIENTS = {
    "asfalto_seco": 0.75,
    "asfalto_mojado": 0.55,
    "asfalto_helado": 0.15,
    "hormigon_seco": 0.80,
    "hormigon_mojado": 0.60,
    "grava_seca": 0.50,
    "grava_mojada": 0.40,
    "tierra_seca": 0.55,
    "tierra_mojada": 0.40,
}

# Standard gravity
G = 9.81  # m/s^2


def calculate_pre_brake_speed(
    longitud_frenada: float,  # Skid mark length in meters
    coef_friccion: float = 0.65,  # Friction coefficient
    pendiente: float = 0.0,  # Grade in percentage (+ uphill, - downhill)
) -> float:
    """
    Calculate pre-braking speed using Stannard Baker formula.

    V = sqrt(2 * mu * g * d)

    Adjusted for grade:
    V = sqrt(2 * g * d * (mu + sin(grade)))

    Args:
        longitud_frenada: Length of skid marks in meters
        coef_friccion: Friction coefficient (mu)
        pendiente: Road grade in percentage

    Returns:
        Pre-braking speed in km/h
    """
    if longitud_frenada <= 0:
        return 0.0

    # Convert grade percentage to sine component
    grade_factor = pendiente / 100  # Approximate for small angles

    # Effective deceleration factor
    decel_factor = coef_friccion + grade_factor

    # Stannard Baker formula
    v_ms = math.sqrt(2 * G * longitud_frenada * decel_factor)

    # Convert to km/h
    v_kmh = v_ms * 3.6

    return round(v_kmh, 1)


def calculate_stopping_distance(
    velocidad_inicial: float,  # Initial speed in km/h
    coef_friccion: float = 0.65,
    tiempo_reaccion: float = 1.5,  # Reaction time in seconds
    pendiente: float = 0.0,
) -> dict:
    """
    Calculate total stopping distance including reaction distance.

    Args:
        velocidad_inicial: Initial speed in km/h
        coef_friccion: Friction coefficient
        tiempo_reaccion: Driver reaction time in seconds
        pendiente: Road grade in percentage

    Returns:
        dict with 'distancia_reaccion', 'distancia_frenada', 'distancia_total'
    """
    # Convert km/h to m/s
    v_ms = velocidad_inicial / 3.6

    # Reaction distance
    d_reaccion = v_ms * tiempo_reaccion

    # Braking distance
    grade_factor = pendiente / 100
    decel_factor = coef_friccion + grade_factor

    if decel_factor <= 0:
        d_frenada = float("inf")
    else:
        d_frenada = (v_ms ** 2) / (2 * G * decel_factor)

    d_total = d_reaccion + d_frenada

    return {
        "distancia_reaccion": round(d_reaccion, 1),
        "distancia_frenada": round(d_frenada, 1),
        "distancia_total": round(d_total, 1),
    }


def get_friction_coefficient(
    superficie: str = "asfalto",
    condicion: str = "seco",
) -> float:
    """
    Get standard friction coefficient for surface type and condition.

    Args:
        superficie: Surface type (asfalto, hormigon, grava, tierra)
        condicion: Condition (seco, mojado, helado)

    Returns:
        Friction coefficient
    """
    key = f"{superficie}_{condicion}"
    return FRICTION_COEFFICIENTS.get(key, 0.65)


def calculate_critical_speed(
    radio_curva: float,  # Curve radius in meters
    coef_friccion: float = 0.65,
    peralte: float = 0.0,  # Superelevation in percentage
) -> float:
    """
    Calculate critical speed for curve negotiation.

    V_crit = sqrt(g * r * (mu + e) / (1 - mu * e))

    Args:
        radio_curva: Curve radius in meters
        coef_friccion: Friction coefficient
        peralte: Superelevation in percentage

    Returns:
        Critical speed in km/h
    """
    e = peralte / 100

    numerator = G * radio_curva * (coef_friccion + e)
    denominator = 1 - coef_friccion * e

    if denominator <= 0:
        return float("inf")

    v_ms = math.sqrt(numerator / denominator)
    v_kmh = v_ms * 3.6

    return round(v_kmh, 1)

"""
Momentum Conservation Calculations.

Used for vehicle-to-vehicle collision analysis.
"""

import math
from typing import Tuple


def verify_momentum_conservation(
    m1: float,  # Mass vehicle 1 (kg)
    v1_pre: float,  # Pre-impact velocity vehicle 1 (km/h)
    theta1_pre: float,  # Pre-impact direction vehicle 1 (degrees)
    m2: float,  # Mass vehicle 2 (kg)
    v2_pre: float,  # Pre-impact velocity vehicle 2 (km/h)
    theta2_pre: float,  # Pre-impact direction vehicle 2 (degrees)
    v1_post: float,  # Post-impact velocity vehicle 1 (km/h)
    theta1_post: float,  # Post-impact direction vehicle 1 (degrees)
    v2_post: float,  # Post-impact velocity vehicle 2 (km/h)
    theta2_post: float,  # Post-impact direction vehicle 2 (degrees)
    tolerance: float = 0.15,  # 15% tolerance
) -> dict:
    """
    Verify conservation of momentum in a collision.

    Returns dict with 'conserved' (bool) and 'error_percent'
    """
    # Convert angles to radians
    def deg_to_rad(deg):
        return deg * math.pi / 180

    # Convert km/h to m/s
    def kmh_to_ms(v):
        return v / 3.6

    # Calculate momentum components
    # Pre-impact
    px1_pre = m1 * kmh_to_ms(v1_pre) * math.cos(deg_to_rad(theta1_pre))
    py1_pre = m1 * kmh_to_ms(v1_pre) * math.sin(deg_to_rad(theta1_pre))
    px2_pre = m2 * kmh_to_ms(v2_pre) * math.cos(deg_to_rad(theta2_pre))
    py2_pre = m2 * kmh_to_ms(v2_pre) * math.sin(deg_to_rad(theta2_pre))

    total_px_pre = px1_pre + px2_pre
    total_py_pre = py1_pre + py2_pre

    # Post-impact
    px1_post = m1 * kmh_to_ms(v1_post) * math.cos(deg_to_rad(theta1_post))
    py1_post = m1 * kmh_to_ms(v1_post) * math.sin(deg_to_rad(theta1_post))
    px2_post = m2 * kmh_to_ms(v2_post) * math.cos(deg_to_rad(theta2_post))
    py2_post = m2 * kmh_to_ms(v2_post) * math.sin(deg_to_rad(theta2_post))

    total_px_post = px1_post + px2_post
    total_py_post = py1_post + py2_post

    # Calculate error
    magnitude_pre = math.sqrt(total_px_pre**2 + total_py_pre**2)
    magnitude_post = math.sqrt(total_px_post**2 + total_py_post**2)

    if magnitude_pre == 0:
        error_percent = 0 if magnitude_post == 0 else 100
    else:
        error_percent = abs(magnitude_post - magnitude_pre) / magnitude_pre * 100

    return {
        "conserved": error_percent <= tolerance * 100,
        "error_percent": round(error_percent, 2),
        "momentum_pre": {"x": round(total_px_pre, 2), "y": round(total_py_pre, 2)},
        "momentum_post": {"x": round(total_px_post, 2), "y": round(total_py_post, 2)},
    }


def calculate_impact_speeds(
    m1: float,  # Mass vehicle 1 (kg)
    m2: float,  # Mass vehicle 2 (kg)
    delta_v1: float,  # Delta-V vehicle 1 (km/h)
    delta_v2: float,  # Delta-V vehicle 2 (km/h)
) -> Tuple[float, float]:
    """
    Calculate pre-impact speeds from Delta-V values.

    Based on conservation of momentum:
    m1 * delta_v1 = m2 * delta_v2

    Returns:
        Tuple of (v1_pre, v2_pre) in km/h
    """
    # From momentum conservation in central impact:
    # v1_pre - v1_post = delta_v1
    # v2_pre - v2_post = delta_v2
    # m1 * v1_pre + m2 * v2_pre = m1 * v1_post + m2 * v2_post

    # Simplified for head-on collision where post-impact velocities are ~0:
    total_momentum = m1 * delta_v1 + m2 * delta_v2

    # Assuming closing speed distributed by mass ratio
    v1_pre = delta_v1 * (m1 + m2) / (2 * m1)
    v2_pre = delta_v2 * (m1 + m2) / (2 * m2)

    return (round(v1_pre, 1), round(v2_pre, 1))


def calculate_coefficient_of_restitution(
    v1_pre: float,
    v2_pre: float,
    v1_post: float,
    v2_post: float,
) -> float:
    """
    Calculate coefficient of restitution for the collision.

    e = (v2_post - v1_post) / (v1_pre - v2_pre)

    e = 0: Perfectly plastic collision
    e = 1: Perfectly elastic collision
    Typical vehicle collisions: 0.1 - 0.4
    """
    closing_speed = v1_pre - v2_pre
    separation_speed = v2_post - v1_post

    if closing_speed == 0:
        return 0

    e = abs(separation_speed / closing_speed)
    return round(min(e, 1.0), 3)

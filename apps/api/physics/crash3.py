"""
CRASH3 Model Implementation.

Based on McHenry (1975) - Calculates Equivalent Barrier Speed (EBS)
from vehicle deformation measurements.

Reference: NHTSA CRASH3 User's Guide and Technical Manual
"""

import math
from typing import List


def calculate_ebs(
    mediciones_C: List[float],  # C1-C6 deformation measurements in cm
    ancho_zona: float,  # Width of damaged zone in cm
    masa: float,  # Vehicle mass in kg
    coef_a: float = 700.0,  # Stiffness coefficient A (kPa)
    coef_b: float = 2400.0,  # Stiffness coefficient B (kPa/m)
    c0: float = 0.0,  # Natural pre-impact profile depth (cm) — C0 correction
    e: float = 0.1,  # Coefficient of restitution (0=plastic, typical car crash: 0.1)
) -> float:
    """
    Calculate Equivalent Barrier Speed (EBS) using CRASH3 model.

    Uses per-point energy integration (trapezoidal approach over C1-C6),
    C0 correction for natural vehicle profile, and restitution correction.

    Formula per measurement point i:
        e_i = A*(Ci - C0) + B*(Ci - C0)²/2   [energy density, kJ/m]
    Total energy:
        E [kJ] = mean(e_i) * L
    Restitution correction (accounts for elastic bounce-back):
        EBS_corrected = EBS_plastic / sqrt(1 - e²)

    Args:
        mediciones_C: 6 crush measurements C1-C6 in cm
        ancho_zona: Width of crush zone in cm
        masa: Vehicle mass in kg
        coef_a: Stiffness A in kPa (kN/m²) — from NHTSA database
        coef_b: Stiffness B in kPa/m (kN/m³)
        c0: Pre-impact natural profile depth in cm (default 0 = flat front)
        e: Coefficient of restitution — 0.10 typical high-speed, 0.30 low-speed

    Returns:
        EBS in km/h
    """
    if not mediciones_C or len(mediciones_C) < 6:
        raise ValueError("Need 6 crush measurements (C1-C6)")
    if masa <= 0:
        raise ValueError("Mass must be positive")
    if not (0.0 <= e < 1.0):
        raise ValueError("Restitution coefficient must be in [0, 1)")

    ancho_m = ancho_zona / 100  # cm → m

    # Per-point energy integration — more accurate than (C_avg)² for non-uniform profiles
    energy_sum = 0.0
    for ci_cm in mediciones_C:
        ci_net_m = max(0.0, ci_cm - c0) / 100  # C0 correction, cm → m
        energy_sum += coef_a * ci_net_m + coef_b * ci_net_m ** 2 / 2

    energy_per_width = energy_sum / len(mediciones_C)  # kJ/m  (mean across 6 points)
    total_energy_J = energy_per_width * ancho_m * 1000   # kJ → J

    ebs_ms = math.sqrt(2 * total_energy_J / masa) if total_energy_J > 0 else 0.0

    # Restitution correction: plastic assumption underestimates speed when e > 0
    # Physical basis: E_crush = (1/2)*m*v² * (1 - e²)  →  v = EBS / sqrt(1 - e²)
    if e > 0:
        ebs_ms = ebs_ms / math.sqrt(1.0 - e ** 2)

    return round(ebs_ms * 3.6, 1)


def calculate_delta_v(
    ebs: float,  # EBS in km/h
    masa_vehiculo: float,  # Vehicle mass in kg
    masa_otro: float,  # Other vehicle mass in kg (0 for barrier)
) -> float:
    """
    Calculate Delta-V from EBS.

    For vehicle-to-vehicle collisions:
    Delta-V = EBS * (m_other / (m_self + m_other))

    Args:
        ebs: Equivalent Barrier Speed in km/h
        masa_vehiculo: Mass of the vehicle being analyzed
        masa_otro: Mass of the other vehicle (0 for barrier test)

    Returns:
        Delta-V in km/h
    """
    if masa_otro == 0:
        # Barrier test - Delta-V equals EBS
        return ebs

    # Vehicle-to-vehicle collision
    total_mass = masa_vehiculo + masa_otro
    delta_v = ebs * (masa_otro / total_mass)

    return round(delta_v, 1)


def estimate_impact_angle(mediciones_C: List[float]) -> float:
    """
    Estimate impact angle from crush profile.

    Symmetric crush suggests head-on, asymmetric suggests angled impact.

    Returns:
        Estimated impact angle in degrees (0 = head-on)
    """
    if len(mediciones_C) < 6:
        return 0

    # Compare left side (C1-C3) to right side (C4-C6)
    left_avg = sum(mediciones_C[:3]) / 3
    right_avg = sum(mediciones_C[3:]) / 3

    if left_avg + right_avg == 0:
        return 0

    # Asymmetry ratio
    asymmetry = (left_avg - right_avg) / (left_avg + right_avg)

    # Map asymmetry to angle (rough approximation)
    angle = asymmetry * 45  # Max 45 degrees

    return round(angle, 1)

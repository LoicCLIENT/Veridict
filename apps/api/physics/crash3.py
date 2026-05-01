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
    coef_a: float = 45.0,  # Stiffness coefficient A (N/cm)
    coef_b: float = 0.15,  # Stiffness coefficient B (N/cm^2)
) -> float:
    """
    Calculate Equivalent Barrier Speed (EBS) using CRASH3 model.

    The CRASH3 model estimates impact speed from crush measurements using:
    EBS = sqrt((A*C_avg + B*C_avg^2/2) * L / m)

    Args:
        mediciones_C: List of 6 crush measurements (C1-C6) in cm
        ancho_zona: Width of crush zone in cm
        masa: Vehicle mass in kg
        coef_a: Stiffness coefficient A (from NHTSA database)
        coef_b: Stiffness coefficient B (from NHTSA database)

    Returns:
        EBS in km/h
    """
    if not mediciones_C or len(mediciones_C) < 6:
        raise ValueError("Need 6 crush measurements (C1-C6)")

    if masa <= 0:
        raise ValueError("Mass must be positive")

    # Calculate average crush depth
    c_avg = sum(mediciones_C) / len(mediciones_C)

    # Convert cm to m for calculations
    c_avg_m = c_avg / 100
    ancho_m = ancho_zona / 100

    # Energy absorbed (simplified CRASH3)
    # E = (A * C_avg + B * C_avg^2 / 2) * L
    energy_per_meter = coef_a * c_avg_m + coef_b * (c_avg_m ** 2) / 2
    total_energy = energy_per_meter * ancho_m * 1000  # Convert to Joules

    # EBS = sqrt(2 * E / m)
    ebs_ms = math.sqrt(2 * total_energy / masa) if total_energy > 0 else 0

    # Convert m/s to km/h
    ebs_kmh = ebs_ms * 3.6

    return round(ebs_kmh, 1)


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

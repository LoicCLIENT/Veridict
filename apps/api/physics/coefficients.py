"""
Vehicle Stiffness Coefficients Database.

Based on NHTSA crash test data.
Coefficients A and B for the CRASH3 model.
"""

# Default coefficients by vehicle category
# A in kPa (kN/m²), B in kPa/m — CRASH3 model with C in meters, L in meters
# Formula: E [kJ] = (A·C + B·C²/2) · L  →  E [J] = E[kJ] · 1000
# Source: derived from NHTSA barrier crash test data (SI calibration)
VEHICLE_COEFFICIENTS = {
    "subcompact": {"A": 580, "B": 1900, "mass_range": (900, 1100)},
    "compact":    {"A": 680, "B": 2300, "mass_range": (1100, 1300)},
    "midsize":    {"A": 760, "B": 2600, "mass_range": (1300, 1500)},
    "fullsize":   {"A": 850, "B": 2900, "mass_range": (1500, 1800)},
    "suv_small":  {"A": 900, "B": 3100, "mass_range": (1400, 1700)},
    "suv_large":  {"A": 1050, "B": 3500, "mass_range": (1800, 2500)},
    "pickup":     {"A": 980, "B": 3300, "mass_range": (1600, 2200)},
    "van":        {"A": 820, "B": 2700, "mass_range": (1700, 2300)},
    "motorcycle": {"A": 180, "B": 600,  "mass_range": (150, 400)},
}

# Specific vehicle models (sample data)
SPECIFIC_VEHICLES = {
    "seat leon":        {"A": 700, "B": 2400, "category": "compact"},
    "volkswagen golf":  {"A": 710, "B": 2450, "category": "compact"},
    "renault clio":     {"A": 610, "B": 2050, "category": "subcompact"},
    "ford focus":       {"A": 690, "B": 2350, "category": "compact"},
    "bmw serie 3":      {"A": 800, "B": 2750, "category": "midsize"},
    "mercedes clase c": {"A": 820, "B": 2800, "category": "midsize"},
    "toyota corolla":   {"A": 695, "B": 2370, "category": "compact"},
    "peugeot 208":      {"A": 600, "B": 2000, "category": "subcompact"},
    "citroen c3":       {"A": 590, "B": 1970, "category": "subcompact"},
    "audi a4":          {"A": 790, "B": 2700, "category": "midsize"},
}


def get_vehicle_coefficients(modelo: str) -> dict:
    """
    Get stiffness coefficients for a vehicle model.

    Args:
        modelo: Vehicle model name

    Returns:
        dict with 'coef_a', 'coef_b', 'category', 'source'
    """
    modelo_lower = modelo.lower()

    # Check specific vehicles first
    for name, data in SPECIFIC_VEHICLES.items():
        if name in modelo_lower:
            return {
                "modelo": modelo,
                "coef_a": data["A"],
                "coef_b": data["B"],
                "categoria": data["category"],
                "fuente": "NHTSA Database (specific)",
            }

    # Fall back to category estimation
    # Try to determine category from model name
    if any(x in modelo_lower for x in ["suv", "q5", "q7", "x3", "x5", "rav4", "cr-v"]):
        category = "suv_small"
    elif any(x in modelo_lower for x in ["pickup", "ranger", "hilux", "navara"]):
        category = "pickup"
    elif any(x in modelo_lower for x in ["van", "vito", "transporter", "berlingo"]):
        category = "van"
    elif any(x in modelo_lower for x in ["serie 5", "serie 7", "clase e", "clase s", "a6", "a8"]):
        category = "fullsize"
    elif any(x in modelo_lower for x in ["serie 3", "clase c", "a4", "passat"]):
        category = "midsize"
    elif any(x in modelo_lower for x in ["polo", "ibiza", "fiesta", "corsa", "208", "clio"]):
        category = "subcompact"
    else:
        category = "compact"  # Default

    data = VEHICLE_COEFFICIENTS[category]
    return {
        "modelo": modelo,
        "coef_a": data["A"],
        "coef_b": data["B"],
        "categoria": category,
        "masa_estimada_kg": sum(data["mass_range"]) / 2,
        "fuente": "NHTSA Database (category estimate)",
    }


def get_category_from_mass(masa_kg: float) -> str:
    """Determine vehicle category from mass."""
    for category, data in VEHICLE_COEFFICIENTS.items():
        min_mass, max_mass = data["mass_range"]
        if min_mass <= masa_kg <= max_mass:
            return category

    # Default based on mass
    if masa_kg < 900:
        return "motorcycle"
    elif masa_kg > 2000:
        return "suv_large"
    else:
        return "midsize"

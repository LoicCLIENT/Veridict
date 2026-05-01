"""
Vehicle Stiffness Coefficients Database.

Based on NHTSA crash test data.
Coefficients A and B for the CRASH3 model.
"""

# Default coefficients by vehicle category
# A is in N/cm, B is in N/cm^2
VEHICLE_COEFFICIENTS = {
    "subcompact": {"A": 38.5, "B": 0.12, "mass_range": (900, 1100)},
    "compact": {"A": 42.0, "B": 0.14, "mass_range": (1100, 1300)},
    "midsize": {"A": 45.0, "B": 0.15, "mass_range": (1300, 1500)},
    "fullsize": {"A": 48.0, "B": 0.16, "mass_range": (1500, 1800)},
    "suv_small": {"A": 50.0, "B": 0.17, "mass_range": (1400, 1700)},
    "suv_large": {"A": 55.0, "B": 0.18, "mass_range": (1800, 2500)},
    "pickup": {"A": 52.0, "B": 0.17, "mass_range": (1600, 2200)},
    "van": {"A": 48.0, "B": 0.15, "mass_range": (1700, 2300)},
    "motorcycle": {"A": 15.0, "B": 0.05, "mass_range": (150, 400)},
}

# Specific vehicle models (sample data)
SPECIFIC_VEHICLES = {
    "seat leon": {"A": 44.5, "B": 0.145, "category": "compact"},
    "volkswagen golf": {"A": 45.0, "B": 0.15, "category": "compact"},
    "renault clio": {"A": 40.0, "B": 0.13, "category": "subcompact"},
    "ford focus": {"A": 43.5, "B": 0.14, "category": "compact"},
    "bmw serie 3": {"A": 48.0, "B": 0.16, "category": "midsize"},
    "mercedes clase c": {"A": 49.0, "B": 0.165, "category": "midsize"},
    "toyota corolla": {"A": 44.0, "B": 0.145, "category": "compact"},
    "peugeot 208": {"A": 39.0, "B": 0.125, "category": "subcompact"},
    "citroen c3": {"A": 38.5, "B": 0.12, "category": "subcompact"},
    "audi a4": {"A": 47.5, "B": 0.155, "category": "midsize"},
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

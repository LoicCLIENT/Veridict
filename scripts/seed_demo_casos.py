#!/usr/bin/env python3
"""
Seed demo cases into the database.
Run with: python scripts/seed_demo_casos.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from datetime import datetime
from models import (
    Caso,
    EstadoCaso,
    TipoColision,
    Ubicacion,
    Vehiculo,
    Resultado,
    Evento,
    CalculoFisico,
    Infraccion,
    Veredicto,
    CompatibilidadVersiones,
)


def create_demo_casos():
    """Create demo cases for the hackathon presentation."""

    casos = []

    # Caso 1: Cambio de carril M-30 Madrid
    caso1 = Caso(
        id="demo-1",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 15, 14, 30),
        ubicacion=Ubicacion(lat=40.4168, lon=-3.7038),
        tipo_colision=TipoColision.LATERAL,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="1234 ABC",
                modelo="Seat Leon 2020",
                masa_kg=1350,
                coef_rigidez_a=44.5,
                coef_rigidez_b=0.145,
                mediciones_C=[12.5, 15.2, 18.3, 16.1, 14.0, 11.2],
                ancho_zona_danada_cm=85,
                version_conductor="Circulaba a 50 km/h cuando el otro vehiculo invadio mi carril sin previo aviso",
            ),
            Vehiculo(
                id="B",
                matricula="5678 DEF",
                modelo="Volkswagen Golf 2019",
                masa_kg=1400,
                coef_rigidez_a=45.0,
                coef_rigidez_b=0.15,
                mediciones_C=[8.2, 11.5, 14.1, 12.3, 9.8, 7.5],
                ancho_zona_danada_cm=65,
                version_conductor="Estaba cambiando de carril correctamente cuando el otro vehiculo acelero y me golpeo",
            ),
        ],
    )
    casos.append(caso1)

    # Caso 2: Atropello en Alcala de Henares
    caso2 = Caso(
        id="demo-2",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 20, 9, 15),
        ubicacion=Ubicacion(lat=40.4825, lon=-3.3645),
        tipo_colision=TipoColision.ATROPELLO,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="9012 GHI",
                modelo="Renault Clio 2021",
                masa_kg=1200,
                coef_rigidez_a=40.0,
                coef_rigidez_b=0.13,
                mediciones_C=[5.5, 8.2, 10.1, 8.8, 6.2, 4.1],
                ancho_zona_danada_cm=120,
                version_conductor="Circulaba a 30 km/h respetando el limite. El peaton cruzo corriendo sin mirar.",
            ),
        ],
    )
    casos.append(caso2)

    # Caso 3: Alcance trasero A-6
    caso3 = Caso(
        id="demo-3",
        estado=EstadoCaso.COMPLETADO,
        fecha_accidente=datetime(2026, 4, 22, 18, 45),
        ubicacion=Ubicacion(lat=40.4500, lon=-3.7200),
        tipo_colision=TipoColision.ALCANCE,
        vehiculos=[
            Vehiculo(
                id="A",
                matricula="3456 JKL",
                modelo="BMW Serie 3 2022",
                masa_kg=1550,
                coef_rigidez_a=48.0,
                coef_rigidez_b=0.16,
                mediciones_C=[18.5, 22.1, 25.8, 23.2, 19.5, 15.8],
                ancho_zona_danada_cm=140,
                version_conductor="El vehiculo de delante freno bruscamente sin motivo aparente",
            ),
            Vehiculo(
                id="B",
                matricula="7890 MNO",
                modelo="Toyota Corolla 2020",
                masa_kg=1380,
                coef_rigidez_a=44.0,
                coef_rigidez_b=0.145,
                mediciones_C=[12.2, 16.5, 19.8, 17.1, 13.5, 10.2],
                ancho_zona_danada_cm=120,
                version_conductor="Tuve que frenar de emergencia porque habia un objeto en la carretera",
            ),
        ],
    )
    casos.append(caso3)

    return casos


def main():
    print("Seeding demo cases...")
    casos = create_demo_casos()

    for caso in casos:
        print(f"  Created: {caso.id} - {caso.tipo_colision.value}")

    print(f"\nTotal: {len(casos)} cases seeded")
    print("\nTo use these cases, start the API server:")
    print("  cd apps/api")
    print("  uvicorn main:app --reload")
    print("\nThen access: http://localhost:8000/api/demo/casos")


if __name__ == "__main__":
    main()

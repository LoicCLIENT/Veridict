"""
Test script for Veridict visualization modules.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.visualization import (
    crear_croquis_escena,
    crear_diagrama_wad,
    crear_diagrama_craneo,
    crear_diagrama_corporal,
)


def test_scene_overhead():
    """Test overhead scene diagram."""
    print("Testing SceneOverheadDiagram...")

    vehiculos = [
        {
            "id": "V1",
            "tipo": "turismo",
            "x": -8,
            "y": 2,
            "orientacion": 0,
            "velocidad": 50,
        },
        {
            "id": "V2",
            "tipo": "turismo",
            "x": 5,
            "y": -1.5,
            "orientacion": 180,
            "velocidad": 40,
        },
    ]

    pdi = {"x": 0, "y": 0.5}

    huellas = [
        {
            "tipo": "huella_frenada",
            "puntos": [
                {"x": -15, "y": 2},
                {"x": -10, "y": 2},
                {"x": -8, "y": 2},
            ],
            "ancho": 0.2,
        }
    ]

    svg = crear_croquis_escena(
        vehiculos=vehiculos,
        pdi=pdi,
        huellas=huellas,
        ancho_carretera=7.0,
        largo_carretera=40.0,
    )

    # Save to file
    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"scene_overhead_{timestamp}.svg"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Saved: {output_path}")
    print(f"  Size: {len(svg)} bytes")
    return True


def test_wad_diagram():
    """Test WAD diagram."""
    print("Testing WADDiagram...")

    svg = crear_diagrama_wad(
        velocidad_impacto=40,
        tipo_impacto="frontal",
        tipo_vehiculo="turismo",
        mostrar_ciclista=True,
    )

    # Save to file
    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"wad_frontal_{timestamp}.svg"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Saved: {output_path}")
    print(f"  Size: {len(svg)} bytes")
    return True


def test_skull_diagram():
    """Test skull anatomy diagram."""
    print("Testing SkullDiagram...")

    lesiones = [
        {
            "name": "Fractura lineal",
            "tipo": "fractura",
            "localizacion": "hueso parietal derecho",
            "gravedad": "grave",
        },
        {
            "name": "Contusion cerebral",
            "tipo": "contusion",
            "localizacion": "lobulo frontal",
            "gravedad": "moderada",
        },
    ]

    svg = crear_diagrama_craneo(
        zona_impacto="parietal",
        lesiones=lesiones,
    )

    # Save to file
    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"skull_diagram_{timestamp}.svg"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Saved: {output_path}")
    print(f"  Size: {len(svg)} bytes")
    return True


def test_body_diagram():
    """Test body anatomy diagram."""
    print("Testing BodyDiagram...")

    lesiones = [
        {"region": "head", "description": "TCE moderado", "ais_score": 3},
        {"region": "chest", "description": "Contusion pulmonar", "ais_score": 3},
        {"region": "lower_limbs", "description": "Fractura tibia", "ais_score": 2},
    ]

    svg = crear_diagrama_corporal(lesiones=lesiones)

    # Save to file
    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"body_diagram_{timestamp}.svg"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"  Saved: {output_path}")
    print(f"  Size: {len(svg)} bytes")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Veridict Visualization Module Tests")
    print("=" * 60)

    results = []

    try:
        results.append(("Scene Overhead", test_scene_overhead()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Scene Overhead", False))

    try:
        results.append(("WAD Diagram", test_wad_diagram()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("WAD Diagram", False))

    try:
        results.append(("Skull Diagram", test_skull_diagram()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Skull Diagram", False))

    try:
        results.append(("Body Diagram", test_body_diagram()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Body Diagram", False))

    print("\n" + "=" * 60)
    print("Results:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    print("=" * 60)

    # Return exit code
    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

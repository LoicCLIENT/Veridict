"""
Test de generación de escenas - Verifica el pipeline completo.

Ejecutar: python -m agents.visualization.scene.test_scene_generation
"""

import json
import os
import sys

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Añadir el directorio raíz del API al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from agents.visualization.scene import (
    DatosCaso,
    generar_escena_desde_caso,
    validate_and_fix,
    generar_screenshots_caso,
    calcular_distancia_frenado,
    calcular_velocidad_desde_huella,
    COEF_FRICCION,
)


def test_calculos_fisicos():
    """Test de cálculos físicos puros."""
    print("\n" + "=" * 60)
    print("TEST: Cálculos Físicos")
    print("=" * 60)

    # Test distancia de frenado
    print("\n📏 Distancia de frenado (50 km/h, asfalto seco):")
    d = calcular_distancia_frenado(50, COEF_FRICCION["seco"])
    print(f"   d = {d:.2f} m")
    assert 10 < d < 20, f"Distancia fuera de rango esperado: {d}"

    print("\n📏 Distancia de frenado (80 km/h, asfalto mojado):")
    d = calcular_distancia_frenado(80, COEF_FRICCION["mojado"])
    print(f"   d = {d:.2f} m")
    assert 40 < d < 80, f"Distancia fuera de rango esperado: {d}"

    # Test velocidad desde huella
    print("\n🚗 Velocidad desde huella (15m, asfalto seco):")
    v = calcular_velocidad_desde_huella(15, COEF_FRICCION["seco"])
    print(f"   v = {v:.2f} km/h")
    assert 40 < v < 60, f"Velocidad fuera de rango esperado: {v}"

    print("\n✅ Cálculos físicos: OK")


def test_escena_lateral():
    """Test de generación de escena tipo lateral (cambio de carril)."""
    print("\n" + "=" * 60)
    print("TEST: Escena Lateral (Cambio de Carril)")
    print("=" * 60)

    datos = DatosCaso(
        tipo_colision="lateral",
        tipo_via="recta",
        vehiculo_a_velocidad_inicial=67.0,
        vehiculo_a_huella_frenada=12.5,
        vehiculo_a_tipo="turismo",
        vehiculo_a_carril=1,
        vehiculo_b_velocidad_inicial=55.0,
        vehiculo_b_huella_frenada=8.0,
        vehiculo_b_tipo="turismo",
        vehiculo_b_carril=2,
        condicion_via="seco",
        num_carriles=2,
        limite_velocidad=50,
    )

    print(f"\n📋 Datos de entrada:")
    print(f"   Vehículo A: {datos.vehiculo_a_velocidad_inicial} km/h, frenada {datos.vehiculo_a_huella_frenada}m")
    print(f"   Vehículo B: {datos.vehiculo_b_velocidad_inicial} km/h, frenada {datos.vehiculo_b_huella_frenada}m")

    scene = generar_escena_desde_caso(datos)

    print(f"\n📊 Escena generada:")
    print(f"   Tipo vía: {scene['road']['type']}")
    print(f"   Carriles: {scene['road']['lanes']}")
    print(f"   Puntos trayectoria A: {len(scene['vehicleA']['trajectory'])}")
    print(f"   Puntos trayectoria B: {len(scene['vehicleB']['trajectory'])}")
    print(f"   Tiempo impacto: {scene['impact']['time']:.2f}s")
    print(f"   Posición impacto: ({scene['impact']['x']:.1f}, {scene['impact']['y']:.1f})")

    # Validar
    scene, validation = validate_and_fix(scene)
    print(f"\n🔍 Validación:")
    print(f"   Válido: {validation.is_valid}")
    print(f"   Warnings: {len(validation.warnings)}")
    for w in validation.warnings:
        print(f"      ⚠️  {w}")
    print(f"   Errores: {len(validation.errors)}")
    for e in validation.errors:
        print(f"      ❌ {e}")
    print(f"   Correcciones: {len(validation.corrections_applied)}")
    for c in validation.corrections_applied:
        print(f"      🔧 {c}")

    assert validation.is_valid, "Escena lateral no válida"
    print("\n✅ Escena lateral: OK")

    return scene


def test_escena_alcance():
    """Test de generación de escena tipo alcance (trasero)."""
    print("\n" + "=" * 60)
    print("TEST: Escena Alcance (Colisión Trasera)")
    print("=" * 60)

    datos = DatosCaso(
        tipo_colision="alcance",
        tipo_via="recta",
        vehiculo_a_velocidad_inicial=80.0,
        vehiculo_a_huella_frenada=25.0,
        vehiculo_a_tipo="turismo",
        vehiculo_a_carril=1,
        vehiculo_b_velocidad_inicial=30.0,
        vehiculo_b_huella_frenada=5.0,
        vehiculo_b_tipo="turismo",
        vehiculo_b_carril=1,  # Mismo carril
        condicion_via="mojado",
        num_carriles=2,
        limite_velocidad=60,
    )

    print(f"\n📋 Datos de entrada:")
    print(f"   Vehículo A: {datos.vehiculo_a_velocidad_inicial} km/h (alcanzador)")
    print(f"   Vehículo B: {datos.vehiculo_b_velocidad_inicial} km/h (alcanzado)")
    print(f"   Condición: {datos.condicion_via}")

    scene = generar_escena_desde_caso(datos)
    scene, validation = validate_and_fix(scene)

    print(f"\n📊 Escena generada:")
    print(f"   Velocidad impacto A: {scene['vehicleA']['impactSpeed']:.1f} km/h")
    print(f"   Velocidad impacto B: {scene['vehicleB']['impactSpeed']:.1f} km/h")
    print(f"   Delta-V A: {scene['impact']['deltaV_A']:.1f} km/h")
    print(f"   Delta-V B: {scene['impact']['deltaV_B']:.1f} km/h")

    print(f"\n🔍 Validación: {'✅' if validation.is_valid else '❌'}")
    for w in validation.warnings:
        print(f"      ⚠️  {w}")

    assert validation.is_valid, "Escena alcance no válida"
    print("\n✅ Escena alcance: OK")

    return scene


def test_escena_atropello():
    """Test de generación de escena tipo atropello."""
    print("\n" + "=" * 60)
    print("TEST: Escena Atropello")
    print("=" * 60)

    datos = DatosCaso(
        tipo_colision="atropello",
        tipo_via="recta",
        vehiculo_a_velocidad_inicial=45.0,
        vehiculo_a_huella_frenada=8.0,
        vehiculo_a_tipo="turismo",
        vehiculo_a_carril=1,
        vehiculo_b_velocidad_inicial=5.0,  # Peatón caminando
        vehiculo_b_huella_frenada=0.0,
        vehiculo_b_tipo="peaton",
        vehiculo_b_carril=1,
        condicion_via="seco",
        num_carriles=2,
        limite_velocidad=50,
    )

    print(f"\n📋 Datos de entrada:")
    print(f"   Vehículo: {datos.vehiculo_a_velocidad_inicial} km/h")
    print(f"   Peatón: {datos.vehiculo_b_velocidad_inicial} km/h")

    scene = generar_escena_desde_caso(datos)
    scene, validation = validate_and_fix(scene)

    print(f"\n📊 Escena generada:")
    print(f"   Puntos trayectoria vehículo: {len(scene['vehicleA']['trajectory'])}")
    print(f"   Puntos trayectoria peatón: {len(scene['vehicleB']['trajectory'])}")
    print(f"   Distancia frenado calculada: {scene['vehicleA']['brakeDistance']:.1f}m")

    print(f"\n🔍 Validación: {'✅' if validation.is_valid else '❌'}")

    assert validation.is_valid, "Escena atropello no válida"
    print("\n✅ Escena atropello: OK")

    return scene


def test_screenshots(scene: dict):
    """Test de generación de screenshots."""
    print("\n" + "=" * 60)
    print("TEST: Generación de Screenshots")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "uploads",
        "_test_screenshots"
    )

    print(f"\n📁 Directorio de salida: {output_dir}")

    screenshots = generar_screenshots_caso(
        scene_data=scene,
        case_id="TEST_001",
        output_dir=output_dir,
    )

    print(f"\n📸 Screenshots generados: {len(screenshots)}")
    for ss in screenshots:
        print(f"   - {ss['nombre']}: {ss['descripcion']}")
        print(f"     SVG: {ss['svg_path']}")

    assert len(screenshots) >= 3, "Deben generarse al menos 3 screenshots"
    print("\n✅ Screenshots: OK")

    return screenshots


def test_json_output(scene: dict):
    """Verifica que el JSON de salida sea compatible con el frontend."""
    print("\n" + "=" * 60)
    print("TEST: Compatibilidad JSON Frontend")
    print("=" * 60)

    # Campos requeridos por AccidentSceneData (TypeScript interface)
    required_road_fields = ["type", "lanes", "laneWidth", "speedLimit"]
    required_vehicle_fields = ["trajectory", "brakeStartTime", "brakeDistance", "initialSpeed", "impactSpeed"]
    required_impact_fields = ["x", "y", "time", "angle", "deltaV_A", "deltaV_B"]
    required_metadata_fields = ["scaleMetersPerUnit", "weatherCondition", "roadCondition", "visibility"]

    print("\n🔍 Verificando campos requeridos...")

    # Road
    for field in required_road_fields:
        assert field in scene["road"], f"Campo road.{field} faltante"
    print("   ✅ road: OK")

    # VehicleA
    for field in required_vehicle_fields:
        assert field in scene["vehicleA"], f"Campo vehicleA.{field} faltante"
    print("   ✅ vehicleA: OK")

    # VehicleB
    for field in required_vehicle_fields:
        assert field in scene["vehicleB"], f"Campo vehicleB.{field} faltante"
    print("   ✅ vehicleB: OK")

    # Impact
    for field in required_impact_fields:
        assert field in scene["impact"], f"Campo impact.{field} faltante"
    print("   ✅ impact: OK")

    # Metadata
    for field in required_metadata_fields:
        assert field in scene["metadata"], f"Campo metadata.{field} faltante"
    print("   ✅ metadata: OK")

    # Verificar que se puede serializar a JSON
    json_str = json.dumps(scene, indent=2)
    assert len(json_str) > 100, "JSON muy corto"
    print(f"\n📄 JSON válido ({len(json_str)} caracteres)")

    # Mostrar ejemplo del JSON
    print("\n📋 Ejemplo de salida (primeros 500 chars):")
    print(json_str[:500] + "...")

    print("\n✅ Compatibilidad JSON: OK")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 60)
    print("🧪 SUITE DE TESTS: Sistema de Generación de Escenas")
    print("=" * 60)

    try:
        # Tests de física
        test_calculos_fisicos()

        # Tests de escenas
        scene_lateral = test_escena_lateral()
        scene_alcance = test_escena_alcance()
        scene_atropello = test_escena_atropello()

        # Test de JSON
        test_json_output(scene_lateral)

        # Test de screenshots (usando escena lateral)
        # test_screenshots(scene_lateral)  # Comentado: requiere output dir

        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

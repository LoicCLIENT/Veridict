"""
Demo: Generación de escena de accidente para AccidentScene2D

Este script muestra cómo generar datos parametrizados para el componente
de visualización 2D del frontend.

Ejecutar: py -3 -m agents.visualization.scene.demo_escena
"""

import json
import os
import sys

# Fix encoding Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from agents.visualization.scene import (
    DatosCaso,
    generar_escena_desde_caso,
    validate_and_fix,
)


def demo_cambio_carril():
    """
    Caso real: Vehículo A circula a 67 km/h por carril derecho.
    Vehículo B a 55 km/h inicia cambio de carril sin mirar.
    Colisión lateral.
    """
    print("\n" + "="*70)
    print("CASO: Colisión lateral por cambio de carril imprudente")
    print("="*70)

    # Datos extraídos del atestado/peritaje
    datos = DatosCaso(
        tipo_colision="lateral",
        tipo_via="recta",

        # Vehículo A - Circulaba recto
        vehiculo_a_tipo="turismo",
        vehiculo_a_velocidad_inicial=67.0,   # km/h (declaración + EDR)
        vehiculo_a_huella_frenada=12.5,      # metros medidos en escena
        vehiculo_a_carril=1,                  # Carril derecho
        vehiculo_a_masa=1450.0,               # kg (ficha técnica)

        # Vehículo B - Cambió de carril
        vehiculo_b_tipo="turismo",
        vehiculo_b_velocidad_inicial=55.0,   # km/h
        vehiculo_b_huella_frenada=8.0,       # metros
        vehiculo_b_carril=2,                  # Carril izquierdo → invadió derecho
        vehiculo_b_masa=1320.0,

        # Impacto (calculado por CRASH3 o similar)
        delta_v_a=18.0,                       # km/h
        delta_v_b=22.0,                       # km/h
        angulo_impacto=25.0,                  # grados

        # Condiciones
        condicion_via="seco",
        num_carriles=2,
        limite_velocidad=50,
        clima="Despejado",
        visibilidad="Buena",
    )

    print("\n[ENTRADA] Datos del caso:")
    print(f"  Vehículo A: {datos.vehiculo_a_velocidad_inicial} km/h, frenada {datos.vehiculo_a_huella_frenada}m")
    print(f"  Vehículo B: {datos.vehiculo_b_velocidad_inicial} km/h, frenada {datos.vehiculo_b_huella_frenada}m")
    print(f"  Tipo colisión: {datos.tipo_colision}")
    print(f"  Condición vía: {datos.condicion_via}")

    # Generar escena
    scene = generar_escena_desde_caso(datos)
    scene, validation = validate_and_fix(scene)

    print("\n[SALIDA] AccidentSceneData generado:")
    print(f"  Puntos trayectoria A: {len(scene['vehicleA']['trajectory'])}")
    print(f"  Puntos trayectoria B: {len(scene['vehicleB']['trajectory'])}")
    print(f"  Vel. impacto A: {scene['vehicleA']['impactSpeed']:.1f} km/h")
    print(f"  Vel. impacto B: {scene['vehicleB']['impactSpeed']:.1f} km/h")
    print(f"  Tiempo total: {scene['impact']['time']:.2f}s")
    print(f"  Posición impacto: ({scene['impact']['x']:.1f}, {scene['impact']['y']:.1f})")

    print(f"\n[VALIDACION] {'OK' if validation.is_valid else 'ERRORES'}")
    if validation.warnings:
        for w in validation.warnings:
            print(f"  Aviso: {w}")

    return scene


def demo_alcance():
    """
    Caso: Colisión por alcance en retención de tráfico.
    Vehículo A no frena a tiempo.
    """
    print("\n" + "="*70)
    print("CASO: Colisión por alcance (rear-end)")
    print("="*70)

    datos = DatosCaso(
        tipo_colision="alcance",
        tipo_via="recta",

        # Vehículo A - El que alcanza (por detrás)
        vehiculo_a_tipo="turismo",
        vehiculo_a_velocidad_inicial=80.0,
        vehiculo_a_huella_frenada=35.0,
        vehiculo_a_carril=1,

        # Vehículo B - El alcanzado (delante, frenando)
        vehiculo_b_tipo="turismo",
        vehiculo_b_velocidad_inicial=25.0,  # Ya frenando
        vehiculo_b_huella_frenada=5.0,
        vehiculo_b_carril=1,  # Mismo carril

        delta_v_a=25.0,
        delta_v_b=15.0,
        angulo_impacto=0.0,  # Impacto directo trasero

        condicion_via="mojado",  # Lluvia
        limite_velocidad=60,
    )

    print("\n[ENTRADA] Datos del caso:")
    print(f"  Vehículo A (alcanzador): {datos.vehiculo_a_velocidad_inicial} km/h")
    print(f"  Vehículo B (alcanzado): {datos.vehiculo_b_velocidad_inicial} km/h")
    print(f"  Condición: {datos.condicion_via} (coef. fricción reducido)")

    scene = generar_escena_desde_caso(datos)
    scene, validation = validate_and_fix(scene)

    print("\n[SALIDA] AccidentSceneData generado:")
    print(f"  Vel. impacto A: {scene['vehicleA']['impactSpeed']:.1f} km/h")
    print(f"  Vel. impacto B: {scene['vehicleB']['impactSpeed']:.1f} km/h")
    print(f"  Delta-V A: {scene['impact']['deltaV_A']:.1f} km/h")
    print(f"  Delta-V B: {scene['impact']['deltaV_B']:.1f} km/h")

    return scene


def demo_atropello():
    """
    Caso: Atropello de peatón en paso de cebra.
    """
    print("\n" + "="*70)
    print("CASO: Atropello de peatón")
    print("="*70)

    datos = DatosCaso(
        tipo_colision="atropello",
        tipo_via="recta",

        # Vehículo
        vehiculo_a_tipo="turismo",
        vehiculo_a_velocidad_inicial=48.0,  # Ligeramente por encima del límite
        vehiculo_a_huella_frenada=10.0,
        vehiculo_a_carril=1,

        # Peatón
        vehiculo_b_tipo="peaton",
        vehiculo_b_velocidad_inicial=5.0,  # Caminando normal
        vehiculo_b_huella_frenada=0.0,
        vehiculo_b_carril=1,

        delta_v_a=15.0,
        delta_v_b=48.0,  # El peatón absorbe casi toda la energía

        condicion_via="seco",
        limite_velocidad=50,
    )

    print("\n[ENTRADA] Datos del caso:")
    print(f"  Vehículo: {datos.vehiculo_a_velocidad_inicial} km/h")
    print(f"  Peatón: {datos.vehiculo_b_velocidad_inicial} km/h (caminando)")
    print(f"  Huella frenada: {datos.vehiculo_a_huella_frenada}m")

    scene = generar_escena_desde_caso(datos)
    scene, validation = validate_and_fix(scene)

    print("\n[SALIDA] AccidentSceneData generado:")
    print(f"  Distancia frenado calculada: {scene['vehicleA']['brakeDistance']:.1f}m")
    print(f"  Vel. impacto vehículo: {scene['vehicleA']['impactSpeed']:.1f} km/h")
    print(f"  Tiempo hasta impacto: {scene['impact']['time']:.2f}s")

    return scene


def mostrar_json_ejemplo(scene: dict):
    """Muestra el JSON listo para el frontend."""
    print("\n" + "="*70)
    print("JSON para AccidentScene2D (ejemplo parcial)")
    print("="*70)

    # Mostrar estructura resumida
    ejemplo = {
        "road": scene["road"],
        "vehicleA": {
            "trajectory": scene["vehicleA"]["trajectory"][:3] + ["... más puntos ..."],
            "brakeStartTime": scene["vehicleA"]["brakeStartTime"],
            "brakeDistance": scene["vehicleA"]["brakeDistance"],
            "initialSpeed": scene["vehicleA"]["initialSpeed"],
            "impactSpeed": scene["vehicleA"]["impactSpeed"],
        },
        "impact": scene["impact"],
        "metadata": scene["metadata"],
    }

    print(json.dumps(ejemplo, indent=2, ensure_ascii=False))


def guardar_json_completo(scene: dict, filename: str):
    """Guarda el JSON completo en un archivo."""
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "uploads", "_demo_scenes"
    )
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=2, ensure_ascii=False)

    print(f"\n[GUARDADO] {filepath}")
    return filepath


def main():
    print("\n" + "#"*70)
    print("#  DEMO: Sistema de Generación de Escenas Veridict")
    print("#  Genera AccidentSceneData parametrizado desde datos del caso")
    print("#"*70)

    # Ejecutar demos
    scene_lateral = demo_cambio_carril()
    scene_alcance = demo_alcance()
    scene_atropello = demo_atropello()

    # Mostrar ejemplo de JSON
    mostrar_json_ejemplo(scene_lateral)

    # Guardar JSONs completos
    print("\n" + "="*70)
    print("Guardando JSONs completos...")
    print("="*70)

    guardar_json_completo(scene_lateral, "escena_lateral.json")
    guardar_json_completo(scene_alcance, "escena_alcance.json")
    guardar_json_completo(scene_atropello, "escena_atropello.json")

    print("\n" + "#"*70)
    print("#  Estos JSONs son directamente usables en <AccidentScene2D />")
    print("#  import sceneData from './escena_lateral.json'")
    print("#  <AccidentScene2D sceneData={sceneData} />")
    print("#"*70)


if __name__ == "__main__":
    main()

"""
Script de Iteracion Rapida para Mejora de Visualizaciones
Ejecuta un ciclo completo: generar -> comparar -> sugerir mejoras -> aplicar

Uso:
    python iterate.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import anthropic
import json
from datetime import datetime

# Importar modulos del sistema
from physics.croquis import generar_croquis_svg
from physics.reconstruction import reconstruir_accidente


def get_current_croquis_code() -> str:
    """Lee el codigo actual de croquis.py para que Claude lo mejore."""
    croquis_path = Path(__file__).parent.parent / "physics" / "croquis.py"
    with open(croquis_path, 'r', encoding='utf-8') as f:
        return f.read()


def iterate_with_feedback(reference_description: str = None):
    """
    Ejecuta una iteracion de mejora usando feedback de Claude.

    Args:
        reference_description: Descripcion textual del documento profesional de referencia
    """

    client = anthropic.Anthropic()
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    # 1. Obtener codigo actual
    print("\n[1/4] Leyendo codigo actual de croquis.py...")
    current_code = get_current_croquis_code()

    # 2. Generar SVG de ejemplo
    print("[2/4] Generando SVG de ejemplo...")
    caso_ejemplo = {
        "vehiculos": [
            {
                "id": "A",
                "tipo": "turismo",
                "marca": "BMW",
                "modelo": "Serie 3",
                "masa": 1500,
                "posicion": {"x": 12, "y": 8},
                "orientacion": 45,
                "velocidad_pre": 65,
                "velocidad_post": 25,
                "delta_v": 40,
                "color": "#3B82F6"
            },
            {
                "id": "B",
                "tipo": "turismo",
                "marca": "Volkswagen",
                "modelo": "Golf",
                "masa": 1200,
                "posicion": {"x": 18, "y": 5},
                "orientacion": -60,
                "velocidad_pre": 45,
                "velocidad_post": 15,
                "delta_v": 30,
                "color": "#EF4444"
            }
        ],
        "pdi": {"x": 15, "y": 6},
        "trayectorias": [
            {"vehiculo": "A", "puntos": [{"x": 5, "y": 12}, {"x": 10, "y": 9}, {"x": 15, "y": 6}]},
            {"vehiculo": "B", "puntos": [{"x": 25, "y": 3}, {"x": 20, "y": 4}, {"x": 15, "y": 6}]}
        ],
        "huellas": [
            {"tipo": "frenada", "vehiculo": "A", "puntos": [{"x": 5, "y": 10}, {"x": 14, "y": 7}]},
            {"tipo": "derrape", "vehiculo": "B", "puntos": [{"x": 16, "y": 4}, {"x": 22, "y": 3}]}
        ]
    }

    svg_content = generar_croquis_svg(
        vehiculos=caso_ejemplo["vehiculos"],
        pdi=caso_ejemplo["pdi"],
        trayectorias=caso_ejemplo["trayectorias"],
        huellas=caso_ejemplo["huellas"],
        titulo="Croquis de Ejemplo - Entrenamiento"
    )

    # Guardar SVG
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    svg_path = output_dir / f"iteration_{timestamp}.svg"
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"    SVG guardado: {svg_path}")

    # 3. Pedir mejoras a Claude
    print("[3/4] Solicitando mejoras a Claude...")

    reference_context = ""
    if reference_description:
        reference_context = f"""
## REFERENCIA PROFESIONAL (descripcion del documento de peritaje):
{reference_description}
"""

    prompt = f"""Eres un experto en visualizacion forense de accidentes de trafico y programacion Python/SVG.

## CODIGO ACTUAL DE GENERACION DE CROQUIS:
```python
{current_code}
```

## SVG GENERADO ACTUALMENTE:
```svg
{svg_content}
```
{reference_context}

## TAREA:
Analiza el codigo y SVG actual, y proporciona MEJORAS CONCRETAS para acercarnos a la calidad de un documento profesional de peritaje.

Los documentos profesionales de peritaje incluyen:
- Vehiculos con siluetas realistas (no rectangulos simples)
- Representaciones en perspectiva o isometrica
- Gradientes y sombras sutiles para dar profundidad
- Flechas de velocidad mas elaboradas con puntas bien definidas
- Mejor tipografia y leyendas
- Iconos para el PDI mas profesionales
- Escala grafica visible
- Norte orientativo
- Cuadricula de referencia

RESPONDE EN JSON con esta estructura exacta:
{{
    "analisis_actual": "Breve analisis del SVG actual",
    "mejoras": [
        {{
            "titulo": "Nombre de la mejora",
            "descripcion": "Que mejora y por que",
            "prioridad": "alta|media|baja",
            "codigo_python": "Codigo Python/SVG para implementar esta mejora (funcion o fragmento)"
        }}
    ],
    "funcion_mejorada": "Codigo completo de una funcion auxiliar nueva que mejore el croquis (ej: dibujar_vehiculo_realista)"
}}

Enfocate en 3-5 mejoras concretas e implementables. El codigo debe ser funcional y poder integrarse en croquis.py."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text

    # Extraer JSON
    import re
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            improvements = json.loads(json_match.group())
        except json.JSONDecodeError:
            improvements = {"raw": response_text}
    else:
        improvements = {"raw": response_text}

    # Guardar resultado
    result_path = output_dir / f"improvements_{timestamp}.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(improvements, f, indent=2, ensure_ascii=False)

    # 4. Mostrar resumen
    print("[4/4] Mostrando mejoras sugeridas...\n")
    print("="*60)
    print("MEJORAS SUGERIDAS POR CLAUDE")
    print("="*60)

    if "analisis_actual" in improvements:
        print(f"\nAnalisis: {improvements['analisis_actual'][:200]}...")

    if "mejoras" in improvements:
        print("\nMejoras prioritarias:")
        for i, mejora in enumerate(improvements["mejoras"], 1):
            print(f"\n{i}. [{mejora.get('prioridad', 'N/A').upper()}] {mejora.get('titulo', 'Sin titulo')}")
            print(f"   {mejora.get('descripcion', '')[:100]}...")

    if "funcion_mejorada" in improvements:
        print("\n" + "-"*60)
        print("NUEVA FUNCION SUGERIDA:")
        print("-"*60)
        print(improvements["funcion_mejorada"][:800])
        print("..." if len(improvements.get("funcion_mejorada", "")) > 800 else "")

    print("\n" + "="*60)
    print(f"Resultados guardados en: {result_path}")
    print("="*60)

    return improvements


def interactive_mode():
    """Modo interactivo para iterar multiples veces."""

    print("\n" + "#"*60)
    print("# MODO INTERACTIVO DE ITERACION")
    print("#"*60)

    print("""
Este modo te permite iterar sobre las visualizaciones.

Opciones:
  1. Ejecutar iteracion (generar SVG + obtener mejoras)
  2. Aplicar mejora especifica al codigo
  3. Ver historial de iteraciones
  4. Salir

""")

    while True:
        choice = input("\nSelecciona opcion (1-4): ").strip()

        if choice == "1":
            ref = input("Descripcion de referencia profesional (Enter para omitir): ").strip()
            iterate_with_feedback(ref if ref else None)

        elif choice == "2":
            print("Para aplicar mejoras, edita manualmente physics/croquis.py")
            print("con el codigo sugerido en el JSON de improvements.")

        elif choice == "3":
            output_dir = Path(__file__).parent / "outputs"
            files = sorted(output_dir.glob("improvements_*.json"), reverse=True)
            print(f"\nHistorial ({len(files)} iteraciones):")
            for f in files[:5]:
                print(f"  - {f.name}")

        elif choice == "4":
            print("Saliendo...")
            break

        else:
            print("Opcion no valida")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--reference", "-r", help="Descripcion de documento de referencia")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        iterate_with_feedback(args.reference)

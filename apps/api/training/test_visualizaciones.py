"""
Script de prueba para el sistema de visualizaciones profesionales.
Genera ejemplos de cada tipo de visualizacion y los guarda en el directorio de outputs.

Uso:
    python training/test_visualizaciones.py
"""

import os
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from datetime import datetime

# Importar los generadores de visualizacion
from physics.visualizacion_profesional import (
    generar_croquis_profesional,
    generar_diagrama_calculo,
    generar_diagrama_wad,
    generar_grafico_energia,
    generar_secuencia_temporal,
)


def guardar_svg(svg_content: str, nombre: str, output_dir: Path) -> str:
    """Guarda un SVG y retorna el path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{nombre}_{timestamp}.svg"
    filepath = output_dir / filename
    filepath.write_text(svg_content, encoding='utf-8')
    return str(filepath)


def test_croquis_profesional(output_dir: Path):
    """Genera un croquis profesional de ejemplo."""
    print("\n[1/5] Generando Croquis Profesional...")

    vehiculos = [
        {
            "id": "A",
            "tipo": "turismo",
            "marca": "SEAT",
            "modelo": "Ibiza",
            "color": "#2563EB",
            "posicion": {"x": -10, "y": 6},
            "orientacion": 20,
            "velocidad_pre": 55,
            "delta_v": 32,
            "masa": 1150,
        },
        {
            "id": "A",  # Posicion final
            "tipo": "turismo",
            "color": "#2563EB",
            "posicion": {"x": 5, "y": 2},
            "orientacion": 45,
            "es_posicion_final": True,
        },
        {
            "id": "B",
            "tipo": "ciclista",
            "marca": "",
            "modelo": "Ciclista",
            "color": "#DC2626",
            "posicion": {"x": 3, "y": -2},
            "orientacion": -90,
            "velocidad_pre": 20,
            "delta_v": 20,
            "masa": 85,
        },
    ]

    pdi = {"x": 0, "y": 0}

    trayectorias = [
        {"vehiculo": "A", "puntos": [{"x": -18, "y": 10}, {"x": -10, "y": 6}, {"x": 0, "y": 0}]},
        {"vehiculo": "B", "puntos": [{"x": 10, "y": -5}, {"x": 3, "y": -2}, {"x": 0, "y": 0}]},
    ]

    huellas = [
        {"tipo": "frenada", "vehiculo": "A", "puntos": [{"x": -15, "y": 8}, {"x": -6, "y": 4}]},
        {"tipo": "arrastre", "vehiculo": "B", "puntos": [{"x": 1, "y": 0}, {"x": 8, "y": -3}]},
    ]

    mediciones = [
        {"inicio": {"x": -15, "y": 8}, "fin": {"x": -6, "y": 4}, "valor": 10.5, "unidad": "m"},
    ]

    svg = generar_croquis_profesional(
        vehiculos=vehiculos,
        pdi=pdi,
        trayectorias=trayectorias,
        huellas=huellas,
        mediciones=mediciones,
        titulo="Atropello a Ciclista",
        subtitulo="Reconstruccion Veridict AI",
    )

    path = guardar_svg(svg, "croquis_profesional", output_dir)
    print(f"    -> Guardado: {path}")
    return path


def test_diagrama_calculo(output_dir: Path):
    """Genera un diagrama de calculo tipo SamRAT."""
    print("\n[2/5] Generando Diagrama de Calculo...")

    svg = generar_diagrama_calculo(
        titulo="Calculo de Velocidad por Huella de Frenada (Stannard-Baker)",
        formula="v = √(2 · μ · g · d) → v = √(2 × 0.75 × 9.81 × 18.5)",
        variables={
            "μ (coef. friccion)": {"valor": 0.75, "unidad": "", "descripcion": "Asfalto seco"},
            "g (gravedad)": {"valor": 9.81, "unidad": "m/s²", "descripcion": "Constante"},
            "d (distancia huella)": {"valor": 18.5, "unidad": "m", "descripcion": "Medida in situ"},
            "pendiente": {"valor": 0, "unidad": "%", "descripcion": "Terreno llano"},
        },
        resultado={
            "valor": 59.3,
            "unidad": "km/h",
            "descripcion": "Velocidad minima al inicio de la huella",
        },
        fases=[
            {
                "nombre": "Percepcion-Reaccion",
                "tiempo": 1.0,
                "distancia": 16.5,
                "descripcion": "Tiempo standard 1s",
            },
            {
                "nombre": "Ejecucion Frenado",
                "tiempo": 0.3,
                "distancia": 4.9,
                "descripcion": "Activacion sistema",
            },
            {
                "nombre": "Frenada Efectiva",
                "tiempo": 2.25,
                "distancia": 18.5,
                "descripcion": "Huella visible calzada",
            },
        ],
    )

    path = guardar_svg(svg, "diagrama_calculo", output_dir)
    print(f"    -> Guardado: {path}")
    return path


def test_diagrama_wad(output_dir: Path):
    """Genera un diagrama biomecanico WAD profesional estilo ITRASA."""
    print("\n[3/5] Generando Diagrama WAD Profesional...")

    # Version con velocidad especifica destacada
    svg = generar_diagrama_wad(
        velocidad_impacto=45,  # Velocidad a destacar
        altura_capot=0.80,
        altura_peaton=1.70,
        tipo_vehiculo="turismo",
        mostrar_ciclista=True,
        width=900,
        height=550,
    )

    path = guardar_svg(svg, "diagrama_wad_profesional", output_dir)
    print(f"    -> Guardado: {path}")

    # Version sin velocidad especifica (muestra solo el template)
    svg2 = generar_diagrama_wad(
        velocidad_impacto=None,
        mostrar_ciclista=True,
    )
    path2 = guardar_svg(svg2, "diagrama_wad_template", output_dir)
    print(f"    -> Guardado: {path2}")

    return path


def test_grafico_energia(output_dir: Path):
    """Genera un grafico de energia cinetica."""
    print("\n[4/5] Generando Grafico de Energia...")

    svg = generar_grafico_energia(
        velocidades=[10, 30, 50, 70, 90, 120],
        masa=1500,
        titulo="Energia Cinetica vs Velocidad - SEAT Ibiza (1150 kg)",
    )

    path = guardar_svg(svg, "grafico_energia", output_dir)
    print(f"    -> Guardado: {path}")
    return path


def test_secuencia_temporal(output_dir: Path):
    """Genera una secuencia temporal del accidente."""
    print("\n[5/5] Generando Secuencia Temporal...")

    frames = [
        {
            "tiempo_ms": 0,
            "descripcion": "Pre-impacto",
            "vehiculos": [
                {"id": "A", "orientacion": 20},
                {"id": "B", "orientacion": -90},
            ],
        },
        {
            "tiempo_ms": 80,
            "descripcion": "Contacto inicial",
            "vehiculos": [
                {"id": "A", "orientacion": 25},
                {"id": "B", "orientacion": -70},
            ],
        },
        {
            "tiempo_ms": 150,
            "descripcion": "Pico impacto",
            "vehiculos": [
                {"id": "A", "orientacion": 35},
                {"id": "B", "orientacion": -45},
            ],
        },
        {
            "tiempo_ms": 300,
            "descripcion": "Separacion",
            "vehiculos": [
                {"id": "A", "orientacion": 40},
                {"id": "B", "orientacion": -20},
            ],
        },
        {
            "tiempo_ms": 800,
            "descripcion": "Pos. final",
            "vehiculos": [
                {"id": "A", "orientacion": 45},
                {"id": "B", "orientacion": 0},
            ],
        },
    ]

    svg = generar_secuencia_temporal(
        frames=frames,
        titulo="Secuencia del Atropello - Analisis Temporal",
    )

    path = guardar_svg(svg, "secuencia_temporal", output_dir)
    print(f"    -> Guardado: {path}")
    return path


def main():
    """Ejecuta todas las pruebas de visualizacion."""
    print("\n" + "="*60)
    print(" TEST DE VISUALIZACIONES PROFESIONALES - VERIDICT AI")
    print("="*60)

    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    resultados = []

    try:
        resultados.append(test_croquis_profesional(output_dir))
        resultados.append(test_diagrama_calculo(output_dir))
        resultados.append(test_diagrama_wad(output_dir))
        resultados.append(test_grafico_energia(output_dir))
        resultados.append(test_secuencia_temporal(output_dir))

        print("\n" + "="*60)
        print(" RESUMEN")
        print("="*60)
        print(f"\n[OK] {len(resultados)} visualizaciones generadas correctamente")
        print(f"\nDirectorio de salida: {output_dir}")
        print("\nArchivos generados:")
        for r in resultados:
            print(f"  - {Path(r).name}")

        print("\n" + "-"*60)
        print("Para ver las visualizaciones, abre los archivos SVG en un navegador.")
        print("-"*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

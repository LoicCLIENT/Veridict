"""
Test script para validar las nuevas visualizaciones 3D profesionales.
Genera ejemplos de cada tipo de diagrama para comparar con las referencias ITRASA.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.visualizacion_3d import (
    generar_wad_isometrico,
    generar_diagrama_craneo,
    crear_escena_3d,
    exportar_escena_html,
    generar_informe_visual_completo,
    PLOTLY_AVAILABLE
)

def main():
    """Genera todas las visualizaciones de prueba."""

    output_dir = os.path.join(os.path.dirname(__file__), "outputs_3d")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("VERIDICT AI - Test de Visualizaciones 3D Profesionales")
    print("=" * 60)
    print(f"\nDirectorio de salida: {output_dir}")
    print(f"Plotly disponible: {PLOTLY_AVAILABLE}\n")

    # ========================================================================
    # TEST 1: Diagrama WAD Isometrico Frontal
    # ========================================================================
    print("[1/5] Generando WAD Isometrico Frontal...")

    try:
        svg_frontal = generar_wad_isometrico(
            velocidad_impacto=40,
            tipo_impacto="frontal",
            altura_peaton=1.70,
            mostrar_ciclista=True
        )

        filepath = os.path.join(output_dir, f"wad_isometrico_frontal_{timestamp}.svg")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_frontal)

        print(f"    [OK] Generado: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # ========================================================================
    # TEST 2: Diagrama WAD Isometrico Lateral
    # ========================================================================
    print("[2/5] Generando WAD Isometrico Lateral...")

    try:
        svg_lateral = generar_wad_isometrico(
            velocidad_impacto=50,
            tipo_impacto="lateral",
            altura_peaton=1.75,
            mostrar_ciclista=True
        )

        filepath = os.path.join(output_dir, f"wad_isometrico_lateral_{timestamp}.svg")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_lateral)

        print(f"    [OK] Generado: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # ========================================================================
    # TEST 3: Diagrama Anatomico de Craneo
    # ========================================================================
    print("[3/5] Generando Diagrama Anatomico de Craneo...")

    try:
        svg_craneo = generar_diagrama_craneo(
            zona_impacto="parietal",
            lesiones=[
                "Fractura de craneo en region parietal derecha",
                "Hematoma subdural agudo",
                "Contusion cerebral con efecto masa",
                "Edema cerebral difuso"
            ]
        )

        filepath = os.path.join(output_dir, f"anatomia_craneo_{timestamp}.svg")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_craneo)

        print(f"    [OK] Generado: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"    [ERROR] {e}")

    # ========================================================================
    # TEST 4: Escena 3D Interactiva (requiere Plotly)
    # ========================================================================
    print("[4/5] Generando Escena 3D Interactiva...")

    if PLOTLY_AVAILABLE:
        try:
            # Datos de ejemplo de un atropello
            vehiculos = [
                {
                    "id": "A",
                    "tipo": "turismo",
                    "posicion": {"x": -5, "y": 2, "z": 0},
                    "orientacion": 10,
                    "color": "#3B82F6",
                    "velocidad": 45
                }
            ]

            peatones = [
                {
                    "id": "V1",
                    "tipo": "adulto",
                    "posicion": {"x": 8, "y": 4, "z": 0},
                    "altura": 1.72
                }
            ]

            pdi = {"x": 0, "y": 3, "z": 0}

            huellas = [
                {
                    "vehiculo": "A",
                    "longitud": 12.5,
                    "puntos": [
                        {"x": -20, "y": 2},
                        {"x": -15, "y": 2.2},
                        {"x": -10, "y": 2.5},
                        {"x": -5, "y": 2.8}
                    ]
                }
            ]

            trayectorias = [
                {
                    "vehiculo": "A",
                    "tipo": "pre_impacto",
                    "color": "#3B82F6",
                    "puntos": [
                        {"x": -25, "y": 1},
                        {"x": -20, "y": 1.5},
                        {"x": -15, "y": 2},
                        {"x": -10, "y": 2.5},
                        {"x": -5, "y": 2.8},
                        {"x": 0, "y": 3}
                    ]
                }
            ]

            fig = crear_escena_3d(
                vehiculos=vehiculos,
                peatones=peatones,
                pdi=pdi,
                huellas=huellas,
                trayectorias=trayectorias,
                dimensiones_carretera=(60, 15),
                titulo="Reconstruccion 3D - Atropello en Via Urbana",
                camara_preset="isometric"
            )

            filepath = os.path.join(output_dir, f"escena_3d_{timestamp}.html")
            exportar_escena_html(fig, filepath)

            print(f"    [OK] Generado: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"    [ERROR] {e}")
    else:
        print("    [SKIP] Plotly no esta instalado")

    # ========================================================================
    # TEST 5: Informe Visual Completo
    # ========================================================================
    print("[5/5] Generando Informe Visual Completo...")

    try:
        datos_accidente = {
            "vehiculos": [
                {
                    "id": "A",
                    "tipo": "turismo",
                    "posicion": {"x": -3, "y": 0, "z": 0},
                    "orientacion": 0,
                    "velocidad": 52
                }
            ],
            "peatones": [
                {
                    "id": "P1",
                    "tipo": "adulto",
                    "posicion": {"x": 5, "y": 2, "z": 0},
                    "altura": 1.68
                }
            ],
            "pdi": {"x": 0, "y": 1, "z": 0},
            "velocidad_impacto": 50,
            "zona_impacto_cabeza": "frontal",
            "lesiones": [
                "TCE severo con perdida de conocimiento",
                "Fractura de base de craneo",
                "Hemorragia subaracnoidea",
                "Fracturas multiples en EEII"
            ],
            "huellas": [],
            "trayectorias": []
        }

        informe_dir = os.path.join(output_dir, f"informe_completo_{timestamp}")
        outputs = generar_informe_visual_completo(datos_accidente, informe_dir)

        print(f"    [OK] Generados {len(outputs)} archivos en: {os.path.basename(informe_dir)}/")
        for key, path in outputs.items():
            print(f"        - {key}: {os.path.basename(path)}")

    except Exception as e:
        print(f"    [ERROR] {e}")

    # ========================================================================
    # RESUMEN
    # ========================================================================
    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
    print(f"\nArchivos generados en: {output_dir}")
    print("\nPara comparar con las referencias ITRASA:")
    print("  - Abrir los SVG en el navegador")
    print("  - Abrir el HTML 3D interactivo (si Plotly disponible)")
    print("  - Comparar con: apps/api/training/reference/*.png")

    return 0


if __name__ == "__main__":
    sys.exit(main())

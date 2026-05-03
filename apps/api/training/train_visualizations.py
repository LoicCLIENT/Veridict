"""
Sistema de Entrenamiento para Agentes de Visualizacion
Compara outputs SVG/2D con documentos profesionales de peritaje

Uso:
    python train_visualizations.py --reference path/to/peritaje.pdf --caso demo-1
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from physics.croquis import generar_croquis_svg
from physics.reconstruction import reconstruir_accidente


class VisualizationTrainer:
    """Entrena y evalua agentes de visualizacion comparando con referencias profesionales."""

    def __init__(self, reference_path: str = None):
        self.client = anthropic.Anthropic()
        self.reference_path = reference_path
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        self.iterations = []

    def load_reference_images(self) -> list[dict]:
        """Carga imagenes del documento de referencia profesional."""
        if not self.reference_path:
            return []

        # Para PDFs, extraer paginas relevantes como imagenes
        # Por ahora asumimos que el usuario provee imagenes directamente
        reference_images = []
        ref_path = Path(self.reference_path)

        if ref_path.is_file() and ref_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            with open(ref_path, 'rb') as f:
                img_data = base64.standard_b64encode(f.read()).decode('utf-8')
                reference_images.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{ref_path.suffix[1:].lower()}",
                        "data": img_data
                    }
                })
        elif ref_path.is_dir():
            for img_file in sorted(ref_path.glob("*.png")) + sorted(ref_path.glob("*.jpg")):
                with open(img_file, 'rb') as f:
                    img_data = base64.standard_b64encode(f.read()).decode('utf-8')
                    reference_images.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{img_file.suffix[1:].lower()}",
                            "data": img_data
                        }
                    })

        return reference_images

    def generate_current_visualization(self, caso_data: dict) -> tuple[str, str]:
        """Genera visualizacion con los agentes actuales."""

        # Reconstruir accidente con datos del caso
        resultado = reconstruir_accidente(caso_data)

        # Generar croquis SVG
        svg_content = generar_croquis_svg(
            vehiculos=resultado.get("vehiculos", []),
            pdi=resultado.get("pdi"),
            trayectorias=resultado.get("trayectorias", []),
            huellas=resultado.get("huellas", []),
            titulo=f"Croquis - Caso {caso_data.get('id', 'test')}"
        )

        # Guardar SVG
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        svg_path = self.output_dir / f"croquis_{timestamp}.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return svg_content, str(svg_path)

    def compare_with_reference(self, svg_content: str, reference_images: list) -> dict:
        """Usa Claude Vision para comparar nuestra visualizacion con la referencia profesional."""

        prompt = """Eres un experto en peritajes de accidentes de trafico y visualizacion forense.

TAREA: Compara la visualizacion generada por nuestro sistema (SVG) con las imagenes de referencia del documento profesional de peritaje.

Analiza los siguientes aspectos y proporciona feedback estructurado:

1. **REPRESENTACION DE VEHICULOS**
   - Profesional: Como se representan los vehiculos (3D, siluetas realistas, dimensiones exactas)
   - Nuestro: Como los representamos nosotros
   - Gap: Que nos falta
   - Mejora sugerida: Como podriamos mejorar

2. **TRAYECTORIAS Y MOVIMIENTOS**
   - Profesional: Como muestran las trayectorias pre/post impacto
   - Nuestro: Como las mostramos
   - Gap: Diferencias
   - Mejora sugerida

3. **PUNTO DE IMPACTO (PDI)**
   - Profesional: Como lo visualizan
   - Nuestro: Como lo hacemos
   - Gap y mejora

4. **HUELLAS Y MARCAS**
   - Frenada, derrape, arrastre - como se representan
   - Comparacion y mejoras

5. **DATOS TECNICOS MOSTRADOS**
   - Velocidades, angulos, Delta-V
   - Leyendas y anotaciones
   - Comparacion

6. **CALIDAD VISUAL GENERAL**
   - Profesionalismo, claridad, uso de colores
   - Nivel de detalle
   - Escala y proporciones

7. **ELEMENTOS FALTANTES**
   - Lista de elementos que aparecen en el profesional pero no en el nuestro
   - Prioridad de implementacion (Alta/Media/Baja)

FORMATO DE RESPUESTA:
Responde en JSON con esta estructura:
{
    "score_general": 0-100,
    "aspectos": {
        "vehiculos": {"score": 0-100, "gap": "...", "mejora": "..."},
        "trayectorias": {"score": 0-100, "gap": "...", "mejora": "..."},
        "pdi": {"score": 0-100, "gap": "...", "mejora": "..."},
        "huellas": {"score": 0-100, "gap": "...", "mejora": "..."},
        "datos_tecnicos": {"score": 0-100, "gap": "...", "mejora": "..."},
        "calidad_visual": {"score": 0-100, "gap": "...", "mejora": "..."}
    },
    "elementos_faltantes": [
        {"elemento": "...", "prioridad": "alta|media|baja", "descripcion": "..."}
    ],
    "top_3_mejoras_inmediatas": [
        {"mejora": "...", "impacto": "alto|medio|bajo", "complejidad": "alta|media|baja"}
    ],
    "codigo_sugerido": "Fragmento de codigo Python/SVG para la mejora mas prioritaria"
}"""

        # Construir mensaje con imagenes
        content = []

        # Agregar SVG como texto (Claude puede analizarlo)
        content.append({
            "type": "text",
            "text": f"## NUESTRA VISUALIZACION (SVG generado):\n```svg\n{svg_content}\n```"
        })

        # Agregar imagenes de referencia
        if reference_images:
            content.append({
                "type": "text",
                "text": "\n## IMAGENES DE REFERENCIA DEL DOCUMENTO PROFESIONAL:"
            })
            content.extend(reference_images)

        content.append({"type": "text", "text": prompt})

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": content}]
        )

        response_text = response.content[0].text

        # Extraer JSON de la respuesta
        try:
            # Buscar JSON en la respuesta
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {"raw_response": response_text, "parse_error": True}

    def run_iteration(self, caso_data: dict) -> dict:
        """Ejecuta una iteracion completa de entrenamiento."""

        print("\n" + "="*60)
        print("ITERACION DE ENTRENAMIENTO")
        print("="*60)

        # 1. Cargar referencias
        print("\n[1/3] Cargando imagenes de referencia...")
        reference_images = self.load_reference_images()
        print(f"    -> {len(reference_images)} imagenes cargadas")

        # 2. Generar visualizacion actual
        print("\n[2/3] Generando visualizacion con agentes actuales...")
        svg_content, svg_path = self.generate_current_visualization(caso_data)
        print(f"    -> SVG guardado en: {svg_path}")

        # 3. Comparar con referencia
        print("\n[3/3] Comparando con documento profesional...")
        comparison = self.compare_with_reference(svg_content, reference_images)

        # Guardar resultado de iteracion
        iteration_result = {
            "timestamp": datetime.now().isoformat(),
            "svg_path": svg_path,
            "comparison": comparison
        }
        self.iterations.append(iteration_result)

        # Guardar log
        log_path = self.output_dir / f"iteration_{len(self.iterations)}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(iteration_result, f, indent=2, ensure_ascii=False)

        # Mostrar resumen
        self._print_summary(comparison)

        return iteration_result

    def _print_summary(self, comparison: dict):
        """Imprime resumen de la comparacion."""

        print("\n" + "-"*60)
        print("RESUMEN DE COMPARACION")
        print("-"*60)

        if comparison.get("parse_error"):
            print("\n[!] Error parseando respuesta JSON")
            print(comparison.get("raw_response", "")[:500])
            return

        score = comparison.get("score_general", "N/A")
        print(f"\nScore General: {score}/100")

        if "aspectos" in comparison:
            print("\nScores por aspecto:")
            for aspecto, data in comparison["aspectos"].items():
                print(f"  - {aspecto}: {data.get('score', 'N/A')}/100")

        if "top_3_mejoras_inmediatas" in comparison:
            print("\nTop 3 Mejoras Prioritarias:")
            for i, mejora in enumerate(comparison["top_3_mejoras_inmediatas"], 1):
                print(f"  {i}. {mejora.get('mejora', 'N/A')}")
                print(f"     Impacto: {mejora.get('impacto', 'N/A')} | Complejidad: {mejora.get('complejidad', 'N/A')}")

        if "codigo_sugerido" in comparison and comparison["codigo_sugerido"]:
            print("\nCodigo sugerido para mejora prioritaria:")
            print("-"*40)
            print(comparison["codigo_sugerido"][:500])
            print("-"*40)


def get_demo_caso_data() -> dict:
    """Datos de ejemplo para testing."""
    return {
        "id": "demo-training",
        "vehiculo_a": {
            "tipo": "turismo",
            "marca": "BMW",
            "modelo": "Serie 3",
            "masa": 1500,
            "velocidad_estimada": 65,
            "angulo_impacto": 15,
            "posicion_final": {"x": 12, "y": 8},
            "orientacion_final": 45
        },
        "vehiculo_b": {
            "tipo": "turismo",
            "marca": "Volkswagen",
            "modelo": "Golf",
            "masa": 1200,
            "velocidad_estimada": 45,
            "angulo_impacto": -30,
            "posicion_final": {"x": 18, "y": 5},
            "orientacion_final": -60
        },
        "pdi": {"x": 15, "y": 6},
        "huellas": [
            {"tipo": "frenada", "vehiculo": "A", "longitud": 12.5, "inicio": {"x": 5, "y": 10}, "fin": {"x": 14, "y": 7}},
            {"tipo": "derrape", "vehiculo": "B", "longitud": 8.3, "inicio": {"x": 16, "y": 4}, "fin": {"x": 22, "y": 3}}
        ],
        "coeficiente_friccion": 0.75,
        "tipo_colision": "frontal-lateral"
    }


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento de agentes de visualizacion")
    parser.add_argument("--reference", "-r", help="Path a imagen/directorio de referencia profesional")
    parser.add_argument("--caso", "-c", help="ID del caso a procesar (o 'demo' para datos de ejemplo)")
    parser.add_argument("--iterations", "-n", type=int, default=1, help="Numero de iteraciones")

    args = parser.parse_args()

    # Inicializar trainer
    trainer = VisualizationTrainer(reference_path=args.reference)

    # Obtener datos del caso
    if args.caso == "demo" or not args.caso:
        caso_data = get_demo_caso_data()
    else:
        # Cargar caso real desde la API
        # Por ahora usar demo
        caso_data = get_demo_caso_data()
        caso_data["id"] = args.caso

    # Ejecutar iteraciones
    for i in range(args.iterations):
        print(f"\n{'#'*60}")
        print(f"# ITERACION {i+1}/{args.iterations}")
        print(f"{'#'*60}")
        trainer.run_iteration(caso_data)

    print("\n" + "="*60)
    print("ENTRENAMIENTO COMPLETADO")
    print(f"Resultados guardados en: {trainer.output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()

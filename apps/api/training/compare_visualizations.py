"""
Comparador Interactivo de Visualizaciones
Genera un reporte HTML con comparacion lado a lado

Uso:
    python compare_visualizations.py --reference reference_images/ --output comparison.html
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import anthropic


def generate_comparison_html(
    svg_content: str,
    reference_images: list[Path],
    analysis: dict,
    output_path: str
):
    """Genera un HTML interactivo con la comparacion."""

    # Convertir imagenes de referencia a base64
    ref_images_b64 = []
    for img_path in reference_images:
        with open(img_path, 'rb') as f:
            data = base64.standard_b64encode(f.read()).decode('utf-8')
            suffix = img_path.suffix[1:].lower()
            if suffix == 'jpg':
                suffix = 'jpeg'
            ref_images_b64.append({
                "name": img_path.name,
                "data": f"data:image/{suffix};base64,{data}"
            })

    # Convertir SVG a data URL
    svg_b64 = base64.standard_b64encode(svg_content.encode()).decode('utf-8')
    svg_data_url = f"data:image/svg+xml;base64,{svg_b64}"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparacion de Visualizaciones - Veridict Training</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 2rem;
            border-bottom: 1px solid #333;
        }}
        .header h1 {{
            font-size: 1.5rem;
            color: #C2E94B;
            margin-bottom: 0.5rem;
        }}
        .header p {{
            color: #888;
            font-size: 0.9rem;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        .panel {{
            background: #1a1a1a;
            border-radius: 12px;
            border: 1px solid #333;
            overflow: hidden;
        }}
        .panel-header {{
            padding: 1rem 1.5rem;
            background: #222;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .panel-header h2 {{
            font-size: 1rem;
            font-weight: 600;
        }}
        .badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .badge-green {{ background: #C2E94B22; color: #C2E94B; }}
        .badge-blue {{ background: #3B82F622; color: #60A5FA; }}
        .panel-content {{
            padding: 1.5rem;
        }}
        .image-container {{
            background: #0f0f0f;
            border-radius: 8px;
            padding: 1rem;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
        }}
        .image-container img, .image-container svg {{
            max-width: 100%;
            max-height: 500px;
            object-fit: contain;
        }}
        .image-tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        .image-tab {{
            padding: 0.5rem 1rem;
            background: #333;
            border: none;
            border-radius: 6px;
            color: #999;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}
        .image-tab.active {{
            background: #C2E94B;
            color: #000;
        }}
        .analysis-section {{
            background: #1a1a1a;
            border-radius: 12px;
            border: 1px solid #333;
            margin-bottom: 2rem;
        }}
        .analysis-header {{
            padding: 1.5rem;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .score-badge {{
            font-size: 2rem;
            font-weight: 700;
            color: #C2E94B;
        }}
        .aspects-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            padding: 1.5rem;
        }}
        .aspect-card {{
            background: #222;
            border-radius: 8px;
            padding: 1rem;
        }}
        .aspect-card h3 {{
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .aspect-score {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .aspect-score.high {{ color: #22C55E; }}
        .aspect-score.medium {{ color: #EAB308; }}
        .aspect-score.low {{ color: #EF4444; }}
        .aspect-gap {{
            font-size: 0.85rem;
            color: #999;
            line-height: 1.4;
        }}
        .improvements-section {{
            padding: 1.5rem;
            border-top: 1px solid #333;
        }}
        .improvements-section h3 {{
            font-size: 1rem;
            margin-bottom: 1rem;
            color: #C2E94B;
        }}
        .improvement-item {{
            display: flex;
            gap: 1rem;
            padding: 1rem;
            background: #222;
            border-radius: 8px;
            margin-bottom: 0.75rem;
        }}
        .improvement-number {{
            width: 32px;
            height: 32px;
            background: #C2E94B;
            color: #000;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .improvement-content h4 {{
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }}
        .improvement-content p {{
            font-size: 0.85rem;
            color: #888;
        }}
        .improvement-tags {{
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }}
        .tag {{
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }}
        .tag-impact {{ background: #22C55E22; color: #22C55E; }}
        .tag-complexity {{ background: #3B82F622; color: #60A5FA; }}
        .code-section {{
            background: #1a1a1a;
            border-radius: 12px;
            border: 1px solid #333;
            overflow: hidden;
        }}
        .code-section h3 {{
            padding: 1rem 1.5rem;
            background: #222;
            border-bottom: 1px solid #333;
            font-size: 1rem;
        }}
        .code-block {{
            padding: 1.5rem;
            background: #0f0f0f;
            overflow-x: auto;
        }}
        .code-block pre {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            color: #e0e0e0;
        }}
        .missing-elements {{
            padding: 1.5rem;
        }}
        .missing-elements h3 {{
            font-size: 1rem;
            margin-bottom: 1rem;
        }}
        .missing-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem 1rem;
            background: #222;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }}
        .priority-badge {{
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .priority-alta {{ background: #EF444422; color: #EF4444; }}
        .priority-media {{ background: #EAB30822; color: #EAB308; }}
        .priority-baja {{ background: #22C55E22; color: #22C55E; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Comparacion de Visualizaciones</h1>
        <p>Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Veridict AI Training System</p>
    </div>

    <div class="container">
        <!-- Comparacion lado a lado -->
        <div class="comparison-grid">
            <div class="panel">
                <div class="panel-header">
                    <h2>Nuestra Visualizacion</h2>
                    <span class="badge badge-green">SVG Generado</span>
                </div>
                <div class="panel-content">
                    <div class="image-container">
                        <img src="{svg_data_url}" alt="SVG Generado">
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <h2>Referencia Profesional</h2>
                    <span class="badge badge-blue">Documento Peritaje</span>
                </div>
                <div class="panel-content">
                    <div class="image-tabs" id="refTabs">
                        {"".join(f'<button class="image-tab {"active" if i==0 else ""}" onclick="showRefImage({i})">{img["name"]}</button>' for i, img in enumerate(ref_images_b64))}
                    </div>
                    <div class="image-container" id="refImageContainer">
                        {f'<img src="{ref_images_b64[0]["data"]}" alt="Referencia">' if ref_images_b64 else '<p style="color:#666">No hay imagenes de referencia</p>'}
                    </div>
                </div>
            </div>
        </div>

        <!-- Analisis -->
        <div class="analysis-section">
            <div class="analysis-header">
                <div>
                    <h2>Analisis de Claude</h2>
                    <p style="color:#888;font-size:0.9rem;margin-top:0.25rem">Comparacion detallada de aspectos</p>
                </div>
                <div class="score-badge">{analysis.get('score_general', 'N/A')}/100</div>
            </div>

            <div class="aspects-grid">
                {"".join(f'''
                <div class="aspect-card">
                    <h3>{aspect.replace('_', ' ').title()}</h3>
                    <div class="aspect-score {'high' if data.get('score', 0) >= 70 else 'medium' if data.get('score', 0) >= 40 else 'low'}">{data.get('score', 'N/A')}</div>
                    <p class="aspect-gap">{data.get('gap', 'Sin informacion')[:100]}...</p>
                </div>
                ''' for aspect, data in analysis.get('aspectos', {}).items())}
            </div>

            <!-- Mejoras prioritarias -->
            <div class="improvements-section">
                <h3>Top Mejoras Prioritarias</h3>
                {"".join(f'''
                <div class="improvement-item">
                    <div class="improvement-number">{i+1}</div>
                    <div class="improvement-content">
                        <h4>{mejora.get('mejora', 'N/A')}</h4>
                        <div class="improvement-tags">
                            <span class="tag tag-impact">Impacto: {mejora.get('impacto', 'N/A')}</span>
                            <span class="tag tag-complexity">Complejidad: {mejora.get('complejidad', 'N/A')}</span>
                        </div>
                    </div>
                </div>
                ''' for i, mejora in enumerate(analysis.get('top_3_mejoras_inmediatas', [])))}
            </div>

            <!-- Elementos faltantes -->
            <div class="missing-elements">
                <h3>Elementos Faltantes</h3>
                {"".join(f'''
                <div class="missing-item">
                    <span class="priority-badge priority-{elem.get('prioridad', 'media').lower()}">{elem.get('prioridad', 'media')}</span>
                    <span>{elem.get('elemento', 'N/A')}</span>
                </div>
                ''' for elem in analysis.get('elementos_faltantes', [])[:10])}
            </div>
        </div>

        <!-- Codigo sugerido -->
        {f'''
        <div class="code-section">
            <h3>Codigo Sugerido para Mejora Prioritaria</h3>
            <div class="code-block">
                <pre>{analysis.get('codigo_sugerido', 'No hay codigo sugerido')}</pre>
            </div>
        </div>
        ''' if analysis.get('codigo_sugerido') else ''}
    </div>

    <script>
        const refImages = {json.dumps([img["data"] for img in ref_images_b64])};

        function showRefImage(index) {{
            document.getElementById('refImageContainer').innerHTML =
                `<img src="${{refImages[index]}}" alt="Referencia">`;
            document.querySelectorAll('.image-tab').forEach((tab, i) => {{
                tab.classList.toggle('active', i === index);
            }});
        }}
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Genera comparacion HTML de visualizaciones")
    parser.add_argument("--svg", "-s", required=True, help="Path al SVG generado")
    parser.add_argument("--reference", "-r", required=True, help="Path a imagen/directorio de referencia")
    parser.add_argument("--analysis", "-a", help="Path a JSON con analisis previo (opcional)")
    parser.add_argument("--output", "-o", default="comparison.html", help="Path de salida HTML")

    args = parser.parse_args()

    # Cargar SVG
    with open(args.svg, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # Cargar imagenes de referencia
    ref_path = Path(args.reference)
    if ref_path.is_file():
        reference_images = [ref_path]
    else:
        reference_images = list(ref_path.glob("*.png")) + list(ref_path.glob("*.jpg"))

    # Cargar o generar analisis
    if args.analysis:
        with open(args.analysis, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    else:
        analysis = {"score_general": "Pendiente", "aspectos": {}, "top_3_mejoras_inmediatas": []}

    # Generar HTML
    output_path = generate_comparison_html(svg_content, reference_images, analysis, args.output)
    print(f"Comparacion generada: {output_path}")


if __name__ == "__main__":
    main()

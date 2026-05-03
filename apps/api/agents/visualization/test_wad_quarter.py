"""
Test script for WAD diagram with quarter-front car view.
Generates example output matching ITRASA style.
"""

import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent / "test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_wad_diagram_quarter(
    velocidad_destacada: int = None,
    mostrar_peaton: bool = True,
    mostrar_ciclista: bool = True,
    output_path: str = None
) -> str:
    """
    Create a WAD diagram using the quarter-front car view.

    Args:
        velocidad_destacada: Velocity to highlight (20, 30, 40, 50 km/h)
        mostrar_peaton: Show pedestrian impact markers (orange triangles)
        mostrar_ciclista: Show cyclist impact markers (black crosses)
        output_path: Path to save SVG

    Returns:
        SVG string
    """

    # Load the car asset
    asset_path = Path(__file__).parent / "assets" / "svg" / "car_quarter_front.svg"
    with open(asset_path, 'r', encoding='utf-8') as f:
        car_svg_content = f.read()

    # Extract just the content between <svg> tags (without the svg wrapper)
    import re
    inner_match = re.search(r'<svg[^>]*>(.*)</svg>', car_svg_content, re.DOTALL)
    car_inner = inner_match.group(1) if inner_match else car_svg_content

    # WAD velocity to position mapping (on the vehicle)
    # Format: velocity -> (x, y) position on the 600x450 car viewbox
    # Positions follow the ITRASA methodology: higher speed = higher WAD = higher on vehicle
    wad_positions = {
        20: (340, 310),   # Lower hood - WAD ~1000mm
        30: (320, 260),   # Mid hood - WAD ~1200mm
        40: (300, 200),   # Upper hood / windshield base - WAD ~1500mm
        50: (280, 140),   # Windshield - WAD ~1800mm
    }

    # WAD reference lines (horizontal lines across the diagram)
    wad_lines = [
        (1000, 320, "#D4A800"),  # WAD 1000 - yellow
        (1500, 220, "#D4A800"),  # WAD 1500 - yellow
    ]

    # Build SVG
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 550" width="800" height="550">',
        '',
        '  <!-- Background -->',
        '  <rect width="800" height="550" fill="#FFFFFF"/>',
        '',
        '  <!-- Title bar -->',
        '  <rect x="0" y="0" width="800" height="45" fill="#1F3329"/>',
        '  <text x="25" y="28" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="16" font-weight="bold">',
        '    Diagrama WAD - Zonas de Impacto Frontal',
        '  </text>',
        '  <text x="775" y="28" fill="#C2E94B" font-family="Arial, sans-serif" font-size="12" text-anchor="end">',
        '    Veridict AI',
        '  </text>',
        '',
        '  <!-- WAD Reference Lines -->',
    ]

    for wad_mm, y_pos, color in wad_lines:
        svg_parts.append(f'''
  <line x1="20" y1="{y_pos + 50}" x2="620" y2="{y_pos + 50}"
        stroke="{color}" stroke-width="2"/>
  <text x="625" y="{y_pos + 54}" fill="#333333" font-family="Arial, sans-serif"
        font-size="12" font-weight="bold">WAD {wad_mm}</text>
        ''')

    # Embed car (offset by margin)
    svg_parts.append('''
  <!-- Car diagram (embedded with offset) -->
  <g transform="translate(50, 55)">
''')
    svg_parts.append(car_inner)
    svg_parts.append('  </g>')

    # Impact markers
    svg_parts.append('''

  <!-- Impact Markers -->
  <g id="impact-markers">
''')

    for vel, (x, y) in wad_positions.items():
        # Offset for the embedded car position
        mx = x + 50
        my = y + 55

        is_highlighted = (vel == velocidad_destacada)

        # Pedestrian marker (orange triangle) - positioned slightly right
        if mostrar_peaton:
            fill_color = "#E67E22" if not is_highlighted else "#E74C3C"
            svg_parts.append(f'''
    <!-- Pedestrian {vel} km/h -->
    <polygon points="{mx},{my - 12} {mx - 10},{my + 6} {mx + 10},{my + 6}"
             fill="{fill_color}" stroke="#000000" stroke-width="1"/>
    <text x="{mx + 18}" y="{my + 2}" fill="{fill_color}"
          font-family="Arial, sans-serif" font-size="11" font-weight="bold">{vel} km/h</text>
''')

        # Cyclist marker (black cross) - positioned slightly left and up
        if mostrar_ciclista:
            cx = mx - 45
            cy = my - 30
            svg_parts.append(f'''
    <!-- Cyclist {vel} km/h -->
    <line x1="{cx - 8}" y1="{cy}" x2="{cx + 8}" y2="{cy}"
          stroke="#000000" stroke-width="3"/>
    <line x1="{cx}" y1="{cy - 8}" x2="{cx}" y2="{cy + 8}"
          stroke="#000000" stroke-width="3"/>
    <text x="{cx - 12}" y="{cy - 15}" fill="#000000"
          font-family="Arial, sans-serif" font-size="10" font-weight="bold">{vel} km/h</text>
''')

        # Highlight circle for selected velocity
        if is_highlighted:
            svg_parts.append(f'''
    <!-- Highlight for {vel} km/h -->
    <circle cx="{mx}" cy="{my}" r="30" fill="none"
            stroke="#E74C3C" stroke-width="3" stroke-dasharray="5,3">
      <animate attributeName="stroke-opacity" values="1;0.4;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
''')

    svg_parts.append('  </g>')

    # Legend
    svg_parts.append('''

  <!-- Legend -->
  <rect x="640" y="60" width="150" height="200" fill="#F9FAFB" stroke="#E5E7EB" rx="6"/>

  <text x="655" y="85" fill="#333333" font-family="Arial, sans-serif" font-size="12" font-weight="bold">
    Leyenda
  </text>
  <line x1="650" y1="95" x2="780" y2="95" stroke="#E5E7EB"/>

  <!-- Pedestrian symbol -->
  <polygon points="670,115 660,130 680,130" fill="#E67E22" stroke="#000000" stroke-width="1"/>
  <text x="690" y="126" fill="#333333" font-family="Arial, sans-serif" font-size="10">
    Impacto frontal
  </text>
  <text x="690" y="138" fill="#333333" font-family="Arial, sans-serif" font-size="10">
    de un joven peaton
  </text>

  <!-- Cyclist symbol -->
  <line x1="662" y1="165" x2="678" y2="165" stroke="#000000" stroke-width="3"/>
  <line x1="670" y1="157" x2="670" y2="173" stroke="#000000" stroke-width="3"/>
  <text x="690" y="162" fill="#333333" font-family="Arial, sans-serif" font-size="10">
    Impacto frontal
  </text>
  <text x="690" y="174" fill="#333333" font-family="Arial, sans-serif" font-size="10">
    de un joven ciclista
  </text>

  <line x1="650" y1="190" x2="780" y2="190" stroke="#E5E7EB"/>

  <text x="655" y="210" fill="#666666" font-family="Arial, sans-serif" font-size="9">
    Velocidades: 20-50 km/h
  </text>
  <text x="655" y="225" fill="#666666" font-family="Arial, sans-serif" font-size="9">
    Zonas WAD: 1000-2000mm
  </text>
  <text x="655" y="248" fill="#888888" font-family="Arial, sans-serif" font-size="8" font-style="italic">
    Metodologia ITRASA
  </text>
''')

    # Footer
    svg_parts.append('''
  <!-- Footer -->
  <text x="790" y="540" fill="#888888" font-family="Arial, sans-serif" font-size="9" text-anchor="end">
    Veridict AI - Reconstruccion Forense
  </text>
''')

    svg_parts.append('</svg>')

    svg_content = '\n'.join(svg_parts)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"WAD diagram saved to: {output_path}")

    return svg_content


if __name__ == "__main__":
    # Generate test outputs

    # 1. Basic WAD diagram with all markers
    output1 = OUTPUT_DIR / "wad_quarter_basic.svg"
    create_wad_diagram_quarter(output_path=str(output1))

    # 2. WAD diagram highlighting 40 km/h impact
    output2 = OUTPUT_DIR / "wad_quarter_40kmh.svg"
    create_wad_diagram_quarter(velocidad_destacada=40, output_path=str(output2))

    # 3. Pedestrian only
    output3 = OUTPUT_DIR / "wad_quarter_peaton.svg"
    create_wad_diagram_quarter(mostrar_ciclista=False, output_path=str(output3))

    print("\nTest outputs generated in:", OUTPUT_DIR)
    print("Files:")
    for f in OUTPUT_DIR.glob("wad_quarter_*.svg"):
        print(f"  - {f.name}")

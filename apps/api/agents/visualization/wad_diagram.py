"""
WAD Diagram - Wrap Around Distance visualization using pre-made assets.

Uses car_side.svg or car_quarter_front.svg asset for professional vehicle rendering.
Adds WAD zones, impact markers, and technical annotations.

Based on ITRASA methodology and Euro NCAP standards.

Supports two view types:
- "side": Traditional lateral view
- "quarter": 3/4 front view (ITRASA reference style)
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .base_asset import (
    AssetBasedDiagram,
    Point,
    Dimension,
    Arrow,
    Label,
    BRAND_COLORS,
    VEHICLE_DIMENSIONS,
    FONT_DATA,
    FONT_LABEL,
)


# ═══════════════════════════════════════════════════════════════════════════════
# WAD ZONE DATA (based on ITRASA/Euro NCAP studies)
# ═══════════════════════════════════════════════════════════════════════════════

# WAD zones mapped to impact velocity ranges
# Format: velocity_kmh -> (wad_mm, zone_name, severity_ais)
WAD_VELOCITY_MAPPING = {
    20: (1000, "Capo posterior", "AIS 1-2"),
    25: (1200, "Capo central", "AIS 2"),
    30: (1400, "Capo anterior", "AIS 2-3"),
    35: (1550, "Base parabrisas", "AIS 3"),
    40: (1700, "Parabrisas inferior", "AIS 3-4"),
    45: (1850, "Parabrisas superior", "AIS 4"),
    50: (2000, "Borde techo", "AIS 4-5"),
    55: (2150, "Techo/Proyeccion", "AIS 5+"),
}

# Impact markers - pedestrian (triangle) and cyclist (cross)
@dataclass
class ImpactMarker:
    """Impact marker for WAD diagram."""
    velocity_kmh: int
    wad_mm: int
    zone: str
    severity: str
    is_highlighted: bool = False


@dataclass
class WADLine:
    """WAD reference line."""
    height_mm: int
    label: str
    color: str = "#EAB308"  # ITRASA yellow


# ═══════════════════════════════════════════════════════════════════════════════
# WAD DIAGRAM CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class WADDiagram(AssetBasedDiagram):
    """
    WAD (Wrap Around Distance) diagram for pedestrian/cyclist impact analysis.

    Shows vehicle profile with WAD zones and impact markers at different velocities.
    """

    def __init__(
        self,
        width: int = 900,
        height: int = 650,
        tipo_impacto: str = "frontal",  # frontal or lateral
        view_type: str = "side",  # "side" or "quarter"
        **kwargs
    ):
        super().__init__(width=width, height=height, **kwargs)

        self.tipo_impacto = tipo_impacto
        self.view_type = view_type  # "side" for lateral view, "quarter" for 3/4 front

        # Vehicle configuration
        self.vehicle_length_m = 4.30  # Default turismo
        self.vehicle_height_m = 1.45

        # Scale: pixels per meter for the vehicle
        self.vehicle_scale = 150  # px per meter

        # Impact markers
        self.markers: List[ImpactMarker] = []
        self.highlighted_velocity: Optional[int] = None

        # WAD lines
        self.wad_lines = [
            WADLine(1000, "WAD 1000"),
            WADLine(1500, "WAD 1500"),
            WADLine(2000, "WAD 2000"),
        ]

        # Show cyclist markers
        self.show_cyclist = True

        # Quarter view specific WAD position mapping (for 3/4 front view)
        # Maps velocity to (x, y) positions on the 600x450 car viewbox
        self._quarter_wad_positions = {
            20: (340, 310),   # Lower hood - WAD ~1000mm
            25: (330, 285),   # Hood surface
            30: (320, 260),   # Mid hood - WAD ~1200mm
            35: (310, 230),   # Upper hood
            40: (300, 200),   # Upper hood / windshield base - WAD ~1500mm
            45: (290, 170),   # Lower windshield
            50: (280, 140),   # Windshield - WAD ~1800mm
            55: (270, 110),   # Upper windshield
        }

    def set_vehicle(self, tipo: str = "turismo"):
        """Set vehicle type and dimensions."""
        dims = VEHICLE_DIMENSIONS.get(
            tipo + "_generico" if tipo in ["turismo", "suv"] else tipo,
            VEHICLE_DIMENSIONS["turismo_generico"]
        )
        self.vehicle_length_m, _, self.vehicle_height_m = dims

    def set_highlighted_velocity(self, velocity_kmh: int):
        """Highlight a specific impact velocity."""
        self.highlighted_velocity = velocity_kmh

    def add_custom_marker(self, velocity_kmh: int, wad_mm: int, zone: str, severity: str):
        """Add a custom impact marker."""
        self.markers.append(ImpactMarker(velocity_kmh, wad_mm, zone, severity))

    def _get_wad_position(self, wad_mm: int) -> Tuple[float, float]:
        """
        Convert WAD value (mm) to position on vehicle silhouette.

        WAD is measured along the vehicle surface from ground contact point.
        Returns (x, y) in pixels relative to vehicle center.
        """
        # Vehicle dimensions in pixels
        veh_length_px = self.vehicle_length_m * self.vehicle_scale
        veh_height_px = self.vehicle_height_m * self.vehicle_scale

        # WAD zones on vehicle (simplified profile)
        # 0-800mm: front bumper to hood edge
        # 800-1200mm: hood
        # 1200-1600mm: windshield base
        # 1600-2000mm: windshield to roof edge
        # 2000+: roof

        wad_m = wad_mm / 1000.0

        # Simplified mapping for lateral view
        if wad_mm <= 800:
            # Front bumper/lower hood area
            x = veh_length_px * 0.45
            y = veh_height_px * (0.3 + 0.2 * (wad_mm / 800))
        elif wad_mm <= 1200:
            # Hood surface
            progress = (wad_mm - 800) / 400
            x = veh_length_px * (0.45 - 0.15 * progress)
            y = veh_height_px * (0.5 + 0.15 * progress)
        elif wad_mm <= 1600:
            # Windshield
            progress = (wad_mm - 1200) / 400
            x = veh_length_px * (0.30 - 0.15 * progress)
            y = veh_height_px * (0.65 + 0.25 * progress)
        elif wad_mm <= 2000:
            # Upper windshield / roof edge
            progress = (wad_mm - 1600) / 400
            x = veh_length_px * (0.15 - 0.1 * progress)
            y = veh_height_px * (0.90 + 0.08 * progress)
        else:
            # Roof / projection
            x = veh_length_px * 0.0
            y = veh_height_px * 1.0

        return (x, -y)  # Negative y because SVG y-axis is inverted

    def _render_wad_lines(self, veh_cx: float, veh_cy: float) -> str:
        """Render horizontal WAD reference lines."""
        elements = ['<!-- WAD Reference Lines -->']

        if self.view_type == "quarter":
            # For quarter view, use fixed positions matching test_wad_quarter.py
            # Ground at y=475 (420 + 55 offset), WAD positions relative to this
            wad_y_mapping = {
                1000: 370,  # WAD 1000
                1500: 270,  # WAD 1500
                2000: 170,  # WAD 2000
            }
            for wad_line in self.wad_lines:
                y = wad_y_mapping.get(wad_line.height_mm, 300)
                elements.append(f'''
            <line x1="20" y1="{y}" x2="{self.width - 280}" y2="{y}"
                  stroke="{wad_line.color}" stroke-width="2" opacity="0.9"/>
            <text x="{self.width - 270}" y="{y + 4}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="12" font-weight="bold">{wad_line.label}</text>
                ''')
        else:
            # Side view - original positioning
            for wad_line in self.wad_lines:
                # Calculate y position
                # WAD height corresponds to distance from ground
                y = veh_cy - (wad_line.height_mm / 1000.0) * self.vehicle_scale

                elements.append(f'''
            <line x1="50" y1="{y}" x2="{self.width - 220}" y2="{y}"
                  stroke="{wad_line.color}" stroke-width="2" opacity="0.9"/>
            <text x="{self.width - 210}" y="{y + 4}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="11" font-weight="bold">{wad_line.label}</text>
            <text x="40" y="{y + 4}" text-anchor="end"
                  fill="{BRAND_COLORS['gris_medio']}" font-family="{FONT_DATA}"
                  font-size="10">{wad_line.height_mm/1000:.1f}m</text>
                ''')

        return '\n'.join(elements)

    def _render_vehicle(self, cx: float, cy: float) -> str:
        """Render the vehicle using the SVG asset."""
        if self.view_type == "quarter":
            # For quarter view, load and embed the car directly with proper offset
            # similar to how test_wad_quarter.py does it
            asset = self.load_asset("car_quarter_front")
            if asset is None:
                return "<!-- Error loading car_quarter_front asset -->"

            # Extract the inner content from the SVG
            import re
            from io import StringIO
            import xml.etree.ElementTree as ET

            # Convert element to string
            svg_str = ET.tostring(asset, encoding='unicode')

            # Extract inner content (remove outer svg tags)
            inner_match = re.search(r'<svg[^>]*>(.*)</svg>', svg_str, re.DOTALL)
            car_inner = inner_match.group(1) if inner_match else svg_str

            # Embed with offset
            return f'''
        <g id="car_quarter_front_wad_vehicle" transform="translate({cx}, {cy})">
            {car_inner}
        </g>
            '''
        else:
            asset_name = "car_side"
            return self.embed_asset(
                asset_name,
                cx, cy,
                width_meters=self.vehicle_length_m,
                rotation=0,
                id_suffix="wad_vehicle"
            )

    def _render_impact_markers(self, veh_cx: float, veh_cy: float) -> str:
        """Render impact markers (triangles for pedestrians, crosses for cyclists)."""
        elements = ['<!-- Impact Markers -->']

        # Generate markers from velocity mapping
        all_markers = []
        for vel, (wad, zone, sev) in WAD_VELOCITY_MAPPING.items():
            is_highlighted = (vel == self.highlighted_velocity)
            all_markers.append(ImpactMarker(vel, wad, zone, sev, is_highlighted))

        # Add custom markers
        all_markers.extend(self.markers)

        for marker in all_markers:
            # Get position on vehicle
            if self.view_type == "quarter" and marker.velocity_kmh in self._quarter_wad_positions:
                # Use predefined quarter view positions
                qx, qy = self._quarter_wad_positions[marker.velocity_kmh]
                # Offset for embedded car position in the diagram
                mx = qx + 50  # offset matches test_wad_quarter.py
                my = qy + 55
            else:
                # Use calculated side view positions
                rel_x, rel_y = self._get_wad_position(marker.wad_mm)
                mx = veh_cx + rel_x
                my = veh_cy + rel_y

            # Pedestrian marker (orange triangle - ITRASA style)
            elements.append(f'''
            <g class="marker-pedestrian-{marker.velocity_kmh}">
                <polygon points="{mx},{my - 10} {mx - 8},{my + 5} {mx + 8},{my + 5}"
                         fill="{BRAND_COLORS['naranja_warning']}" stroke="#000000" stroke-width="1"/>
                <text x="{mx + 15}" y="{my}"
                      fill="{BRAND_COLORS['naranja_warning']}" font-family="{FONT_DATA}"
                      font-size="11" font-weight="bold">{marker.velocity_kmh} km/h</text>
            </g>
            ''')

            # Cyclist marker (black cross - ITRASA style)
            if self.show_cyclist:
                cx = mx - 30
                cy_marker = my - 25

                elements.append(f'''
                <g class="marker-cyclist-{marker.velocity_kmh}">
                    <line x1="{cx - 6}" y1="{cy_marker}" x2="{cx + 6}" y2="{cy_marker}"
                          stroke="#000000" stroke-width="2.5"/>
                    <line x1="{cx}" y1="{cy_marker - 6}" x2="{cx}" y2="{cy_marker + 6}"
                          stroke="#000000" stroke-width="2.5"/>
                </g>
                ''')

            # Highlight circle for selected velocity
            if marker.is_highlighted:
                elements.append(f'''
                <circle cx="{mx}" cy="{my}" r="25" fill="none"
                        stroke="{BRAND_COLORS['rojo_alerta']}" stroke-width="3">
                    <animate attributeName="r" values="20;28;20" dur="1.5s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="1;0.6;1" dur="1.5s" repeatCount="indefinite"/>
                </circle>
                ''')

        return '\n'.join(elements)

    def _render_legend(self) -> str:
        """Render the legend panel."""
        lx = self.width - 200
        ly = 70

        elements = [
            f'''
            <rect x="{lx}" y="{ly}" width="185" height="320"
                  fill="{BRAND_COLORS['blanco']}" stroke="{BRAND_COLORS['gris_claro']}"
                  stroke-width="1" rx="6"/>

            <text x="{lx + 15}" y="{ly + 22}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="13" font-weight="bold">Leyenda - Zonas WAD</text>
            <line x1="{lx + 10}" y1="{ly + 32}" x2="{lx + 175}" y2="{ly + 32}"
                  stroke="{BRAND_COLORS['gris_claro']}"/>

            <!-- Pedestrian symbol -->
            <polygon points="{lx + 25},{ly + 48} {lx + 17},{ly + 62} {lx + 33},{ly + 62}"
                     fill="{BRAND_COLORS['naranja_warning']}" stroke="#000000" stroke-width="1"/>
            <text x="{lx + 45}" y="{ly + 58}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="11">Impacto peaton</text>

            <!-- Cyclist symbol -->
            <line x1="{lx + 19}" y1="{ly + 82}" x2="{lx + 31}" y2="{ly + 82}"
                  stroke="#000000" stroke-width="2.5"/>
            <line x1="{lx + 25}" y1="{ly + 76}" x2="{lx + 25}" y2="{ly + 88}"
                  stroke="#000000" stroke-width="2.5"/>
            <text x="{lx + 45}" y="{ly + 86}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="11">Impacto ciclista</text>

            <line x1="{lx + 10}" y1="{ly + 100}" x2="{lx + 175}" y2="{ly + 100}"
                  stroke="{BRAND_COLORS['gris_claro']}"/>

            <text x="{lx + 15}" y="{ly + 118}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="11" font-weight="bold">Velocidad → Zona:</text>
            '''
        ]

        # Add velocity-zone mapping
        y_offset = ly + 138
        for i, (vel, (wad, zone, sev)) in enumerate(list(WAD_VELOCITY_MAPPING.items())[:6]):
            elements.append(f'''
            <text x="{lx + 20}" y="{y_offset + i * 26}"
                  fill="{BRAND_COLORS['naranja_warning']}" font-family="{FONT_DATA}"
                  font-size="10" font-weight="bold">{vel} km/h</text>
            <text x="{lx + 75}" y="{y_offset + i * 26}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="9">→ {zone}</text>
            ''')

        elements.append(f'''
            <line x1="{lx + 10}" y1="{ly + 295}" x2="{lx + 175}" y2="{ly + 295}"
                  stroke="{BRAND_COLORS['gris_claro']}"/>
            <text x="{lx + 15}" y="{ly + 310}"
                  fill="{BRAND_COLORS['gris_medio']}" font-family="{FONT_LABEL}"
                  font-size="8" font-style="italic">Basado en ITRASA/Euro NCAP</text>
        ''')

        return '\n'.join(elements)

    def _render_interpretation_panel(self) -> str:
        """Render the interpretation panel at bottom."""
        tipo_texto = "Frontal" if self.tipo_impacto == "frontal" else "Lateral"

        return f'''
        <rect x="25" y="{self.height - 115}" width="620" height="95"
              fill="#F9FAFB" stroke="{BRAND_COLORS['gris_claro']}" stroke-width="1" rx="6"/>

        <text x="40" y="{self.height - 90}"
              fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
              font-size="12" font-weight="bold">Interpretacion - Impacto {tipo_texto}</text>

        <text x="40" y="{self.height - 68}"
              fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}" font-size="10">
            • 15-25 km/h: Impacto en capo → Lesiones moderadas (AIS 1-2)
        </text>
        <text x="40" y="{self.height - 50}"
              fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}" font-size="10">
            • 30-40 km/h: Impacto en parabrisas → Lesiones graves, TCE (AIS 3-4)
        </text>
        <text x="340" y="{self.height - 68}"
              fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}" font-size="10">
            • 45-55 km/h: Impacto en techo/pilar → Lesiones criticas (AIS 5+)
        </text>
        <text x="340" y="{self.height - 50}"
              fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}" font-size="10">
            • &gt;55 km/h: Proyeccion completa → Riesgo vital muy alto
        </text>
        '''

    def build_svg(self) -> str:
        """Build the complete WAD diagram SVG."""
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" '
            f'font-family="{FONT_LABEL}">',

            # Background
            f'<rect width="{self.width}" height="{self.height}" fill="{self.background}"/>',

            # Header
            self.add_header(
                f"Diagrama WAD - Impacto {'Frontal' if self.tipo_impacto == 'frontal' else 'Lateral'}",
                "Zonas de Contacto Cabeza"
            ),
        ]

        # Vehicle position (centered horizontally, lower third of canvas)
        if self.view_type == "quarter":
            # Quarter view needs different positioning
            veh_cx = 50   # Embedded car offset x
            veh_cy = 55   # Embedded car offset y
        else:
            veh_cx = 380
            veh_cy = 360

        # WAD reference lines
        svg.append(self._render_wad_lines(veh_cx, veh_cy))

        # Vehicle
        svg.append(self._render_vehicle(veh_cx, veh_cy))

        # Impact markers
        svg.append(self._render_impact_markers(veh_cx, veh_cy))

        # Legend
        svg.append(self._render_legend())

        # Interpretation panel
        svg.append(self._render_interpretation_panel())

        # Footer
        svg.append(self.add_footer())

        svg.append('</svg>')

        return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def crear_diagrama_wad(
    velocidad_impacto: int = None,
    tipo_impacto: str = "frontal",
    tipo_vehiculo: str = "turismo",
    mostrar_ciclista: bool = True,
    view_type: str = "side",
    output_path: str = None
) -> str:
    """
    Create a WAD diagram.

    Args:
        velocidad_impacto: Velocity to highlight (km/h)
        tipo_impacto: "frontal" or "lateral"
        tipo_vehiculo: Vehicle type (turismo, suv, etc.)
        mostrar_ciclista: Show cyclist markers
        view_type: "side" for lateral view, "quarter" for 3/4 front (ITRASA style)
        output_path: Optional path to save SVG

    Returns:
        SVG string
    """
    diagram = WADDiagram(tipo_impacto=tipo_impacto, view_type=view_type)
    diagram.set_vehicle(tipo_vehiculo)
    diagram.show_cyclist = mostrar_ciclista

    if velocidad_impacto:
        diagram.set_highlighted_velocity(velocidad_impacto)

    svg = diagram.build_svg()

    if output_path:
        diagram.save(output_path)

    return svg

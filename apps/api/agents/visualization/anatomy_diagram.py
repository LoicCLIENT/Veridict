"""
AnatomyDiagram - Anatomical injury visualization using pre-made SVG assets.

Uses body_frontal.svg and skull_lateral.svg for professional medical illustrations.
Adds injury markers, zones, and annotations for forensic analysis.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .base_asset import (
    AssetBasedDiagram,
    Point,
    Label,
    BRAND_COLORS,
    FONT_DATA,
    FONT_LABEL,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ANATOMICAL ZONE DATA
# ═══════════════════════════════════════════════════════════════════════════════

# Cranial bone zones with colors
CRANIAL_ZONES = {
    "frontal": {"color": "#FBBF24", "label": "Hueso Frontal"},
    "parietal": {"color": "#60A5FA", "label": "Hueso Parietal"},
    "temporal": {"color": "#F97316", "label": "Hueso Temporal"},
    "occipital": {"color": "#22C55E", "label": "Hueso Occipital"},
    "esfenoides": {"color": "#EC4899", "label": "Esfenoides"},
    "etmoides": {"color": "#8B5CF6", "label": "Etmoides"},
    "nasal": {"color": "#FCD34D", "label": "Huesos Nasales"},
    "maxilar": {"color": "#FCA5A5", "label": "Maxilar"},
    "cigomatico": {"color": "#A78BFA", "label": "Cigomatico"},
    "mandibula": {"color": "#FDE68A", "label": "Mandibula"},
}

# Body regions for injury mapping
BODY_REGIONS = {
    "head": {"label": "Cabeza", "color": "#DC2626"},
    "neck": {"label": "Cuello", "color": "#F97316"},
    "chest": {"label": "Torax", "color": "#3B82F6"},
    "abdomen": {"label": "Abdomen", "color": "#22C55E"},
    "pelvis": {"label": "Pelvis", "color": "#8B5CF6"},
    "upper_limbs": {"label": "Miembros Superiores", "color": "#FBBF24"},
    "lower_limbs": {"label": "Miembros Inferiores", "color": "#EC4899"},
}

# AIS (Abbreviated Injury Scale) severity colors
AIS_COLORS = {
    1: "#22C55E",  # Minor
    2: "#84CC16",  # Moderate
    3: "#FBBF24",  # Serious
    4: "#F97316",  # Severe
    5: "#DC2626",  # Critical
    6: "#7F1D1D",  # Maximum (unsurvivable)
}


@dataclass
class InjuryMarker:
    """Represents an injury on the anatomy diagram."""
    region: str  # Body region or cranial zone
    description: str
    ais_score: int  # 1-6
    position_offset: Tuple[float, float] = (0, 0)  # Relative offset in %


@dataclass
class LesionAnnotation:
    """Detailed lesion annotation."""
    name: str
    tipo: str  # contusion, fractura, hemorragia, laceracion
    localizacion: str
    gravedad: str  # leve, moderada, grave, critica


# ═══════════════════════════════════════════════════════════════════════════════
# SKULL DIAGRAM CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class SkullDiagram(AssetBasedDiagram):
    """
    Anatomical skull diagram showing cranial bones and injury zones.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        view: str = "lateral",  # lateral or frontal
        **kwargs
    ):
        super().__init__(width=width, height=height, **kwargs)

        self.view = view
        self.impact_zone: Optional[str] = None
        self.injuries: List[InjuryMarker] = []
        self.lesions: List[LesionAnnotation] = []

    def set_impact_zone(self, zone: str):
        """Set the primary impact zone (cranial bone)."""
        if zone in CRANIAL_ZONES:
            self.impact_zone = zone

    def add_injury(self, injury: InjuryMarker):
        """Add an injury marker."""
        self.injuries.append(injury)

    def add_lesion(self, lesion: LesionAnnotation):
        """Add a detailed lesion annotation."""
        self.lesions.append(lesion)

    def _get_zone_position(self, zone: str) -> Tuple[float, float]:
        """Get the position of a cranial zone on the diagram."""
        # Positions for lateral view (relative to skull center, % of skull size)
        lateral_positions = {
            "frontal": (0.25, -0.35),
            "parietal": (0.0, -0.45),
            "temporal": (0.25, 0.0),
            "occipital": (-0.35, -0.20),
            "nasal": (0.45, 0.05),
            "maxilar": (0.35, 0.25),
            "cigomatico": (0.40, 0.0),
            "mandibula": (0.15, 0.40),
        }
        return lateral_positions.get(zone, (0, 0))

    def _render_skull_asset(self, cx: float, cy: float) -> str:
        """Render the skull SVG asset."""
        asset_name = "skull_lateral" if self.view == "lateral" else "skull_frontal"

        return self.embed_asset(
            asset_name,
            cx, cy,
            height_meters=0.25,  # ~25cm skull height
            id_suffix="anatomy"
        )

    def _render_impact_highlight(self, cx: float, cy: float, skull_size: float) -> str:
        """Render the impact zone highlight."""
        if not self.impact_zone:
            return ''

        zone_info = CRANIAL_ZONES.get(self.impact_zone)
        if not zone_info:
            return ''

        # Get zone position
        rel_x, rel_y = self._get_zone_position(self.impact_zone)
        zx = cx + rel_x * skull_size
        zy = cy + rel_y * skull_size

        return f'''
        <!-- Impact Zone Highlight -->
        <g id="impact-highlight">
            <circle cx="{zx}" cy="{zy}" r="{skull_size * 0.2}"
                    fill="none" stroke="{BRAND_COLORS['rojo_alerta']}" stroke-width="3">
                <animate attributeName="r"
                         values="{skull_size * 0.15};{skull_size * 0.22};{skull_size * 0.15}"
                         dur="1.5s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="1;0.6;1" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <text x="{zx}" y="{zy - skull_size * 0.25}"
                  fill="{BRAND_COLORS['rojo_alerta']}" font-family="{FONT_LABEL}"
                  font-size="12" font-weight="bold" text-anchor="middle">
                ZONA DE IMPACTO
            </text>
        </g>
        '''

    def _render_zone_legend(self) -> str:
        """Render the cranial bone legend."""
        lx = self.width - 220
        ly = 80

        elements = [
            f'''
            <rect x="{lx}" y="{ly}" width="200" height="280"
                  fill="{BRAND_COLORS['blanco']}" stroke="{BRAND_COLORS['gris_claro']}"
                  stroke-width="1" rx="8"/>
            <text x="{lx + 15}" y="{ly + 25}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="13" font-weight="bold">Huesos del Craneo</text>
            <line x1="{lx + 10}" y1="{ly + 35}" x2="{lx + 190}" y2="{ly + 35}"
                  stroke="{BRAND_COLORS['gris_claro']}"/>
            '''
        ]

        zones = ["frontal", "parietal", "temporal", "occipital", "nasal", "cigomatico", "mandibula"]
        for i, zone in enumerate(zones):
            zone_info = CRANIAL_ZONES.get(zone, {})
            y = ly + 55 + i * 32

            elements.append(f'''
            <rect x="{lx + 15}" y="{y}" width="18" height="18" rx="3"
                  fill="{zone_info.get('color', '#999')}" opacity="0.7"/>
            <text x="{lx + 42}" y="{y + 14}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="12">{zone_info.get('label', zone.title())}</text>
            ''')

        return '\n'.join(elements)

    def _render_lesions_panel(self) -> str:
        """Render the lesions panel."""
        if not self.lesions:
            return ''

        py = self.height - 130
        elements = [
            f'''
            <rect x="25" y="{py}" width="{self.width - 260}" height="110"
                  fill="#FEF2F2" stroke="#FECACA" rx="8"/>
            <text x="40" y="{py + 22}"
                  fill="{BRAND_COLORS['rojo_alerta']}" font-family="{FONT_LABEL}"
                  font-size="13" font-weight="bold">Lesiones Identificadas:</text>
            '''
        ]

        for i, lesion in enumerate(self.lesions[:4]):
            y = py + 45 + i * 20
            elements.append(f'''
            <text x="50" y="{y}"
                  fill="#7F1D1D" font-family="{FONT_LABEL}" font-size="11">
                • {lesion.name}: {lesion.tipo} en {lesion.localizacion} ({lesion.gravedad})
            </text>
            ''')

        return '\n'.join(elements)

    def build_svg(self) -> str:
        """Build the complete skull diagram SVG."""
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
                "Anatomia Craneal - Zonas de Lesion",
                "Analisis Biomecanico Forense"
            ),
        ]

        # Skull position and size
        skull_cx = 300
        skull_cy = 320
        skull_size = 200

        # Skull asset
        svg.append(self._render_skull_asset(skull_cx, skull_cy))

        # Impact zone highlight
        svg.append(self._render_impact_highlight(skull_cx, skull_cy, skull_size))

        # Legend
        svg.append(self._render_zone_legend())

        # Lesions panel
        svg.append(self._render_lesions_panel())

        # Footer
        svg.append(self.add_footer())

        svg.append('</svg>')

        return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# BODY DIAGRAM CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BodyDiagram(AssetBasedDiagram):
    """
    Full body diagram showing injury locations and severity.
    """

    def __init__(
        self,
        width: int = 700,
        height: int = 900,
        view: str = "frontal",
        **kwargs
    ):
        super().__init__(width=width, height=height, **kwargs)

        self.view = view
        self.injuries: List[InjuryMarker] = []

    def add_injury(
        self,
        region: str,
        description: str,
        ais_score: int,
        offset: Tuple[float, float] = (0, 0)
    ):
        """Add an injury to the body diagram."""
        self.injuries.append(InjuryMarker(region, description, ais_score, offset))

    def _get_region_position(self, region: str) -> Tuple[float, float]:
        """Get the center position of a body region."""
        # Relative positions (% of body height from top)
        positions = {
            "head": (0.5, 0.08),
            "neck": (0.5, 0.14),
            "chest": (0.5, 0.28),
            "abdomen": (0.5, 0.42),
            "pelvis": (0.5, 0.52),
            "upper_limbs": (0.20, 0.32),  # Left side
            "lower_limbs": (0.40, 0.75),
        }
        return positions.get(region, (0.5, 0.5))

    def _render_body_asset(self, cx: float, cy: float) -> str:
        """Render the body SVG asset."""
        return self.embed_asset(
            "body_frontal",
            cx, cy,
            height_meters=1.75,  # Average human height
            id_suffix="body"
        )

    def _render_injury_markers(self, body_x: float, body_y: float, body_h: float) -> str:
        """Render injury markers on the body."""
        elements = ['<!-- Injury Markers -->']

        for injury in self.injuries:
            rel_x, rel_y = self._get_region_position(injury.region)

            # Apply offset
            rel_x += injury.position_offset[0]
            rel_y += injury.position_offset[1]

            # Calculate absolute position
            mx = body_x + (rel_x - 0.5) * body_h * 0.4
            my = body_y - body_h / 2 + rel_y * body_h

            # AIS color
            color = AIS_COLORS.get(injury.ais_score, BRAND_COLORS["rojo_alerta"])

            # Marker circle
            elements.append(f'''
            <g class="injury-marker-{injury.region}">
                <circle cx="{mx}" cy="{my}" r="12"
                        fill="{color}" stroke="{BRAND_COLORS['blanco']}" stroke-width="2"/>
                <text x="{mx}" y="{my + 4}"
                      fill="{BRAND_COLORS['blanco']}" font-family="{FONT_DATA}"
                      font-size="10" font-weight="bold" text-anchor="middle">
                    {injury.ais_score}
                </text>
            </g>
            ''')

        return '\n'.join(elements)

    def _render_ais_legend(self) -> str:
        """Render the AIS severity legend."""
        lx = self.width - 180
        ly = 80

        elements = [
            f'''
            <rect x="{lx}" y="{ly}" width="160" height="200"
                  fill="{BRAND_COLORS['blanco']}" stroke="{BRAND_COLORS['gris_claro']}"
                  stroke-width="1" rx="8"/>
            <text x="{lx + 15}" y="{ly + 22}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="12" font-weight="bold">Escala AIS</text>
            <line x1="{lx + 10}" y1="{ly + 32}" x2="{lx + 150}" y2="{ly + 32}"
                  stroke="{BRAND_COLORS['gris_claro']}"/>
            '''
        ]

        ais_labels = {
            1: "Menor",
            2: "Moderada",
            3: "Seria",
            4: "Severa",
            5: "Critica",
            6: "Maxima",
        }

        for i, (ais, label) in enumerate(ais_labels.items()):
            y = ly + 52 + i * 25
            elements.append(f'''
            <circle cx="{lx + 25}" cy="{y}" r="10"
                    fill="{AIS_COLORS[ais]}"/>
            <text x="{lx + 25}" y="{y + 4}"
                  fill="{BRAND_COLORS['blanco']}" font-family="{FONT_DATA}"
                  font-size="9" font-weight="bold" text-anchor="middle">{ais}</text>
            <text x="{lx + 45}" y="{y + 4}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="11">{label}</text>
            ''')

        return '\n'.join(elements)

    def _render_injuries_list(self) -> str:
        """Render the list of injuries."""
        if not self.injuries:
            return ''

        py = self.height - 160
        elements = [
            f'''
            <rect x="25" y="{py}" width="{self.width - 220}" height="140"
                  fill="#F9FAFB" stroke="{BRAND_COLORS['gris_claro']}" rx="8"/>
            <text x="40" y="{py + 22}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}"
                  font-size="12" font-weight="bold">Lesiones Documentadas:</text>
            '''
        ]

        for i, injury in enumerate(self.injuries[:5]):
            y = py + 45 + i * 22
            region_info = BODY_REGIONS.get(injury.region, {})
            elements.append(f'''
            <circle cx="50" cy="{y - 4}" r="6" fill="{AIS_COLORS.get(injury.ais_score, '#999')}"/>
            <text x="65" y="{y}"
                  fill="{BRAND_COLORS['gris_oscuro']}" font-family="{FONT_LABEL}" font-size="11">
                {region_info.get('label', injury.region)}: {injury.description} (AIS {injury.ais_score})
            </text>
            ''')

        return '\n'.join(elements)

    def build_svg(self) -> str:
        """Build the complete body diagram SVG."""
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
                "Diagrama de Lesiones Corporales",
                "Evaluacion Biomecanica"
            ),
        ]

        # Body position and size
        body_cx = 280
        body_cy = 420
        body_height = 550

        # Body asset
        svg.append(self._render_body_asset(body_cx, body_cy))

        # Injury markers
        svg.append(self._render_injury_markers(body_cx, body_cy, body_height))

        # AIS Legend
        svg.append(self._render_ais_legend())

        # Injuries list
        svg.append(self._render_injuries_list())

        # Footer
        svg.append(self.add_footer())

        svg.append('</svg>')

        return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def crear_diagrama_craneo(
    zona_impacto: str = None,
    lesiones: List[Dict[str, str]] = None,
    output_path: str = None
) -> str:
    """
    Create a skull diagram.

    Args:
        zona_impacto: Cranial bone zone (frontal, parietal, temporal, occipital)
        lesiones: List of lesion dicts with name, tipo, localizacion, gravedad
        output_path: Optional path to save SVG

    Returns:
        SVG string
    """
    diagram = SkullDiagram()

    if zona_impacto:
        diagram.set_impact_zone(zona_impacto)

    for lesion in (lesiones or []):
        diagram.add_lesion(LesionAnnotation(
            name=lesion.get("name", "Lesion"),
            tipo=lesion.get("tipo", "contusion"),
            localizacion=lesion.get("localizacion", ""),
            gravedad=lesion.get("gravedad", "moderada")
        ))

    svg = diagram.build_svg()

    if output_path:
        diagram.save(output_path)

    return svg


def crear_diagrama_corporal(
    lesiones: List[Dict[str, Any]] = None,
    output_path: str = None
) -> str:
    """
    Create a body diagram with injury markers.

    Args:
        lesiones: List of injury dicts with region, description, ais_score
        output_path: Optional path to save SVG

    Returns:
        SVG string
    """
    diagram = BodyDiagram()

    for lesion in (lesiones or []):
        diagram.add_injury(
            region=lesion.get("region", "chest"),
            description=lesion.get("description", ""),
            ais_score=lesion.get("ais_score", 2)
        )

    svg = diagram.build_svg()

    if output_path:
        diagram.save(output_path)

    return svg

"""
AssetBasedDiagram - Base class for SVG composition using pre-made assets.

The LLM cannot generate organic shapes well (cars become rectangles, skulls become circles).
This class loads professional SVG assets and only composes, scales and annotates on top.

Rules:
- Vehicles at real scale (Seat Ibiza = 3.81m x 1.64m)
- Mandatory dimensions (cotas) in all croquis
- Visible graphic scale in scene diagrams
- Zero gradients, zero shadows, zero effects
- Typography: Geist Mono for data, Geist Sans for labels
"""

import os
import re
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from xml.etree import ElementTree as ET


# ═══════════════════════════════════════════════════════════════════════════════
# BRAND CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

BRAND_COLORS = {
    "verde": "#1F3329",      # Primary dark green
    "lima": "#C2E94B",       # Accent lime
    "blanco": "#FFFFFF",
    "gris_oscuro": "#374151",
    "gris_medio": "#6B7280",
    "gris_claro": "#E5E7EB",
    "rojo_alerta": "#DC2626",
    "azul_info": "#3B82F6",
    "naranja_warning": "#F97316",
}

# Standard vehicle dimensions (meters)
VEHICLE_DIMENSIONS = {
    "seat_ibiza": (3.81, 1.64, 1.44),      # L x W x H
    "seat_leon": (4.37, 1.80, 1.46),
    "vw_golf": (4.28, 1.79, 1.45),
    "renault_clio": (4.05, 1.73, 1.44),
    "turismo_generico": (4.30, 1.75, 1.45),
    "suv_generico": (4.50, 1.85, 1.70),
    "furgoneta": (5.50, 2.00, 2.20),
    "moto": (2.20, 0.80, 1.20),
    "bicicleta": (1.80, 0.60, 1.10),
}

# Typography
FONT_DATA = "Geist Mono, monospace"
FONT_LABEL = "Geist Sans, Arial, sans-serif"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Point:
    """2D point with optional label."""
    x: float
    y: float
    label: str = ""

    def translate(self, dx: float, dy: float) -> "Point":
        return Point(self.x + dx, self.y + dy, self.label)

    def scale(self, factor: float) -> "Point":
        return Point(self.x * factor, self.y * factor, self.label)

    def rotate(self, angle_deg: float, origin: "Point" = None) -> "Point":
        """Rotate point around origin (default 0,0)."""
        if origin is None:
            origin = Point(0, 0)

        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        dx = self.x - origin.x
        dy = self.y - origin.y

        new_x = origin.x + dx * cos_a - dy * sin_a
        new_y = origin.y + dx * sin_a + dy * cos_a

        return Point(new_x, new_y, self.label)


@dataclass
class Dimension:
    """Technical dimension annotation (cota)."""
    start: Point
    end: Point
    value: float
    unit: str = "m"
    offset: float = 20  # Offset from line in pixels
    precision: int = 2


@dataclass
class Arrow:
    """Arrow annotation for velocity vectors, directions, etc."""
    start: Point
    end: Point
    label: str = ""
    color: str = BRAND_COLORS["verde"]
    width: float = 2


@dataclass
class Label:
    """Text label annotation."""
    position: Point
    text: str
    font_size: int = 12
    color: str = BRAND_COLORS["gris_oscuro"]
    anchor: str = "middle"  # start, middle, end
    is_data: bool = False  # True = Geist Mono, False = Geist Sans


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET BASED DIAGRAM BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class AssetBasedDiagram:
    """
    Base class for creating SVG diagrams using pre-made assets.

    The agent loads professional SVG assets, scales them to real dimensions,
    composes them on a canvas, and adds CAD-style annotations.
    """

    # Path to assets directory
    ASSETS_DIR = Path(__file__).parent / "assets" / "svg"

    def __init__(
        self,
        width: int = 900,
        height: int = 650,
        margin: int = 50,
        background: str = BRAND_COLORS["blanco"]
    ):
        self.width = width
        self.height = height
        self.margin = margin
        self.background = background

        # Canvas coordinate system
        self.canvas_width = width - 2 * margin
        self.canvas_height = height - 2 * margin

        # Scale factor: pixels per meter (default, can be adjusted)
        self.pixels_per_meter = 50.0

        # Loaded assets cache
        self._assets: Dict[str, ET.Element] = {}

        # SVG elements to render
        self._elements: List[str] = []
        self._annotations: List[str] = []

    # ═══════════════════════════════════════════════════════════════════════════
    # ASSET LOADING
    # ═══════════════════════════════════════════════════════════════════════════

    def load_asset(self, asset_name: str) -> Optional[ET.Element]:
        """
        Load an SVG asset from the assets directory.

        Args:
            asset_name: Name of the asset file (without .svg extension)

        Returns:
            Parsed SVG element or None if not found
        """
        if asset_name in self._assets:
            return self._assets[asset_name]

        asset_path = self.ASSETS_DIR / f"{asset_name}.svg"

        if not asset_path.exists():
            print(f"Warning: Asset not found: {asset_path}")
            return None

        try:
            # Parse SVG with namespace handling
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

            tree = ET.parse(asset_path)
            root = tree.getroot()

            self._assets[asset_name] = root
            return root

        except Exception as e:
            print(f"Error loading asset {asset_name}: {e}")
            return None

    def get_asset_viewbox(self, asset: ET.Element) -> Tuple[float, float, float, float]:
        """Extract viewBox from SVG element."""
        viewbox = asset.get("viewBox")
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                return tuple(float(p) for p in parts)

        # Fallback to width/height attributes
        width = float(asset.get("width", "100").replace("px", ""))
        height = float(asset.get("height", "100").replace("px", ""))
        return (0, 0, width, height)

    def embed_asset(
        self,
        asset_name: str,
        x: float,
        y: float,
        width_meters: float = None,
        height_meters: float = None,
        rotation: float = 0,
        flip_horizontal: bool = False,
        flip_vertical: bool = False,
        id_suffix: str = "",
    ) -> str:
        """
        Embed an SVG asset at a specific position with scaling and rotation.

        Args:
            asset_name: Name of the asset file
            x, y: Position in pixels (canvas coordinates)
            width_meters: Desired width in meters (scaled to pixels)
            height_meters: Desired height in meters (scaled to pixels)
            rotation: Rotation in degrees
            flip_horizontal: Mirror horizontally
            flip_vertical: Mirror vertically
            id_suffix: Unique ID suffix for the embedded element

        Returns:
            SVG group element string
        """
        asset = self.load_asset(asset_name)
        if asset is None:
            return f'<!-- Asset not found: {asset_name} -->'

        vb = self.get_asset_viewbox(asset)
        vb_width, vb_height = vb[2] - vb[0], vb[3] - vb[1]

        # Calculate target dimensions
        if width_meters:
            target_width = width_meters * self.pixels_per_meter
            target_height = target_width * (vb_height / vb_width)
        elif height_meters:
            target_height = height_meters * self.pixels_per_meter
            target_width = target_height * (vb_width / vb_height)
        else:
            target_width = vb_width
            target_height = vb_height

        # Calculate scale factors
        scale_x = target_width / vb_width
        scale_y = target_height / vb_height

        # Apply flips
        if flip_horizontal:
            scale_x = -scale_x
        if flip_vertical:
            scale_y = -scale_y

        # Build transform string
        transforms = []

        # Translate to position
        transforms.append(f"translate({x}, {y})")

        # Rotate around center
        if rotation != 0:
            transforms.append(f"rotate({rotation}, 0, 0)")

        # Scale
        transforms.append(f"scale({scale_x}, {scale_y})")

        # Translate to center asset at origin
        transforms.append(f"translate({-vb_width/2}, {-vb_height/2})")

        transform_str = " ".join(transforms)

        # Extract inner content of SVG (skip the root svg element)
        inner_content = []
        for child in asset:
            inner_content.append(ET.tostring(child, encoding='unicode'))

        group_id = f"{asset_name}_{id_suffix}" if id_suffix else asset_name

        return f'''
        <g id="{group_id}" transform="{transform_str}">
            {''.join(inner_content)}
        </g>
        '''

    # ═══════════════════════════════════════════════════════════════════════════
    # ANNOTATION HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    def add_point_marker(
        self,
        point: Point,
        radius: float = 5,
        color: str = BRAND_COLORS["rojo_alerta"],
        label: str = None,
        label_offset: Tuple[float, float] = (10, -10)
    ) -> str:
        """Add a point marker with optional label."""
        elements = [
            f'<circle cx="{point.x}" cy="{point.y}" r="{radius}" '
            f'fill="{color}" stroke="none"/>'
        ]

        if label or point.label:
            text = label or point.label
            lx = point.x + label_offset[0]
            ly = point.y + label_offset[1]
            elements.append(
                f'<text x="{lx}" y="{ly}" fill="{color}" '
                f'font-family="{FONT_DATA}" font-size="10" font-weight="bold">'
                f'{text}</text>'
            )

        return '\n'.join(elements)

    def add_dimension(self, dim: Dimension) -> str:
        """
        Add a technical dimension annotation (cota).

        Creates a dimension line with extension lines and centered value text.
        """
        dx = dim.end.x - dim.start.x
        dy = dim.end.y - dim.start.y
        length = math.sqrt(dx*dx + dy*dy)

        if length == 0:
            return ''

        # Unit vector perpendicular to dimension line
        nx, ny = -dy / length, dx / length

        # Offset points for dimension line
        offset = dim.offset
        s1 = Point(dim.start.x + nx * offset, dim.start.y + ny * offset)
        e1 = Point(dim.end.x + nx * offset, dim.end.y + ny * offset)

        # Midpoint for text
        mx = (s1.x + e1.x) / 2
        my = (s1.y + e1.y) / 2

        # Format value
        value_str = f"{dim.value:.{dim.precision}f} {dim.unit}"

        # Calculate text rotation
        angle = math.degrees(math.atan2(dy, dx))
        if angle > 90 or angle < -90:
            angle += 180

        return f'''
        <!-- Dimension: {value_str} -->
        <!-- Extension lines -->
        <line x1="{dim.start.x}" y1="{dim.start.y}"
              x2="{s1.x}" y2="{s1.y}"
              stroke="{BRAND_COLORS['gris_medio']}" stroke-width="0.5"/>
        <line x1="{dim.end.x}" y1="{dim.end.y}"
              x2="{e1.x}" y2="{e1.y}"
              stroke="{BRAND_COLORS['gris_medio']}" stroke-width="0.5"/>

        <!-- Dimension line -->
        <line x1="{s1.x}" y1="{s1.y}" x2="{e1.x}" y2="{e1.y}"
              stroke="{BRAND_COLORS['gris_oscuro']}" stroke-width="1"/>

        <!-- Arrows -->
        <polygon points="{s1.x},{s1.y} {s1.x + 6*dx/length},{s1.y + 6*dy/length - 3*nx}
                         {s1.x + 6*dx/length},{s1.y + 6*dy/length + 3*nx}"
                 fill="{BRAND_COLORS['gris_oscuro']}"/>
        <polygon points="{e1.x},{e1.y} {e1.x - 6*dx/length},{e1.y - 6*dy/length - 3*nx}
                         {e1.x - 6*dx/length},{e1.y - 6*dy/length + 3*nx}"
                 fill="{BRAND_COLORS['gris_oscuro']}"/>

        <!-- Value text -->
        <text x="{mx}" y="{my - 5}"
              fill="{BRAND_COLORS['gris_oscuro']}"
              font-family="{FONT_DATA}" font-size="11"
              text-anchor="middle"
              transform="rotate({angle}, {mx}, {my - 5})">
            {value_str}
        </text>
        '''

    def add_arrow(self, arrow: Arrow) -> str:
        """Add an arrow annotation."""
        dx = arrow.end.x - arrow.start.x
        dy = arrow.end.y - arrow.start.y
        length = math.sqrt(dx*dx + dy*dy)

        if length == 0:
            return ''

        # Unit vector
        ux, uy = dx / length, dy / length

        # Arrow head size
        head_len = 10
        head_width = 5

        # Arrow head points
        hx1 = arrow.end.x - head_len * ux - head_width * uy
        hy1 = arrow.end.y - head_len * uy + head_width * ux
        hx2 = arrow.end.x - head_len * ux + head_width * uy
        hy2 = arrow.end.y - head_len * uy - head_width * ux

        elements = [
            f'<line x1="{arrow.start.x}" y1="{arrow.start.y}" '
            f'x2="{arrow.end.x - head_len * ux}" y2="{arrow.end.y - head_len * uy}" '
            f'stroke="{arrow.color}" stroke-width="{arrow.width}"/>',

            f'<polygon points="{arrow.end.x},{arrow.end.y} {hx1},{hy1} {hx2},{hy2}" '
            f'fill="{arrow.color}"/>'
        ]

        if arrow.label:
            # Label at midpoint
            mx = (arrow.start.x + arrow.end.x) / 2
            my = (arrow.start.y + arrow.end.y) / 2 - 8
            elements.append(
                f'<text x="{mx}" y="{my}" fill="{arrow.color}" '
                f'font-family="{FONT_DATA}" font-size="10" text-anchor="middle">'
                f'{arrow.label}</text>'
            )

        return '\n'.join(elements)

    def add_label(self, label: Label) -> str:
        """Add a text label."""
        font = FONT_DATA if label.is_data else FONT_LABEL
        return (
            f'<text x="{label.position.x}" y="{label.position.y}" '
            f'fill="{label.color}" font-family="{font}" '
            f'font-size="{label.font_size}" text-anchor="{label.anchor}">'
            f'{label.text}</text>'
        )

    def add_scale_bar(
        self,
        x: float,
        y: float,
        length_meters: float = 5,
        divisions: int = 5
    ) -> str:
        """
        Add a graphic scale bar.

        Args:
            x, y: Position of scale bar
            length_meters: Total length in meters
            divisions: Number of divisions
        """
        total_width = length_meters * self.pixels_per_meter
        div_width = total_width / divisions

        elements = [f'<!-- Scale bar: {length_meters}m -->']

        for i in range(divisions):
            fill = BRAND_COLORS["gris_oscuro"] if i % 2 == 0 else BRAND_COLORS["blanco"]
            stroke = BRAND_COLORS["gris_oscuro"]
            elements.append(
                f'<rect x="{x + i * div_width}" y="{y}" '
                f'width="{div_width}" height="8" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )

        # Labels
        for i in range(divisions + 1):
            value = i * length_meters / divisions
            lx = x + i * div_width
            elements.append(
                f'<text x="{lx}" y="{y + 20}" '
                f'fill="{BRAND_COLORS["gris_oscuro"]}" '
                f'font-family="{FONT_DATA}" font-size="9" text-anchor="middle">'
                f'{value:.0f}</text>'
            )

        # Unit label
        elements.append(
            f'<text x="{x + total_width + 15}" y="{y + 6}" '
            f'fill="{BRAND_COLORS["gris_oscuro"]}" '
            f'font-family="{FONT_LABEL}" font-size="10">m</text>'
        )

        return '\n'.join(elements)

    def add_north_indicator(self, x: float, y: float, size: float = 30) -> str:
        """Add a north arrow indicator."""
        return f'''
        <!-- North indicator -->
        <g transform="translate({x}, {y})">
            <polygon points="0,{-size} {-size*0.3},{size*0.5} 0,{size*0.3} {size*0.3},{size*0.5}"
                     fill="{BRAND_COLORS['gris_oscuro']}" stroke="none"/>
            <polygon points="0,{-size} {size*0.3},{size*0.5} 0,{size*0.3}"
                     fill="{BRAND_COLORS['blanco']}" stroke="{BRAND_COLORS['gris_oscuro']}" stroke-width="0.5"/>
            <text x="0" y="{-size - 5}" fill="{BRAND_COLORS['gris_oscuro']}"
                  font-family="{FONT_LABEL}" font-size="12" font-weight="bold"
                  text-anchor="middle">N</text>
        </g>
        '''

    # ═══════════════════════════════════════════════════════════════════════════
    # SVG GENERATION
    # ═══════════════════════════════════════════════════════════════════════════

    def add_header(
        self,
        title: str,
        subtitle: str = "",
        height: int = 50
    ) -> str:
        """Add a header bar with title."""
        elements = [
            f'<rect x="0" y="0" width="{self.width}" height="{height}" '
            f'fill="{BRAND_COLORS["verde"]}"/>',

            f'<text x="{self.margin}" y="{height/2 + 5}" '
            f'fill="{BRAND_COLORS["blanco"]}" font-family="{FONT_LABEL}" '
            f'font-size="16" font-weight="bold">{title}</text>',
        ]

        if subtitle:
            elements.append(
                f'<text x="{self.width - self.margin}" y="{height/2 + 5}" '
                f'fill="{BRAND_COLORS["lima"]}" font-family="{FONT_LABEL}" '
                f'font-size="12" text-anchor="end">{subtitle}</text>'
            )

        return '\n'.join(elements)

    def add_footer(self) -> str:
        """Add Veridict footer."""
        return (
            f'<text x="{self.width - 10}" y="{self.height - 10}" '
            f'fill="{BRAND_COLORS["gris_medio"]}" font-family="{FONT_LABEL}" '
            f'font-size="9" text-anchor="end">Veridict AI - Reconstruccion Forense</text>'
        )

    def build_svg(self) -> str:
        """
        Build the final SVG string.

        Subclasses should override this method to compose their specific diagram.
        """
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">',

            # Background
            f'<rect width="{self.width}" height="{self.height}" fill="{self.background}"/>',

            # Content area
            f'<g id="content" transform="translate({self.margin}, {self.margin})">',
        ]

        # Add all elements
        svg.extend(self._elements)

        svg.append('</g>')

        # Add annotations on top
        svg.extend(self._annotations)

        # Footer
        svg.append(self.add_footer())

        svg.append('</svg>')

        return '\n'.join(svg)

    def save(self, filepath: str) -> str:
        """Save the SVG to a file."""
        svg_content = self.build_svg()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return filepath

    # ═══════════════════════════════════════════════════════════════════════════
    # COORDINATE HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    def meters_to_pixels(self, meters: float) -> float:
        """Convert meters to pixels."""
        return meters * self.pixels_per_meter

    def pixels_to_meters(self, pixels: float) -> float:
        """Convert pixels to meters."""
        return pixels / self.pixels_per_meter

    def world_to_canvas(self, x_meters: float, y_meters: float) -> Tuple[float, float]:
        """
        Convert world coordinates (meters) to canvas coordinates (pixels).

        World origin (0,0) is at center of canvas.
        Y-axis is inverted (positive up in world, positive down in SVG).
        """
        cx = self.canvas_width / 2 + x_meters * self.pixels_per_meter
        cy = self.canvas_height / 2 - y_meters * self.pixels_per_meter
        return (cx, cy)

    def canvas_to_world(self, x_pixels: float, y_pixels: float) -> Tuple[float, float]:
        """Convert canvas coordinates (pixels) to world coordinates (meters)."""
        x_meters = (x_pixels - self.canvas_width / 2) / self.pixels_per_meter
        y_meters = (self.canvas_height / 2 - y_pixels) / self.pixels_per_meter
        return (x_meters, y_meters)

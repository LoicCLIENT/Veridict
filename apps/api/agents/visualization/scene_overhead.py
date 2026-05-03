"""
SceneOverheadDiagram - Overhead view of accident scene.

Composes pre-made SVG assets (car_top.svg, bicycle_side.svg, etc.) on a
canvas with scale bar, north indicator, dimensions, and annotations.

Rules:
- Vehicles at real scale (Seat Ibiza = 3.81m x 1.64m)
- Visible graphic scale
- North indicator
- Mandatory dimensions (cotas)
- Zero effects (gradients, shadows)
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


@dataclass
class VehiclePosition:
    """Vehicle position in scene."""
    id: str
    tipo: str  # turismo, suv, moto, bicicleta
    x_meters: float  # Position X in meters
    y_meters: float  # Position Y in meters
    rotation: float  # Rotation in degrees (0 = facing right/+X)
    velocidad: float = 0  # km/h
    color_marker: str = None  # Override color for marker
    label: str = None  # Custom label


@dataclass
class TraceMarking:
    """Trace marking on road (skid marks, debris, etc.)."""
    tipo: str  # huella_frenada, restos, liquidos
    puntos: List[Tuple[float, float]]  # List of (x, y) in meters
    ancho_metros: float = 0.2


class SceneOverheadDiagram(AssetBasedDiagram):
    """
    Overhead view of accident scene with vehicles, road, and annotations.
    """

    def __init__(
        self,
        width: int = 1000,
        height: int = 700,
        scale_meters_per_screen: float = 30,  # How many meters fit on screen width
        **kwargs
    ):
        super().__init__(width=width, height=height, **kwargs)

        # Adjust pixels per meter based on desired scale
        self.pixels_per_meter = (width - 2 * self.margin) / scale_meters_per_screen

        # Scene elements
        self.vehicles: List[VehiclePosition] = []
        self.traces: List[TraceMarking] = []
        self.pdi: Optional[Point] = None  # Point of impact
        self.labels: List[Label] = []
        self.arrows: List[Arrow] = []
        self.dimensions: List[Dimension] = []

        # Road configuration
        self.road_width_meters = 7.0  # Default 2-lane road
        self.road_length_meters = 40.0
        self.lane_count = 2

    def set_road(
        self,
        width_meters: float,
        length_meters: float,
        lane_count: int = 2
    ):
        """Configure the road dimensions."""
        self.road_width_meters = width_meters
        self.road_length_meters = length_meters
        self.lane_count = lane_count

    def add_vehicle(self, vehicle: VehiclePosition):
        """Add a vehicle to the scene."""
        self.vehicles.append(vehicle)

    def add_trace(self, trace: TraceMarking):
        """Add a trace marking (skid mark, debris, etc.)."""
        self.traces.append(trace)

    def set_pdi(self, x_meters: float, y_meters: float, label: str = "PDI"):
        """Set the point of impact."""
        self.pdi = Point(x_meters, y_meters, label)

    def add_velocity_vector(
        self,
        vehicle_id: str,
        dx_meters: float,
        dy_meters: float,
        label: str = None
    ):
        """Add a velocity vector to a vehicle."""
        vehicle = next((v for v in self.vehicles if v.id == vehicle_id), None)
        if vehicle:
            start = Point(*self.world_to_canvas(vehicle.x_meters, vehicle.y_meters))
            end = Point(*self.world_to_canvas(
                vehicle.x_meters + dx_meters,
                vehicle.y_meters + dy_meters
            ))
            color = vehicle.color_marker or BRAND_COLORS["azul_info"]
            self.arrows.append(Arrow(start, end, label or "", color, 2))

    def add_measurement(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        label_override: str = None
    ):
        """Add a distance measurement between two points in meters."""
        # Calculate actual distance
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Convert to canvas coordinates
        start = Point(*self.world_to_canvas(x1, y1))
        end = Point(*self.world_to_canvas(x2, y2))

        dim = Dimension(start, end, distance, "m", offset=25, precision=2)
        self.dimensions.append(dim)

    def _render_road(self) -> str:
        """Render the road surface."""
        # Road bounds in canvas coordinates
        half_w = self.road_width_meters / 2
        half_l = self.road_length_meters / 2

        x1, y1 = self.world_to_canvas(-half_l, half_w)
        x2, y2 = self.world_to_canvas(half_l, -half_w)

        road_w = x2 - x1
        road_h = y2 - y1

        elements = [
            '<!-- Road surface -->',
            f'<rect x="{x1}" y="{y1}" width="{road_w}" height="{road_h}" '
            f'fill="#4B5563" stroke="none"/>',
        ]

        # Lane markings
        if self.lane_count >= 2:
            # Center line (dashed)
            cx1, cy = self.world_to_canvas(-half_l, 0)
            cx2, _ = self.world_to_canvas(half_l, 0)

            elements.append(
                f'<line x1="{cx1}" y1="{cy}" x2="{cx2}" y2="{cy}" '
                f'stroke="#FBBF24" stroke-width="3" stroke-dasharray="20,10"/>'
            )

        # Edge lines (solid white)
        for offset in [half_w - 0.3, -half_w + 0.3]:
            ex1, ey = self.world_to_canvas(-half_l, offset)
            ex2, _ = self.world_to_canvas(half_l, offset)
            elements.append(
                f'<line x1="{ex1}" y1="{ey}" x2="{ex2}" y2="{ey}" '
                f'stroke="#FFFFFF" stroke-width="2"/>'
            )

        return '\n'.join(elements)

    def _render_traces(self) -> str:
        """Render trace markings (skid marks, etc.)."""
        elements = ['<!-- Trace markings -->']

        for trace in self.traces:
            if len(trace.puntos) < 2:
                continue

            # Convert points to canvas coordinates
            canvas_points = [self.world_to_canvas(x, y) for x, y in trace.puntos]

            # Build path
            path_d = f"M {canvas_points[0][0]},{canvas_points[0][1]}"
            for px, py in canvas_points[1:]:
                path_d += f" L {px},{py}"

            # Style based on type
            if trace.tipo == "huella_frenada":
                stroke_color = "#1F2937"
                stroke_width = trace.ancho_metros * self.pixels_per_meter
                opacity = 0.7
            elif trace.tipo == "restos":
                stroke_color = "#9CA3AF"
                stroke_width = 2
                opacity = 0.6
            else:
                stroke_color = "#60A5FA"
                stroke_width = 3
                opacity = 0.5

            elements.append(
                f'<path d="{path_d}" fill="none" '
                f'stroke="{stroke_color}" stroke-width="{stroke_width}" '
                f'opacity="{opacity}" stroke-linecap="round"/>'
            )

        return '\n'.join(elements)

    def _render_vehicles(self) -> str:
        """Render vehicles using SVG assets."""
        elements = ['<!-- Vehicles -->']

        for veh in self.vehicles:
            # Get vehicle dimensions
            dims_key = veh.tipo + "_generico" if veh.tipo in ["turismo", "suv"] else veh.tipo
            dims = VEHICLE_DIMENSIONS.get(dims_key, VEHICLE_DIMENSIONS["turismo_generico"])
            length, width, _ = dims

            # Canvas position
            cx, cy = self.world_to_canvas(veh.x_meters, veh.y_meters)

            # Select appropriate asset
            if veh.tipo in ["turismo", "suv", "furgoneta"]:
                asset_name = "car_top"
            elif veh.tipo == "bicicleta":
                asset_name = "bicycle_side"
            elif veh.tipo == "moto":
                asset_name = "bicycle_side"  # Use bicycle as fallback
            else:
                asset_name = "car_top"

            # Embed asset
            # car_top.svg: viewBox 100x200, where height (200) = car length
            # So we use height_meters to scale properly
            embedded = self.embed_asset(
                asset_name,
                cx, cy,
                height_meters=length,  # Asset height = vehicle length in top view
                rotation=veh.rotation - 90,  # Asset faces up (north), adjust to face right
                id_suffix=veh.id
            )
            elements.append(embedded)

            # Vehicle label
            label_y = cy - length * self.pixels_per_meter / 2 - 15
            elements.append(
                f'<text x="{cx}" y="{label_y}" '
                f'fill="{BRAND_COLORS["gris_oscuro"]}" '
                f'font-family="{FONT_LABEL}" font-size="12" font-weight="bold" '
                f'text-anchor="middle">{veh.label or veh.id}</text>'
            )

            # Velocity indicator
            if veh.velocidad > 0:
                elements.append(
                    f'<text x="{cx}" y="{label_y - 15}" '
                    f'fill="{BRAND_COLORS["azul_info"]}" '
                    f'font-family="{FONT_DATA}" font-size="10" '
                    f'text-anchor="middle">{veh.velocidad:.0f} km/h</text>'
                )

        return '\n'.join(elements)

    def _render_pdi(self) -> str:
        """Render point of impact."""
        if not self.pdi:
            return ''

        cx, cy = self.world_to_canvas(self.pdi.x, self.pdi.y)

        return f'''
        <!-- Point of Impact -->
        <g id="pdi">
            <line x1="{cx-12}" y1="{cy-12}" x2="{cx+12}" y2="{cy+12}"
                  stroke="{BRAND_COLORS['rojo_alerta']}" stroke-width="3"/>
            <line x1="{cx-12}" y1="{cy+12}" x2="{cx+12}" y2="{cy-12}"
                  stroke="{BRAND_COLORS['rojo_alerta']}" stroke-width="3"/>
            <circle cx="{cx}" cy="{cy}" r="20" fill="none"
                    stroke="{BRAND_COLORS['rojo_alerta']}" stroke-width="2" stroke-dasharray="5,3"/>
            <text x="{cx}" y="{cy - 28}"
                  fill="{BRAND_COLORS['rojo_alerta']}"
                  font-family="{FONT_LABEL}" font-size="11" font-weight="bold"
                  text-anchor="middle">{self.pdi.label}</text>
        </g>
        '''

    def build_svg(self) -> str:
        """Build the complete scene SVG."""
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">',

            # Background
            f'<rect width="{self.width}" height="{self.height}" fill="#E5E7EB"/>',

            # Header
            self.add_header("Croquis de la Escena - Vista Cenital", "Veridict AI"),
        ]

        # Content area
        svg.append(f'<g id="scene" transform="translate({self.margin}, {self.margin + 50})">')

        # Road
        svg.append(self._render_road())

        # Traces (skid marks)
        svg.append(self._render_traces())

        # Vehicles
        svg.append(self._render_vehicles())

        # Point of impact
        svg.append(self._render_pdi())

        svg.append('</g>')

        # Annotations layer
        svg.append('<g id="annotations">')

        # Arrows
        for arrow in self.arrows:
            svg.append(self.add_arrow(arrow))

        # Dimensions
        for dim in self.dimensions:
            svg.append(self.add_dimension(dim))

        # Labels
        for label in self.labels:
            svg.append(self.add_label(label))

        svg.append('</g>')

        # Scale bar (bottom left)
        scale_x = self.margin + 20
        scale_y = self.height - 50
        svg.append(self.add_scale_bar(scale_x, scale_y, length_meters=5, divisions=5))

        # North indicator (top right)
        north_x = self.width - self.margin - 30
        north_y = self.margin + 80
        svg.append(self.add_north_indicator(north_x, north_y))

        # Footer
        svg.append(self.add_footer())

        svg.append('</svg>')

        return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def crear_croquis_escena(
    vehiculos: List[Dict[str, Any]],
    pdi: Dict[str, float] = None,
    huellas: List[Dict[str, Any]] = None,
    ancho_carretera: float = 7.0,
    largo_carretera: float = 40.0,
    escala: float = 30,  # metros que caben en pantalla
    output_path: str = None,
) -> str:
    """
    Convenience function to create an overhead scene diagram.

    Args:
        vehiculos: List of vehicle dicts with keys:
            - id: Vehicle ID (e.g., "V1")
            - tipo: turismo, suv, bicicleta, moto
            - x, y: Position in meters
            - orientacion: Rotation in degrees
            - velocidad: Speed in km/h (optional)
        pdi: Point of impact dict with x, y keys
        huellas: List of trace markings
        ancho_carretera: Road width in meters
        largo_carretera: Road length in meters
        escala: How many meters fit on screen width
        output_path: Path to save SVG (optional)

    Returns:
        SVG string
    """
    diagram = SceneOverheadDiagram(scale_meters_per_screen=escala)
    diagram.set_road(ancho_carretera, largo_carretera)

    # Add vehicles
    for v in vehiculos:
        diagram.add_vehicle(VehiclePosition(
            id=v.get("id", "V"),
            tipo=v.get("tipo", "turismo"),
            x_meters=v.get("x", 0),
            y_meters=v.get("y", 0),
            rotation=v.get("orientacion", 0),
            velocidad=v.get("velocidad", 0),
            label=v.get("label"),
        ))

    # Add point of impact
    if pdi:
        diagram.set_pdi(pdi.get("x", 0), pdi.get("y", 0))

    # Add traces
    for h in (huellas or []):
        puntos = [(p.get("x", 0), p.get("y", 0)) for p in h.get("puntos", [])]
        if puntos:
            diagram.add_trace(TraceMarking(
                tipo=h.get("tipo", "huella_frenada"),
                puntos=puntos,
                ancho_metros=h.get("ancho", 0.2)
            ))

    svg = diagram.build_svg()

    if output_path:
        diagram.save(output_path)

    return svg

"""
Visualization module for Veridict forensic reconstruction.

Asset-based SVG composition - uses professional pre-made SVGs as base,
only composes, scales and annotates on top.

Key principles:
- Vehicles at real scale (Seat Ibiza = 3.81m x 1.64m)
- Mandatory dimensions (cotas) in all croquis
- Visible graphic scale in scene diagrams
- Zero gradients, shadows, effects
- Typography: Geist Mono for data, Geist Sans for labels
"""

from .base_asset import (
    AssetBasedDiagram,
    Point,
    Dimension,
    Arrow,
    Label,
    BRAND_COLORS,
    VEHICLE_DIMENSIONS,
)
from .scene_overhead import (
    SceneOverheadDiagram,
    VehiclePosition,
    TraceMarking,
    crear_croquis_escena,
)
from .wad_diagram import (
    WADDiagram,
    crear_diagrama_wad,
)
from .anatomy_diagram import (
    SkullDiagram,
    BodyDiagram,
    crear_diagrama_craneo,
    crear_diagrama_corporal,
)
from .telemetry_chart import (
    TelemetryChart,
    crear_grafico_velocidad,
    crear_grafico_energia,
    crear_grafico_trayectorias,
)

__all__ = [
    # Base classes
    "AssetBasedDiagram",
    "Point",
    "Dimension",
    "Arrow",
    "Label",
    "BRAND_COLORS",
    "VEHICLE_DIMENSIONS",
    # Scene diagrams
    "SceneOverheadDiagram",
    "VehiclePosition",
    "TraceMarking",
    "crear_croquis_escena",
    # WAD diagrams
    "WADDiagram",
    "crear_diagrama_wad",
    # Anatomy diagrams
    "SkullDiagram",
    "BodyDiagram",
    "crear_diagrama_craneo",
    "crear_diagrama_corporal",
    # Telemetry charts
    "TelemetryChart",
    "crear_grafico_velocidad",
    "crear_grafico_energia",
    "crear_grafico_trayectorias",
]

"""
TelemetryChart - Scientific publication quality charts for forensic analysis.

Uses matplotlib with seaborn whitegrid style and Veridict brand palette.
Output formats: PNG, SVG, PDF for reports.

Brand palette:
- Primary: #1F3329 (verde oscuro)
- Accent: #C2E94B (lima)
"""

import io
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.ticker import MaxNLocator
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None


# ═══════════════════════════════════════════════════════════════════════════════
# BRAND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BRAND_COLORS = {
    "verde": "#1F3329",
    "lima": "#C2E94B",
    "blanco": "#FFFFFF",
    "gris_oscuro": "#374151",
    "gris_medio": "#6B7280",
    "gris_claro": "#E5E7EB",
    "rojo": "#DC2626",
    "azul": "#3B82F6",
    "naranja": "#F97316",
    "amarillo": "#FBBF24",
}

# Color palette for multi-series plots
PALETTE_SEQUENTIAL = [
    BRAND_COLORS["verde"],
    BRAND_COLORS["lima"],
    BRAND_COLORS["azul"],
    BRAND_COLORS["naranja"],
    BRAND_COLORS["rojo"],
]


def setup_veridict_style():
    """Configure matplotlib/seaborn for Veridict brand styling."""
    if not MATPLOTLIB_AVAILABLE:
        return

    # Use seaborn whitegrid if available
    if SEABORN_AVAILABLE:
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.1)

    # Matplotlib rcParams
    plt.rcParams.update({
        # Fonts - prefer Geist, fallback to system fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Geist Sans', 'Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,

        # Colors
        'axes.facecolor': '#FAFAFA',
        'figure.facecolor': '#FFFFFF',
        'axes.edgecolor': BRAND_COLORS["gris_claro"],
        'axes.labelcolor': BRAND_COLORS["gris_oscuro"],
        'xtick.color': BRAND_COLORS["gris_medio"],
        'ytick.color': BRAND_COLORS["gris_medio"],
        'text.color': BRAND_COLORS["gris_oscuro"],
        'grid.color': BRAND_COLORS["gris_claro"],

        # Grid
        'axes.grid': True,
        'grid.alpha': 0.6,
        'grid.linewidth': 0.5,

        # Lines
        'lines.linewidth': 2,
        'lines.markersize': 6,

        # Figure
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,

        # Legend
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': BRAND_COLORS["gris_claro"],
    })


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TimeSeries:
    """Time series data for telemetry plots."""
    name: str
    time: List[float]  # seconds
    values: List[float]
    unit: str = ""
    color: str = None


@dataclass
class PhaseMarker:
    """Marker for phases in telemetry (pre-impact, impact, post-impact)."""
    time: float
    label: str
    color: str = BRAND_COLORS["rojo"]
    linestyle: str = "--"


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY CHART CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class TelemetryChart:
    """
    Scientific publication quality charts for telemetry and forensic data.
    """

    def __init__(
        self,
        figsize: Tuple[float, float] = (10, 6),
        title: str = "",
        subtitle: str = ""
    ):
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required. Install with: pip install matplotlib")

        setup_veridict_style()

        self.figsize = figsize
        self.title = title
        self.subtitle = subtitle

        self.fig = None
        self.ax = None
        self.axes = []  # For multi-panel plots

        self._series: List[TimeSeries] = []
        self._phase_markers: List[PhaseMarker] = []

    def _create_figure(self, nrows: int = 1, ncols: int = 1, sharex: bool = True):
        """Create matplotlib figure."""
        self.fig, axes = plt.subplots(
            nrows, ncols,
            figsize=self.figsize,
            sharex=sharex,
            squeeze=False
        )
        self.axes = axes.flatten().tolist()
        self.ax = self.axes[0]
        return self.fig, self.axes

    def add_series(self, series: TimeSeries):
        """Add a time series to the chart."""
        self._series.append(series)

    def add_phase_marker(self, marker: PhaseMarker):
        """Add a phase marker (vertical line at specific time)."""
        self._phase_markers.append(marker)

    def plot_velocity_time(
        self,
        velocidades: Dict[str, List[Tuple[float, float]]],
        t_impacto: float = None,
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Plot velocity vs time for multiple vehicles.

        Args:
            velocidades: Dict of vehicle_id -> list of (time, velocity) tuples
            t_impacto: Time of impact (seconds)
            output_path: Path to save (PNG, SVG, or PDF)

        Returns:
            SVG string if no output_path, else the path
        """
        self._create_figure()

        colors = iter(PALETTE_SEQUENTIAL)

        for veh_id, data in velocidades.items():
            times = [d[0] for d in data]
            vels = [d[1] for d in data]
            color = next(colors, BRAND_COLORS["verde"])

            self.ax.plot(times, vels, label=veh_id, color=color, linewidth=2)
            self.ax.scatter(times, vels, color=color, s=20, zorder=5)

        # Impact marker
        if t_impacto is not None:
            self.ax.axvline(
                t_impacto,
                color=BRAND_COLORS["rojo"],
                linestyle="--",
                linewidth=1.5,
                label="Impacto"
            )

        # Phase markers
        for marker in self._phase_markers:
            self.ax.axvline(
                marker.time,
                color=marker.color,
                linestyle=marker.linestyle,
                linewidth=1.5,
                label=marker.label
            )

        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Velocidad (km/h)")
        self.ax.set_title(self.title or "Perfil de Velocidad vs Tiempo")
        self.ax.legend(loc="best")
        self.ax.set_xlim(left=0)
        self.ax.set_ylim(bottom=0)

        # Add Veridict watermark
        self._add_watermark()

        return self._finalize(output_path)

    def plot_acceleration_time(
        self,
        aceleraciones: Dict[str, List[Tuple[float, float]]],
        t_impacto: float = None,
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Plot acceleration vs time (g-forces).

        Args:
            aceleraciones: Dict of vehicle_id -> list of (time, accel_g) tuples
            t_impacto: Time of impact
            output_path: Path to save

        Returns:
            SVG string or path
        """
        self._create_figure()

        colors = iter(PALETTE_SEQUENTIAL)

        for veh_id, data in aceleraciones.items():
            times = [d[0] for d in data]
            accels = [d[1] for d in data]
            color = next(colors, BRAND_COLORS["verde"])

            self.ax.plot(times, accels, label=veh_id, color=color, linewidth=2)

        # Zero reference line
        self.ax.axhline(0, color=BRAND_COLORS["gris_medio"], linewidth=0.5)

        # Impact marker
        if t_impacto is not None:
            self.ax.axvline(
                t_impacto,
                color=BRAND_COLORS["rojo"],
                linestyle="--",
                linewidth=1.5,
                label="Impacto"
            )

        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Aceleracion (g)")
        self.ax.set_title(self.title or "Perfil de Aceleracion")
        self.ax.legend(loc="best")

        self._add_watermark()
        return self._finalize(output_path)

    def plot_energy_distribution(
        self,
        energias: Dict[str, float],
        total_energy: float = None,
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Plot energy distribution bar chart.

        Args:
            energias: Dict of category -> energy in kJ
            total_energy: Total energy for percentage calculation
            output_path: Path to save

        Returns:
            SVG string or path
        """
        self._create_figure(figsize=(8, 5))

        categories = list(energias.keys())
        values = list(energias.values())

        # Create horizontal bar chart
        bars = self.ax.barh(
            categories,
            values,
            color=PALETTE_SEQUENTIAL[:len(categories)],
            edgecolor=BRAND_COLORS["gris_oscuro"],
            linewidth=0.5
        )

        # Add value labels
        for bar, val in zip(bars, values):
            width = bar.get_width()
            label = f"{val:.1f} kJ"
            if total_energy and total_energy > 0:
                pct = (val / total_energy) * 100
                label += f" ({pct:.0f}%)"

            self.ax.text(
                width + max(values) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                label,
                va='center',
                fontsize=9,
                color=BRAND_COLORS["gris_oscuro"]
            )

        self.ax.set_xlabel("Energia (kJ)")
        self.ax.set_title(self.title or "Distribucion de Energia del Impacto")
        self.ax.set_xlim(right=max(values) * 1.3)

        self._add_watermark()
        return self._finalize(output_path)

    def plot_trajectory_xy(
        self,
        trayectorias: Dict[str, List[Tuple[float, float]]],
        pdi: Tuple[float, float] = None,
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Plot 2D trajectory view (bird's eye).

        Args:
            trayectorias: Dict of vehicle_id -> list of (x, y) coordinates
            pdi: Point of impact (x, y)
            output_path: Path to save

        Returns:
            SVG string or path
        """
        self._create_figure(figsize=(10, 8))

        colors = iter(PALETTE_SEQUENTIAL)

        for veh_id, coords in trayectorias.items():
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            color = next(colors, BRAND_COLORS["verde"])

            # Plot trajectory line
            self.ax.plot(xs, ys, label=veh_id, color=color, linewidth=2)

            # Start point (circle)
            self.ax.scatter([xs[0]], [ys[0]], color=color, s=80, marker='o', zorder=5)

            # End point (square)
            self.ax.scatter([xs[-1]], [ys[-1]], color=color, s=80, marker='s', zorder=5)

            # Direction arrow at end
            if len(xs) >= 2:
                dx = xs[-1] - xs[-2]
                dy = ys[-1] - ys[-2]
                self.ax.annotate(
                    '',
                    xy=(xs[-1], ys[-1]),
                    xytext=(xs[-2], ys[-2]),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2)
                )

        # Point of impact
        if pdi:
            self.ax.scatter(
                [pdi[0]], [pdi[1]],
                color=BRAND_COLORS["rojo"],
                s=150,
                marker='X',
                label="PDI",
                zorder=10
            )
            self.ax.annotate(
                'PDI',
                xy=pdi,
                xytext=(pdi[0] + 1, pdi[1] + 1),
                fontsize=10,
                color=BRAND_COLORS["rojo"],
                fontweight='bold'
            )

        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_title(self.title or "Trayectorias de Vehiculos")
        self.ax.legend(loc="best")
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.5)

        self._add_watermark()
        return self._finalize(output_path)

    def plot_damage_distribution(
        self,
        zonas: Dict[str, float],
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Plot damage distribution as radar/polar chart.

        Args:
            zonas: Dict of zone name -> damage severity (0-100)
            output_path: Path to save

        Returns:
            SVG string or path
        """
        categories = list(zonas.keys())
        values = list(zonas.values())

        # Number of variables
        N = len(categories)

        # Compute angle for each category
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        values += values[:1]  # Complete the loop
        angles += angles[:1]

        # Create polar plot
        self.fig, self.ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        # Draw the chart
        self.ax.plot(angles, values, color=BRAND_COLORS["verde"], linewidth=2)
        self.ax.fill(angles, values, color=BRAND_COLORS["lima"], alpha=0.4)

        # Set category labels
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(categories, fontsize=10)

        # Set radial limits
        self.ax.set_ylim(0, 100)
        self.ax.set_title(self.title or "Distribucion de Danos por Zona")

        self._add_watermark()
        return self._finalize(output_path)

    def plot_multi_panel(
        self,
        panels: List[Dict[str, Any]],
        output_path: str = None
    ) -> Union[str, bytes]:
        """
        Create a multi-panel figure with different chart types.

        Args:
            panels: List of panel configs, each with:
                - type: "velocity", "acceleration", "trajectory", "bar"
                - data: Data for that panel type
                - title: Panel title
            output_path: Path to save

        Returns:
            SVG string or path
        """
        n_panels = len(panels)
        nrows = (n_panels + 1) // 2
        ncols = min(2, n_panels)

        self._create_figure(nrows=nrows, ncols=ncols)
        self.fig.set_size_inches(12, 4 * nrows)

        for idx, panel in enumerate(panels):
            ax = self.axes[idx]
            panel_type = panel.get("type", "line")
            data = panel.get("data", {})
            title = panel.get("title", "")

            if panel_type == "velocity":
                colors = iter(PALETTE_SEQUENTIAL)
                for veh_id, points in data.items():
                    times = [p[0] for p in points]
                    vels = [p[1] for p in points]
                    ax.plot(times, vels, label=veh_id, color=next(colors))
                ax.set_xlabel("Tiempo (s)")
                ax.set_ylabel("Velocidad (km/h)")

            elif panel_type == "acceleration":
                colors = iter(PALETTE_SEQUENTIAL)
                for veh_id, points in data.items():
                    times = [p[0] for p in points]
                    accels = [p[1] for p in points]
                    ax.plot(times, accels, label=veh_id, color=next(colors))
                ax.axhline(0, color=BRAND_COLORS["gris_medio"], linewidth=0.5)
                ax.set_xlabel("Tiempo (s)")
                ax.set_ylabel("Aceleracion (g)")

            elif panel_type == "bar":
                categories = list(data.keys())
                values = list(data.values())
                ax.bar(categories, values, color=PALETTE_SEQUENTIAL[:len(categories)])
                ax.set_ylabel(panel.get("unit", ""))

            ax.set_title(title)
            ax.legend(loc="best")

        # Hide empty axes
        for idx in range(len(panels), len(self.axes)):
            self.axes[idx].set_visible(False)

        self.fig.suptitle(self.title, fontsize=14, fontweight='bold', y=1.02)
        self.fig.tight_layout()

        self._add_watermark()
        return self._finalize(output_path)

    def _add_watermark(self):
        """Add Veridict watermark to the figure."""
        self.fig.text(
            0.99, 0.01,
            "Veridict AI - Reconstruccion Forense",
            fontsize=8,
            color=BRAND_COLORS["gris_medio"],
            ha='right',
            va='bottom',
            alpha=0.7
        )

    def _finalize(self, output_path: str = None) -> Union[str, bytes]:
        """Finalize and return the chart."""
        self.fig.tight_layout()

        if output_path:
            # Determine format from extension
            ext = Path(output_path).suffix.lower()
            fmt = ext[1:] if ext else 'png'
            self.fig.savefig(output_path, format=fmt, bbox_inches='tight')
            plt.close(self.fig)
            return output_path

        else:
            # Return SVG string
            buf = io.BytesIO()
            self.fig.savefig(buf, format='svg', bbox_inches='tight')
            plt.close(self.fig)
            buf.seek(0)
            return buf.read().decode('utf-8')

    def close(self):
        """Close the figure."""
        if self.fig:
            plt.close(self.fig)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def crear_grafico_velocidad(
    datos_velocidad: Dict[str, List[Tuple[float, float]]],
    t_impacto: float = None,
    titulo: str = "Perfil de Velocidad",
    output_path: str = None
) -> str:
    """
    Create a velocity vs time chart.

    Args:
        datos_velocidad: Dict of vehicle_id -> [(time, velocity), ...]
        t_impacto: Impact time in seconds
        titulo: Chart title
        output_path: Optional path to save

    Returns:
        SVG string or file path
    """
    chart = TelemetryChart(title=titulo)
    return chart.plot_velocity_time(datos_velocidad, t_impacto, output_path)


def crear_grafico_energia(
    distribucion_energia: Dict[str, float],
    energia_total: float = None,
    titulo: str = "Distribucion de Energia",
    output_path: str = None
) -> str:
    """
    Create an energy distribution chart.

    Args:
        distribucion_energia: Dict of category -> energy in kJ
        energia_total: Total energy for percentage
        titulo: Chart title
        output_path: Optional path to save

    Returns:
        SVG string or file path
    """
    chart = TelemetryChart(title=titulo)
    return chart.plot_energy_distribution(distribucion_energia, energia_total, output_path)


def crear_grafico_trayectorias(
    trayectorias: Dict[str, List[Tuple[float, float]]],
    pdi: Tuple[float, float] = None,
    titulo: str = "Trayectorias",
    output_path: str = None
) -> str:
    """
    Create a 2D trajectory plot.

    Args:
        trayectorias: Dict of vehicle_id -> [(x, y), ...]
        pdi: Point of impact (x, y)
        titulo: Chart title
        output_path: Optional path to save

    Returns:
        SVG string or file path
    """
    chart = TelemetryChart(title=titulo)
    return chart.plot_trajectory_xy(trayectorias, pdi, output_path)

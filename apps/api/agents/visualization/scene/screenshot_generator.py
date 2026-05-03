"""
Screenshot Generator - Genera capturas SVG/PNG de la escena en momentos clave.

Momentos clave generados:
- inicio: Posición inicial de los vehículos
- pre_frenada: 1 segundo antes del inicio de frenada
- frenada: Momento en que comienza la frenada
- pre_impacto: 0.5 segundos antes del impacto
- impacto: Momento exacto del impacto
- post_impacto: 1 segundo después del impacto
"""

import math
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import uuid

# Para exportar PNG (opcional, requiere cairosvg)
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


@dataclass
class MomentoCaptura:
    """Definición de un momento para capturar."""
    nombre: str
    tiempo_normalizado: float  # 0-100 (porcentaje del timeline)
    descripcion: str
    destacar_frenada: bool = False
    destacar_impacto: bool = False


# Colores de marca Veridict
COLORS = {
    "verde_oscuro": "#1F3329",
    "lima": "#C2E94B",
    "gris": "#374151",
    "rojo": "#DC2626",
    "naranja": "#F97316",
    "azul": "#3B82F6",
    "blanco": "#FFFFFF",
    "negro": "#000000",
    "fondo": "#0d110d",
}


def interpolar_punto(trajectory: List[Dict], tiempo_normalizado: float, tiempo_total: float) -> Dict:
    """
    Interpola la posición de un vehículo en un tiempo dado.

    Args:
        trajectory: Lista de puntos de trayectoria
        tiempo_normalizado: Porcentaje del timeline (0-100)
        tiempo_total: Tiempo total de la simulación en segundos

    Returns:
        Diccionario con x, y, speed interpolados
    """
    if not trajectory:
        return {"x": 0, "y": 0, "speed": 0}

    # Convertir tiempo normalizado a tiempo real
    tiempo_real = (tiempo_normalizado / 100) * tiempo_total

    # Encontrar puntos anterior y siguiente
    prev_point = trajectory[0]
    next_point = trajectory[-1]

    for i in range(len(trajectory) - 1):
        if trajectory[i]["time"] <= tiempo_real <= trajectory[i + 1]["time"]:
            prev_point = trajectory[i]
            next_point = trajectory[i + 1]
            break

    # Interpolar
    dt = next_point["time"] - prev_point["time"]
    if dt == 0:
        t = 0
    else:
        t = (tiempo_real - prev_point["time"]) / dt

    t = max(0, min(1, t))

    return {
        "x": prev_point["x"] + (next_point["x"] - prev_point["x"]) * t,
        "y": prev_point["y"] + (next_point["y"] - prev_point["y"]) * t,
        "speed": prev_point["speed"] + (next_point["speed"] - prev_point["speed"]) * t,
    }


def calcular_rotacion(trajectory: List[Dict], tiempo_normalizado: float, tiempo_total: float) -> float:
    """Calcula la rotación del vehículo basada en la dirección de movimiento."""
    if len(trajectory) < 2:
        return 0

    tiempo_real = (tiempo_normalizado / 100) * tiempo_total

    # Encontrar dos puntos cercanos para calcular dirección
    for i in range(len(trajectory) - 1):
        if trajectory[i]["time"] <= tiempo_real <= trajectory[i + 1]["time"]:
            dx = trajectory[i + 1]["x"] - trajectory[i]["x"]
            dy = trajectory[i + 1]["y"] - trajectory[i]["y"]
            return math.degrees(math.atan2(dy, dx))

    return 0


class SceneScreenshotGenerator:
    """Generador de capturas de escena."""

    def __init__(
        self,
        scene_data: Dict[str, Any],
        output_dir: str = "uploads/_screenshots",
        case_id: Optional[str] = None,
    ):
        self.scene = scene_data
        self.output_dir = Path(output_dir)
        self.case_id = case_id or str(uuid.uuid4())[:8]

        # Crear directorio de salida
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuración de escena
        self.scene_width = 800
        self.scene_height = 500
        self.view_box = "-30 -30 160 90"

        # Calcular tiempo total
        self.tiempo_total = self.scene.get("impact", {}).get("time", 4.0)

    def _calcular_momentos(self) -> List[MomentoCaptura]:
        """Calcula los momentos clave para capturar."""
        impact_time = self.scene.get("impact", {}).get("time", 4.0)
        brake_time_a = self.scene.get("vehicleA", {}).get("brakeStartTime", 2.0)
        brake_time_b = self.scene.get("vehicleB", {}).get("brakeStartTime", 2.0)
        brake_time = min(brake_time_a, brake_time_b)

        momentos = [
            MomentoCaptura(
                nombre="inicio",
                tiempo_normalizado=0,
                descripcion="Posición inicial de los vehículos",
            ),
            MomentoCaptura(
                nombre="pre_frenada",
                tiempo_normalizado=max(0, (brake_time - 1.0) / impact_time * 100),
                descripcion="1 segundo antes del inicio de frenada",
            ),
            MomentoCaptura(
                nombre="frenada",
                tiempo_normalizado=(brake_time / impact_time) * 100,
                descripcion="Inicio de la maniobra de frenado",
                destacar_frenada=True,
            ),
            MomentoCaptura(
                nombre="pre_impacto",
                tiempo_normalizado=max(0, (impact_time - 0.5) / impact_time * 100),
                descripcion="0.5 segundos antes del impacto",
            ),
            MomentoCaptura(
                nombre="impacto",
                tiempo_normalizado=100,
                descripcion="Momento del impacto",
                destacar_impacto=True,
            ),
        ]

        return momentos

    def _generar_svg_carretera(self) -> str:
        """Genera el SVG de la carretera."""
        road = self.scene.get("road", {})
        lanes = road.get("lanes", 2)
        lane_width = road.get("laneWidth", 3.5)
        road_type = road.get("type", "straight")
        speed_limit = road.get("speedLimit", 50)

        total_width = lanes * lane_width
        half_width = total_width / 2

        svg_parts = []

        # Fondo de carretera
        svg_parts.append(f'''
        <rect x="-40" y="{-half_width - 3}" width="200" height="{total_width + 6}" fill="#2A2E2A"/>
        <rect x="-40" y="{-half_width}" width="200" height="{total_width}" fill="#3A3E3A"/>
        ''')

        # Líneas de borde
        svg_parts.append(f'''
        <line x1="-40" y1="{-half_width}" x2="160" y2="{-half_width}" stroke="#FFFFFF" stroke-width="0.3"/>
        <line x1="-40" y1="{half_width}" x2="160" y2="{half_width}" stroke="#FFFFFF" stroke-width="0.3"/>
        ''')

        # Línea central (doble amarilla)
        svg_parts.append('''
        <line x1="-40" y1="-0.2" x2="160" y2="-0.2" stroke="#FFD700" stroke-width="0.2"/>
        <line x1="-40" y1="0.2" x2="160" y2="0.2" stroke="#FFD700" stroke-width="0.2"/>
        ''')

        # Líneas de carril (discontinuas)
        for i in range(1, lanes):
            y = -half_width + i * lane_width
            if abs(y) > 0.5:  # No dibujar sobre la línea central
                svg_parts.append(f'''
                <line x1="-40" y1="{y}" x2="160" y2="{y}"
                      stroke="#FFFFFF" stroke-width="0.15" stroke-dasharray="4,6"/>
                ''')

        # Señal de velocidad
        svg_parts.append(f'''
        <g transform="translate(-25, {-half_width - 8})">
            <circle r="3" fill="#FFFFFF" stroke="#DC2626" stroke-width="0.5"/>
            <text y="1" font-size="2.5" fill="#1F2937" text-anchor="middle" font-family="Arial" font-weight="bold">
                {speed_limit}
            </text>
        </g>
        ''')

        return '\n'.join(svg_parts)

    def _generar_svg_vehiculo(
        self,
        x: float,
        y: float,
        rotation: float,
        vehicle_id: str,
        speed: float,
        color: str,
        is_braking: bool = False,
        is_impact: bool = False,
    ) -> str:
        """Genera el SVG de un vehículo."""
        car_length = 5.5
        car_width = 2.2

        # Colores según vehículo
        if vehicle_id == "A":
            body_color = COLORS["azul"]
            highlight = "#60A5FA"
        else:
            body_color = COLORS["naranja"]
            highlight = "#FB923C"

        svg = f'''
        <g transform="translate({x}, {y}) rotate({rotation})">
            <!-- Sombra -->
            <ellipse cx="0.4" cy="0.4" rx="{car_length/2 + 0.3}" ry="{car_width/2 + 0.2}"
                     fill="#000000" opacity="0.4"/>

            <!-- Carrocería -->
            <rect x="{-car_length/2}" y="{-car_width/2}" width="{car_length}" height="{car_width}"
                  rx="0.8" fill="{body_color}"
                  stroke="{"#EF4444" if is_impact else "#1E3A5F"}"
                  stroke-width="{"0.4" if is_impact else "0.15"}"/>

            <!-- Parabrisas -->
            <rect x="{car_length/2 - 2.2}" y="{-car_width/2 + 0.25}" width="1.4" height="{car_width - 0.5}"
                  rx="0.15" fill="#0F172A"/>

            <!-- Identificador -->
            <circle cx="0" cy="0" r="1.2" fill="{body_color}" stroke="#FFFFFF" stroke-width="0.15"/>
            <text x="0" y="0.4" font-size="1.4" fill="#FFFFFF" text-anchor="middle"
                  font-family="monospace" font-weight="bold">{vehicle_id}</text>

            <!-- Luces traseras (rojas si frena) -->
            <rect x="{-car_length/2}" y="{-car_width/2 + 0.2}" width="0.2" height="0.6"
                  fill="{"#FF0000" if is_braking else "#991B1B"}"/>
            <rect x="{-car_length/2}" y="{car_width/2 - 0.8}" width="0.2" height="0.6"
                  fill="{"#FF0000" if is_braking else "#991B1B"}"/>
        '''

        # Efecto de impacto
        if is_impact:
            svg += f'''
            <circle cx="{car_length/2 if vehicle_id == "A" else -car_length/2}" cy="0" r="1.5"
                    fill="#EF4444" opacity="0.6"/>
            '''

        svg += '</g>'

        # Etiqueta de velocidad
        label_y = y - 6 if y < 0 else y + 6
        svg += f'''
        <g transform="translate({x}, {label_y})">
            <rect x="-8" y="-2.5" width="16" height="5" fill="{COLORS["fondo"]}"
                  opacity="0.9" rx="0.5" stroke="{body_color}" stroke-width="0.2"/>
            <text x="0" y="1.2" font-size="3" fill="{body_color}" text-anchor="middle"
                  font-family="monospace" font-weight="bold">{speed:.0f} km/h</text>
        </g>
        '''

        return svg

    def _generar_svg_impacto(self, x: float, y: float, show_animation: bool = False) -> str:
        """Genera el marcador de punto de impacto."""
        svg = f'''
        <g transform="translate({x}, {y})">
            <circle r="2" fill="none" stroke="#EF4444" stroke-width="0.5" stroke-dasharray="1,0.5"/>
            <circle r="1" fill="#EF4444"/>
            <circle r="0.5" fill="#FFFFFF"/>
            <text x="0" y="-4" font-size="3" fill="#EF4444" text-anchor="middle" font-family="monospace">
                ⚠ IMPACTO
            </text>
        </g>
        '''
        return svg

    def _generar_svg_trayectorias(
        self,
        tiempo_normalizado: float,
        mostrar_completa: bool = False,
    ) -> str:
        """Genera las líneas de trayectoria."""
        svg_parts = []

        for key, color in [("vehicleA", COLORS["azul"]), ("vehicleB", COLORS["naranja"])]:
            vehicle = self.scene.get(key, {})
            trajectory = vehicle.get("trajectory", [])

            if not trajectory:
                continue

            # Filtrar puntos hasta el tiempo actual
            tiempo_real = (tiempo_normalizado / 100) * self.tiempo_total
            if mostrar_completa:
                visible_points = trajectory
            else:
                visible_points = [p for p in trajectory if p["time"] <= tiempo_real]

            if len(visible_points) < 2:
                continue

            # Construir path
            path_d = f"M {visible_points[0]['x']} {visible_points[0]['y']}"
            for p in visible_points[1:]:
                path_d += f" L {p['x']} {p['y']}"

            svg_parts.append(f'''
            <path d="{path_d}" fill="none" stroke="{color}"
                  stroke-width="0.4" stroke-dasharray="1,0.5" opacity="0.6"/>
            ''')

        return '\n'.join(svg_parts)

    def _generar_svg_mediciones(self, pos_a: Dict, pos_b: Dict) -> str:
        """Genera las mediciones entre vehículos."""
        dx = pos_b["x"] - pos_a["x"]
        dy = pos_b["y"] - pos_a["y"]
        distancia = math.sqrt(dx**2 + dy**2)

        if distancia < 5:
            return ""

        mid_x = (pos_a["x"] + pos_b["x"]) / 2
        mid_y = (pos_a["y"] + pos_b["y"]) / 2

        return f'''
        <line x1="{pos_a["x"]}" y1="{pos_a["y"]}" x2="{pos_b["x"]}" y2="{pos_b["y"]}"
              stroke="{COLORS["lima"]}" stroke-width="0.2" stroke-dasharray="1,0.5"/>
        <rect x="{mid_x - 6}" y="{mid_y - 2.5}" width="12" height="5"
              fill="{COLORS["fondo"]}" opacity="0.9" rx="0.5"/>
        <text x="{mid_x}" y="{mid_y + 1}" font-size="3" fill="{COLORS["lima"]}"
              text-anchor="middle" font-family="monospace" font-weight="bold">
            {distancia:.1f}m
        </text>
        '''

    def _generar_svg_escena(self, momento: MomentoCaptura) -> str:
        """Genera el SVG completo de la escena en un momento dado."""
        # Obtener posiciones de vehículos
        vehicle_a = self.scene.get("vehicleA", {})
        vehicle_b = self.scene.get("vehicleB", {})

        pos_a = interpolar_punto(
            vehicle_a.get("trajectory", []),
            momento.tiempo_normalizado,
            self.tiempo_total
        )
        pos_b = interpolar_punto(
            vehicle_b.get("trajectory", []),
            momento.tiempo_normalizado,
            self.tiempo_total
        )

        rot_a = calcular_rotacion(
            vehicle_a.get("trajectory", []),
            momento.tiempo_normalizado,
            self.tiempo_total
        )
        rot_b = calcular_rotacion(
            vehicle_b.get("trajectory", []),
            momento.tiempo_normalizado,
            self.tiempo_total
        )

        # Determinar si está frenando
        tiempo_real = (momento.tiempo_normalizado / 100) * self.tiempo_total
        is_braking_a = tiempo_real >= vehicle_a.get("brakeStartTime", 9999)
        is_braking_b = tiempo_real >= vehicle_b.get("brakeStartTime", 9999)

        # Construir SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{self.view_box}"
     width="{self.scene_width}" height="{self.scene_height}">

    <!-- Fondo -->
    <rect x="-50" y="-50" width="250" height="150" fill="{COLORS["fondo"]}"/>

    <!-- Header -->
    <rect x="-30" y="-28" width="160" height="8" fill="{COLORS["verde_oscuro"]}" rx="1"/>
    <text x="-25" y="-22" font-size="4" fill="{COLORS["lima"]}" font-family="Arial" font-weight="bold">
        VERIDICT FORENSICS
    </text>
    <text x="125" y="-22" font-size="3" fill="{COLORS["lima"]}" text-anchor="end" font-family="monospace">
        {momento.descripcion}
    </text>

    <!-- Carretera -->
    {self._generar_svg_carretera()}

    <!-- Trayectorias -->
    {self._generar_svg_trayectorias(momento.tiempo_normalizado)}

    <!-- Punto de impacto (si corresponde) -->
    {self._generar_svg_impacto(
        self.scene.get("impact", {}).get("x", 0),
        self.scene.get("impact", {}).get("y", 0)
    ) if momento.destacar_impacto else ""}

    <!-- Vehículos -->
    {self._generar_svg_vehiculo(
        pos_a["x"], pos_a["y"], rot_a, "A", pos_a["speed"],
        COLORS["azul"], is_braking_a, momento.destacar_impacto
    )}
    {self._generar_svg_vehiculo(
        pos_b["x"], pos_b["y"], rot_b, "B", pos_b["speed"],
        COLORS["naranja"], is_braking_b, momento.destacar_impacto
    )}

    <!-- Mediciones -->
    {self._generar_svg_mediciones(pos_a, pos_b)}

    <!-- Footer -->
    <text x="125" y="57" font-size="2.5" fill="#666666" text-anchor="end" font-family="monospace">
        T: {(momento.tiempo_normalizado / 100 * self.tiempo_total):.2f}s | Caso: {self.case_id}
    </text>

    <!-- Escala -->
    <g transform="translate(-25, 50)">
        <line x1="0" y1="0" x2="20" y2="0" stroke="{COLORS["lima"]}" stroke-width="0.5"/>
        <line x1="0" y1="-1" x2="0" y2="1" stroke="{COLORS["lima"]}" stroke-width="0.5"/>
        <line x1="20" y1="-1" x2="20" y2="1" stroke="{COLORS["lima"]}" stroke-width="0.5"/>
        <text x="10" y="4" font-size="2.5" fill="{COLORS["lima"]}" text-anchor="middle" font-family="monospace">
            20m
        </text>
    </g>

</svg>'''

        return svg

    def generar_capturas(self) -> List[Dict[str, Any]]:
        """
        Genera todas las capturas de la escena.

        Returns:
            Lista de diccionarios con información de cada captura
        """
        momentos = self._calcular_momentos()
        capturas = []

        for momento in momentos:
            # Generar SVG
            svg_content = self._generar_svg_escena(momento)

            # Guardar SVG
            svg_filename = f"{self.case_id}_{momento.nombre}.svg"
            svg_path = self.output_dir / svg_filename

            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            captura_info = {
                "nombre": momento.nombre,
                "descripcion": momento.descripcion,
                "tiempo_segundos": (momento.tiempo_normalizado / 100) * self.tiempo_total,
                "svg_path": str(svg_path),
                "png_path": None,
            }

            # Exportar PNG si cairosvg está disponible
            if HAS_CAIROSVG:
                png_filename = f"{self.case_id}_{momento.nombre}.png"
                png_path = self.output_dir / png_filename

                try:
                    cairosvg.svg2png(
                        bytestring=svg_content.encode("utf-8"),
                        write_to=str(png_path),
                        output_width=self.scene_width * 2,  # 2x para mejor calidad
                        output_height=self.scene_height * 2,
                    )
                    captura_info["png_path"] = str(png_path)
                except Exception as e:
                    print(f"Error exportando PNG: {e}")

            capturas.append(captura_info)

        return capturas


def generar_screenshots_caso(
    scene_data: Dict[str, Any],
    case_id: Optional[str] = None,
    output_dir: str = "uploads/_screenshots",
) -> List[Dict[str, Any]]:
    """
    Función principal para generar screenshots de un caso.

    Args:
        scene_data: Datos de la escena (AccidentSceneData)
        case_id: ID del caso (opcional)
        output_dir: Directorio de salida

    Returns:
        Lista de capturas generadas con sus paths
    """
    generator = SceneScreenshotGenerator(
        scene_data=scene_data,
        output_dir=output_dir,
        case_id=case_id,
    )

    return generator.generar_capturas()

"""
Visualizacion 3D Profesional para Reconstruccion de Accidentes.

Este modulo genera visualizaciones 3D de alta calidad similares a las
herramientas profesionales (Virtual Crash, PC-Crash, CloudCompare):

- Escenas 3D interactivas con vehiculos, peatones y carretera
- Diagramas WAD isometricos (vista 3/4)
- Animaciones de secuencia del accidente
- Exportacion a HTML interactivo y PNG estatico

Requiere: plotly, numpy
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None  # Type stub for when Plotly is not installed


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES Y CONFIGURACION
# ═══════════════════════════════════════════════════════════════════════════════

COLORS_3D = {
    "vehiculo_a": "#3B82F6",  # Azul
    "vehiculo_b": "#DC2626",  # Rojo
    "peaton": "#22C55E",      # Verde
    "ciclista": "#F97316",    # Naranja
    "carretera": "#4B5563",   # Gris asfalto
    "linea_carril": "#FCD34D", # Amarillo
    "hierba": "#22C55E",      # Verde hierba
    "pdi": "#EF4444",         # Rojo impacto
    "trayectoria": "#8B5CF6", # Morado
    "huella_frenada": "#1F2937",
}


@dataclass
class Vehiculo3D:
    """Representa un vehiculo para renderizado 3D."""
    id: str
    tipo: str  # turismo, suv, furgoneta, moto, bicicleta
    posicion: Tuple[float, float, float]  # x, y, z (metros)
    orientacion: float  # grados (0 = mirando +X)
    dimensiones: Tuple[float, float, float] = None  # largo, ancho, alto
    color: str = None
    velocidad: float = 0.0  # km/h

    def __post_init__(self):
        if self.dimensiones is None:
            dims = {
                "turismo": (4.5, 1.8, 1.4),
                "suv": (4.8, 2.0, 1.7),
                "furgoneta": (5.5, 2.0, 2.2),
                "moto": (2.2, 0.8, 1.2),
                "bicicleta": (1.8, 0.6, 1.1),
            }
            self.dimensiones = dims.get(self.tipo, (4.5, 1.8, 1.4))
        if self.color is None:
            self.color = COLORS_3D.get(f"vehiculo_{self.id.lower()}", "#6B7280")


@dataclass
class Peaton3D:
    """Representa un peaton/ciclista para renderizado 3D."""
    id: str
    tipo: str  # adulto, nino, ciclista
    posicion: Tuple[float, float, float]
    orientacion: float = 0.0
    altura: float = 1.70
    color: str = None

    def __post_init__(self):
        if self.color is None:
            self.color = COLORS_3D.get(self.tipo, "#22C55E")


# ═══════════════════════════════════════════════════════════════════════════════
# GEOMETRIA 3D DE VEHICULOS
# ═══════════════════════════════════════════════════════════════════════════════

def _crear_vertices_vehiculo(
    largo: float,
    ancho: float,
    alto: float,
    altura_capo: float = 0.9
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Crea los vertices de un vehiculo tipo turismo.
    Retorna arrays x, y, z de los vertices.
    """
    # Vehiculo simplificado pero reconocible
    # Base del vehiculo (chasis)
    base_h = 0.3  # Altura del chasis

    # Puntos del perfil lateral (normalizado 0-1 en largo)
    # Formato: (x_norm, z_bottom, z_top)
    perfil = [
        (0.0, base_h, altura_capo * alto),           # Frontal bajo
        (0.15, base_h, altura_capo * alto + 0.1),    # Capo
        (0.25, base_h, alto * 0.95),                 # Inicio parabrisas
        (0.40, base_h, alto),                        # Techo frontal
        (0.70, base_h, alto),                        # Techo trasero
        (0.85, base_h, alto * 0.85),                 # Luneta trasera
        (1.0, base_h, base_h + 0.4),                 # Trasero
    ]

    vertices_x = []
    vertices_y = []
    vertices_z = []

    # Crear vertices para ambos lados
    for x_norm, z_bot, z_top in perfil:
        x = x_norm * largo - largo / 2  # Centrado en origen

        # Lado izquierdo
        vertices_x.extend([x, x])
        vertices_y.extend([-ancho/2, -ancho/2])
        vertices_z.extend([z_bot, z_top])

        # Lado derecho
        vertices_x.extend([x, x])
        vertices_y.extend([ancho/2, ancho/2])
        vertices_z.extend([z_bot, z_top])

    return np.array(vertices_x), np.array(vertices_y), np.array(vertices_z)


def _crear_mesh_vehiculo_simple(
    largo: float,
    ancho: float,
    alto: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[List[int]]]:
    """
    Crea un mesh simplificado de un vehiculo usando cajas.
    Retorna x, y, z vertices y lista de caras (indices i,j,k).
    """
    # Cuerpo principal (caja)
    cuerpo_h = alto * 0.55
    techo_h = alto - cuerpo_h

    # Vertices del cuerpo
    x = np.array([
        -largo/2, largo/2, largo/2, -largo/2,  # Base inferior
        -largo/2, largo/2, largo/2, -largo/2,  # Base superior cuerpo
    ])
    y = np.array([
        -ancho/2, -ancho/2, ancho/2, ancho/2,
        -ancho/2, -ancho/2, ancho/2, ancho/2,
    ])
    z = np.array([
        0.2, 0.2, 0.2, 0.2,
        cuerpo_h, cuerpo_h, cuerpo_h, cuerpo_h,
    ])

    # Techo (mas estrecho y retrasado)
    techo_largo = largo * 0.5
    techo_ancho = ancho * 0.9
    x_techo = np.array([
        -techo_largo/2, techo_largo/2, techo_largo/2, -techo_largo/2,
        -techo_largo/2, techo_largo/2, techo_largo/2, -techo_largo/2,
    ]) + largo * 0.05  # Ligeramente hacia atras
    y_techo = np.array([
        -techo_ancho/2, -techo_ancho/2, techo_ancho/2, techo_ancho/2,
        -techo_ancho/2, -techo_ancho/2, techo_ancho/2, techo_ancho/2,
    ])
    z_techo = np.array([
        cuerpo_h, cuerpo_h, cuerpo_h, cuerpo_h,
        alto, alto, alto, alto,
    ])

    # Combinar vertices
    x = np.concatenate([x, x_techo])
    y = np.concatenate([y, y_techo])
    z = np.concatenate([z, z_techo])

    return x, y, z


def _rotar_puntos(
    x: np.ndarray,
    y: np.ndarray,
    angulo_grados: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Rota puntos alrededor del eje Z."""
    angulo = math.radians(angulo_grados)
    cos_a = math.cos(angulo)
    sin_a = math.sin(angulo)

    x_rot = x * cos_a - y * sin_a
    y_rot = x * sin_a + y * cos_a

    return x_rot, y_rot


# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE ESCENA 3D CON PLOTLY
# ═══════════════════════════════════════════════════════════════════════════════

def crear_escena_3d(
    vehiculos: List[Dict[str, Any]],
    peatones: List[Dict[str, Any]] = None,
    pdi: Dict[str, float] = None,
    trayectorias: List[Dict[str, Any]] = None,
    huellas: List[Dict[str, Any]] = None,
    dimensiones_carretera: Tuple[float, float] = (50, 20),
    titulo: str = "Reconstruccion 3D del Accidente",
    mostrar_mediciones: bool = True,
    camara_preset: str = "isometric",  # isometric, top, front, side
) -> "go.Figure":
    """
    Genera una escena 3D interactiva del accidente.

    Args:
        vehiculos: Lista de vehiculos con posicion, orientacion, tipo
        peatones: Lista de peatones/ciclistas
        pdi: Punto de impacto {x, y, z}
        trayectorias: Trayectorias pre/post impacto
        huellas: Huellas de frenada
        dimensiones_carretera: (largo, ancho) en metros
        titulo: Titulo de la escena
        camara_preset: Configuracion de camara

    Returns:
        Plotly Figure con la escena 3D interactiva
    """

    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly no esta instalado. Instalar con: pip install plotly")

    fig = go.Figure()

    largo_carretera, ancho_carretera = dimensiones_carretera

    # ═══════════════════════════════════════════════════════════════════════
    # CARRETERA
    # ═══════════════════════════════════════════════════════════════════════

    # Superficie de asfalto
    x_road = np.array([[-largo_carretera/2, largo_carretera/2, largo_carretera/2, -largo_carretera/2]])
    y_road = np.array([[-ancho_carretera/2, -ancho_carretera/2, ancho_carretera/2, ancho_carretera/2]])
    z_road = np.zeros_like(x_road)

    fig.add_trace(go.Surface(
        x=x_road[0], y=y_road[0], z=z_road[0].reshape(1, -1),
        colorscale=[[0, COLORS_3D["carretera"]], [1, COLORS_3D["carretera"]]],
        showscale=False,
        opacity=0.9,
        name="Carretera",
        hoverinfo="skip"
    ))

    # Lineas de carril (discontinuas simuladas con segmentos)
    n_lineas = int(largo_carretera / 3)
    for i in range(n_lineas):
        if i % 2 == 0:  # Solo lineas alternas para efecto discontinuo
            x_start = -largo_carretera/2 + i * 3
            x_end = x_start + 2
            fig.add_trace(go.Scatter3d(
                x=[x_start, x_end],
                y=[0, 0],
                z=[0.01, 0.01],
                mode="lines",
                line=dict(color=COLORS_3D["linea_carril"], width=6),
                showlegend=False,
                hoverinfo="skip"
            ))

    # ═══════════════════════════════════════════════════════════════════════
    # VEHICULOS
    # ═══════════════════════════════════════════════════════════════════════

    for i, veh_data in enumerate(vehiculos or []):
        veh = Vehiculo3D(
            id=veh_data.get("id", f"V{i+1}"),
            tipo=veh_data.get("tipo", "turismo"),
            posicion=(
                veh_data.get("posicion", {}).get("x", 0),
                veh_data.get("posicion", {}).get("y", 0),
                veh_data.get("posicion", {}).get("z", 0)
            ),
            orientacion=veh_data.get("orientacion", 0),
            color=veh_data.get("color"),
            velocidad=veh_data.get("velocidad", 0)
        )

        largo, ancho, alto = veh.dimensiones

        # Crear mesh del vehiculo
        x, y, z = _crear_mesh_vehiculo_simple(largo, ancho, alto)

        # Rotar
        x_rot, y_rot = _rotar_puntos(x, y, veh.orientacion)

        # Trasladar
        x_final = x_rot + veh.posicion[0]
        y_final = y_rot + veh.posicion[1]
        z_final = z + veh.posicion[2]

        # Crear mesh3d
        fig.add_trace(go.Mesh3d(
            x=x_final,
            y=y_final,
            z=z_final,
            color=veh.color,
            opacity=0.9,
            alphahull=0,
            name=f"Vehiculo {veh.id}",
            hovertemplate=f"Vehiculo {veh.id}<br>Vel: {veh.velocidad:.0f} km/h<extra></extra>"
        ))

        # Etiqueta del vehiculo
        fig.add_trace(go.Scatter3d(
            x=[veh.posicion[0]],
            y=[veh.posicion[1]],
            z=[alto + 0.5],
            mode="text",
            text=[f"{veh.id}"],
            textfont=dict(size=16, color=veh.color),
            showlegend=False,
            hoverinfo="skip"
        ))

        # Vector de velocidad
        if veh.velocidad > 0:
            arrow_len = min(veh.velocidad / 20, 5)  # Max 5m de flecha
            angle_rad = math.radians(veh.orientacion)

            fig.add_trace(go.Scatter3d(
                x=[veh.posicion[0], veh.posicion[0] + arrow_len * math.cos(angle_rad)],
                y=[veh.posicion[1], veh.posicion[1] + arrow_len * math.sin(angle_rad)],
                z=[alto/2, alto/2],
                mode="lines",
                line=dict(color=veh.color, width=4),
                showlegend=False,
                hoverinfo="skip"
            ))

    # ═══════════════════════════════════════════════════════════════════════
    # PEATONES / CICLISTAS
    # ═══════════════════════════════════════════════════════════════════════

    for i, peat_data in enumerate(peatones or []):
        peat = Peaton3D(
            id=peat_data.get("id", f"P{i+1}"),
            tipo=peat_data.get("tipo", "adulto"),
            posicion=(
                peat_data.get("posicion", {}).get("x", 0),
                peat_data.get("posicion", {}).get("y", 0),
                peat_data.get("posicion", {}).get("z", 0)
            ),
            altura=peat_data.get("altura", 1.70),
            color=peat_data.get("color")
        )

        # Representar como cilindro + esfera (cuerpo + cabeza)
        # Cuerpo (cilindro simplificado como linea gruesa)
        fig.add_trace(go.Scatter3d(
            x=[peat.posicion[0], peat.posicion[0]],
            y=[peat.posicion[1], peat.posicion[1]],
            z=[0, peat.altura * 0.75],
            mode="lines",
            line=dict(color=peat.color, width=15),
            name=f"{peat.tipo.title()} {peat.id}",
            hovertemplate=f"{peat.tipo.title()}<br>Altura: {peat.altura:.2f}m<extra></extra>"
        ))

        # Cabeza (esfera)
        u = np.linspace(0, 2 * np.pi, 15)
        v = np.linspace(0, np.pi, 10)
        r = 0.12  # Radio cabeza

        x_head = r * np.outer(np.cos(u), np.sin(v)) + peat.posicion[0]
        y_head = r * np.outer(np.sin(u), np.sin(v)) + peat.posicion[1]
        z_head = r * np.outer(np.ones(np.size(u)), np.cos(v)) + peat.altura * 0.85

        fig.add_trace(go.Surface(
            x=x_head, y=y_head, z=z_head,
            colorscale=[[0, peat.color], [1, peat.color]],
            showscale=False,
            opacity=1,
            showlegend=False,
            hoverinfo="skip"
        ))

        # Si es ciclista, agregar bicicleta
        if peat.tipo == "ciclista":
            # Ruedas simplificadas
            for offset in [-0.4, 0.4]:
                theta = np.linspace(0, 2 * np.pi, 20)
                wheel_x = 0.35 * np.cos(theta) + peat.posicion[0] + offset
                wheel_y = np.zeros_like(theta) + peat.posicion[1]
                wheel_z = 0.35 * np.sin(theta) + 0.35

                fig.add_trace(go.Scatter3d(
                    x=wheel_x, y=wheel_y, z=wheel_z,
                    mode="lines",
                    line=dict(color="#1F2937", width=3),
                    showlegend=False,
                    hoverinfo="skip"
                ))

    # ═══════════════════════════════════════════════════════════════════════
    # PUNTO DE IMPACTO
    # ═══════════════════════════════════════════════════════════════════════

    if pdi:
        px, py, pz = pdi.get("x", 0), pdi.get("y", 0), pdi.get("z", 0)

        # Marcador principal
        fig.add_trace(go.Scatter3d(
            x=[px], y=[py], z=[pz + 0.1],
            mode="markers+text",
            marker=dict(size=15, color=COLORS_3D["pdi"], symbol="x"),
            text=["PDI"],
            textposition="top center",
            textfont=dict(size=14, color=COLORS_3D["pdi"]),
            name="Punto de Impacto",
            hovertemplate=f"PDI<br>X: {px:.2f}m<br>Y: {py:.2f}m<extra></extra>"
        ))

        # Circulos concentricos en el suelo
        for r in [1, 2, 3]:
            theta = np.linspace(0, 2 * np.pi, 50)
            fig.add_trace(go.Scatter3d(
                x=r * np.cos(theta) + px,
                y=r * np.sin(theta) + py,
                z=np.zeros_like(theta) + 0.02,
                mode="lines",
                line=dict(color=COLORS_3D["pdi"], width=2, dash="dash"),
                opacity=0.5 - r * 0.1,
                showlegend=False,
                hoverinfo="skip"
            ))

    # ═══════════════════════════════════════════════════════════════════════
    # HUELLAS DE FRENADA
    # ═══════════════════════════════════════════════════════════════════════

    for huella in (huellas or []):
        puntos = huella.get("puntos", [])
        if len(puntos) >= 2:
            x_h = [p.get("x", 0) for p in puntos]
            y_h = [p.get("y", 0) for p in puntos]
            z_h = [0.01] * len(puntos)

            fig.add_trace(go.Scatter3d(
                x=x_h, y=y_h, z=z_h,
                mode="lines",
                line=dict(color=COLORS_3D["huella_frenada"], width=12),
                opacity=0.7,
                name=f"Huella {huella.get('vehiculo', '')}",
                hovertemplate=f"Huella de frenada<br>Long: {huella.get('longitud', 0):.2f}m<extra></extra>"
            ))

    # ═══════════════════════════════════════════════════════════════════════
    # TRAYECTORIAS
    # ═══════════════════════════════════════════════════════════════════════

    for tray in (trayectorias or []):
        puntos = tray.get("puntos", [])
        if len(puntos) >= 2:
            x_t = [p.get("x", 0) for p in puntos]
            y_t = [p.get("y", 0) for p in puntos]
            z_t = [0.5] * len(puntos)  # Elevar trayectoria

            color = tray.get("color", COLORS_3D["trayectoria"])

            fig.add_trace(go.Scatter3d(
                x=x_t, y=y_t, z=z_t,
                mode="lines",
                line=dict(color=color, width=3, dash="dash"),
                opacity=0.8,
                name=f"Trayectoria {tray.get('vehiculo', '')}",
            ))

    # ═══════════════════════════════════════════════════════════════════════
    # CONFIGURACION DE CAMARA Y LAYOUT
    # ═══════════════════════════════════════════════════════════════════════

    # Presets de camara
    camera_presets = {
        "isometric": dict(
            eye=dict(x=1.5, y=1.5, z=1.2),
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0)
        ),
        "top": dict(
            eye=dict(x=0, y=0, z=2.5),
            up=dict(x=0, y=1, z=0),
            center=dict(x=0, y=0, z=0)
        ),
        "front": dict(
            eye=dict(x=2, y=0, z=0.5),
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0)
        ),
        "side": dict(
            eye=dict(x=0, y=2, z=0.5),
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0)
        ),
    }

    camera = camera_presets.get(camara_preset, camera_presets["isometric"])

    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br><sub>Veridict AI - Reconstruccion Forense</sub>",
            x=0.5,
            font=dict(size=18)
        ),
        scene=dict(
            xaxis=dict(
                title="X (m)",
                backgroundcolor="#F3F4F6",
                gridcolor="white",
                showbackground=True,
                range=[-largo_carretera/2 - 5, largo_carretera/2 + 5]
            ),
            yaxis=dict(
                title="Y (m)",
                backgroundcolor="#F3F4F6",
                gridcolor="white",
                showbackground=True,
                range=[-ancho_carretera/2 - 5, ancho_carretera/2 + 5]
            ),
            zaxis=dict(
                title="Z (m)",
                backgroundcolor="#F3F4F6",
                gridcolor="white",
                showbackground=True,
                range=[0, 5]
            ),
            camera=camera,
            aspectmode="data",
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="white",
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA WAD ISOMETRICO (SVG)
# ═══════════════════════════════════════════════════════════════════════════════

def generar_wad_isometrico(
    velocidad_impacto: float = None,
    tipo_impacto: str = "frontal",  # frontal, lateral
    altura_peaton: float = 1.70,
    mostrar_ciclista: bool = True,
    width: int = 900,
    height: int = 650,
) -> str:
    """
    Genera un diagrama WAD con vista isometrica 3/4 estilo ITRASA.

    El vehiculo se muestra como dibujo tecnico lineal desde una perspectiva
    3/4 frontal-superior, con marcadores de impacto posicionados sobre la carroceria.

    Args:
        velocidad_impacto: Velocidad a destacar (km/h)
        tipo_impacto: "frontal" o "lateral"
        altura_peaton: Altura del peaton (m)
        mostrar_ciclista: Si True, muestra marcadores de ciclista

    Returns:
        SVG string del diagrama WAD isometrico
    """

    # Zonas de impacto WAD - posiciones SVG relativas al centro del coche
    # Formato: {velocidad: (svg_x_offset, svg_y_offset, zona_descripcion)}
    # Basado en estudios ITRASA/Euro NCAP: a mayor velocidad, el impacto es mas alto
    # Posiciones calibradas para el nuevo dibujo con proporciones realistas
    zonas_frontal = {
        20: (60, 50, "Capo trasero"),          # Parte trasera del capo - baja velocidad
        30: (20, 25, "Capo central"),          # Centro del capo
        40: (-20, -5, "Parabrisas base"),      # Base del parabrisas
        50: (-50, -45, "Techo/Pilar A"),       # Zona alta - techo
    }

    zonas_lateral = {
        20: (20, 35, "Puerta"),
        30: (-15, 10, "Ventana"),
        40: (-50, -20, "Pilar B"),
        50: (-85, -55, "Techo"),
    }

    zonas = zonas_frontal if tipo_impacto == "frontal" else zonas_lateral

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" ',
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
    ]

    # Fondo blanco limpio (estilo tecnico)
    svg.append(f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>')

    # Header
    tipo_texto = "Frontal" if tipo_impacto == "frontal" else "Lateral"
    svg.append(f'''
    <rect x="0" y="0" width="{width}" height="50" fill="#1F2937"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="16" font-weight="bold">
        Diagrama WAD - Impacto {tipo_texto} - Zonas de Contacto Cabeza
    </text>
    ''')

    # Centro del vehiculo en el SVG
    veh_cx = 380
    veh_cy = 340

    if tipo_impacto == "frontal":
        # =======================================================================
        # COCHE VISTA 3/4 SUPERIOR - Estilo ITRASA profesional
        # Vista desde arriba-adelante-derecha (bird's eye 3/4 angle ~30°)
        # Proporciones realistas de un turismo compacto/sedan
        # =======================================================================
        svg.append(f'''
        <g transform="translate({veh_cx}, {veh_cy})" id="vehiculo-itrasa">
            <!-- ============================================================ -->
            <!-- CUERPO PRINCIPAL - Silueta exterior cerrada                  -->
            <!-- Proporciones: largo ~4.5m, ancho ~1.8m, en perspectiva       -->
            <!-- ============================================================ -->

            <!-- Contorno exterior completo del coche -->
            <path d="M -100,-90
                     L -115,-70
                     L -125,-30
                     L -130,10
                     L -125,50
                     L -100,70
                     L -60,75
                     L -20,78
                     L 40,82
                     L 90,85
                     L 130,80
                     L 155,65
                     L 165,40
                     L 168,10
                     L 165,-20
                     L 155,-45
                     L 130,-60
                     L 90,-70
                     L 40,-80
                     L -20,-85
                     L -60,-88
                     L -100,-90"
                  fill="none" stroke="#2D3748" stroke-width="2.5"/>

            <!-- ============================================================ -->
            <!-- TECHO / CABINA - Vista superior                              -->
            <!-- ============================================================ -->
            <path d="M -70,-65
                     C -50,-70 -20,-72 20,-70
                     L 55,-65
                     L 70,-55
                     L 75,-40
                     L 75,-25
                     L 70,-10
                     L 55,5
                     L 20,15
                     L -20,18
                     L -55,15
                     L -80,5
                     L -90,-15
                     L -90,-40
                     L -80,-55
                     L -70,-65"
                  fill="none" stroke="#2D3748" stroke-width="1.8"/>

            <!-- ============================================================ -->
            <!-- PARABRISAS - Marco trapezoidal inclinado                     -->
            <!-- ============================================================ -->
            <path d="M -65,-55
                     L -55,-35
                     L -45,-20
                     L 30,-15
                     L 55,-20
                     L 65,-35
                     L 70,-50
                     L 50,-58
                     L 10,-60
                     L -30,-58
                     L -65,-55"
                  fill="none" stroke="#2D3748" stroke-width="1.5"/>

            <!-- ============================================================ -->
            <!-- CAPÓ (HOOD) - Superficie principal visible                   -->
            <!-- ============================================================ -->
            <path d="M -45,-20
                     L -70,10
                     L -75,45
                     L -50,60
                     L 60,70
                     L 120,60
                     L 145,35
                     L 155,0
                     L 145,-30
                     L 110,-45
                     L 65,-35
                     L 30,-15
                     L -45,-20"
                  fill="none" stroke="#2D3748" stroke-width="1.5"/>

            <!-- Línea central del capó -->
            <path d="M -10,-15 L 40,25"
                  fill="none" stroke="#4A5568" stroke-width="1" stroke-dasharray="6,3"/>

            <!-- Relieves del capó (líneas de estilo) -->
            <path d="M -30,-5 L 80,15"
                  fill="none" stroke="#718096" stroke-width="0.8"/>
            <path d="M -40,25 L 100,45"
                  fill="none" stroke="#718096" stroke-width="0.8"/>

            <!-- ============================================================ -->
            <!-- LUNETA TRASERA                                               -->
            <!-- ============================================================ -->
            <path d="M -80,-15
                     L -100,-5
                     L -105,25
                     L -90,40
                     L -50,48
                     L 0,50
                     L 30,45
                     L 50,35
                     L 55,15
                     L 30,5
                     L -20,0
                     L -55,0
                     L -80,-15"
                  fill="none" stroke="#2D3748" stroke-width="1.2"/>

            <!-- ============================================================ -->
            <!-- PASO DE RUEDA TRASERO IZQUIERDO                              -->
            <!-- ============================================================ -->
            <path d="M -125,20
                     C -130,40 -120,65 -90,70
                     C -60,75 -40,60 -35,40"
                  fill="none" stroke="#2D3748" stroke-width="2"/>

            <!-- Rueda trasera (vista 3/4) -->
            <ellipse cx="-82" cy="55" rx="32" ry="18"
                     fill="none" stroke="#2D3748" stroke-width="2"/>
            <ellipse cx="-82" cy="55" rx="20" ry="11"
                     fill="none" stroke="#4A5568" stroke-width="1.2"/>
            <ellipse cx="-82" cy="55" rx="8" ry="5"
                     fill="none" stroke="#4A5568" stroke-width="1"/>

            <!-- ============================================================ -->
            <!-- PASO DE RUEDA DELANTERO DERECHO                              -->
            <!-- ============================================================ -->
            <path d="M 90,55
                     C 95,70 115,82 140,78
                     C 160,74 168,55 165,35"
                  fill="none" stroke="#2D3748" stroke-width="2"/>

            <!-- Rueda delantera (vista 3/4, más visible) -->
            <ellipse cx="130" cy="60" rx="30" ry="17"
                     fill="none" stroke="#2D3748" stroke-width="2"/>
            <ellipse cx="130" cy="60" rx="18" ry="10"
                     fill="none" stroke="#4A5568" stroke-width="1.2"/>
            <ellipse cx="130" cy="60" rx="7" ry="4"
                     fill="none" stroke="#4A5568" stroke-width="1"/>

            <!-- ============================================================ -->
            <!-- FAROS                                                        -->
            <!-- ============================================================ -->
            <!-- Faro delantero derecho -->
            <ellipse cx="140" cy="15" rx="20" ry="12"
                     fill="none" stroke="#2D3748" stroke-width="1.5"/>

            <!-- Faro delantero izquierdo (parcialmente visible) -->
            <ellipse cx="-60" cy="40" rx="18" ry="10"
                     fill="none" stroke="#2D3748" stroke-width="1.2"/>

            <!-- ============================================================ -->
            <!-- PARRILLA FRONTAL                                             -->
            <!-- ============================================================ -->
            <path d="M 80,50 L 130,45"
                  fill="none" stroke="#2D3748" stroke-width="1.8"/>
            <path d="M 90,60 L 135,55"
                  fill="none" stroke="#4A5568" stroke-width="1.2"/>

            <!-- ============================================================ -->
            <!-- ESPEJO RETROVISOR IZQUIERDO                                  -->
            <!-- ============================================================ -->
            <ellipse cx="-95" cy="-25" rx="12" ry="8"
                     fill="none" stroke="#2D3748" stroke-width="1.5"/>
            <path d="M -86,-28 L -78,-32"
                  fill="none" stroke="#2D3748" stroke-width="1"/>

            <!-- ============================================================ -->
            <!-- PILARES (A, B, C)                                            -->
            <!-- ============================================================ -->
            <!-- Pilar A izquierdo -->
            <path d="M -65,-55 L -78,-70"
                  fill="none" stroke="#2D3748" stroke-width="2"/>

            <!-- Pilar A derecho -->
            <path d="M 70,-50 L 95,-58"
                  fill="none" stroke="#2D3748" stroke-width="1.8"/>

            <!-- Pilar B -->
            <path d="M 10,-60 L 15,0"
                  fill="none" stroke="#2D3748" stroke-width="1.5"/>

            <!-- Pilar C -->
            <path d="M -50,15 L -70,40"
                  fill="none" stroke="#2D3748" stroke-width="1.5"/>
        </g>
        ''')
    else:
        # Vista lateral - perfil del coche compacto (estilo ITRASA)
        svg.append(f'''
        <g transform="translate({veh_cx}, {veh_cy})" id="vehiculo-lateral">
            <!-- Contorno superior del coche (techo y ventanas) -->
            <path d="M -180,40
                     L -180,0
                     L -150,-30
                     L -100,-60
                     L -40,-80
                     L 40,-85
                     L 100,-80
                     L 150,-55
                     L 180,-20
                     L 190,20
                     L 190,60"
                  fill="none" stroke="#333" stroke-width="1.8"/>

            <!-- Linea inferior (carroceria) -->
            <path d="M -180,60 L -180,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>
            <path d="M -180,90 L -140,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>
            <path d="M -50,90 L 60,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>
            <path d="M 150,90 L 190,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>
            <path d="M 190,90 L 190,60"
                  fill="none" stroke="#333" stroke-width="1.8"/>

            <!-- Ventanas -->
            <path d="M -145,-25
                     L -90,-55
                     L -30,-72
                     L 50,-75
                     L 110,-60
                     L 145,-30
                     L 130,5
                     L -120,5 Z"
                  fill="none" stroke="#333" stroke-width="1.2"/>

            <!-- Pilar A -->
            <path d="M -145,-25 L -160,5"
                  fill="none" stroke="#333" stroke-width="1.5"/>

            <!-- Pilar B -->
            <path d="M 10,-73 L 20,5"
                  fill="none" stroke="#333" stroke-width="1.5"/>

            <!-- Pilar C -->
            <path d="M 110,-60 L 130,5"
                  fill="none" stroke="#333" stroke-width="1.5"/>

            <!-- Paso de rueda trasero -->
            <path d="M -140,90
                     C -140,60 -115,40 -95,40
                     C -75,40 -50,60 -50,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>

            <!-- Paso de rueda delantero -->
            <path d="M 60,90
                     C 60,60 85,40 105,40
                     C 125,40 150,60 150,90"
                  fill="none" stroke="#333" stroke-width="1.8"/>

            <!-- Rueda trasera -->
            <circle cx="-95" cy="75" r="42" fill="none" stroke="#333" stroke-width="1.8"/>
            <circle cx="-95" cy="75" r="28" fill="none" stroke="#333" stroke-width="1"/>
            <circle cx="-95" cy="75" r="10" fill="none" stroke="#333" stroke-width="0.8"/>

            <!-- Rueda delantera -->
            <circle cx="105" cy="75" r="42" fill="none" stroke="#333" stroke-width="1.8"/>
            <circle cx="105" cy="75" r="28" fill="none" stroke="#333" stroke-width="1"/>
            <circle cx="105" cy="75" r="10" fill="none" stroke="#333" stroke-width="0.8"/>

            <!-- Detalles: faros, manijas -->
            <ellipse cx="175" cy="30" rx="12" ry="20" fill="none" stroke="#333" stroke-width="1.2"/>
            <ellipse cx="-175" cy="30" rx="10" ry="15" fill="none" stroke="#333" stroke-width="1.2"/>
            <path d="M -80,15 L -40,15" fill="none" stroke="#333" stroke-width="1"/>
            <path d="M 40,15 L 80,15" fill="none" stroke="#333" stroke-width="1"/>
        </g>
        ''')

    # =======================================================================
    # LINEAS WAD (horizontales de referencia de altura) - Estilo ITRASA amarillo
    # =======================================================================
    wad_lines = [
        {"altura": 1.0, "label": "WAD 1000", "color": "#EAB308"},  # Amarillo como ITRASA
        {"altura": 1.5, "label": "WAD 1500", "color": "#EAB308"},  # Amarillo como ITRASA
    ]

    for wad in wad_lines:
        # Convertir altura a Y en el SVG (escala ~80px/m, invertido)
        wad_y = veh_cy - wad["altura"] * 80 - 50

        svg.append(f'''
        <line x1="50" y1="{wad_y}" x2="580" y2="{wad_y}"
              stroke="{wad['color']}" stroke-width="2" opacity="0.9"/>
        <text x="590" y="{wad_y + 4}" fill="#374151" font-size="11" font-weight="bold">
            {wad['label']}
        </text>
        <text x="35" y="{wad_y + 4}" fill="#6B7280" font-size="10" text-anchor="end">
            {wad['altura']:.1f}m
        </text>
        ''')

    # =======================================================================
    # MARCADORES DE IMPACTO - Estilo ITRASA
    # Triangulos naranjas para peatones, cruces negras para ciclistas
    # =======================================================================
    svg.append('<g id="marcadores-impacto">')

    for vel, (x_off, y_off, zona) in zonas.items():
        # Posicion del marcador sobre el coche
        marker_x = veh_cx + x_off
        marker_y = veh_cy + y_off

        # Triangulo naranja para peaton (estilo ITRASA)
        svg.append(f'''
        <g class="marcador-peaton-{vel}">
            <polygon points="{marker_x},{marker_y - 10} {marker_x - 8},{marker_y + 5} {marker_x + 8},{marker_y + 5}"
                     fill="#F97316" stroke="#000000" stroke-width="1"/>
            <text x="{marker_x + 15}" y="{marker_y}"
                  fill="#F97316" font-size="11" font-weight="bold">
                {vel} km/h
            </text>
        </g>
        ''')

        # Cruz negra para ciclista (estilo ITRASA) - posicionada arriba y a la izquierda
        if mostrar_ciclista:
            cx = marker_x - 30
            cy = marker_y - 25
            svg.append(f'''
            <g class="marcador-ciclista-{vel}">
                <line x1="{cx - 6}" y1="{cy}" x2="{cx + 6}" y2="{cy}"
                      stroke="#000000" stroke-width="2.5"/>
                <line x1="{cx}" y1="{cy - 6}" x2="{cx}" y2="{cy + 6}"
                      stroke="#000000" stroke-width="2.5"/>
                <text x="{cx - 15}" y="{cy - 8}" text-anchor="end"
                      fill="#000000" font-size="10" font-weight="bold">
                    {vel} km/h
                </text>
            </g>
            ''')

    svg.append('</g>')

    # Destacar velocidad especifica si se proporciona
    if velocidad_impacto and int(velocidad_impacto) in zonas:
        x_off, y_off, zona = zonas[int(velocidad_impacto)]
        marker_x = veh_cx + x_off
        marker_y = veh_cy + y_off

        svg.append(f'''
        <g class="velocidad-destacada">
            <circle cx="{marker_x}" cy="{marker_y}" r="25" fill="none"
                    stroke="#DC2626" stroke-width="3">
                <animate attributeName="r" values="20;28;20" dur="1.5s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="1;0.6;1" dur="1.5s" repeatCount="indefinite"/>
            </circle>
        </g>
        ''')

    # =======================================================================
    # PANEL DE LEYENDA (derecha)
    # =======================================================================
    legend_x = 650
    legend_y = 70

    svg.append(f'''
    <rect x="{legend_x}" y="{legend_y}" width="230" height="280"
          fill="white" stroke="#E5E7EB" stroke-width="1" rx="6"/>

    <text x="{legend_x + 15}" y="{legend_y + 22}" fill="#111827" font-size="13" font-weight="bold">
        Leyenda - Zonas de Impacto
    </text>
    <line x1="{legend_x + 10}" y1="{legend_y + 32}" x2="{legend_x + 220}" y2="{legend_y + 32}"
          stroke="#E5E7EB"/>

    <!-- Simbolo peaton - triangulo naranja -->
    <polygon points="{legend_x + 25},{legend_y + 48} {legend_x + 17},{legend_y + 62} {legend_x + 33},{legend_y + 62}"
             fill="#F97316" stroke="#000000" stroke-width="1"/>
    <text x="{legend_x + 45}" y="{legend_y + 58}" fill="#374151" font-size="11">
        Impacto frontal peaton
    </text>

    <!-- Simbolo ciclista - cruz negra -->
    <line x1="{legend_x + 19}" y1="{legend_y + 82}" x2="{legend_x + 31}" y2="{legend_y + 82}"
          stroke="#000000" stroke-width="2.5"/>
    <line x1="{legend_x + 25}" y1="{legend_y + 76}" x2="{legend_x + 25}" y2="{legend_y + 88}"
          stroke="#000000" stroke-width="2.5"/>
    <text x="{legend_x + 45}" y="{legend_y + 86}" fill="#374151" font-size="11">
        Impacto frontal ciclista
    </text>

    <line x1="{legend_x + 10}" y1="{legend_y + 100}" x2="{legend_x + 220}" y2="{legend_y + 100}"
          stroke="#E5E7EB"/>

    <text x="{legend_x + 15}" y="{legend_y + 118}" fill="#111827" font-size="11" font-weight="bold">
        Velocidad y zona de contacto:
    </text>
    ''')

    # Leyenda de cada velocidad
    for i, (vel, (_, _, zona)) in enumerate(zonas.items()):
        y_item = legend_y + 135 + i * 28
        svg.append(f'''
        <text x="{legend_x + 20}" y="{y_item}" fill="#F97316" font-size="11" font-weight="bold">
            {vel} km/h
        </text>
        <text x="{legend_x + 75}" y="{y_item}" fill="#374151" font-size="10">
            → {zona}
        </text>
        ''')

    svg.append(f'''
    <line x1="{legend_x + 10}" y1="{legend_y + 255}" x2="{legend_x + 220}" y2="{legend_y + 255}"
          stroke="#E5E7EB"/>
    <text x="{legend_x + 15}" y="{legend_y + 270}" fill="#6B7280" font-size="8" font-style="italic">
        Basado en estudios ITRASA/Euro NCAP
    </text>
    ''')

    # =======================================================================
    # PANEL DE INTERPRETACION (inferior)
    # =======================================================================
    svg.append(f'''
    <rect x="25" y="{height - 105}" width="600" height="90" fill="#F9FAFB"
          stroke="#E5E7EB" stroke-width="1" rx="6"/>

    <text x="40" y="{height - 82}" fill="#111827" font-size="12" font-weight="bold">
        Interpretacion - Impacto {tipo_texto}
    </text>

    <text x="40" y="{height - 62}" fill="#374151" font-size="10">
        • 15-25 km/h: Impacto en capo → Lesiones moderadas (AIS 1-2)
    </text>
    <text x="40" y="{height - 45}" fill="#374151" font-size="10">
        • 30-40 km/h: Impacto en parabrisas → Lesiones graves, TCE (AIS 3-4)
    </text>
    <text x="330" y="{height - 62}" fill="#374151" font-size="10">
        • 45-55 km/h: Impacto en techo/pilar → Lesiones criticas (AIS 5+)
    </text>
    <text x="330" y="{height - 45}" fill="#374151" font-size="10">
        • &gt;55 km/h: Proyeccion completa → Riesgo vital muy alto
    </text>
    ''')

    # Credito
    svg.append(f'''
    <text x="{width - 20}" y="{height - 8}" text-anchor="end" fill="#9CA3AF" font-size="9">
        Veridict AI - Reconstruccion Forense
    </text>
    ''')

    svg.append('</svg>')

    return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA ANATOMICO DE CRANEO
# ═══════════════════════════════════════════════════════════════════════════════

def generar_diagrama_craneo(
    zona_impacto: str = "frontal",
    lesiones: List[str] = None,
    width: int = 700,
    height: int = 500,
) -> str:
    """
    Genera un diagrama anatomico del craneo mostrando zonas de lesion.

    Args:
        zona_impacto: frontal, parietal, temporal, occipital
        lesiones: Lista de lesiones a destacar

    Returns:
        SVG del diagrama anatomico
    """

    # Colores por zona del craneo
    colores_zonas = {
        "frontal": "#FBBF24",     # Amarillo
        "parietal": "#60A5FA",    # Azul claro
        "temporal": "#F97316",    # Naranja
        "occipital": "#22C55E",   # Verde
        "esfenoides": "#EC4899",  # Rosa
        "etmoides": "#8B5CF6",    # Morado
        "nasal": "#FCD34D",
        "maxilar": "#FCA5A5",
        "cigomatico": "#A78BFA",
        "mandibula": "#FDE68A",
    }

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" ',
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
    ]

    # Fondo
    svg.append(f'''
    <rect width="{width}" height="{height}" fill="#FFFFFF"/>

    <!-- Header -->
    <rect x="0" y="0" width="{width}" height="50" fill="#1E3A5F"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="16" font-weight="bold">
        Anatomia Craneal - Zonas de Lesion por Impacto
    </text>
    ''')

    # Centro del craneo
    cx, cy = 280, 280

    # Dibujar craneo (perfil lateral estilizado)
    svg.append(f'''
    <g transform="translate({cx}, {cy})">
        <!-- Contorno principal del craneo -->
        <path d="M 0,-120
                 C 80,-120 140,-80 150,-20
                 C 155,20 150,60 130,90
                 C 110,120 60,140 20,150
                 C -20,155 -60,140 -90,110
                 C -130,70 -150,20 -145,-30
                 C -140,-80 -100,-120 0,-120 Z"
              fill="none" stroke="#374151" stroke-width="3"/>

        <!-- Hueso Frontal -->
        <path d="M -80,-100
                 C -40,-115 40,-115 80,-100
                 C 100,-85 110,-60 100,-40
                 L 50,-30
                 L -50,-30
                 L -100,-40
                 C -110,-60 -100,-85 -80,-100 Z"
              fill="{colores_zonas['frontal']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
        <text x="-30" y="-60" fill="#111827" font-size="11" font-weight="bold">Frontal</text>

        <!-- Hueso Parietal -->
        <path d="M 80,-100
                 C 120,-80 140,-40 145,0
                 C 145,40 130,70 100,90
                 L 50,60
                 L 50,-30
                 L 100,-40
                 C 110,-60 100,-85 80,-100 Z"
              fill="{colores_zonas['parietal']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
        <text x="80" y="0" fill="#111827" font-size="11" font-weight="bold">Parietal</text>

        <!-- Hueso Temporal -->
        <path d="M 100,90
                 C 80,110 50,120 20,125
                 L 30,80
                 L 50,60
                 L 100,90 Z"
              fill="{colores_zonas['temporal']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
        <text x="50" y="100" fill="#111827" font-size="10">Temporal</text>

        <!-- Hueso Occipital -->
        <path d="M -80,-100
                 C -110,-80 -135,-40 -140,0
                 C -140,40 -120,80 -90,100
                 L -50,70
                 L -50,-30
                 L -100,-40
                 C -110,-60 -100,-85 -80,-100 Z"
              fill="{colores_zonas['occipital']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
        <text x="-110" y="30" fill="#111827" font-size="10">Occipital</text>

        <!-- Mandibula -->
        <path d="M 20,125
                 C 0,140 -30,145 -60,135
                 C -90,125 -95,100 -90,80
                 L -50,70
                 L 30,80
                 L 20,125 Z"
              fill="{colores_zonas['mandibula']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
        <text x="-40" y="115" fill="#111827" font-size="10">Mandibula</text>

        <!-- Orbita (ojo) -->
        <ellipse cx="30" cy="-10" rx="25" ry="20" fill="#F3F4F6" stroke="#374151" stroke-width="1"/>

        <!-- Nasal -->
        <path d="M 10,-5 L 20,30 L 0,40 L -10,30 L 0,-5 Z"
              fill="{colores_zonas['nasal']}" stroke="#374151" stroke-width="1" opacity="0.7"/>

        <!-- Cigomatico -->
        <path d="M 55,-5
                 C 70,10 75,40 60,60
                 L 30,50
                 L 45,20
                 L 55,-5 Z"
              fill="{colores_zonas['cigomatico']}" stroke="#374151" stroke-width="1" opacity="0.7"/>
    </g>
    ''')

    # Destacar zona de impacto
    zona_coords = {
        "frontal": (cx - 30, cy - 70),
        "parietal": (cx + 90, cy),
        "temporal": (cx + 60, cy + 90),
        "occipital": (cx - 100, cy + 20),
    }

    if zona_impacto in zona_coords:
        zx, zy = zona_coords[zona_impacto]
        svg.append(f'''
        <g class="zona-impacto">
            <circle cx="{zx}" cy="{zy}" r="35" fill="none"
                    stroke="#DC2626" stroke-width="3">
                <animate attributeName="r" values="30;40;30" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <text x="{zx}" y="{zy - 45}" text-anchor="middle"
                  fill="#DC2626" font-size="12" font-weight="bold">
                ZONA DE IMPACTO
            </text>
        </g>
        ''')

    # Leyenda de colores
    legend_x = 480
    legend_y = 80

    svg.append(f'''
    <rect x="{legend_x}" y="{legend_y}" width="200" height="280"
          fill="white" stroke="#E5E7EB" rx="8"/>
    <text x="{legend_x + 15}" y="{legend_y + 25}" fill="#111827" font-size="13" font-weight="bold">
        Huesos del Craneo
    </text>
    <line x1="{legend_x + 10}" y1="{legend_y + 35}" x2="{legend_x + 190}" y2="{legend_y + 35}"
          stroke="#E5E7EB"/>
    ''')

    zonas_leyenda = ["frontal", "parietal", "temporal", "occipital", "nasal", "cigomatico", "mandibula"]
    for i, zona in enumerate(zonas_leyenda):
        y = legend_y + 55 + i * 32
        svg.append(f'''
        <rect x="{legend_x + 15}" y="{y}" width="18" height="18" rx="3"
              fill="{colores_zonas[zona]}" opacity="0.7"/>
        <text x="{legend_x + 42}" y="{y + 14}" fill="#374151" font-size="12">
            {zona.title()}
        </text>
        ''')

    # Panel de lesiones
    if lesiones:
        svg.append(f'''
        <rect x="25" y="{height - 120}" width="{width - 240}" height="100"
              fill="#FEF2F2" stroke="#FECACA" rx="8"/>
        <text x="40" y="{height - 95}" fill="#DC2626" font-size="13" font-weight="bold">
            Lesiones Identificadas:
        </text>
        ''')

        for i, lesion in enumerate(lesiones[:4]):
            y = height - 75 + i * 18
            svg.append(f'''
            <text x="50" y="{y}" fill="#7F1D1D" font-size="11">
                • {lesion}
            </text>
            ''')

    # Footer
    svg.append(f'''
    <text x="{width - 20}" y="{height - 10}" text-anchor="end" fill="#9CA3AF" font-size="9">
        Veridict AI - Analisis Biomecanico Forense
    </text>
    ''')

    svg.append('</svg>')

    return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE EXPORTACION
# ═══════════════════════════════════════════════════════════════════════════════

def exportar_escena_html(
    fig: "go.Figure",
    filepath: str,
    include_plotlyjs: bool = True
) -> str:
    """Exporta una escena 3D a HTML interactivo."""

    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly no esta instalado")

    fig.write_html(
        filepath,
        include_plotlyjs=include_plotlyjs,
        full_html=True
    )

    return filepath


def exportar_escena_imagen(
    fig: "go.Figure",
    filepath: str,
    format: str = "png",
    width: int = 1200,
    height: int = 800,
    scale: int = 2
) -> str:
    """Exporta una escena 3D a imagen estatica."""

    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly no esta instalado")

    try:
        fig.write_image(
            filepath,
            format=format,
            width=width,
            height=height,
            scale=scale
        )
        return filepath
    except Exception as e:
        # Si kaleido no esta instalado, intentar con orca o retornar error
        raise RuntimeError(f"No se pudo exportar imagen. Instalar kaleido: pip install kaleido. Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCION DE CONVENIENCIA PARA GENERAR TODAS LAS VISUALIZACIONES
# ═══════════════════════════════════════════════════════════════════════════════

def generar_informe_visual_completo(
    datos_accidente: Dict[str, Any],
    output_dir: str = "./outputs",
) -> Dict[str, str]:
    """
    Genera un conjunto completo de visualizaciones para un accidente.

    Args:
        datos_accidente: Diccionario con todos los datos del accidente
        output_dir: Directorio de salida

    Returns:
        Dict con rutas a los archivos generados
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outputs = {}

    # 1. Escena 3D interactiva
    if PLOTLY_AVAILABLE:
        try:
            fig = crear_escena_3d(
                vehiculos=datos_accidente.get("vehiculos", []),
                peatones=datos_accidente.get("peatones", []),
                pdi=datos_accidente.get("pdi"),
                trayectorias=datos_accidente.get("trayectorias", []),
                huellas=datos_accidente.get("huellas", []),
                titulo="Reconstruccion 3D"
            )
            html_path = os.path.join(output_dir, f"escena_3d_{timestamp}.html")
            exportar_escena_html(fig, html_path)
            outputs["escena_3d_html"] = html_path
        except Exception as e:
            print(f"Error generando escena 3D: {e}")

    # 2. Diagrama WAD isometrico frontal
    try:
        vel_impacto = datos_accidente.get("velocidad_impacto")
        wad_frontal = generar_wad_isometrico(
            velocidad_impacto=vel_impacto,
            tipo_impacto="frontal"
        )
        wad_frontal_path = os.path.join(output_dir, f"wad_frontal_{timestamp}.svg")
        with open(wad_frontal_path, 'w', encoding='utf-8') as f:
            f.write(wad_frontal)
        outputs["wad_frontal"] = wad_frontal_path
    except Exception as e:
        print(f"Error generando WAD frontal: {e}")

    # 3. Diagrama WAD isometrico lateral
    try:
        wad_lateral = generar_wad_isometrico(
            velocidad_impacto=vel_impacto,
            tipo_impacto="lateral"
        )
        wad_lateral_path = os.path.join(output_dir, f"wad_lateral_{timestamp}.svg")
        with open(wad_lateral_path, 'w', encoding='utf-8') as f:
            f.write(wad_lateral)
        outputs["wad_lateral"] = wad_lateral_path
    except Exception as e:
        print(f"Error generando WAD lateral: {e}")

    # 4. Diagrama anatomico
    try:
        zona = datos_accidente.get("zona_impacto_cabeza", "parietal")
        lesiones = datos_accidente.get("lesiones", [])
        craneo = generar_diagrama_craneo(
            zona_impacto=zona,
            lesiones=lesiones
        )
        craneo_path = os.path.join(output_dir, f"anatomia_craneo_{timestamp}.svg")
        with open(craneo_path, 'w', encoding='utf-8') as f:
            f.write(craneo)
        outputs["anatomia_craneo"] = craneo_path
    except Exception as e:
        print(f"Error generando diagrama anatomico: {e}")

    return outputs

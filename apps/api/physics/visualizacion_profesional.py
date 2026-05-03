"""
Visualizacion Profesional para Peritajes Forenses.

Genera visualizaciones de alta calidad similares a las de documentos
profesionales de peritaje (ITRASA, Virtual Crash, SamRAT, etc.):

- Vehiculos con siluetas realistas en perspectiva isometrica
- Diagramas de impacto con mediciones precisas
- Graficos de calculos fisicos con formulas
- Diagramas biomecanicos WAD
- Comparaciones de energia cinetica
- Secuencias temporales de simulacion

Basado en el analisis del documento profesional ITRASA.
"""

import math
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES Y ESTILOS PROFESIONALES
# ═══════════════════════════════════════════════════════════════════════════════

# Paleta de colores profesional (basada en documentos ITRASA)
COLORS = {
    "vehiculo_a": "#2563EB",      # Azul profesional
    "vehiculo_b": "#DC2626",      # Rojo profesional
    "vehiculo_a_light": "#60A5FA",
    "vehiculo_b_light": "#F87171",
    "pdi": "#22C55E",             # Verde impacto
    "trayectoria": "#6B7280",     # Gris trayectoria
    "medicion": "#F59E0B",        # Naranja mediciones
    "fondo_calzada": "#374151",   # Gris oscuro asfalto
    "linea_carril": "#FBBF24",    # Amarillo lineas
    "texto": "#111827",
    "texto_claro": "#FFFFFF",
    "gradiente_velocidad_alto": "#EF4444",
    "gradiente_velocidad_bajo": "#22C55E",
    "energia_alta": "#DC2626",
    "energia_media": "#F59E0B",
    "energia_baja": "#22C55E",
    "grid": "#E5E7EB",
    "fondo": "#F9FAFB",
    "panel": "#1F2937",
    "acento": "#C2E94B",          # Verde Veridict
}

# Siluetas SVG de vehiculos (paths simplificados pero realistas)
VEHICLE_PATHS = {
    "turismo": {
        "body": "M-22,-8 L-18,-8 L-16,-12 L-6,-14 L6,-14 L16,-12 L18,-8 L22,-8 L22,8 L-22,8 Z",
        "cabin": "M-14,-12 L-10,-18 L10,-18 L14,-12 Z",
        "wheels": [(-16, 8), (-16, -8), (16, 8), (16, -8)],
        "width": 44,
        "height": 32,
    },
    "suv": {
        "body": "M-24,-10 L-20,-10 L-18,-14 L-8,-16 L8,-16 L18,-14 L20,-10 L24,-10 L24,10 L-24,10 Z",
        "cabin": "M-16,-14 L-12,-22 L12,-22 L16,-14 Z",
        "wheels": [(-18, 10), (-18, -10), (18, 10), (18, -10)],
        "width": 48,
        "height": 36,
    },
    "furgoneta": {
        "body": "M-28,-10 L-24,-10 L-22,-18 L18,-18 L22,-10 L28,-10 L28,10 L-28,10 Z",
        "cabin": "M-20,-18 L-16,-24 L-8,-24 L-4,-18 Z",
        "wheels": [(-22, 10), (-22, -10), (22, 10), (22, -10)],
        "width": 56,
        "height": 40,
    },
    "motocicleta": {
        "body": "M-12,-3 L-8,-3 L-6,-6 L6,-6 L8,-3 L12,-3 L12,3 L-12,3 Z",
        "cabin": None,
        "wheels": [(-8, 0), (8, 0)],
        "width": 24,
        "height": 12,
    },
    "ciclista": {
        "body": "M-8,-2 L8,-2 L8,2 L-8,2 Z",
        "cabin": None,
        "wheels": [(-6, 0), (6, 0)],
        "width": 16,
        "height": 8,
    },
    "peaton": {
        "body": "M-3,-6 L3,-6 L3,6 L-3,6 Z",
        "cabin": "M0,-10 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0",  # Cabeza circular
        "wheels": [],
        "width": 8,
        "height": 20,
    }
}


@dataclass
class VehiculoRender:
    """Datos para renderizar un vehiculo."""
    id: str
    tipo: str
    marca: str
    modelo: str
    color: str
    posicion: tuple  # (x, y) en metros
    orientacion: float  # grados
    velocidad: float  # km/h
    es_posicion_final: bool = False
    opacidad: float = 1.0


@dataclass
class MedicionRender:
    """Datos para renderizar una medicion."""
    inicio: tuple
    fin: tuple
    valor: float
    unidad: str
    etiqueta: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# GENERADORES SVG PROFESIONALES
# ═══════════════════════════════════════════════════════════════════════════════

def _create_gradient_defs() -> str:
    """Crea definiciones de gradientes para efectos profesionales."""
    return f'''
    <defs>
        <!-- Gradiente de asfalto -->
        <linearGradient id="asfaltoGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#4B5563;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1F2937;stop-opacity:1" />
        </linearGradient>

        <!-- Gradiente vehiculo A -->
        <linearGradient id="vehiculoAGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1D4ED8;stop-opacity:1" />
        </linearGradient>

        <!-- Gradiente vehiculo B -->
        <linearGradient id="vehiculoBGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#EF4444;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#B91C1C;stop-opacity:1" />
        </linearGradient>

        <!-- Gradiente velocidad (verde a rojo) -->
        <linearGradient id="velocidadGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#22C55E;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#F59E0B;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#EF4444;stop-opacity:1" />
        </linearGradient>

        <!-- Sombra drop shadow -->
        <filter id="sombra" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>

        <!-- Glow para PDI -->
        <filter id="glowPDI">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <!-- Patron de asfalto -->
        <pattern id="asfaltoPattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect width="20" height="20" fill="#374151"/>
            <circle cx="3" cy="3" r="0.5" fill="#4B5563" opacity="0.5"/>
            <circle cx="13" cy="8" r="0.3" fill="#4B5563" opacity="0.5"/>
            <circle cx="7" cy="15" r="0.4" fill="#4B5563" opacity="0.5"/>
        </pattern>
    </defs>
    '''


def _render_vehiculo_isometrico(
    vehiculo: VehiculoRender,
    escala: float,
    cx0: float,
    cy0: float
) -> str:
    """Renderiza un vehiculo con perspectiva isometrica."""

    tipo = vehiculo.tipo.lower()
    if tipo not in VEHICLE_PATHS:
        tipo = "turismo"

    paths = VEHICLE_PATHS[tipo]

    # Convertir posicion a SVG
    px = cx0 + vehiculo.posicion[0] * escala
    py = cy0 - vehiculo.posicion[1] * escala  # Y invertido

    # Escala del vehiculo
    v_scale = escala / 18.0 * 0.9

    # Determinar gradiente y opacidad
    grad_id = "vehiculoAGrad" if vehiculo.id.upper() == "A" else "vehiculoBGrad"
    fill = f"url(#{grad_id})" if not vehiculo.es_posicion_final else "none"
    stroke = vehiculo.color
    opacity = vehiculo.opacidad
    stroke_width = 2 if vehiculo.es_posicion_final else 1.5
    dash = "4,2" if vehiculo.es_posicion_final else "none"

    # Transformacion
    transform = f"translate({px:.1f},{py:.1f}) rotate({-vehiculo.orientacion}) scale({v_scale})"

    svg_parts = [f'<g transform="{transform}" opacity="{opacity}" filter="url(#sombra)">']

    # Cuerpo del vehiculo
    svg_parts.append(
        f'<path d="{paths["body"]}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}" stroke-dasharray="{dash}"/>'
    )

    # Cabina (si existe)
    if paths.get("cabin"):
        cabin_fill = "#1F2937" if not vehiculo.es_posicion_final else "none"
        svg_parts.append(
            f'<path d="{paths["cabin"]}" fill="{cabin_fill}" stroke="{stroke}" '
            f'stroke-width="1" opacity="0.8"/>'
        )

    # Ruedas
    for wx, wy in paths.get("wheels", []):
        wheel_fill = "#111827" if not vehiculo.es_posicion_final else "none"
        svg_parts.append(
            f'<ellipse cx="{wx}" cy="{wy}" rx="4" ry="3" '
            f'fill="{wheel_fill}" stroke="#374151" stroke-width="0.5"/>'
        )

    svg_parts.append('</g>')

    # Etiqueta del vehiculo
    label_y_offset = -paths["height"] / 2 * v_scale - 12
    svg_parts.append(
        f'<text x="{px:.1f}" y="{py + label_y_offset:.1f}" '
        f'text-anchor="middle" fill="{stroke}" font-size="14" font-weight="bold" '
        f'font-family="Arial, sans-serif">{vehiculo.id}</text>'
    )

    return '\n'.join(svg_parts)


def _render_medicion(
    medicion: MedicionRender,
    escala: float,
    cx0: float,
    cy0: float
) -> str:
    """Renderiza una linea de medicion con cotas."""

    x1 = cx0 + medicion.inicio[0] * escala
    y1 = cy0 - medicion.inicio[1] * escala
    x2 = cx0 + medicion.fin[0] * escala
    y2 = cy0 - medicion.fin[1] * escala

    # Calcular punto medio y angulo
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

    # Perpendicular para las marcas de cota
    length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if length < 1:
        return ""

    ux = (x2 - x1) / length
    uy = (y2 - y1) / length
    px, py = -uy, ux  # Perpendicular

    cota_len = 8  # Longitud de las marcas de cota

    svg = f'''
    <g class="medicion">
        <!-- Linea principal -->
        <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"
              stroke="{COLORS['medicion']}" stroke-width="1.5" stroke-dasharray="4,2"/>

        <!-- Marcas de cota -->
        <line x1="{x1 + px*cota_len:.1f}" y1="{y1 + py*cota_len:.1f}"
              x2="{x1 - px*cota_len:.1f}" y2="{y1 - py*cota_len:.1f}"
              stroke="{COLORS['medicion']}" stroke-width="2"/>
        <line x1="{x2 + px*cota_len:.1f}" y1="{y2 + py*cota_len:.1f}"
              x2="{x2 - px*cota_len:.1f}" y2="{y2 - py*cota_len:.1f}"
              stroke="{COLORS['medicion']}" stroke-width="2"/>

        <!-- Texto de medicion -->
        <rect x="{mx - 25:.1f}" y="{my - 10:.1f}" width="50" height="16"
              fill="white" stroke="{COLORS['medicion']}" rx="3"/>
        <text x="{mx:.1f}" y="{my + 3:.1f}" text-anchor="middle"
              fill="{COLORS['medicion']}" font-size="11" font-weight="bold"
              font-family="Arial, sans-serif">
            {medicion.valor:.2f} {medicion.unidad}
        </text>
    </g>
    '''
    return svg


def _render_pdi_profesional(
    pdi: tuple,
    escala: float,
    cx0: float,
    cy0: float
) -> str:
    """Renderiza el Punto de Impacto con estilo profesional."""

    px = cx0 + pdi[0] * escala
    py = cy0 - pdi[1] * escala

    return f'''
    <g class="pdi" filter="url(#glowPDI)">
        <!-- Circulos concentricos -->
        <circle cx="{px:.1f}" cy="{py:.1f}" r="18" fill="none"
                stroke="{COLORS['pdi']}" stroke-width="2" opacity="0.3"/>
        <circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="none"
                stroke="{COLORS['pdi']}" stroke-width="2" opacity="0.5"/>
        <circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{COLORS['pdi']}" opacity="0.9"/>

        <!-- Cruz central -->
        <line x1="{px-5:.1f}" y1="{py:.1f}" x2="{px+5:.1f}" y2="{py:.1f}"
              stroke="white" stroke-width="2"/>
        <line x1="{px:.1f}" y1="{py-5:.1f}" x2="{px:.1f}" y2="{py+5:.1f}"
              stroke="white" stroke-width="2"/>

        <!-- Etiqueta -->
        <text x="{px:.1f}" y="{py + 30:.1f}" text-anchor="middle"
              fill="{COLORS['pdi']}" font-size="12" font-weight="bold"
              font-family="Arial, sans-serif">PDI</text>
    </g>
    '''


def _render_flecha_velocidad(
    origen: tuple,
    velocidad: float,
    angulo: float,
    color: str,
    escala: float,
    cx0: float,
    cy0: float,
    max_vel: float = 100.0
) -> str:
    """Renderiza una flecha de velocidad con gradiente."""

    x1 = cx0 + origen[0] * escala
    y1 = cy0 - origen[1] * escala

    # Longitud proporcional a velocidad
    arrow_len = min(velocidad / max_vel * 80, 100)
    angle_rad = math.radians(-angulo)  # SVG Y invertido

    x2 = x1 + arrow_len * math.cos(angle_rad)
    y2 = y1 + arrow_len * math.sin(angle_rad)

    # Punta de flecha elaborada
    ux = (x2 - x1) / arrow_len if arrow_len > 0 else 0
    uy = (y2 - y1) / arrow_len if arrow_len > 0 else 0

    # Puntos de la punta
    tip_len = 15
    tip_width = 8
    ax1 = x2 - tip_len * ux + tip_width * uy
    ay1 = y2 - tip_len * uy - tip_width * ux
    ax2 = x2 - tip_len * ux - tip_width * uy
    ay2 = y2 - tip_len * uy + tip_width * ux

    return f'''
    <g class="flecha-velocidad">
        <!-- Linea principal con degradado -->
        <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2 - tip_len*ux:.1f}" y2="{y2 - tip_len*uy:.1f}"
              stroke="{color}" stroke-width="3" stroke-linecap="round"/>

        <!-- Punta de flecha -->
        <polygon points="{x2:.1f},{y2:.1f} {ax1:.1f},{ay1:.1f} {ax2:.1f},{ay2:.1f}"
                 fill="{color}"/>

        <!-- Etiqueta de velocidad -->
        <text x="{x2 + 10*ux:.1f}" y="{y2 + 10*uy - 5:.1f}"
              fill="{color}" font-size="12" font-weight="bold"
              font-family="Arial, sans-serif">
            {velocidad:.0f} km/h
        </text>
    </g>
    '''


def _render_huella_profesional(
    inicio: tuple,
    fin: tuple,
    tipo: str,
    vehiculo_id: str,
    escala: float,
    cx0: float,
    cy0: float
) -> str:
    """Renderiza huellas de frenada/derrape con estilo profesional."""

    x1 = cx0 + inicio[0] * escala
    y1 = cy0 - inicio[1] * escala
    x2 = cx0 + fin[0] * escala
    y2 = cy0 - fin[1] * escala

    # Estilos por tipo de huella
    estilos = {
        "frenada": {"color": "#1F2937", "width": 6, "dash": "12,4", "opacity": 0.8},
        "derrape": {"color": "#7C3AED", "width": 8, "dash": "20,6", "opacity": 0.7},
        "arrastre": {"color": "#92400E", "width": 10, "dash": "4,2", "opacity": 0.6},
    }

    estilo = estilos.get(tipo, estilos["frenada"])

    # Doble linea para simular neumaticos
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx**2 + dy**2)
    if length < 1:
        return ""

    # Perpendicular normalizado
    px = -dy / length * 3
    py = dx / length * 3

    return f'''
    <g class="huella-{tipo}">
        <line x1="{x1 + px:.1f}" y1="{y1 + py:.1f}" x2="{x2 + px:.1f}" y2="{y2 + py:.1f}"
              stroke="{estilo['color']}" stroke-width="{estilo['width']}"
              stroke-dasharray="{estilo['dash']}" stroke-linecap="round"
              opacity="{estilo['opacity']}"/>
        <line x1="{x1 - px:.1f}" y1="{y1 - py:.1f}" x2="{x2 - px:.1f}" y2="{y2 - py:.1f}"
              stroke="{estilo['color']}" stroke-width="{estilo['width']}"
              stroke-dasharray="{estilo['dash']}" stroke-linecap="round"
              opacity="{estilo['opacity']}"/>
    </g>
    '''


# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE CROQUIS PROFESIONAL COMPLETO
# ═══════════════════════════════════════════════════════════════════════════════

def generar_croquis_profesional(
    vehiculos: List[Dict[str, Any]],
    pdi: Dict[str, float],
    trayectorias: List[Dict[str, Any]] = None,
    huellas: List[Dict[str, Any]] = None,
    mediciones: List[Dict[str, Any]] = None,
    titulo: str = "Croquis de Reconstruccion",
    subtitulo: str = "",
    width: int = 900,
    height: int = 700,
    mostrar_grid: bool = True,
    mostrar_escala: bool = True,
    mostrar_norte: bool = True,
) -> str:
    """
    Genera un croquis profesional estilo ITRASA/Virtual Crash.

    Args:
        vehiculos: Lista de vehiculos con posiciones inicial/final
        pdi: Punto de impacto {x, y}
        trayectorias: Trayectorias de los vehiculos
        huellas: Huellas en calzada
        mediciones: Mediciones a mostrar
        titulo: Titulo del croquis
        subtitulo: Subtitulo adicional
        width: Ancho del SVG
        height: Alto del SVG

    Returns:
        SVG string del croquis profesional
    """

    escala = 22.0  # px por metro (mayor resolucion)
    cx0 = width / 2
    cy0 = height / 2 - 50

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
        _create_gradient_defs(),
    ]

    # Fondo
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="{COLORS["fondo"]}" rx="12"/>')

    # Header profesional
    svg_parts.append(f'''
    <rect x="0" y="0" width="{width}" height="60" fill="{COLORS['panel']}" rx="12 12 0 0"/>
    <text x="20" y="28" fill="{COLORS['acento']}" font-size="18" font-weight="bold">
        VERIDICT AI
    </text>
    <text x="20" y="48" fill="{COLORS['texto_claro']}" font-size="14">
        {titulo}
    </text>
    <text x="{width - 20}" y="28" fill="{COLORS['texto_claro']}" font-size="11" text-anchor="end">
        {subtitulo if subtitulo else datetime.now().strftime("%d/%m/%Y %H:%M")}
    </text>
    ''')

    # Area de dibujo con fondo de asfalto
    draw_y = 70
    draw_h = height - 180
    svg_parts.append(f'''
    <rect x="20" y="{draw_y}" width="{width - 40}" height="{draw_h}"
          fill="url(#asfaltoPattern)" rx="8" stroke="#374151" stroke-width="1"/>
    ''')

    # Grid de referencia
    if mostrar_grid:
        for i in range(-15, 16):
            gx, _ = cx0 + i * 5 * escala, 0
            _, gy = 0, cy0 - i * 5 * escala
            if draw_y < gy < draw_y + draw_h:
                svg_parts.append(
                    f'<line x1="20" y1="{gy:.0f}" x2="{width-20}" y2="{gy:.0f}" '
                    f'stroke="#4B5563" stroke-width="0.5" opacity="0.3"/>'
                )
            if 20 < gx < width - 20:
                svg_parts.append(
                    f'<line x1="{gx:.0f}" y1="{draw_y}" x2="{gx:.0f}" y2="{draw_y + draw_h}" '
                    f'stroke="#4B5563" stroke-width="0.5" opacity="0.3"/>'
                )

    # Huellas en calzada
    if huellas:
        for huella in huellas:
            inicio = (huella.get("inicio", {}).get("x", 0), huella.get("inicio", {}).get("y", 0))
            fin = (huella.get("fin", {}).get("x", 0), huella.get("fin", {}).get("y", 0))
            if isinstance(huella.get("puntos"), list) and len(huella["puntos"]) >= 2:
                inicio = (huella["puntos"][0].get("x", 0), huella["puntos"][0].get("y", 0))
                fin = (huella["puntos"][-1].get("x", 0), huella["puntos"][-1].get("y", 0))
            svg_parts.append(_render_huella_profesional(
                inicio, fin,
                huella.get("tipo", "frenada"),
                huella.get("vehiculo", "A"),
                escala, cx0, cy0
            ))

    # Trayectorias
    if trayectorias:
        for tray in trayectorias:
            puntos = tray.get("puntos", [])
            if len(puntos) >= 2:
                vehiculo = tray.get("vehiculo", "A")
                color = COLORS["vehiculo_a"] if vehiculo.upper() == "A" else COLORS["vehiculo_b"]

                path_d = f"M {cx0 + puntos[0]['x'] * escala:.1f},{cy0 - puntos[0]['y'] * escala:.1f}"
                for p in puntos[1:]:
                    path_d += f" L {cx0 + p['x'] * escala:.1f},{cy0 - p['y'] * escala:.1f}"

                svg_parts.append(
                    f'<path d="{path_d}" fill="none" stroke="{color}" '
                    f'stroke-width="2" stroke-dasharray="8,4" opacity="0.7"/>'
                )

    # PDI
    if pdi:
        pdi_coords = (pdi.get("x", 0), pdi.get("y", 0))
        svg_parts.append(_render_pdi_profesional(pdi_coords, escala, cx0, cy0))

    # Vehiculos
    for veh in vehiculos:
        vehiculo = VehiculoRender(
            id=veh.get("id", "X"),
            tipo=veh.get("tipo", "turismo"),
            marca=veh.get("marca", ""),
            modelo=veh.get("modelo", ""),
            color=veh.get("color", COLORS["vehiculo_a"]),
            posicion=(veh.get("posicion", {}).get("x", 0), veh.get("posicion", {}).get("y", 0)),
            orientacion=veh.get("orientacion", 0),
            velocidad=veh.get("velocidad_pre", 0),
            es_posicion_final=veh.get("es_posicion_final", False),
            opacidad=0.5 if veh.get("es_posicion_final") else 1.0
        )
        svg_parts.append(_render_vehiculo_isometrico(vehiculo, escala, cx0, cy0))

        # Flecha de velocidad
        if veh.get("velocidad_pre") and not veh.get("es_posicion_final"):
            svg_parts.append(_render_flecha_velocidad(
                (veh["posicion"]["x"], veh["posicion"]["y"]),
                veh["velocidad_pre"],
                veh.get("orientacion", 0),
                veh.get("color", COLORS["vehiculo_a"]),
                escala, cx0, cy0
            ))

    # Mediciones
    if mediciones:
        for med in mediciones:
            m = MedicionRender(
                inicio=(med["inicio"]["x"], med["inicio"]["y"]),
                fin=(med["fin"]["x"], med["fin"]["y"]),
                valor=med["valor"],
                unidad=med.get("unidad", "m"),
                etiqueta=med.get("etiqueta", "")
            )
            svg_parts.append(_render_medicion(m, escala, cx0, cy0))

    # Norte
    if mostrar_norte:
        nx, ny = width - 60, draw_y + 40
        svg_parts.append(f'''
        <g transform="translate({nx},{ny})">
            <circle cx="0" cy="0" r="20" fill="white" stroke="#374151" stroke-width="1"/>
            <polygon points="0,-15 4,8 0,2 -4,8" fill="#DC2626"/>
            <polygon points="0,15 4,-8 0,-2 -4,-8" fill="#374151"/>
            <text x="0" y="-25" text-anchor="middle" font-size="12" font-weight="bold" fill="#374151">N</text>
        </g>
        ''')

    # Escala grafica
    if mostrar_escala:
        sx, sy = 60, draw_y + draw_h - 30
        escala_m = 10  # 10 metros
        escala_px = escala_m * escala
        svg_parts.append(f'''
        <g transform="translate({sx},{sy})">
            <rect x="0" y="0" width="{escala_px}" height="8" fill="white" stroke="#374151"/>
            <rect x="0" y="0" width="{escala_px/2}" height="8" fill="#374151"/>
            <text x="0" y="-5" font-size="10" fill="white">0</text>
            <text x="{escala_px/2}" y="-5" font-size="10" fill="white" text-anchor="middle">{escala_m//2}</text>
            <text x="{escala_px}" y="-5" font-size="10" fill="white" text-anchor="end">{escala_m} m</text>
        </g>
        ''')

    # Panel de leyenda inferior
    ly = height - 100
    svg_parts.append(f'<rect x="0" y="{ly}" width="{width}" height="100" fill="{COLORS["panel"]}" rx="0 0 12 12"/>')

    # Info de vehiculos en leyenda
    for i, veh in enumerate(vehiculos[:2]):
        col_x = 30 + i * (width // 2 - 40)
        color = veh.get("color", COLORS["vehiculo_a"] if i == 0 else COLORS["vehiculo_b"])

        svg_parts.append(f'''
        <rect x="{col_x}" y="{ly + 15}" width="16" height="16" fill="{color}" rx="3"/>
        <text x="{col_x + 24}" y="{ly + 28}" fill="white" font-size="13" font-weight="bold">
            Vehiculo {veh.get("id", chr(65+i))}: {veh.get("marca", "")} {veh.get("modelo", "")}
        </text>
        <text x="{col_x}" y="{ly + 48}" fill="#9CA3AF" font-size="11">
            V. pre-impacto: <tspan fill="white" font-weight="bold">{veh.get("velocidad_pre", 0):.0f} km/h</tspan>
        </text>
        <text x="{col_x}" y="{ly + 65}" fill="#9CA3AF" font-size="11">
            Delta-V: <tspan fill="{COLORS['acento']}" font-weight="bold">{veh.get("delta_v", 0):.0f} km/h</tspan>
        </text>
        <text x="{col_x}" y="{ly + 82}" fill="#9CA3AF" font-size="11">
            Masa: <tspan fill="white">{veh.get("masa", 0):.0f} kg</tspan>
        </text>
        ''')

    # Marca de agua
    svg_parts.append(f'''
    <text x="{width - 20}" y="{height - 15}" text-anchor="end"
          fill="#6B7280" font-size="9" opacity="0.7">
        Generado por Veridict AI - Reconstruccion Forense
    </text>
    ''')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA DE CALCULOS TIPO SamRAT
# ═══════════════════════════════════════════════════════════════════════════════

def generar_diagrama_calculo(
    titulo: str,
    formula: str,
    variables: Dict[str, Dict[str, Any]],
    resultado: Dict[str, Any],
    fases: List[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 500,
) -> str:
    """
    Genera un diagrama de calculo estilo SamRAT.

    Args:
        titulo: Titulo del calculo
        formula: Formula principal (LaTeX-like)
        variables: Dict de variables {nombre: {valor, unidad, descripcion}}
        resultado: {valor, unidad, descripcion}
        fases: Lista de fases del calculo (ej: reaccion, ejecucion, frenada)

    Returns:
        SVG string del diagrama
    """

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
        _create_gradient_defs(),
    ]

    # Fondo
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="{COLORS["fondo"]}" rx="12"/>')

    # Header
    svg_parts.append(f'''
    <rect x="0" y="0" width="{width}" height="50" fill="{COLORS['panel']}" rx="12 12 0 0"/>
    <text x="20" y="32" fill="{COLORS['acento']}" font-size="16" font-weight="bold">
        {titulo}
    </text>
    ''')

    # Formula principal
    svg_parts.append(f'''
    <rect x="20" y="60" width="{width - 40}" height="60" fill="white" rx="8"
          stroke="{COLORS['acento']}" stroke-width="2"/>
    <text x="{width//2}" y="98" text-anchor="middle" fill="{COLORS['texto']}"
          font-size="18" font-family="'Times New Roman', serif" font-style="italic">
        {formula}
    </text>
    ''')

    # Variables
    var_y = 140
    col_width = (width - 60) // min(len(variables), 4)
    for i, (nombre, data) in enumerate(variables.items()):
        vx = 30 + (i % 4) * col_width
        vy = var_y + (i // 4) * 70

        svg_parts.append(f'''
        <rect x="{vx}" y="{vy}" width="{col_width - 20}" height="60" fill="#F3F4F6" rx="6"/>
        <text x="{vx + 10}" y="{vy + 22}" fill="{COLORS['texto']}" font-size="12" font-weight="bold">
            {nombre}
        </text>
        <text x="{vx + 10}" y="{vy + 42}" fill="{COLORS['vehiculo_a']}" font-size="16" font-weight="bold">
            {data.get('valor', 0):.2f} {data.get('unidad', '')}
        </text>
        <text x="{vx + 10}" y="{vy + 55}" fill="#6B7280" font-size="9">
            {data.get('descripcion', '')[:30]}
        </text>
        ''')

    # Fases del calculo (si existen)
    if fases:
        fase_y = var_y + 80 + (len(variables) // 4) * 70
        fase_width = (width - 60) // len(fases)

        svg_parts.append(f'''
        <text x="30" y="{fase_y}" fill="{COLORS['texto']}" font-size="13" font-weight="bold">
            Fases del proceso:
        </text>
        ''')

        for i, fase in enumerate(fases):
            fx = 30 + i * fase_width
            fy = fase_y + 15

            # Color segun tipo de fase
            color = COLORS['vehiculo_b'] if 'frenada' in fase.get('nombre', '').lower() else \
                    COLORS['medicion'] if 'reaccion' in fase.get('nombre', '').lower() else \
                    COLORS['vehiculo_a']

            svg_parts.append(f'''
            <rect x="{fx}" y="{fy}" width="{fase_width - 15}" height="80" fill="{color}20"
                  rx="6" stroke="{color}" stroke-width="1"/>
            <text x="{fx + 10}" y="{fy + 20}" fill="{color}" font-size="11" font-weight="bold">
                {fase.get('nombre', f'Fase {i+1}')}
            </text>
            <text x="{fx + 10}" y="{fy + 40}" fill="{COLORS['texto']}" font-size="14" font-weight="bold">
                {fase.get('tiempo', 0):.2f} s
            </text>
            <text x="{fx + 10}" y="{fy + 58}" fill="{COLORS['texto']}" font-size="12">
                {fase.get('distancia', 0):.2f} m
            </text>
            <text x="{fx + 10}" y="{fy + 72}" fill="#6B7280" font-size="9">
                {fase.get('descripcion', '')[:25]}
            </text>
            ''')

            # Flecha de conexion
            if i < len(fases) - 1:
                arrow_x = fx + fase_width - 10
                svg_parts.append(f'''
                <polygon points="{arrow_x},{fy + 40} {arrow_x + 8},{fy + 45} {arrow_x},{fy + 50}"
                         fill="#9CA3AF"/>
                ''')

    # Resultado final
    res_y = height - 90
    svg_parts.append(f'''
    <rect x="20" y="{res_y}" width="{width - 40}" height="70" fill="{COLORS['acento']}20"
          rx="8" stroke="{COLORS['acento']}" stroke-width="2"/>
    <text x="40" y="{res_y + 28}" fill="{COLORS['texto']}" font-size="14" font-weight="bold">
        RESULTADO:
    </text>
    <text x="40" y="{res_y + 52}" fill="{COLORS['panel']}" font-size="24" font-weight="bold">
        {resultado.get('valor', 0):.2f} {resultado.get('unidad', '')}
    </text>
    <text x="{width - 40}" y="{res_y + 45}" text-anchor="end" fill="#6B7280" font-size="12">
        {resultado.get('descripcion', '')}
    </text>
    ''')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA BIOMECANICO WAD - ESTILO PROFESIONAL ITRASA
# ═══════════════════════════════════════════════════════════════════════════════

def _calcular_wad(velocidad_kmh: float) -> float:
    """Calcula el WAD usando la formula empirica estandar."""
    return 0.0024 * velocidad_kmh ** 2 + 0.127 * velocidad_kmh + 0.003


def _dibujar_perfil_vehiculo_lateral(x: float, y: float, escala: float = 1.0) -> str:
    """
    Genera un perfil lateral detallado de un turismo.
    El punto (x, y) corresponde a la parte delantera inferior del vehiculo.
    Escala 1.0 = vehiculo de ~4.5m de largo, altura capo ~0.8m
    """
    # Dimensiones base (en pixels, escala 1.0)
    # Longitud total ~350px, altura max ~90px

    return f'''
    <g transform="translate({x},{y}) scale({escala})">
        <!-- Sombra del vehiculo -->
        <ellipse cx="175" cy="8" rx="160" ry="8" fill="#00000020"/>

        <!-- Rueda trasera -->
        <circle cx="290" cy="0" r="28" fill="#1F2937"/>
        <circle cx="290" cy="0" r="20" fill="#374151"/>
        <circle cx="290" cy="0" r="8" fill="#6B7280"/>

        <!-- Rueda delantera -->
        <circle cx="70" cy="0" r="28" fill="#1F2937"/>
        <circle cx="70" cy="0" r="20" fill="#374151"/>
        <circle cx="70" cy="0" r="8" fill="#6B7280"/>

        <!-- Carroceria inferior - perfil lateral -->
        <path d="M 0,-28
                 L 15,-35
                 L 40,-35
                 Q 55,-35 60,-40
                 L 60,-55
                 Q 62,-75 80,-85
                 L 150,-90
                 Q 180,-90 200,-75
                 L 220,-55
                 Q 225,-45 240,-40
                 L 320,-40
                 Q 345,-40 350,-30
                 L 350,-28
                 Q 350,-15 330,0
                 L 320,0
                 Q 310,-28 290,-28
                 Q 270,-28 260,0
                 L 100,0
                 Q 90,-28 70,-28
                 Q 50,-28 40,0
                 L 20,0
                 Q 5,-10 0,-28
                 Z"
              fill="#3B82F6" stroke="#1D4ED8" stroke-width="1.5"/>

        <!-- Ventanas -->
        <path d="M 82,-82
                 L 145,-87
                 Q 170,-87 185,-75
                 L 205,-55
                 Q 208,-50 200,-48
                 L 90,-48
                 Q 82,-50 82,-60
                 Z"
              fill="#87CEEB" stroke="#1D4ED8" stroke-width="1" opacity="0.8"/>

        <!-- Linea de la puerta -->
        <line x1="145" y1="-87" x2="145" y2="-40" stroke="#1D4ED8" stroke-width="1"/>

        <!-- Manilla puerta -->
        <rect x="155" y="-55" width="15" height="4" rx="2" fill="#1D4ED8"/>

        <!-- Faro delantero -->
        <ellipse cx="15" cy="-40" rx="12" ry="8" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1"/>

        <!-- Faro trasero -->
        <rect x="340" y="-38" width="8" height="12" rx="2" fill="#EF4444" stroke="#B91C1C" stroke-width="1"/>

        <!-- Espejo retrovisor -->
        <ellipse cx="70" cy="-75" rx="8" ry="5" fill="#1F2937"/>
    </g>
    '''


def generar_diagrama_wad(
    velocidad_impacto: float = None,
    altura_capot: float = 0.80,
    altura_peaton: float = 1.70,
    tipo_vehiculo: str = "turismo",
    mostrar_ciclista: bool = True,
    width: int = 900,
    height: int = 550,
) -> str:
    """
    Genera un diagrama biomecanico WAD profesional estilo ITRASA.
    Muestra perfil lateral del vehiculo con lineas de ALTURA WAD horizontales
    (WAD 1000 = 1m de altura, WAD 1500 = 1.5m de altura) y marcadores de
    impacto para diferentes velocidades posicionados sobre el vehiculo.

    Args:
        velocidad_impacto: Velocidad especifica a destacar (opcional)
        altura_capot: Altura del borde delantero del capo (m)
        altura_peaton: Altura del peaton (m)
        tipo_vehiculo: Tipo de vehiculo (turismo, suv, furgoneta)
        mostrar_ciclista: Si True, muestra tambien marcadores de ciclista

    Returns:
        SVG string del diagrama WAD profesional
    """

    # Velocidades estandar para los marcadores
    velocidades = [20, 30, 40, 50]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
    ]

    # Definiciones
    svg_parts.append('''
    <defs>
        <linearGradient id="fondoWAD" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#F8FAFC;stop-opacity:1" />
        </linearGradient>
        <pattern id="gridWAD" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#E5E7EB" stroke-width="0.5"/>
        </pattern>
    </defs>
    ''')

    # Fondo
    svg_parts.append(f'''
    <rect width="{width}" height="{height}" fill="url(#fondoWAD)"/>
    <rect width="{width}" height="{height}" fill="url(#gridWAD)" opacity="0.3"/>
    ''')

    # Header
    svg_parts.append(f'''
    <rect x="0" y="0" width="{width}" height="55" fill="#1E3A5F"/>
    <text x="25" y="35" fill="#FFFFFF" font-size="18" font-weight="bold">
        Diagrama WAD - Zonas de Impacto Cabeza segun Velocidad
    </text>
    ''')

    # Configuracion del area de dibujo
    # Escala: 150 pixels = 1 metro de altura
    escala_altura = 150

    # Posiciones
    suelo_y = 420  # Linea del suelo
    veh_x = 100    # Inicio del vehiculo

    # Linea del suelo
    svg_parts.append(f'''
    <line x1="50" y1="{suelo_y}" x2="620" y2="{suelo_y}"
          stroke="#374151" stroke-width="3"/>
    <text x="40" y="{suelo_y + 5}" text-anchor="end" fill="#6B7280" font-size="10">0 m</text>
    ''')

    # Dibujar vehiculo con perfil lateral detallado
    svg_parts.append(f'''
    <g transform="translate({veh_x},{suelo_y})">
        <!-- Sombra -->
        <ellipse cx="200" cy="5" rx="180" ry="6" fill="#00000015"/>

        <!-- Rueda trasera -->
        <circle cx="340" cy="-25" r="25" fill="#1F2937"/>
        <circle cx="340" cy="-25" r="18" fill="#4B5563"/>
        <circle cx="340" cy="-25" r="6" fill="#9CA3AF"/>

        <!-- Rueda delantera -->
        <circle cx="80" cy="-25" r="25" fill="#1F2937"/>
        <circle cx="80" cy="-25" r="18" fill="#4B5563"/>
        <circle cx="80" cy="-25" r="6" fill="#9CA3AF"/>

        <!-- Carroceria - Perfil lateral turismo -->
        <path d="M 10,-50
                 L 30,-55
                 L 50,-60
                 C 60,-65 70,-80 90,-100
                 L 120,-110
                 C 150,-115 200,-115 250,-110
                 L 310,-95
                 C 340,-85 370,-70 385,-55
                 L 400,-50
                 L 400,-25
                 C 400,-10 380,0 365,0
                 L 315,0
                 C 300,-25 280,-25 260,-25
                 C 240,-25 220,0 200,0
                 L 125,0
                 C 110,-25 90,-25 80,-25
                 C 70,-25 50,0 35,0
                 L 10,0
                 C 0,-10 0,-30 10,-50
                 Z"
              fill="#3B82F6" stroke="#1D4ED8" stroke-width="2"/>

        <!-- Ventanas -->
        <path d="M 95,-97
                 L 120,-105
                 C 145,-108 190,-108 230,-103
                 L 280,-90
                 C 290,-85 295,-75 285,-70
                 L 110,-70
                 C 100,-72 95,-80 95,-97
                 Z"
              fill="#87CEEB" stroke="#1D4ED8" stroke-width="1" opacity="0.85"/>

        <!-- Pilar B (division de ventanas) -->
        <line x1="190" y1="-105" x2="190" y2="-70" stroke="#1D4ED8" stroke-width="3"/>

        <!-- Manilla puerta -->
        <rect x="145" y="-80" width="18" height="4" rx="2" fill="#1D4ED8"/>

        <!-- Faro delantero -->
        <ellipse cx="25" cy="-55" rx="15" ry="10" fill="#FEF9C3" stroke="#F59E0B" stroke-width="1"/>

        <!-- Faro trasero -->
        <rect x="390" y="-52" width="8" height="15" rx="2" fill="#EF4444" stroke="#B91C1C"/>

        <!-- Espejo -->
        <ellipse cx="85" cy="-95" rx="10" ry="6" fill="#374151"/>

        <!-- Lineas de detalle -->
        <line x1="50" y1="-55" x2="350" y2="-55" stroke="#1D4ED8" stroke-width="0.5" opacity="0.5"/>
    </g>
    ''')

    # Lineas horizontales de ALTURA WAD (no distancia)
    # WAD 1000 = 1m de altura, WAD 1500 = 1.5m de altura
    lineas_altura = [
        {"altura_m": 1.0, "label": "WAD 1000", "color": "#10B981", "desc": "1.0 m"},
        {"altura_m": 1.5, "label": "WAD 1500", "color": "#F59E0B", "desc": "1.5 m"},
    ]

    for linea in lineas_altura:
        y_linea = suelo_y - (linea["altura_m"] * escala_altura)
        svg_parts.append(f'''
        <line x1="50" y1="{y_linea}" x2="620" y2="{y_linea}"
              stroke="{linea['color']}" stroke-width="2" stroke-dasharray="10,5"/>
        <rect x="555" y="{y_linea - 12}" width="65" height="20" fill="{linea['color']}" rx="3"/>
        <text x="587" y="{y_linea + 3}" text-anchor="middle" fill="white" font-size="10" font-weight="bold">
            {linea['label']}
        </text>
        <text x="40" y="{y_linea + 5}" text-anchor="end" fill="#6B7280" font-size="10">
            {linea['desc']}
        </text>
        ''')

    # Posiciones de impacto en el vehiculo segun velocidad
    # Mapeamos velocidades a posiciones X sobre el vehiculo y alturas Y
    # A mayor velocidad, el impacto es mas hacia adelante y mas alto
    posiciones_impacto = {
        20: {"x": veh_x + 340, "zona": "Capo trasero", "altura_rel": 0.75},
        30: {"x": veh_x + 280, "zona": "Capo central", "altura_rel": 0.85},
        40: {"x": veh_x + 200, "zona": "Parabrisas", "altura_rel": 1.05},
        50: {"x": veh_x + 150, "zona": "Techo/Pilar A", "altura_rel": 1.20},
    }

    colores_velocidad = {
        20: "#22C55E",  # Verde
        30: "#84CC16",  # Lima
        40: "#F59E0B",  # Naranja
        50: "#EF4444",  # Rojo
    }

    # Marcadores de peaton (triangulos)
    svg_parts.append('<g id="marcadores-peaton">')
    for vel in velocidades:
        pos = posiciones_impacto[vel]
        marker_x = pos["x"]
        marker_y = suelo_y - (pos["altura_rel"] * escala_altura)
        color = colores_velocidad[vel]

        svg_parts.append(f'''
        <g class="marcador-peaton-{vel}">
            <polygon points="{marker_x},{marker_y-15} {marker_x-10},{marker_y+3} {marker_x+10},{marker_y+3}"
                     fill="{color}" stroke="#111827" stroke-width="1.5"/>
            <text x="{marker_x}" y="{marker_y - 22}" text-anchor="middle"
                  fill="{color}" font-size="11" font-weight="bold">
                {vel}
            </text>
        </g>
        ''')
    svg_parts.append('</g>')

    # Marcadores de ciclista (cruces) - posicionados ligeramente diferentes
    if mostrar_ciclista:
        svg_parts.append('<g id="marcadores-ciclista">')
        for vel in velocidades:
            pos = posiciones_impacto[vel]
            # Ciclista impacta mas adelante y mas alto
            marker_x = pos["x"] - 30
            marker_y = suelo_y - (pos["altura_rel"] * escala_altura) - 20

            svg_parts.append(f'''
            <g class="marcador-ciclista-{vel}">
                <line x1="{marker_x-7}" y1="{marker_y}" x2="{marker_x+7}" y2="{marker_y}"
                      stroke="#7C3AED" stroke-width="3"/>
                <line x1="{marker_x}" y1="{marker_y-7}" x2="{marker_x}" y2="{marker_y+7}"
                      stroke="#7C3AED" stroke-width="3"/>
            </g>
            ''')
        svg_parts.append('</g>')

    # Panel de leyenda
    legend_x = 650
    legend_y = 70

    svg_parts.append(f'''
    <rect x="{legend_x}" y="{legend_y}" width="235" height="320"
          fill="white" stroke="#E5E7EB" stroke-width="1" rx="8"/>

    <text x="{legend_x + 15}" y="{legend_y + 25}" fill="#111827" font-size="14" font-weight="bold">
        Leyenda - Impacto Cabeza
    </text>

    <line x1="{legend_x + 10}" y1="{legend_y + 35}" x2="{legend_x + 225}" y2="{legend_y + 35}"
          stroke="#E5E7EB"/>

    <!-- Simbolos -->
    <polygon points="{legend_x + 25},{legend_y + 50} {legend_x + 15},{legend_y + 68} {legend_x + 35},{legend_y + 68}"
             fill="#F97316" stroke="#111827" stroke-width="1"/>
    <text x="{legend_x + 50}" y="{legend_y + 63}" fill="#374151" font-size="12">Peaton adulto</text>

    <line x1="{legend_x + 18}" y1="{legend_y + 90}" x2="{legend_x + 32}" y2="{legend_y + 90}" stroke="#7C3AED" stroke-width="3"/>
    <line x1="{legend_x + 25}" y1="{legend_y + 83}" x2="{legend_x + 25}" y2="{legend_y + 97}" stroke="#7C3AED" stroke-width="3"/>
    <text x="{legend_x + 50}" y="{legend_y + 95}" fill="#374151" font-size="12">Ciclista</text>

    <line x1="{legend_x + 10}" y1="{legend_y + 110}" x2="{legend_x + 225}" y2="{legend_y + 110}"
          stroke="#E5E7EB"/>

    <text x="{legend_x + 15}" y="{legend_y + 130}" fill="#111827" font-size="12" font-weight="bold">
        Velocidad → Zona impacto:
    </text>
    ''')

    # Leyenda de velocidades
    for i, vel in enumerate(velocidades):
        y_off = legend_y + 150 + i * 32
        pos = posiciones_impacto[vel]
        svg_parts.append(f'''
        <rect x="{legend_x + 15}" y="{y_off}" width="16" height="16" rx="3" fill="{colores_velocidad[vel]}"/>
        <text x="{legend_x + 40}" y="{y_off + 13}" fill="#374151" font-size="11" font-weight="bold">
            {vel} km/h
        </text>
        <text x="{legend_x + 100}" y="{y_off + 13}" fill="#6B7280" font-size="10">
            {pos['zona']}
        </text>
        ''')

    svg_parts.append(f'''
    <line x1="{legend_x + 10}" y1="{legend_y + 285}" x2="{legend_x + 225}" y2="{legend_y + 285}"
          stroke="#E5E7EB"/>
    <text x="{legend_x + 15}" y="{legend_y + 305}" fill="#6B7280" font-size="9" font-style="italic">
        Basado en estudios ITRASA/Euro NCAP
    </text>
    ''')

    # Panel inferior explicativo
    svg_parts.append(f'''
    <rect x="25" y="{height - 95}" width="600" height="80" fill="#F8FAFC"
          stroke="#E5E7EB" stroke-width="1" rx="8"/>

    <text x="40" y="{height - 70}" fill="#111827" font-size="12" font-weight="bold">
        Interpretacion de las Zonas de Impacto
    </text>

    <text x="40" y="{height - 50}" fill="#374151" font-size="10">
        • 15-25 km/h: Impacto en capo trasero/central - Lesiones moderadas
    </text>
    <text x="40" y="{height - 35}" fill="#374151" font-size="10">
        • 30-40 km/h: Impacto en parabrisas - Lesiones graves (TCE probable)
    </text>
    <text x="320" y="{height - 50}" fill="#374151" font-size="10">
        • 45-55 km/h: Impacto en techo/Pilar A - Lesiones muy graves/fatales
    </text>
    <text x="320" y="{height - 35}" fill="#374151" font-size="10">
        • &gt;55 km/h: Proyeccion completa sobre vehiculo
    </text>
    ''')

    # Velocidad destacada si se especifica
    if velocidad_impacto is not None and velocidad_impacto in posiciones_impacto:
        pos = posiciones_impacto.get(int(velocidad_impacto), posiciones_impacto[50])
        marker_x = pos["x"]
        marker_y = suelo_y - (pos["altura_rel"] * escala_altura)

        svg_parts.append(f'''
        <g class="velocidad-destacada">
            <circle cx="{marker_x}" cy="{marker_y}" r="30" fill="none"
                    stroke="#DC2626" stroke-width="3">
                <animate attributeName="r" values="25;35;25" dur="1.5s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <rect x="{marker_x - 35}" y="{marker_y - 55}" width="70" height="22"
                  fill="#DC2626" rx="4"/>
            <text x="{marker_x}" y="{marker_y - 39}" text-anchor="middle"
                  fill="white" font-size="11" font-weight="bold">
                {velocidad_impacto:.0f} km/h
            </text>
        </g>
        ''')
    elif velocidad_impacto is not None:
        # Interpolar posicion para velocidades no estandar
        if velocidad_impacto < 20:
            ref_vel = 20
        elif velocidad_impacto > 50:
            ref_vel = 50
        else:
            ref_vel = min(velocidades, key=lambda x: abs(x - velocidad_impacto))

        pos = posiciones_impacto[ref_vel]
        marker_x = pos["x"]
        marker_y = suelo_y - (pos["altura_rel"] * escala_altura)

        svg_parts.append(f'''
        <g class="velocidad-destacada">
            <circle cx="{marker_x}" cy="{marker_y}" r="30" fill="none"
                    stroke="#DC2626" stroke-width="3">
                <animate attributeName="r" values="25;35;25" dur="1.5s" repeatCount="indefinite"/>
            </circle>
            <rect x="{marker_x - 35}" y="{marker_y - 55}" width="70" height="22"
                  fill="#DC2626" rx="4"/>
            <text x="{marker_x}" y="{marker_y - 39}" text-anchor="middle"
                  fill="white" font-size="11" font-weight="bold">
                {velocidad_impacto:.0f} km/h
            </text>
        </g>
        ''')

    # Creditos
    svg_parts.append(f'''
    <text x="{width - 15}" y="{height - 8}" text-anchor="end" fill="#9CA3AF" font-size="9">
        Veridict AI - Reconstruccion Forense
    </text>
    ''')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# GRAFICO DE ENERGIA COMPARATIVO
# ═══════════════════════════════════════════════════════════════════════════════

def generar_grafico_energia(
    velocidades: List[float],
    masa: float = 1500,
    titulo: str = "Comparativa de Energia Cinetica",
    width: int = 700,
    height: int = 400,
) -> str:
    """
    Genera un grafico de barras comparando energia cinetica a diferentes velocidades.
    Similar a los graficos del documento ITRASA.

    Args:
        velocidades: Lista de velocidades a comparar (km/h)
        masa: Masa del vehiculo (kg)
        titulo: Titulo del grafico

    Returns:
        SVG string del grafico
    """

    # Calcular energias
    energias = []
    for v in velocidades:
        v_ms = v / 3.6
        ec = 0.5 * masa * v_ms ** 2
        energias.append({"velocidad": v, "energia_j": ec, "energia_kj": ec / 1000})

    max_energia = max(e["energia_j"] for e in energias)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
        _create_gradient_defs(),
    ]

    # Fondo
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="{COLORS["fondo"]}" rx="12"/>')

    # Header
    svg_parts.append(f'''
    <rect x="0" y="0" width="{width}" height="50" fill="{COLORS['panel']}" rx="12 12 0 0"/>
    <text x="20" y="32" fill="{COLORS['acento']}" font-size="16" font-weight="bold">
        {titulo}
    </text>
    <text x="{width - 20}" y="32" fill="#9CA3AF" font-size="11" text-anchor="end">
        Masa: {masa} kg | Ec = 1/2 * m * v²
    </text>
    ''')

    # Area del grafico
    chart_x, chart_y = 80, 80
    chart_w, chart_h = width - 120, height - 150

    # Eje Y
    svg_parts.append(f'''
    <line x1="{chart_x}" y1="{chart_y}" x2="{chart_x}" y2="{chart_y + chart_h}"
          stroke="#374151" stroke-width="2"/>
    <text x="{chart_x - 10}" y="{chart_y + chart_h // 2}" text-anchor="middle"
          fill="#6B7280" font-size="11" transform="rotate(-90,{chart_x - 40},{chart_y + chart_h // 2})">
        Energia (kJ)
    </text>
    ''')

    # Eje X
    svg_parts.append(f'''
    <line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}"
          stroke="#374151" stroke-width="2"/>
    <text x="{chart_x + chart_w // 2}" y="{chart_y + chart_h + 40}" text-anchor="middle"
          fill="#6B7280" font-size="11">
        Velocidad (km/h)
    </text>
    ''')

    # Barras
    bar_width = chart_w / (len(energias) * 1.5)
    bar_spacing = chart_w / len(energias)

    for i, e in enumerate(energias):
        bar_x = chart_x + i * bar_spacing + bar_spacing * 0.25
        bar_height = (e["energia_j"] / max_energia) * (chart_h - 20)
        bar_y = chart_y + chart_h - bar_height

        # Color segun nivel de energia
        if e["velocidad"] <= 30:
            color = COLORS["energia_baja"]
        elif e["velocidad"] <= 60:
            color = COLORS["energia_media"]
        else:
            color = COLORS["energia_alta"]

        svg_parts.append(f'''
        <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}"
              fill="{color}" rx="4" opacity="0.9"/>

        <!-- Valor encima de la barra -->
        <text x="{bar_x + bar_width/2}" y="{bar_y - 8}" text-anchor="middle"
              fill="{COLORS['texto']}" font-size="11" font-weight="bold">
            {e["energia_kj"]:.1f} kJ
        </text>

        <!-- Velocidad debajo -->
        <text x="{bar_x + bar_width/2}" y="{chart_y + chart_h + 18}" text-anchor="middle"
              fill="{COLORS['texto']}" font-size="12" font-weight="bold">
            {e["velocidad"]:.0f}
        </text>
        ''')

    # Leyenda de colores
    leyenda_y = height - 35
    svg_parts.append(f'''
    <rect x="20" y="{leyenda_y - 8}" width="{width - 40}" height="25" fill="#F3F4F6" rx="4"/>

    <rect x="40" y="{leyenda_y}" width="12" height="12" fill="{COLORS['energia_baja']}" rx="2"/>
    <text x="58" y="{leyenda_y + 10}" fill="#6B7280" font-size="10">Baja (&lt;30 km/h)</text>

    <rect x="180" y="{leyenda_y}" width="12" height="12" fill="{COLORS['energia_media']}" rx="2"/>
    <text x="198" y="{leyenda_y + 10}" fill="#6B7280" font-size="10">Media (30-60 km/h)</text>

    <rect x="340" y="{leyenda_y}" width="12" height="12" fill="{COLORS['energia_alta']}" rx="2"/>
    <text x="358" y="{leyenda_y + 10}" fill="#6B7280" font-size="10">Alta (&gt;60 km/h)</text>
    ''')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# SECUENCIA TEMPORAL DE SIMULACION
# ═══════════════════════════════════════════════════════════════════════════════

def generar_secuencia_temporal(
    frames: List[Dict[str, Any]],
    titulo: str = "Secuencia Temporal del Accidente",
    width: int = 1000,
    height: int = 300,
) -> str:
    """
    Genera una secuencia temporal mostrando multiples frames del accidente.

    Args:
        frames: Lista de frames con {tiempo_ms, descripcion, vehiculos}
        titulo: Titulo de la secuencia

    Returns:
        SVG string de la secuencia
    """

    n_frames = min(len(frames), 5)
    frame_width = (width - 60) // n_frames

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Arial, sans-serif">',
        _create_gradient_defs(),
    ]

    # Fondo
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="{COLORS["fondo"]}" rx="12"/>')

    # Header
    svg_parts.append(f'''
    <rect x="0" y="0" width="{width}" height="40" fill="{COLORS['panel']}" rx="12 12 0 0"/>
    <text x="20" y="26" fill="{COLORS['acento']}" font-size="14" font-weight="bold">
        {titulo}
    </text>
    ''')

    # Linea temporal
    timeline_y = height - 40
    svg_parts.append(f'''
    <line x1="40" y1="{timeline_y}" x2="{width - 40}" y2="{timeline_y}"
          stroke="#374151" stroke-width="3"/>
    ''')

    # Frames
    for i, frame in enumerate(frames[:n_frames]):
        fx = 40 + i * frame_width
        fy = 60
        fw = frame_width - 20
        fh = height - 120

        # Recuadro del frame
        svg_parts.append(f'''
        <rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="#374151" rx="6"/>
        <text x="{fx + fw//2}" y="{fy + 20}" text-anchor="middle" fill="white" font-size="11" font-weight="bold">
            t = {frame.get('tiempo_ms', i*100)} ms
        </text>
        ''')

        # Mini representacion de vehiculos
        mini_cx = fx + fw // 2
        mini_cy = fy + fh // 2

        for j, veh in enumerate(frame.get('vehiculos', [])[:2]):
            vx = mini_cx + (j - 0.5) * 30
            vy = mini_cy
            color = COLORS['vehiculo_a'] if j == 0 else COLORS['vehiculo_b']

            svg_parts.append(f'''
            <rect x="{vx - 12}" y="{vy - 8}" width="24" height="16"
                  fill="{color}" rx="3" transform="rotate({veh.get('orientacion', 0)},{vx},{vy})"/>
            ''')

        # Punto en la linea temporal
        point_x = fx + fw // 2
        svg_parts.append(f'''
        <circle cx="{point_x}" cy="{timeline_y}" r="8" fill="{COLORS['acento']}"/>
        <text x="{point_x}" y="{timeline_y + 20}" text-anchor="middle" fill="#6B7280" font-size="9">
            {frame.get('descripcion', '')[:15]}
        </text>
        ''')

        # Flecha conectora
        if i < n_frames - 1:
            svg_parts.append(f'''
            <line x1="{fx + fw + 5}" y1="{fy + fh//2}" x2="{fx + fw + 15}" y2="{fy + fh//2}"
                  stroke="#9CA3AF" stroke-width="2" marker-end="url(#arrow)"/>
            ''')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)

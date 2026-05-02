"""
Generador de croquis SVG para reconstrucción de accidentes.

Produce un croquis 2D con:
  - Posición inicial estimada de cada vehículo
  - Trayectoria de aproximación (línea de movimiento)
  - Punto de impacto (PDI) marcado claramente
  - Huellas en calzada (frenada, derrape, arrastre) con color y trazo diferenciado
  - Daños secundarios (valla, vehículo aparcado, árbol, etc.)
  - Vectores de velocidad post-impacto
  - Posición final de cada vehículo
  - Leyenda completa
"""

import math
import base64
from typing import Optional, TYPE_CHECKING
from physics.reconstruction import ReconstructionResult

if TYPE_CHECKING:
    from models import EscenaAccidente, HuellaCalzada, DañoSecundario


# Colores por vehículo
COLOR_A = "#2563EB"        # azul
COLOR_B = "#DC2626"        # rojo
COLOR_PDI = "#16A34A"      # verde
COLOR_GRID = "#E5E7EB"
COLOR_TEXT = "#111827"
COLOR_WARN = "#D97706"
COLOR_FRENADA = "#1F2937"  # negro — huella de frenada
COLOR_DERRAPE = "#7C3AED"  # violeta — yaw mark
COLOR_ARRASTRE = "#92400E" # marrón — arrastre post-impacto
COLOR_DAÑO_SEC = "#F97316" # naranja — daño secundario


def _metro_a_px(m: float, escala: float) -> float:
    return m * escala


def _arrow(x1: float, y1: float, x2: float, y2: float, color: str, label: str = "", stroke_width: float = 2.5) -> str:
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx**2 + dy**2)
    if length < 1:
        return ""
    # Punta de flecha
    ux, uy = dx / length, dy / length
    ax1 = x2 - 12 * ux + 5 * uy
    ay1 = y2 - 12 * uy - 5 * ux
    ax2 = x2 - 12 * ux - 5 * uy
    ay2 = y2 - 12 * uy + 5 * ux
    svg = (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="none"/>'
        f'<polygon points="{x2:.1f},{y2:.1f} {ax1:.1f},{ay1:.1f} {ax2:.1f},{ay2:.1f}" fill="{color}"/>'
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        svg += f'<text x="{mx+6:.1f}" y="{my-6:.1f}" fill="{color}" font-size="11" font-weight="bold">{label}</text>'
    return svg


def _dashed_line(x1, y1, x2, y2, color, width=1.5) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}" stroke-dasharray="6,4" opacity="0.7"/>'
    )


def _car_icon(cx: float, cy: float, angle_deg: float, color: str, label: str, filled: bool = True) -> str:
    w, h = 18, 10
    angle_rad = math.radians(-angle_deg)  # SVG Y invertido
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    def rot(x, y):
        return cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a

    corners = [rot(-w/2, -h/2), rot(w/2, -h/2), rot(w/2, h/2), rot(-w/2, h/2)]
    pts = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in corners)
    fill = color if filled else "white"
    svg = f'<polygon points="{pts}" fill="{fill}" stroke="{color}" stroke-width="2" opacity="0.85"/>'
    svg += f'<text x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle" fill="white" font-size="10" font-weight="bold">{label}</text>'
    return svg


def _huella_svg(
    inicio: tuple[float, float],
    fin: tuple[float, float],
    tipo: str,
    curvatura: str,
    color: str,
    to_svg,
) -> str:
    """Dibuja una huella en la calzada con trazo diferenciado por tipo."""
    ix, iy = to_svg(*inicio)
    fx, fy = to_svg(*fin)

    # Trazo base
    if tipo == "frenada":
        dash = "4,3"
        width = 3.5
    elif tipo == "derrape":
        dash = "8,4"
        width = 4.0
    elif tipo == "arrastre":
        dash = "2,2"
        width = 5.0
    else:
        dash = "6,3"
        width = 2.5

    # Si hay curvatura, añadir un arco aproximado con punto de control
    if curvatura != "recta":
        # Punto de control perpendicular al segmento (curva de Bézier cuadrática)
        mx, my = (ix + fx) / 2, (iy + fy) / 2
        dx, dy = fx - ix, fy - iy
        perp_x = -dy * 0.3
        perp_y = dx * 0.3
        if curvatura == "curva_derecha":
            perp_x, perp_y = -perp_x, -perp_y
        cx_ctrl = mx + perp_x
        cy_ctrl = my + perp_y
        path = f'<path d="M {ix:.1f},{iy:.1f} Q {cx_ctrl:.1f},{cy_ctrl:.1f} {fx:.1f},{fy:.1f}" '
        path += f'stroke="{color}" stroke-width="{width}" fill="none" stroke-dasharray="{dash}" opacity="0.85"/>'
        return path

    return (
        f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" '
        f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" opacity="0.85"/>'
    )


def _daño_secundario_svg(
    posicion: tuple[float, float],
    tipo: str,
    descripcion: str,
    to_svg,
) -> str:
    """Dibuja un daño secundario como símbolo en el croquis."""
    px, py = to_svg(*posicion)

    iconos = {
        "vehiculo_aparcado": "🚗",
        "valla": "⬛",
        "arbol": "🌳",
        "bordillo": "▬",
        "señal": "⚠",
        "muro": "▪",
        "otro": "✕",
    }
    simbolo = iconos.get(tipo, "✕")

    svg = (
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{COLOR_DAÑO_SEC}" opacity="0.9"/>'
        f'<text x="{px:.1f}" y="{py+4:.1f}" text-anchor="middle" font-size="9" fill="white" font-weight="bold">D</text>'
    )
    # Etiqueta truncada
    label = descripcion[:20] + ("…" if len(descripcion) > 20 else "")
    svg += f'<text x="{px+12:.1f}" y="{py-8:.1f}" font-size="9" fill="{COLOR_DAÑO_SEC}">{label}</text>'
    return svg


def generar_croquis_svg(
    resultado: ReconstructionResult,
    pos_final_a: tuple[float, float] = (5.0, 2.0),
    pos_final_b: tuple[float, float] = (-4.0, -1.5),
    angulo_pre_a: float = 0.0,
    angulo_pre_b: float = 180.0,
    tipo_colision: str = "colisión",
    modelo_a: str = "Vehículo A",
    modelo_b: str = "Vehículo B",
    escena: Optional["EscenaAccidente"] = None,
    width: int = 700,
    height: int = 520,
) -> str:
    """
    Genera el croquis del accidente como string SVG.

    Coordenadas en metros, con el PDI en el origen (0, 0).
    SVG: Y crece hacia abajo, por eso invertimos Y para que Norte = arriba.
    """
    escala = 18.0   # px por metro

    # Centro del canvas = PDI
    cx0 = width / 2
    cy0 = height / 2 - 30

    def to_svg(x_m: float, y_m: float):
        return cx0 + x_m * escala, cy0 - y_m * escala   # Y invertido

    # Puntos clave
    ix_a, iy_a = to_svg(*resultado.pos_inicial_a)
    fx_a, fy_a = to_svg(*pos_final_a)
    ix_b, iy_b = to_svg(*resultado.pos_inicial_b)
    fx_b, fy_b = to_svg(*pos_final_b)
    pdi_x, pdi_y = to_svg(0, 0)

    # Vectores post-impacto (longitud proporcional a velocidad, máx 80px)
    max_v = max(resultado.v_post_a_kmh, resultado.v_post_b_kmh, 1)
    arrow_scale = 70 / max_v

    va_post = resultado.v_post_a_kmh * arrow_scale
    vb_post = resultado.v_post_b_kmh * arrow_scale

    vec_ax = pdi_x + va_post * math.cos(math.radians(-resultado.angle_post_a_deg))
    vec_ay = pdi_y + va_post * math.sin(math.radians(-resultado.angle_post_a_deg))
    vec_bx = pdi_x + vb_post * math.cos(math.radians(-resultado.angle_post_b_deg))
    vec_by = pdi_y + vb_post * math.sin(math.radians(-resultado.angle_post_b_deg))

    # ── SVG ──────────────────────────────────────────────────────────────────
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="Arial, sans-serif">',

        # Fondo
        f'<rect width="{width}" height="{height}" fill="#F9FAFB" rx="8"/>',

        # Título
        f'<text x="{width//2}" y="28" text-anchor="middle" fill="{COLOR_TEXT}" '
        f'font-size="15" font-weight="bold">Croquis de Reconstrucción — {tipo_colision.upper()}</text>',

        # Grid de referencia (cada 5 m)
    ]

    # Grid
    for i in range(-10, 11):
        gx, _ = to_svg(i * 5, 0)
        _, gy = to_svg(0, i * 5)
        svg_parts.append(f'<line x1="{gx:.0f}" y1="40" x2="{gx:.0f}" y2="{height-120}" stroke="{COLOR_GRID}" stroke-width="1"/>')
        svg_parts.append(f'<line x1="20" y1="{gy:.0f}" x2="{width-20}" y2="{gy:.0f}" stroke="{COLOR_GRID}" stroke-width="1"/>')

    # Ejes
    svg_parts.append(f'<line x1="{cx0}" y1="40" x2="{cx0}" y2="{height-120}" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="2,4"/>')
    svg_parts.append(f'<line x1="20" y1="{cy0}" x2="{width-20}" y2="{cy0}" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="2,4"/>')
    svg_parts.append(f'<text x="{cx0+4}" y="54" fill="#9CA3AF" font-size="10">N</text>')

    # ── Huellas en calzada ────────────────────────────────────────────────────
    if escena:
        color_huella = {
            "frenada": COLOR_FRENADA,
            "derrape": COLOR_DERRAPE,
            "arrastre": COLOR_ARRASTRE,
            "aceleracion": COLOR_WARN,
        }
        for huella in escena.huellas:
            color_v = COLOR_A if huella.vehiculo_id == "A" else (COLOR_B if huella.vehiculo_id == "B" else COLOR_FRENADA)
            color_h = color_huella.get(huella.tipo, color_v)
            svg_parts.append(_huella_svg(
                inicio=huella.inicio,
                fin=huella.fin,
                tipo=huella.tipo,
                curvatura=huella.curvatura,
                color=color_h,
                to_svg=to_svg,
            ))

        # ── Daños secundarios ─────────────────────────────────────────────────
        for daño in escena.daños_secundarios:
            svg_parts.append(_daño_secundario_svg(
                posicion=daño.posicion,
                tipo=daño.tipo,
                descripcion=daño.descripcion,
                to_svg=to_svg,
            ))

    # ── Trayectorias de aproximación (líneas discontinuas) ────────────────────
    svg_parts.append(_dashed_line(ix_a, iy_a, pdi_x, pdi_y, COLOR_A, 2))
    svg_parts.append(_dashed_line(ix_b, iy_b, pdi_x, pdi_y, COLOR_B, 2))

    # ── Trayectorias post-impacto (líneas discontinuas hacia posición final) ──
    svg_parts.append(_dashed_line(pdi_x, pdi_y, fx_a, fy_a, COLOR_A, 1.5))
    svg_parts.append(_dashed_line(pdi_x, pdi_y, fx_b, fy_b, COLOR_B, 1.5))

    # ── Vectores de velocidad post-impacto ────────────────────────────────────
    svg_parts.append(_arrow(pdi_x, pdi_y, vec_ax, vec_ay, COLOR_A, f"{resultado.v_post_a_kmh:.0f} km/h"))
    svg_parts.append(_arrow(pdi_x, pdi_y, vec_bx, vec_by, COLOR_B, f"{resultado.v_post_b_kmh:.0f} km/h"))

    # ── Vehículos posición inicial ─────────────────────────────────────────────
    svg_parts.append(_car_icon(ix_a, iy_a, angulo_pre_a, COLOR_A, "A"))
    svg_parts.append(_car_icon(ix_b, iy_b, angulo_pre_b, COLOR_B, "B"))

    # ── Vehículos posición final ───────────────────────────────────────────────
    svg_parts.append(_car_icon(fx_a, fy_a, resultado.angle_post_a_deg, COLOR_A, "A", filled=False))
    svg_parts.append(_car_icon(fx_b, fy_b, resultado.angle_post_b_deg, COLOR_B, "B", filled=False))

    # ── PDI ───────────────────────────────────────────────────────────────────
    svg_parts.append(f'<circle cx="{pdi_x:.1f}" cy="{pdi_y:.1f}" r="10" fill="{COLOR_PDI}" opacity="0.9"/>')
    svg_parts.append(f'<text x="{pdi_x:.1f}" y="{pdi_y+4:.1f}" text-anchor="middle" fill="white" font-size="9" font-weight="bold">PDI</text>')

    # ── Leyenda ───────────────────────────────────────────────────────────────
    ly = height - 112
    svg_parts.append(f'<rect x="0" y="{ly}" width="{width}" height="112" fill="#F3F4F6" rx="0"/>')
    svg_parts.append(f'<line x1="0" y1="{ly}" x2="{width}" y2="{ly}" stroke="{COLOR_GRID}" stroke-width="1.5"/>')

    # Columna A
    svg_parts += [
        f'<rect x="20" y="{ly+8}" width="12" height="12" fill="{COLOR_A}" rx="2"/>',
        f'<text x="38" y="{ly+19}" fill="{COLOR_TEXT}" font-size="12" font-weight="bold">{modelo_a}</text>',
        f'<text x="20" y="{ly+35}" fill="{COLOR_TEXT}" font-size="11">Vel. impacto: <tspan font-weight="bold">{resultado.v_pre_a_kmh:.0f} km/h</tspan></text>',
        f'<text x="20" y="{ly+50}" fill="{COLOR_TEXT}" font-size="11">Vel. post-impacto: <tspan font-weight="bold">{resultado.v_post_a_kmh:.0f} km/h</tspan></text>',
        f'<text x="20" y="{ly+65}" fill="{COLOR_TEXT}" font-size="11">Delta-V: <tspan font-weight="bold">{resultado.delta_v_a_kmh:.0f} km/h</tspan></text>',
        f'<text x="20" y="{ly+80}" fill="{COLOR_TEXT}" font-size="11">Ángulo salida: <tspan font-weight="bold">{resultado.angle_post_a_deg:.0f}°</tspan></text>',
    ]

    # Columna B
    col2 = width // 2 - 20
    svg_parts += [
        f'<rect x="{col2}" y="{ly+8}" width="12" height="12" fill="{COLOR_B}" rx="2"/>',
        f'<text x="{col2+18}" y="{ly+19}" fill="{COLOR_TEXT}" font-size="12" font-weight="bold">{modelo_b}</text>',
        f'<text x="{col2}" y="{ly+35}" fill="{COLOR_TEXT}" font-size="11">Vel. impacto: <tspan font-weight="bold">{resultado.v_pre_b_kmh:.0f} km/h</tspan></text>',
        f'<text x="{col2}" y="{ly+50}" fill="{COLOR_TEXT}" font-size="11">Vel. post-impacto: <tspan font-weight="bold">{resultado.v_post_b_kmh:.0f} km/h</tspan></text>',
        f'<text x="{col2}" y="{ly+65}" fill="{COLOR_TEXT}" font-size="11">Delta-V: <tspan font-weight="bold">{resultado.delta_v_b_kmh:.0f} km/h</tspan></text>',
        f'<text x="{col2}" y="{ly+80}" fill="{COLOR_TEXT}" font-size="11">Ángulo salida: <tspan font-weight="bold">{resultado.angle_post_b_deg:.0f}°</tspan></text>',
    ]

    # Fila inferior: coef. restitución + error momento
    error_color = COLOR_WARN if resultado.error_momento_pct > 15 else COLOR_PDI
    svg_parts += [
        f'<text x="20" y="{ly+98}" fill="{COLOR_TEXT}" font-size="11">'
        f'Coef. restitución: <tspan font-weight="bold">e={resultado.coef_restitucion:.3f}</tspan>'
        f'  |  Error momento: <tspan fill="{error_color}" font-weight="bold">{resultado.error_momento_pct:.1f}%</tspan>'
        f'  |  Escala: 1 div = 5 m'
        f'</text>',
    ]

    # Leyenda de huellas
    leyenda_huellas = [
        (COLOR_FRENADA, "4,3", "Frenada"),
        (COLOR_DERRAPE, "8,4", "Derrape/yaw"),
        (COLOR_ARRASTRE, "2,2", "Arrastre post-imp."),
        (COLOR_DAÑO_SEC, None, "Daño secundario"),
    ]
    lx = width - 170
    for i, (col, dash, label) in enumerate(leyenda_huellas):
        ly_item = ly + 8 + i * 14
        if dash:
            svg_parts.append(
                f'<line x1="{lx}" y1="{ly_item+5}" x2="{lx+22}" y2="{ly_item+5}" '
                f'stroke="{col}" stroke-width="3" stroke-dasharray="{dash}"/>'
            )
        else:
            svg_parts.append(f'<circle cx="{lx+11}" cy="{ly_item+5}" r="5" fill="{col}"/>')
        svg_parts.append(f'<text x="{lx+27}" y="{ly_item+9}" fill="{COLOR_TEXT}" font-size="10">{label}</text>')

    # Advertencias
    if resultado.advertencias:
        warn_text = " · ".join(resultado.advertencias[:2])
        svg_parts.append(
            f'<text x="{width//2}" y="{ly+98}" text-anchor="middle" fill="{COLOR_WARN}" font-size="9" font-style="italic">{warn_text}</text>'
        )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generar_croquis_base64(
    resultado: ReconstructionResult,
    **kwargs,
) -> str:
    """Devuelve el SVG codificado en base64 (para incrustar en PDF o HTML)."""
    svg = generar_croquis_svg(resultado, **kwargs)
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

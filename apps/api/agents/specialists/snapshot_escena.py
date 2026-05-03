"""SnapshotEscenaAgent — captura un instante de la EscenaSimulacionData como SVG.

Sin LLM. Toma la `EscenaSimulacionData` ya producida por el SimulationAgent y
renderiza un SVG estático cenital en el instante `t_segundos` solicitado, con
los actores en su posición interpolada, su rotación, las trayectorias visibles
hasta `t`, los obstáculos, las huellas, el punto de impacto si ya ha ocurrido
y un rótulo descriptivo. Persiste el SVG en `uploads/_frames_simulacion/` y
devuelve URL pública + ImagenAnalizada en el `_log`.

Es lo que permite que el orquestador-perito "pegue fotos" de la reconstrucción
en momentos concretos para ilustrar la cronología en el PDF.
"""

from __future__ import annotations

import math
import time
import uuid
from pathlib import Path
from typing import Any

from config import get_settings
from models import EscenaSimulacionData, ImagenAnalizada, ToolCallLog


_FRAMES_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "_frames_simulacion"
_FRAMES_DIR.mkdir(parents=True, exist_ok=True)


# Paleta — sincronizada con EscenaSimulacionView.tsx
def _color_actor(tipo: str, color_user: str | None) -> str:
    if color_user:
        return color_user
    return {
        "turismo": "#3B82F6",
        "camion": "#8B5CF6", "autobus": "#8B5CF6",
        "motocicleta": "#F97316", "ciclomotor": "#F97316",
        "bicicleta": "#10B981",
        "peaton": "#EF4444",
        "mobiliario_urbano": "#6B7280",
    }.get(tipo, "#9CA3AF")


def _color_obstaculo(tipo: str) -> tuple[str, str, float]:
    table = {
        "edificio": ("#3f3f46", "#1f1f22", 0.55),
        "zona_terriza": ("#5c4a32", "#5c4a32", 0.65),
        "talud": ("#7a5a32", "#7a5a32", 0.6),
        "vegetacion": ("#365314", "#1A2A0E", 0.7),
        "muro": ("#737373", "#262626", 0.75),
        "barrera": ("#737373", "#262626", 0.75),
        "quitamiedos": ("#737373", "#262626", 0.75),
        "acera": ("#52525B", "#3F3F46", 0.7),
        "bordillo": ("#52525B", "#3F3F46", 0.7),
    }
    return table.get(tipo, ("#4B5563", "#1F2937", 0.7))


def _interp_actor(actor, t: float) -> dict[str, Any]:
    """Devuelve {x, y, rotation, v_kmh, frenando} interpolando la trayectoria."""
    traj = actor.trayectoria or []
    if not traj:
        return {"x": 0, "y": 0, "rotation": 0, "v_kmh": 0, "frenando": False}
    if t <= traj[0].t:
        p = traj[0]
        rot = p.rotation_deg if p.rotation_deg is not None else 0.0
        return {"x": p.x, "y": p.y, "rotation": rot, "v_kmh": p.v_kmh,
                "frenando": bool(p.frenando)}
    if t >= traj[-1].t:
        p = traj[-1]
        prev = traj[-2] if len(traj) >= 2 else p
        rot = p.rotation_deg if p.rotation_deg is not None else math.degrees(
            math.atan2(p.y - prev.y, p.x - prev.x)
        )
        return {"x": p.x, "y": p.y, "rotation": rot, "v_kmh": p.v_kmh,
                "frenando": bool(p.frenando)}
    prev, nxt = traj[0], traj[-1]
    for i in range(len(traj) - 1):
        if traj[i].t <= t <= traj[i + 1].t:
            prev, nxt = traj[i], traj[i + 1]
            break
    span = (nxt.t - prev.t) or 1e-6
    f = (t - prev.t) / span
    x = prev.x + (nxt.x - prev.x) * f
    y = prev.y + (nxt.y - prev.y) * f
    v = prev.v_kmh + (nxt.v_kmh - prev.v_kmh) * f
    if prev.rotation_deg is not None and nxt.rotation_deg is not None:
        rot = prev.rotation_deg + (nxt.rotation_deg - prev.rotation_deg) * f
    else:
        rot = math.degrees(math.atan2(nxt.y - prev.y, nxt.x - prev.x))
    frena = bool(prev.frenando) or bool(nxt.frenando)
    if actor.frena_desde_t is not None and t >= actor.frena_desde_t:
        frena = True
    return {"x": x, "y": y, "rotation": rot, "v_kmh": v, "frenando": frena}


def _scene_bounds(escena: EscenaSimulacionData) -> dict:
    """Mismo cálculo que el frontend — solo trayectorias e impacto, NO obstáculos."""
    minX, maxX, minY, maxY = float("inf"), float("-inf"), float("inf"), float("-inf")
    for a in escena.actores or []:
        for p in a.trayectoria or []:
            minX = min(minX, p.x); maxX = max(maxX, p.x)
            minY = min(minY, p.y); maxY = max(maxY, p.y)
    if escena.impacto:
        minX = min(minX, escena.impacto.x); maxX = max(maxX, escena.impacto.x)
        minY = min(minY, escena.impacto.y); maxY = max(maxY, escena.impacto.y)
    if not (math.isfinite(minX) and math.isfinite(maxX)):
        minX, maxX, minY, maxY = -20, 20, -15, 15
    if (maxX - minX) < 30:
        c = (minX + maxX) / 2; minX, maxX = c - 15, c + 15
    if (maxY - minY) < 22:
        c = (minY + maxY) / 2; minY, maxY = c - 11, c + 11
    padX = max(6, (maxX - minX) * 0.12)
    padY = max(6, (maxY - minY) * 0.12)
    return {"minX": minX - padX, "minY": minY - padY,
            "width": (maxX - minX) + 2 * padX,
            "height": (maxY - minY) + 2 * padY}


# ── Render helpers ────────────────────────────────────────────────────────

def _svg_road(escena: EscenaSimulacionData, b: dict) -> str:
    via = escena.via
    total = via.ancho_total_m or (via.carriles * via.ancho_carril_m)
    half = total / 2
    eje = getattr(via, "eje_via", None)
    parts: list[str] = []
    if isinstance(eje, list) and len(eje) >= 2:
        d = " ".join(f"{'M' if i == 0 else 'L'} {x} {y}" for i, (x, y) in enumerate(eje))
        parts.append(
            f'<path d="{d}" fill="none" stroke="#4B5563" stroke-width="{total + 3}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        parts.append(
            f'<path d="{d}" fill="none" stroke="#2a2f2a" stroke-width="{total}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        if via.carriles >= 2:
            parts.append(
                f'<path d="{d}" fill="none" stroke="#FFD700" stroke-width="0.18" '
                f'stroke-dasharray="2,1.5" stroke-linejoin="round"/>'
            )
        return "".join(parts)
    xs = b["minX"] - 5
    xe = b["minX"] + b["width"] + 5
    parts.append(
        f'<rect x="{xs}" y="{-half - 1.5}" width="{xe - xs}" height="{total + 3}" fill="#3A3E3A"/>'
    )
    parts.append(
        f'<rect x="{xs}" y="{-half}" width="{xe - xs}" height="{total}" fill="#2a2f2a"/>'
    )
    if via.carriles >= 2:
        parts.append(
            f'<line x1="{xs}" y1="0" x2="{xe}" y2="0" stroke="#FFD700" stroke-width="0.18"/>'
        )
    return "".join(parts)


def _svg_obstaculo(ob, b: dict) -> str:
    if not ob.poligono:
        return ""
    fill, stroke, op = _color_obstaculo(ob.tipo.value if hasattr(ob.tipo, "value") else str(ob.tipo))
    pts = " ".join(f"{x},{y}" for x, y in ob.poligono)
    out = (
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="0.12" opacity="{op}"/>'
    )
    desc = (ob.descripcion or "")[:38]
    if desc:
        lx, ly = ob.poligono[0]
        within = (b["minX"] <= lx <= b["minX"] + b["width"] and
                  b["minY"] <= ly <= b["minY"] + b["height"])
        if within:
            FONT = 0.8
            w = max(2.5, len(desc) * FONT * 0.55)
            out += (
                f'<g transform="translate({lx},{ly - 1.1})">'
                f'<rect x="{-w/2}" y="{-FONT*0.95}" width="{w}" height="{FONT*1.4}" '
                f'rx="0.18" fill="#0d110d" opacity="0.85" stroke="{stroke}" stroke-width="0.06"/>'
                f'<text x="0" y="{FONT*0.25}" font-size="{FONT}" fill="#cbd5e1" '
                f'text-anchor="middle" font-family="monospace">{desc}</text>'
                f'</g>'
            )
    return out


def _svg_trayectoria(actor, t_now: float) -> str:
    traj = [p for p in (actor.trayectoria or []) if p.t <= t_now]
    if len(traj) < 2:
        return ""
    color = _color_actor(actor.tipo.value if hasattr(actor.tipo, "value") else str(actor.tipo),
                         actor.color)
    d = " ".join(f"{'M' if i == 0 else 'L'} {p.x} {p.y}" for i, p in enumerate(traj))
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="0.22" '
        f'stroke-dasharray="0.8,0.4" opacity="0.55"/>'
    )


def _svg_actor(actor, st: dict, is_at_impact: bool) -> str:
    tipo = actor.tipo.value if hasattr(actor.tipo, "value") else str(actor.tipo)
    color = _color_actor(tipo, actor.color)
    L = actor.largo_m or (4.6 if tipo == "turismo" else 2.0 if tipo in ("motocicleta", "bicicleta") else 0.6)
    W = actor.ancho_m or (1.8 if tipo == "turismo" else 0.55 if tipo in ("motocicleta", "bicicleta") else 0.6)
    rot = st["rotation"]
    g_open = (
        f'<g transform="translate({st["x"]:.3f},{st["y"]:.3f}) rotate({rot:.2f})">'
    )
    body = ""
    if tipo in ("turismo", "camion", "autobus"):
        sk = "#EF4444" if is_at_impact else "#0F172A"
        sw = "0.3" if is_at_impact else "0.12"
        body = (
            f'<ellipse cx="0.2" cy="0.2" rx="{L/2 + 0.2}" ry="{W/2 + 0.15}" fill="#000" opacity="0.4"/>'
            f'<rect x="{-L/2}" y="{-W/2}" width="{L}" height="{W}" rx="0.4" '
            f'fill="{color}" stroke="{sk}" stroke-width="{sw}"/>'
            f'<rect x="{L/2 - L*0.4}" y="{-W/2 + 0.18}" width="{L*0.18}" height="{W - 0.36}" '
            f'fill="#0F172A" opacity="0.7"/>'
            f'<circle cx="0" cy="0" r="0.6" fill="#0F172A" stroke="#fff" stroke-width="0.06"/>'
            f'<text x="0" y="0.3" font-size="0.85" fill="#fff" text-anchor="middle" '
            f'font-family="monospace">{(actor.id or "?")[:1].upper()}</text>'
        )
    elif tipo in ("bicicleta", "motocicleta", "ciclomotor"):
        body = (
            f'<ellipse cx="0.1" cy="0.1" rx="{L/2 + 0.1}" ry="{W/2 + 0.05}" fill="#000" opacity="0.35"/>'
            f'<line x1="{-L/2}" y1="0" x2="{L/2}" y2="0" stroke="{color}" stroke-width="0.2"/>'
            f'<circle cx="{-L/2 + 0.15}" cy="0" r="0.3" fill="none" stroke="#222" stroke-width="0.08"/>'
            f'<circle cx="{L/2 - 0.15}" cy="0" r="0.3" fill="none" stroke="#222" stroke-width="0.08"/>'
            f'<circle cx="0" cy="0" r="0.32" fill="{color}" stroke="#0F172A" stroke-width="0.08"/>'
            f'<text x="0" y="-0.6" font-size="0.7" fill="{color}" text-anchor="middle" '
            f'font-family="monospace" font-weight="bold">{(actor.id or "?")[:4]}</text>'
        )
    elif tipo == "peaton":
        body = (
            f'<ellipse cx="0.05" cy="0.05" rx="0.35" ry="0.2" fill="#000" opacity="0.4"/>'
            f'<circle r="0.32" fill="{color}" stroke="#0F172A" stroke-width="0.08"/>'
            f'<line x1="0" y1="0" x2="0.5" y2="0" stroke="#fff" stroke-width="0.1"/>'
        )
    else:
        body = f'<rect x="{-L/2}" y="{-W/2}" width="{L}" height="{W}" fill="{color}" opacity="0.8"/>'
    return g_open + body + "</g>"


def _svg_speed_label(actor, st: dict) -> str:
    tipo = actor.tipo.value if hasattr(actor.tipo, "value") else str(actor.tipo)
    color = _color_actor(tipo, actor.color)
    FONT = 0.95
    txt = f'{int(round(st["v_kmh"]))} km/h'
    w = max(3.2, len(txt) * FONT * 0.6)
    return (
        f'<g transform="translate({st["x"]:.3f},{st["y"] - 1.7:.3f})">'
        f'<rect x="{-w/2}" y="{-FONT*0.95}" width="{w}" height="{FONT*1.45}" rx="0.22" '
        f'fill="#0d110d" opacity="0.9" stroke="{color}" stroke-width="0.07"/>'
        f'<text x="0" y="{FONT*0.32}" font-size="{FONT}" fill="{color}" '
        f'text-anchor="middle" font-family="monospace" font-weight="bold">{txt}</text>'
        f'</g>'
    )


def _build_svg(escena: EscenaSimulacionData, t: float, descripcion: str) -> str:
    b = _scene_bounds(escena)
    is_at_impact = bool(escena.impacto and t >= escena.impacto.t - 0.05 and t <= escena.impacto.t + 1.5)

    # Trayectorias visibles hasta t
    trayectorias = "".join(_svg_trayectoria(a, t) for a in (escena.actores or []))
    # Obstáculos (clippeados)
    obstaculos = "".join(_svg_obstaculo(o, b) for o in (escena.obstaculos or []))
    # Huellas
    huellas_svg = ""
    for h in (escena.huellas or []):
        dash = ' stroke-dasharray="0.6,0.4"' if (h.tipo == "derrape") else ""
        huellas_svg += (
            f'<line x1="{h.inicio[0]}" y1="{h.inicio[1]}" x2="{h.fin[0]}" y2="{h.fin[1]}" '
            f'stroke="#1a1a1a" stroke-width="0.4"{dash} opacity="0.85"/>'
        )

    # Actores e impacto
    actor_states = [(a, _interp_actor(a, t)) for a in (escena.actores or [])]
    actores_svg = "".join(_svg_actor(a, st, is_at_impact) for a, st in actor_states)
    speed_lbls = "".join(_svg_speed_label(a, st) for a, st in actor_states)

    impacto_svg = ""
    if is_at_impact and escena.impacto:
        impacto_svg = (
            f'<g transform="translate({escena.impacto.x},{escena.impacto.y})">'
            f'<circle r="2.5" fill="none" stroke="#EF4444" stroke-width="0.2" opacity="0.6"/>'
            f'<circle r="0.7" fill="#EF4444"/>'
            f'<circle r="0.35" fill="#FFFFFF"/>'
            f'</g>'
        )

    # Footer con t y descripción
    desc = (descripcion or "")[:160].replace("&", "&amp;").replace("<", "&lt;")
    footer = (
        f'<g transform="translate({b["minX"] + 1},{b["minY"] + b["height"] - 0.5})">'
        f'<rect x="0" y="-2.4" width="{b["width"] - 2}" height="2.6" '
        f'fill="#0d110d" opacity="0.92" stroke="#C2E94B" stroke-width="0.08"/>'
        f'<text x="0.4" y="-1.2" font-size="0.85" fill="#C2E94B" font-family="monospace" '
        f'font-weight="bold">t = {t:.2f} s</text>'
        f'<text x="0.4" y="-0.2" font-size="0.75" fill="#cbd5e1" font-family="monospace">{desc}</text>'
        f'</g>'
    )

    # Banda exterior con sombreado de fondo
    bg = (
        f'<rect x="{b["minX"]}" y="{b["minY"]}" width="{b["width"]}" height="{b["height"]}" '
        f'fill="#1a1f1a"/>'
    )
    # Grid suave
    grid = (
        f'<defs><pattern id="g" patternUnits="userSpaceOnUse" width="5" height="5">'
        f'<path d="M 5 0 L 0 0 0 5" fill="none" stroke="#2a3a2a" stroke-width="0.1"/></pattern>'
        f'<clipPath id="clip"><rect x="{b["minX"]}" y="{b["minY"]}" width="{b["width"]}" '
        f'height="{b["height"]}"/></clipPath></defs>'
        f'<rect x="{b["minX"]}" y="{b["minY"]}" width="{b["width"]}" height="{b["height"]}" '
        f'fill="url(#g)" opacity="0.5"/>'
    )

    width_px = 1100
    height_px = int(width_px * b["height"] / b["width"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" '
        f'viewBox="{b["minX"]:.2f} {b["minY"]:.2f} {b["width"]:.2f} {b["height"]:.2f}" '
        f'preserveAspectRatio="xMidYMid meet">'
        f'{bg}{grid}'
        f'{_svg_road(escena, b)}'
        f'<g clip-path="url(#clip)">{obstaculos}</g>'
        f'{trayectorias}{huellas_svg}{impacto_svg}{actores_svg}{speed_lbls}'
        f'{footer}'
        f'</svg>'
    )


async def capturar_instante(
    escena: EscenaSimulacionData | dict | None,
    t_segundos: float,
    descripcion: str = "",
    actor_principal_id: str | None = None,
) -> dict:
    """Renderiza un SVG cenital de la escena en `t_segundos`, lo persiste y
    devuelve URL pública + ToolCallLog con la ImagenAnalizada.

    Si `escena` es dict, lo valida primero contra `EscenaSimulacionData`.
    """
    t0 = time.time()

    if escena is None:
        falta = "No hay EscenaSimulacionData disponible — corre `reconstruir_escena` antes."
        return {
            "datos": {"frame_url": None, "falta_info": falta},
            "_log": ToolCallLog(
                agente="SnapshotEscenaAgent",
                pregunta=f"capturar_instante(t={t_segundos:.2f})",
                inputs={"t_segundos": t_segundos, "descripcion": descripcion},
                resultado_resumen="error",
                falta_info=falta,
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    if isinstance(escena, dict):
        try:
            escena = EscenaSimulacionData.model_validate(escena)
        except Exception as e:
            falta = f"EscenaSimulacionData inválida: {e}"
            return {
                "datos": {"frame_url": None, "falta_info": falta},
                "_log": ToolCallLog(
                    agente="SnapshotEscenaAgent",
                    pregunta=f"capturar_instante(t={t_segundos:.2f})",
                    inputs={"t_segundos": t_segundos, "descripcion": descripcion},
                    resultado_resumen="error",
                    falta_info=falta,
                    duracion_ms=int((time.time() - t0) * 1000),
                ),
            }

    duracion = escena.duracion_s or 4.0
    t = max(0.0, min(float(t_segundos), float(duracion)))

    svg = _build_svg(escena, t, descripcion)
    fname = f"snap_{uuid.uuid4().hex[:10]}_t{t:.2f}.svg"
    abs_path = _FRAMES_DIR / fname
    abs_path.write_text(svg, encoding="utf-8")
    settings = get_settings()
    base = settings.api_base_url.rstrip("/")
    url = f"{base}/uploads/_frames_simulacion/{fname}"

    imagen = ImagenAnalizada(
        url=url,
        descripcion=(descripcion or f"Snapshot cenital en t={t:.2f}s"),
        fuente="SimulationAgent",
        relevancia=f"snapshot escena t={t:.2f}s",
    )
    return {
        "datos": {
            "frame_url": url,
            "t_segundos": t,
            "descripcion": descripcion,
            "actor_principal_id": actor_principal_id,
        },
        "_log": ToolCallLog(
            agente="SnapshotEscenaAgent",
            pregunta=f"capturar_instante(t={t:.2f})",
            inputs={"t_segundos": t, "descripcion": descripcion,
                    "actor_principal_id": actor_principal_id},
            resultado_resumen=(
                f"Snapshot generado en t={t:.2f}s con {len(escena.actores)} actores."
            ),
            fuentes_consultadas=["EscenaSimulacionData (SimulationAgent)"],
            imagenes=[imagen],
            duracion_ms=int((time.time() - t0) * 1000),
        ),
    }

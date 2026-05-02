"""SimulacionAgent — cálculos físicos + frames de impacto.

Modelos físicos soportados:
- balance_momento_alcance
- velocidad_por_huella (Stannard Baker)
- distancia_detencion (con pendiente y μ)
- atropello_throw (Searle)
"""

from __future__ import annotations

import math
import time
from typing import Any, Optional

from models import ToolCallLog


G = 9.81


async def simular(modelo: str, parametros: dict[str, Any]) -> dict:
    t0 = time.time()
    falta = None
    if modelo == "balance_momento_alcance":
        out = _balance_momento(parametros)
    elif modelo == "velocidad_por_huella":
        out = _stannard_baker(parametros)
    elif modelo == "distancia_detencion":
        out = _distancia_detencion(parametros)
    elif modelo == "atropello_throw":
        out = _searle_throw(parametros)
    elif modelo == "tiempo_huella":
        out = _tiempo_huella(parametros)
    else:
        out = {"error": f"modelo no soportado: {modelo}"}
        falta = f"Pidió el modelo {modelo!r} pero solo conocemos balance_momento_alcance, velocidad_por_huella, distancia_detencion, atropello_throw, tiempo_huella."

    if "_falta" in out:
        falta = out.pop("_falta")

    log = ToolCallLog(
        agente="SimulacionAgent",
        pregunta=f"Simulación física: {modelo}",
        inputs={"modelo": modelo, "parametros": parametros},
        resultado_resumen=out.get("resumen") or out.get("error", ""),
        fuentes_consultadas=["NumPy local", "Manuales Limpert / Stannard Baker / Searle"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}


# ── Implementaciones físicas ───────────────────────────────────────────────

def _balance_momento(p: dict) -> dict:
    """v_a, v_b en km/h; m_a, m_b en kg → Δv, energía, frames."""
    try:
        v_a = float(p["v_a_kmh"]); v_b = float(p["v_b_kmh"])
        m_a = float(p["m_a_kg"]); m_b = float(p["m_b_kg"])
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito v_a_kmh, v_b_kmh, m_a_kg y m_b_kg para el balance de momento."}

    delta_v = abs(v_a - v_b)
    v_a_ms = v_a / 3.6; v_b_ms = v_b / 3.6
    # Inelástica perfecta
    v_post_ms = (m_a * v_a_ms + m_b * v_b_ms) / (m_a + m_b)
    v_post_kmh = v_post_ms * 3.6
    # Energía absorbida = energía inicial - energía final solidaria
    e_ini = 0.5 * m_a * v_a_ms ** 2 + 0.5 * m_b * v_b_ms ** 2
    e_fin = 0.5 * (m_a + m_b) * v_post_ms ** 2
    e_abs = e_ini - e_fin

    # Pulso de impacto (estimación: 100-150 ms para vehículos)
    duracion_ms = 120
    a_pico = (delta_v / 3.6) / (duracion_ms / 1000)  # m/s²
    a_pico_g = a_pico / G

    frames = [
        {"t_ms": 0, "descripcion": f"Pre-impacto: A a {v_a} km/h, B a {v_b} km/h"},
        {"t_ms": 30, "descripcion": "Contacto inicial: arranca la deformación de los frontales"},
        {"t_ms": duracion_ms, "descripcion": f"Pico de deceleración: {a_pico_g:.1f} g"},
        {"t_ms": duracion_ms + 200,
         "descripcion": f"Vehículos solidarios a {v_post_kmh:.1f} km/h"},
    ]

    return {
        "delta_v_kmh": round(delta_v, 1),
        "v_post_solidaria_kmh": round(v_post_kmh, 1),
        "energia_disipada_kj": round(e_abs / 1000, 2),
        "deceleracion_pico_g": round(a_pico_g, 1),
        "duracion_pulso_ms": duracion_ms,
        "frames": frames,
        "modelo_aplicado": "balance_momento_alcance",
        "asunciones": ["colisión inelástica perfecta", "pulso de 120 ms (rango típico turismo-camión)"],
        "resumen": f"Δv={delta_v:.0f} km/h, pico {a_pico_g:.1f} g durante {duracion_ms} ms, energía disipada {e_abs/1000:.1f} kJ.",
    }


def _stannard_baker(p: dict) -> dict:
    """v = √(2·μ·g·d). d en m, μ adimensional, pendiente opcional (decimal)."""
    try:
        d = float(p["distancia_m"])
        mu = float(p.get("coef_friccion", 0.7))
        pendiente = float(p.get("pendiente_pct", 0)) / 100
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito distancia_m (huella) y opcionalmente coef_friccion y pendiente_pct."}

    mu_eff = mu + pendiente   # ascendente suma, descendente resta
    v_ms = math.sqrt(2 * mu_eff * G * d)
    v_kmh = v_ms * 3.6
    return {
        "velocidad_minima_kmh": round(v_kmh, 1),
        "modelo_aplicado": "stannard_baker",
        "formula": "v = √(2 · (μ + sin(θ)) · g · d)",
        "asunciones": [f"μ={mu}", f"pendiente={pendiente*100}%", "frenada plena con neumáticos bloqueados"],
        "resumen": f"Velocidad mínima del vehículo: {v_kmh:.1f} km/h con huella de {d} m, μ={mu}.",
    }


def _distancia_detencion(p: dict) -> dict:
    """Distancia y tiempo para detener desde una velocidad dada.

    Si `incluir_tiempo_reaccion=False` (recomendado para alinear con la práctica
    pericial, ya que el atestado suele indicar 'el conductor frena'), solo se
    cuenta la frenada pura. Por defecto incluye reacción + frenada."""
    try:
        v_kmh = float(p["v_kmh"])
        mu = float(p.get("coef_friccion", 0.7))
        pendiente = float(p.get("pendiente_pct", 0)) / 100
        t_reaccion = float(p.get("t_reaccion_s", 1.0))
        incluir_tr = bool(p.get("incluir_tiempo_reaccion", True))
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito v_kmh, opcional coef_friccion, pendiente_pct, t_reaccion_s, incluir_tiempo_reaccion."}

    v_ms = v_kmh / 3.6
    mu_eff = max(0.05, mu + pendiente)
    a = mu_eff * G
    d_reaccion = v_ms * t_reaccion if incluir_tr else 0.0
    t_frenada = v_ms / a
    d_frenada = v_ms ** 2 / (2 * a)
    d_total = d_reaccion + d_frenada
    t_total = (t_reaccion if incluir_tr else 0.0) + t_frenada
    asunciones = [f"μ={mu}", f"pendiente={pendiente*100}%"]
    if incluir_tr:
        asunciones.append(f"t reacción={t_reaccion}s")
    else:
        asunciones.append("solo frenada (sin tiempo de reacción)")
    return {
        "v_kmh": v_kmh,
        "incluir_tiempo_reaccion": incluir_tr,
        "distancia_reaccion_m": round(d_reaccion, 2),
        "distancia_frenada_m": round(d_frenada, 2),
        "distancia_total_m": round(d_total, 2),
        "tiempo_frenada_s": round(t_frenada, 2),
        "tiempo_total_s": round(t_total, 2),
        "modelo_aplicado": "distancia_detencion",
        "asunciones": asunciones,
        "resumen": (
            f"A {v_kmh} km/h con μ={mu}, pendiente {pendiente*100:.0f}%"
            + (f", t_reacción={t_reaccion}s" if incluir_tr else " (solo frenada)") +
            f": recorre {d_total:.2f} m en {t_total:.2f} s "
            f"(frenada {d_frenada:.2f} m / {t_frenada:.2f} s)."
        ),
    }


def _tiempo_huella(p: dict) -> dict:
    """Tiempo total desde percepción del riesgo hasta el final de la huella de frenado.

    t_total = t_reaccion + t_ejecucion + t_frenada
    donde t_frenada se obtiene de la longitud de huella y la deceleración (μ·g + pendiente).
    Es el cálculo de IURGI para demostrar la evitabilidad temporal del accidente.
    """
    try:
        d_huella = float(p["distancia_m"])
        mu = float(p.get("coef_friccion", 0.7))
        pendiente = float(p.get("pendiente_pct", 0)) / 100
        t_reaccion = float(p.get("t_reaccion_s", 1.0))
        t_ejecucion = float(p.get("t_ejecucion_s", 0.5))
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito distancia_m (huella), opcional coef_friccion, pendiente_pct, t_reaccion_s (def 1.0), t_ejecucion_s (def 0.5)."}

    mu_eff = max(0.05, mu + pendiente)
    # v inicial al iniciar bloqueo (Stannard-Baker inverso): v = sqrt(2·a·d)
    v_ms = math.sqrt(2 * mu_eff * G * d_huella)
    v_kmh = v_ms * 3.6
    t_frenada = v_ms / (mu_eff * G)
    t_total = t_reaccion + t_ejecucion + t_frenada
    return {
        "distancia_huella_m": d_huella,
        "velocidad_inicio_huella_kmh": round(v_kmh, 1),
        "t_reaccion_s": t_reaccion,
        "t_ejecucion_s": t_ejecucion,
        "t_frenada_s": round(t_frenada, 2),
        "t_total_s": round(t_total, 2),
        "modelo_aplicado": "tiempo_huella",
        "formula": "t_total = t_reaccion + t_ejecucion + sqrt(2·d/(μ·g))/(μ·g)",
        "asunciones": [f"μ_eff={mu_eff:.2f}", f"pendiente={pendiente*100}%",
                       f"t_reacción={t_reaccion}s", f"t_ejecución={t_ejecucion}s"],
        "resumen": (
            f"Desde percepción del riesgo hasta el final de la huella ({d_huella} m): "
            f"t_total = {t_total:.2f} s (reacción {t_reaccion}s + ejecución {t_ejecucion}s + "
            f"frenada {t_frenada:.2f}s). Velocidad al iniciar el bloqueo: {v_kmh:.1f} km/h."
        ),
    }


def _searle_throw(p: dict) -> dict:
    """Atropello — distancia de proyección Searle: v = √(2·g·μ·d / (1 - μ·tan(θ_proy)))."""
    try:
        d_proy = float(p["distancia_proyeccion_m"])
        mu = float(p.get("coef_friccion_peaton", 0.65))
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito distancia_proyeccion_m (de impacto a posición final del peatón)."}

    v_ms_min = math.sqrt(2 * G * mu * d_proy)
    v_kmh = v_ms_min * 3.6
    return {
        "velocidad_minima_atropello_kmh": round(v_kmh, 1),
        "modelo_aplicado": "atropello_searle",
        "formula": "v_min = √(2·g·μ·d_proyección)",
        "asunciones": [f"μ peatón-asfalto = {mu}", "modelo Searle límite inferior"],
        "resumen": f"Velocidad mínima del vehículo en el atropello: {v_kmh:.1f} km/h (proyección {d_proy} m).",
    }

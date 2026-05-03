"""PhysicsAgent — cálculos físicos deterministas (fuente de verdad).

Este agente NO genera imágenes ni croquis. Solo aplica modelos físicos
clásicos (Stannard-Baker, Searle, balance de momento, energía cinética,
distancia/tiempo de detención) y devuelve cifras objetivas que el resto
del pipeline (BiomecanicaAgent, SimulacionAgent, AtestadoAgent, perito
coordinador) consume como entrada.

Modelos soportados:
- balance_momento_alcance
- velocidad_por_huella       (Stannard-Baker)
- distancia_detencion        (con pendiente y μ)
- atropello_throw            (Searle)
- tiempo_huella              (reacción + ejecución + frenada)
- energia_cinetica           (Ec = ½·m·v²)
"""

from __future__ import annotations

import math
import time
from typing import Any

from models import ToolCallLog


G = 9.81


async def calcular(modelo: str, parametros: dict[str, Any]) -> dict:
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
    elif modelo == "energia_cinetica":
        out = _energia_cinetica(parametros)
    else:
        out = {"error": f"modelo no soportado: {modelo}"}
        falta = (
            f"Pidió el modelo {modelo!r} pero solo conocemos "
            "balance_momento_alcance, velocidad_por_huella, distancia_detencion, "
            "atropello_throw, tiempo_huella, energia_cinetica."
        )

    if "_falta" in out:
        falta = out.pop("_falta")

    log = ToolCallLog(
        agente="PhysicsAgent",
        pregunta=f"Cálculo físico: {modelo}",
        inputs={"modelo": modelo, "parametros": parametros},
        resultado_resumen=out.get("resumen") or out.get("error", ""),
        fuentes_consultadas=["NumPy local", "Manuales Limpert / Stannard-Baker / Searle"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}


# ── Implementaciones físicas ───────────────────────────────────────────────

def _balance_momento(p: dict) -> dict:
    try:
        v_a = float(p["v_a_kmh"]); v_b = float(p["v_b_kmh"])
        m_a = float(p["m_a_kg"]); m_b = float(p["m_b_kg"])
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito v_a_kmh, v_b_kmh, m_a_kg y m_b_kg para el balance de momento."}

    delta_v = abs(v_a - v_b)
    v_a_ms = v_a / 3.6; v_b_ms = v_b / 3.6
    v_post_ms = (m_a * v_a_ms + m_b * v_b_ms) / (m_a + m_b)
    v_post_kmh = v_post_ms * 3.6
    e_ini = 0.5 * m_a * v_a_ms ** 2 + 0.5 * m_b * v_b_ms ** 2
    e_fin = 0.5 * (m_a + m_b) * v_post_ms ** 2
    e_abs = e_ini - e_fin

    duracion_ms = 120
    a_pico = (delta_v / 3.6) / (duracion_ms / 1000)
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
    """v = √(2·μ·g·d). Default μ=0.75 (asfalto seco, valor pericial habitual)."""
    try:
        d = float(p["distancia_m"])
        mu = float(p.get("coef_friccion", 0.75))
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

    Default μ=0.75 (asfalto seco). Por convenio pericial (ITRASA et al.) se
    puede pasar `incluir_tiempo_reaccion=False` para reportar SOLO la frenada
    pura, separando claramente reacción y frenada en el output.
    """
    try:
        v_kmh = float(p["v_kmh"])
        mu = float(p.get("coef_friccion", 0.75))
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
            f": frenada pura {d_frenada:.2f} m / {t_frenada:.2f} s"
            + (f"; total con reacción {d_total:.2f} m / {t_total:.2f} s." if incluir_tr else ".")
        ),
    }


def _tiempo_huella(p: dict) -> dict:
    """Tiempo total desde percepción del riesgo hasta el final de la huella.

    t_total = t_reaccion + t_ejecucion + t_frenada
    Default μ=0.75. t_ejecucion default 0 s (ITRASA no lo añade); ponerlo a
    >0 si se quiere modelar latencia mecánica del freno.
    """
    try:
        d_huella = float(p["distancia_m"])
        mu = float(p.get("coef_friccion", 0.75))
        pendiente = float(p.get("pendiente_pct", 0)) / 100
        t_reaccion = float(p.get("t_reaccion_s", 1.0))
        t_ejecucion = float(p.get("t_ejecucion_s", 0.0))
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito distancia_m (huella), opcional coef_friccion, pendiente_pct, t_reaccion_s (def 1.0), t_ejecucion_s (def 0.0)."}

    mu_eff = max(0.05, mu + pendiente)
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


def _energia_cinetica(p: dict) -> dict:
    """Ec = ½·m·v². Acepta una v_kmh única o una lista v_kmh_lista para
    devolver la tabla comparativa estilo ITRASA (10/20/50 km/h)."""
    try:
        m = float(p["masa_kg"])
    except (KeyError, ValueError, TypeError):
        return {"_falta": "Necesito masa_kg (y v_kmh o v_kmh_lista)."}

    velocidades_in = p.get("v_kmh_lista")
    if velocidades_in is None:
        v = p.get("v_kmh")
        if v is None:
            return {"_falta": "Necesito v_kmh (escalar) o v_kmh_lista (array de km/h)."}
        velocidades_in = [v]

    try:
        velocidades = [float(x) for x in velocidades_in]
    except (ValueError, TypeError):
        return {"_falta": "v_kmh_lista debe ser un array de números en km/h."}

    tabla = []
    for vk in velocidades:
        v_ms = vk / 3.6
        ec_j = 0.5 * m * v_ms ** 2
        tabla.append({
            "v_kmh": vk,
            "energia_cinetica_j": round(ec_j, 1),
            "energia_cinetica_kj": round(ec_j / 1000, 3),
        })

    if len(tabla) == 1:
        t0_ = tabla[0]
        resumen = (
            f"Ec = {t0_['energia_cinetica_j']:.0f} J ({t0_['energia_cinetica_kj']:.2f} kJ) "
            f"para m={m} kg a {t0_['v_kmh']} km/h."
        )
    else:
        partes = " · ".join(
            f"{t['v_kmh']} km/h → {t['energia_cinetica_j']:.0f} J" for t in tabla
        )
        ec_max = tabla[-1]["energia_cinetica_j"]
        ec_min = tabla[0]["energia_cinetica_j"]
        factor = ec_max / ec_min if ec_min > 0 else None
        resumen = (
            f"Ec para m={m} kg → {partes}"
            + (f" (×{factor:.1f} entre extremos)." if factor else ".")
        )

    return {
        "masa_kg": m,
        "tabla": tabla,
        "modelo_aplicado": "energia_cinetica",
        "formula": "Ec = ½ · m · v²",
        "resumen": resumen,
    }

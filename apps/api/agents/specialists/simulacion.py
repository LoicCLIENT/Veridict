"""SimulacionAgent — recreación visual del siniestro.

NO calcula nada por sí mismo: consume velocidades/masas/posiciones que el
PhysicsAgent (cálculos) ya ha producido y las renderiza como un frame SVG
del croquis (vehículos, trayectorias, PDI, huellas, vectores de velocidad).

El frame se persiste en `apps/api/uploads/_frames_simulacion/` y se devuelve
al Perito coordinador con su URL pública para citarlo en el informe.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Optional

from config import get_settings
from models import ImagenAnalizada, ToolCallLog
from physics.croquis import generar_croquis_svg
from physics.reconstruction import reconstruir_colision


_FRAMES_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "_frames_simulacion"
_FRAMES_DIR.mkdir(parents=True, exist_ok=True)


EVENTOS_DOC = {
    "croquis_general": "Vista cenital del siniestro completo: posiciones iniciales, PDI, posiciones finales y vectores post-impacto.",
    "pre_impacto": "Trayectorias de aproximación de A y B antes del PDI.",
    "impacto": "Posición de los vehículos en el momento del contacto (PDI), con ángulo relativo.",
    "post_impacto": "Posiciones finales y vectores de velocidad post-impacto.",
    "huellas": "Mismo croquis pero realzando las huellas en calzada (frenada, derrape, arrastre).",
}


async def generar_frame(
    evento: str,
    masa_a: float,
    masa_b: float,
    ebs_a_kmh: float,
    ebs_b_kmh: float,
    angulo_pre_a: float = 0.0,
    angulo_pre_b: float = 180.0,
    tipo_colision: str = "colision",
    modelo_a: str = "Vehiculo A",
    modelo_b: str = "Vehiculo B",
    pos_final_a: Optional[list[float]] = None,
    pos_final_b: Optional[list[float]] = None,
    huellas_post_a_m: Optional[float] = None,
    huellas_post_b_m: Optional[float] = None,
    mu: float = 0.75,
) -> dict:
    """Genera y persiste un frame SVG del siniestro. Devuelve URL pública + metadata."""
    t0 = time.time()
    pos_a = tuple(pos_final_a) if pos_final_a else (5.0, 2.0)
    pos_b = tuple(pos_final_b) if pos_final_b else (-4.0, -1.5)

    falta = None
    try:
        resultado = reconstruir_colision(
            masa_a=masa_a, masa_b=masa_b,
            ebs_a_kmh=ebs_a_kmh, ebs_b_kmh=ebs_b_kmh,
            angulo_pre_a=angulo_pre_a, angulo_pre_b=angulo_pre_b,
            pos_final_a=pos_a, pos_final_b=pos_b,
            huellas_post_a_m=huellas_post_a_m,
            huellas_post_b_m=huellas_post_b_m,
            mu=mu,
        )
        svg = generar_croquis_svg(
            resultado=resultado,
            pos_final_a=pos_a, pos_final_b=pos_b,
            angulo_pre_a=angulo_pre_a, angulo_pre_b=angulo_pre_b,
            tipo_colision=tipo_colision,
            modelo_a=modelo_a, modelo_b=modelo_b,
        )
    except Exception as e:
        falta = (
            f"El motor de simulación no pudo reconstruir el frame {evento!r}: {e}. "
            f"Confirma masas, velocidades y posiciones finales (que vienen del PhysicsAgent)."
        )
        return {
            "datos": {"error": str(e), "frame_url": None, "evento": evento, "falta_info": falta},
            "_log": ToolCallLog(
                agente="SimulacionAgent", pregunta=f"generar_frame: {evento}",
                inputs={"evento": evento}, resultado_resumen="error",
                fuentes_consultadas=["physics.reconstruction (motor interno)"],
                falta_info=falta, duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    # Calidad de la reconstrucción: si el balance de momento se desvía >15 %,
    # significa que las velocidades/ángulos pasados son físicamente
    # inconsistentes. NO publicamos ese frame: devolvemos `falta_info` para
    # que el perito ajuste los inputs (probablemente las velocidades vienen
    # de una estimación libre en vez de un cálculo previo del PhysicsAgent).
    LIMITE_ERROR_MOMENTO_PCT = 15.0
    if resultado.error_momento_pct > LIMITE_ERROR_MOMENTO_PCT:
        msg = (
            f"Frame {evento!r} rechazado: error de momento "
            f"{resultado.error_momento_pct:.1f}% > {LIMITE_ERROR_MOMENTO_PCT}%. "
            f"Las velocidades de impacto que has pasado (A={ebs_a_kmh} km/h, "
            f"B={ebs_b_kmh} km/h) no son físicamente consistentes con las masas "
            f"(A={masa_a} kg, B={masa_b} kg) y los ángulos. Vuelve a llamar al "
            f"PhysicsAgent (calcular_fisica) para validar las velocidades antes "
            f"de pedir el frame."
        )
        return {
            "datos": {
                "frame_url": None, "evento": evento, "rechazado": True,
                "error_momento_pct": round(resultado.error_momento_pct, 2),
                "v_pre_a_kmh": round(resultado.v_pre_a_kmh, 1),
                "v_pre_b_kmh": round(resultado.v_pre_b_kmh, 1),
                "falta_info": msg,
            },
            "_log": ToolCallLog(
                agente="SimulacionAgent",
                pregunta=f"generar_frame: {evento} (rechazado)",
                inputs={"evento": evento, "ebs_a_kmh": ebs_a_kmh, "ebs_b_kmh": ebs_b_kmh,
                        "masa_a": masa_a, "masa_b": masa_b},
                resultado_resumen=msg,
                fuentes_consultadas=["physics.reconstruction (motor interno)"],
                falta_info=msg,
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    fname = f"{uuid.uuid4().hex[:10]}_{evento}.svg"
    abs_path = _FRAMES_DIR / fname
    abs_path.write_text(svg, encoding="utf-8")
    settings = get_settings()
    base = settings.api_base_url.rstrip("/")
    url = f"{base}/uploads/_frames_simulacion/{fname}"

    delta_v_a = round(resultado.delta_v_a_kmh, 1)
    delta_v_b = round(resultado.delta_v_b_kmh, 1)

    descripcion = (
        f"Frame {evento}. v_pre A={resultado.v_pre_a_kmh:.1f} km/h, "
        f"B={resultado.v_pre_b_kmh:.1f} km/h. "
        f"Δv A={delta_v_a}, Δv B={delta_v_b} km/h. "
        f"Error de momento: {resultado.error_momento_pct:.1f}%."
    )
    imagen = ImagenAnalizada(
        url=url, descripcion=descripcion, fuente="SimulacionAgent",
        relevancia=f"croquis evento '{evento}'",
    )

    log = ToolCallLog(
        agente="SimulacionAgent",
        pregunta=f"generar_frame: {evento}",
        inputs={"evento": evento, "masa_a": masa_a, "masa_b": masa_b,
                "ebs_a_kmh": ebs_a_kmh, "ebs_b_kmh": ebs_b_kmh,
                "angulo_pre_a": angulo_pre_a, "angulo_pre_b": angulo_pre_b},
        resultado_resumen=descripcion,
        fuentes_consultadas=["Motor Veridict (physics.reconstruction + physics.croquis)"],
        imagenes=[imagen],
        falta_info=(
            "; ".join(resultado.advertencias) if resultado.advertencias else None
        ),
        duracion_ms=int((time.time() - t0) * 1000),
    )

    return {
        "datos": {
            "evento": evento,
            "frame_url": url,
            "delta_v_a_kmh": delta_v_a, "delta_v_b_kmh": delta_v_b,
            "v_pre_a_kmh": round(resultado.v_pre_a_kmh, 1),
            "v_pre_b_kmh": round(resultado.v_pre_b_kmh, 1),
            "v_post_a_kmh": round(resultado.v_post_a_kmh, 1),
            "v_post_b_kmh": round(resultado.v_post_b_kmh, 1),
            "coef_restitucion": round(resultado.coef_restitucion, 3),
            "error_momento_pct": round(resultado.error_momento_pct, 2),
            "advertencias": resultado.advertencias,
        },
        "_log": log,
    }

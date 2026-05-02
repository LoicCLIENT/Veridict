"""AtestadoAgent — verificación física de declaraciones y análisis de imágenes
de daños/escena con visión Claude.
"""

from __future__ import annotations

import time
from typing import Optional

import anthropic

from config import get_claude, get_settings
from models import ImagenAnalizada, ToolCallLog


SYS_VISION_DAMAGE = """Eres un perito visual de daños en vehículos accidentados.
Recibes una foto y devuelves una descripción técnica BREVE en español:
- Pieza dañada (parachoques, parabrisas, capó, techo, lateral, puerta, etc.).
- Lado (delantero/trasero, izq/dcho).
- Tipo de daño (deformación, hendidura, rotura, rasguño, cristal estallado).
- Si se aprecian indicios de altura del impacto (marca de cuerpo en parabrisas,
  hendidura en techo, etc.), descríbelo.
NO atribuyas culpa, NO afirmes velocidades. 80 palabras máximo. Sin emojis."""


async def verificar_declaraciones(
    declaracion: Optional[str],
    velocidad_calculada_kmh: Optional[float],
    velocidad_declarada_kmh: Optional[float],
) -> dict:
    """Contraste textual + numérico declaración ↔ física."""
    t0 = time.time()
    if velocidad_calculada_kmh is None or velocidad_declarada_kmh is None:
        out = {
            "compatible": None,
            "observacion": "No hay datos suficientes para contrastar (falta velocidad calculada o declarada).",
        }
        falta = "Pasa primero por SimulacionAgent para obtener una velocidad calculada con la que comparar."
    else:
        diff = velocidad_calculada_kmh - velocidad_declarada_kmh
        compatible = abs(diff) <= 0.15 * max(velocidad_declarada_kmh, 1)
        out = {
            "velocidad_declarada_kmh": velocidad_declarada_kmh,
            "velocidad_calculada_kmh": velocidad_calculada_kmh,
            "diferencia_kmh": round(diff, 1),
            "compatible": compatible,
            "observacion": (
                f"Declaración: {velocidad_declarada_kmh} km/h. Cálculo físico: {velocidad_calculada_kmh} km/h. "
                f"Diferencia {diff:+.1f} km/h. "
                + ("Compatibles dentro del 15%." if compatible else
                   "Incompatibles: la evidencia física supera el margen del 15%.")
            ),
        }
        falta = None
        if declaracion:
            out["declaracion_textual"] = declaracion

    log = ToolCallLog(
        agente="AtestadoAgent",
        pregunta="Contraste declaración del conductor vs evidencia física",
        inputs={"declaracion": declaracion,
                "v_calc": velocidad_calculada_kmh, "v_decl": velocidad_declarada_kmh},
        resultado_resumen=out["observacion"],
        fuentes_consultadas=["Atestado del caso", "SimulacionAgent (output previo)"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}


async def analizar_imagen_dano(image_url: str, contexto: Optional[str] = None) -> dict:
    """Visión Claude sobre una foto de daños del vehículo."""
    t0 = time.time()
    settings = get_settings()
    if not settings.anthropic_api_key:
        return {
            "datos": {"error": "ANTHROPIC_API_KEY no configurada — no se pudo invocar visión."},
            "_log": ToolCallLog(
                agente="AtestadoAgent.vision", pregunta="análisis visual de daño",
                inputs={"image_url": image_url}, resultado_resumen="omitido (sin API key)",
                falta_info="Configurar ANTHROPIC_API_KEY para activar análisis visual.",
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    client = get_claude()
    user_content = [
        {"type": "image", "source": {"type": "url", "url": image_url}},
        {"type": "text",
         "text": (contexto or "Describe los daños técnicamente y la posible zona/altura de impacto.")},
    ]
    descripcion = ""
    error = None
    try:
        resp = await client.messages.create(
            model=settings.model_sonnet,
            max_tokens=400,
            system=SYS_VISION_DAMAGE,
            messages=[{"role": "user", "content": user_content}],
        )
        descripcion = "".join(b.text for b in resp.content if hasattr(b, "text"))
    except anthropic.APIError as e:
        error = str(e)

    fuente_img = "Mapillary" if "mapillary" in image_url.lower() else "perito"
    imagen = ImagenAnalizada(
        url=image_url, descripcion=descripcion or None, fuente=fuente_img,
        relevancia=contexto or "análisis visual",
    )
    log = ToolCallLog(
        agente="AtestadoAgent.vision",
        pregunta="Análisis visual de imagen de daño",
        inputs={"image_url": image_url, "contexto": contexto},
        resultado_resumen=(descripcion[:200] + "…") if descripcion and len(descripcion) > 200 else descripcion,
        fuentes_consultadas=["Claude visión"],
        imagenes=[imagen],
        falta_info=error,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": {"descripcion": descripcion, "error": error}, "_log": log}

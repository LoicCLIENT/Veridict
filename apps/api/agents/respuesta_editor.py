"""Editor incremental de respuestas del informe pericial.

Cuando el perito humano aporta un dato que el sistema le había pedido, NO se
regenera el informe entero (caro, lento, riesgoso). Se reescribe SOLO la
respuesta C_i afectada con un prompt focalizado, manteniendo intactos:
  - El resumen del caso
  - Las fichas técnicas, normativa, cálculos, biomecánica y conformidad
  - Las demás respuestas C_j (j ≠ i)
  - Los tool calls y trazabilidad

Usa Sonnet 4.6 (no Opus) y NO invoca tools — el contexto ya está consolidado
en el informe inicial generado por el Perito.
"""

from __future__ import annotations

import json
import re
from typing import Optional

from anthropic import APIError

from config import get_claude, get_settings
from models import Caso, Cita, RespuestaPregunta


SYSTEM_EDITOR = """Eres VERIDICT-EDITOR, especialista en edición pericial incremental.

Recibes UNA respuesta C_i de un informe pericial ya redactada, junto con el contexto técnico consolidado del caso (fichas técnicas, cálculos, normativa, biomecánica, hechos del atestado y, si aplica, un dato NUEVO aportado por el perito firmante).

Tu cometido: REESCRIBIR esa respuesta integrando el dato nuevo o manteniéndola coherente con la nueva información, conservando:
- El tono pericial UNE-EN 16775 (registro técnico, español de España).
- La estructura: párrafo único de 100-200 palabras.
- Las citas correctas (calculo, normativa, ficha_tecnica, hecho, imagen, meteo, escena).
- La trazabilidad: cada afirmación cuantitativa o normativa debe tener cita.

REGLAS DURAS:
- NO inventes datos que no estén en el contexto aportado.
- NO atribuyas culpa.
- NO modifiques otras respuestas.
- Si el dato nuevo HACE INCOMPATIBLE la respuesta anterior, reformula la conclusión (no la maquilles); ajusta la confianza a la baja si procede.
- Si el dato nuevo CONFIRMA la respuesta anterior, refuérzala citándolo.
- Si el dato nuevo es IRRELEVANTE para esta C_i, devuelve la respuesta anterior y baja la confianza solo si el dato cuestiona alguno de sus pilares.

Devuelve EXCLUSIVAMENTE un JSON con esta forma (sin markdown):

{
  "respuesta": "Párrafo único 100-200 palabras, registro pericial.",
  "confianza": 0.0-1.0,
  "citas": [{"tipo": "...", "referencia": "...", "extracto": "..."}],
  "razon_edicion": "Frase breve explicando qué cambió y por qué."
}"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first, last = text.find("{"), text.rfind("}")
        if 0 <= first < last:
            return json.loads(text[first : last + 1])
        raise


def _payload_para_editor(caso: Caso, target: RespuestaPregunta,
                        dato_nuevo: Optional[str]) -> dict:
    """Construye un payload compacto con el contexto necesario para editar la respuesta."""
    informe = caso.informe
    if informe is None:
        raise ValueError("El caso no tiene informe generado.")

    return {
        "encargo": caso.encargo.model_dump(mode="json") if caso.encargo else None,
        "siniestro_breve": {
            "fecha": caso.fecha_accidente.isoformat() if caso.fecha_accidente else None,
            "tipo_colision": caso.tipo_colision.value if caso.tipo_colision else None,
        },
        "respuesta_actual": {
            "pregunta_id": target.pregunta_id,
            "pregunta": target.pregunta,
            "respuesta": target.respuesta,
            "confianza": target.confianza,
            "citas": [c.model_dump() for c in target.citas],
        },
        "dato_nuevo_del_perito": dato_nuevo,
        "fichas_tecnicas": [
            {"id": f.vehiculo_id, "marca": f.marca, "modelo": f.modelo,
             "masa_kg": f.masa_kg, "ancho_m": f.ancho_m,
             "altura_parachoques_m": f.altura_parachoques_m,
             "sistemas_seguridad": f.sistemas_seguridad}
            for f in informe.fichas_tecnicas
        ],
        "calculos": [
            {"nombre": c.nombre, "valor": c.valor, "unidad": c.unidad,
             "formula": c.formula, "justificacion": c.justificacion[:300]}
            for c in informe.calculos
        ],
        "normativa_disponible": [
            {"referencia": n.referencia, "titulo": n.titulo, "boe": n.boe,
             "extracto": (n.extracto or "")[:240]}
            for n in informe.normativa_aplicable[:8]
        ],
        "biomecanica_resumen": (
            {
                "wad": informe.analisis_biomecanico.wad.model_dump(mode="json")
                       if informe.analisis_biomecanico.wad else None,
                "energia_cinetica_kj": informe.analisis_biomecanico.energia_cinetica_kj,
                "ais3_pct": informe.analisis_biomecanico.probabilidad_ais3_pct,
                "compatibilidad": informe.analisis_biomecanico.compatibilidad_velocidad_lesion,
                "tiene_analisis_craneal": informe.analisis_biomecanico.analisis_craneal is not None,
            }
            if informe.analisis_biomecanico else None
        ),
        "conformidad_atestado_resumen": (
            {
                "valoracion_global": informe.conformidad_atestado.valoracion_global,
                "n_incongruencias": len(informe.conformidad_atestado.incongruencias),
                "n_omisiones": len(informe.conformidad_atestado.elementos_omitidos),
            }
            if informe.conformidad_atestado else None
        ),
        "contexto_meteo": (
            informe.contexto_meteo.model_dump(mode="json")
            if informe.contexto_meteo else None
        ),
        "contexto_escena_breve": (
            {
                "direccion_resuelta": informe.contexto_escena.direccion_resuelta,
                "via_principal_nombre": informe.contexto_escena.via_principal_nombre,
                "velocidad_maxima_kmh": informe.contexto_escena.velocidad_maxima_kmh,
                "pendiente_pct": informe.contexto_escena.pendiente_pct,
            }
            if informe.contexto_escena else None
        ),
        "hechos_atestado_breve": (
            {
                "numero_atestado": caso.hechos_atestado.numero_atestado,
                "cuerpo_actuante": caso.hechos_atestado.cuerpo_actuante,
                "hay_huellas_frenada": caso.hechos_atestado.hay_huellas_frenada,
                "velocidades_declaradas": [
                    v.model_dump(mode="json")
                    for v in caso.hechos_atestado.velocidades_declaradas
                ],
                "declaraciones": (caso.hechos_atestado.declaraciones or "")[:600],
            }
            if caso.hechos_atestado else None
        ),
    }


async def editar_respuesta(
    caso: Caso,
    pregunta_id: str,
    dato_nuevo: Optional[str],
    razon: str = "Información complementaria aportada por el perito firmante",
) -> Optional[RespuestaPregunta]:
    """Reescribe una sola respuesta C_i con LLM. Devuelve la nueva o None si no existe."""
    informe = caso.informe
    if informe is None:
        return None
    target = next((r for r in informe.respuestas if r.pregunta_id == pregunta_id), None)
    if target is None:
        return None

    payload = _payload_para_editor(caso, target, dato_nuevo)
    user_msg = (
        f"Contexto y respuesta a editar (motivo: {razon}):\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nDevuelve SOLO el JSON especificado en las instrucciones."
    )

    settings = get_settings()
    if not settings.anthropic_api_key:
        return target  # sin clave no editamos

    client = get_claude()
    try:
        resp = await client.messages.create(
            model=settings.model_sonnet,
            max_tokens=2048,
            system=SYSTEM_EDITOR,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        data = _extract_json(text)
    except (APIError, ValueError, json.JSONDecodeError):
        return target

    nueva = RespuestaPregunta(
        pregunta_id=target.pregunta_id,
        pregunta=target.pregunta,
        respuesta=data.get("respuesta") or target.respuesta,
        confianza=float(data.get("confianza", target.confianza)),
        citas=[Cita(**c) for c in data.get("citas", [])] or target.citas,
    )
    return nueva

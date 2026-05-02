"""Perito coordinador.

Pipeline real con Anthropic tool_use:

1. Recibe el caso completo (encargo, vehículos, hechos, lesiones).
2. En su system prompt tiene la lista de tools y una rúbrica por tipo de encargo.
3. Itera con Claude: el modelo decide qué tool llamar; ejecutamos; le devolvemos
   el resultado; repetimos hasta `stop_reason="end_turn"` o tope de iteraciones.
4. En el último turno, el Perito DEBE devolver un JSON final con respuestas C1, C2,
   C3, info_faltante y confianza_global.
"""

from __future__ import annotations

import json
import re
from typing import Any

from anthropic import APIError

from agents.tools import TOOLS, dispatch
from config import get_claude, get_settings
from models import (
    Caso,
    Cita,
    FichaTecnicaVehiculo,
    FuenteNormativa,
    ImagenAnalizada,
    InformePericial,
    InfoFaltante,
    PrioridadInfoFaltante,
    RespuestaPregunta,
    ToolCallLog,
    CalculoFisico,
)


MAX_TURNS = 12  # Tope de seguridad para el loop de tools
MODEL_PERITO_DEFAULT = "claude-opus-4-7"


SYSTEM_PROMPT = """Eres VERIDICT-PERITO, un perito forense de accidentes de tráfico que coordina varios agentes especialistas.

Trabajas en español de España. Tu objetivo es producir un BORRADOR de informe pericial UNE-EN 16775 que responda a las preguntas del encargo, citando las evidencias que recopilas con las herramientas a tu disposición.

DISPONES DE ESTAS TOOLS (ya descritas en el schema):
- consultar_escena(lat, lon, radio_m): geometría real, señales, imágenes Mapillary.
- consultar_meteo(lat, lon, fecha_iso): meteorología histórica.
- consultar_ficha_tecnica(marca, modelo, anio): ficha técnica del vehículo.
- consultar_legal(tipo_encargo, fecha_siniestro_iso, palabras_clave): normativa + BOE.
- simular_fisica(modelo, parametros): cálculos físicos deterministas.
- verificar_atestado(velocidad_calculada_kmh, velocidad_declarada_kmh, declaracion): contraste compatibilidad.
- analizar_imagen_dano(image_url, contexto): análisis visual de daños.

REGLAS:

1. NO ATRIBUYES CULPA — solo expones hechos, normativa y cálculos. La calificación última es del perito firmante y del juez.

2. ESTRATEGIA DE INVESTIGACIÓN según el encargo:
   - responsabilidad_trafico: ficha + legal + simular(distancia_detencion) + verificar_atestado.
   - velocidad_impacto: ficha + simular(velocidad_por_huella o balance_momento) + verificar_atestado.
   - seguridad_pasiva: ficha + simular(balance_momento) + legal(palabras=['airbag','antiempotramiento','ECE-R12','FMVSS-208']).
   - atropello: ficha + escena + simular(atropello_throw o velocidad_por_huella) + legal(palabras=['ciclista','peatón','vulnerable','art.46','art.45']).
   - mecanica_fallo: ficha + legal.
   - cuantia_danos: ficha + legal + (lesividad si aplica).

3. Si una tool devuelve `falta_info`, INCLUYE esa pregunta como `info_faltante` en tu JSON final, dirigida al perito humano. NUNCA inventes datos.

4. SI EN `imagenes_perito` HAY URLs, ES OBLIGATORIO llamar `analizar_imagen_dano` para CADA UNA antes de redactar las respuestas finales (puedes pasar 'contexto' indicando qué buscas: altura del impacto, deformación, etc.). Si EscenaAgent devuelve imágenes Mapillary, también puedes invocar `analizar_imagen_dano` sobre 1 ó 2 para describir la geometría del lugar.

5. CITAS OBLIGATORIAS. Toda afirmación cuantitativa o normativa va con cita {tipo, referencia, extracto}.
   Tipos válidos: 'calculo' | 'normativa' | 'ficha_tecnica' | 'hecho' | 'imagen' | 'meteo' | 'escena'.

6. EFICIENCIA: como máximo 8-10 tool calls. No repitas la misma tool con los mismos inputs.

7. Una vez tengas suficiente información, EMITE TU RESPUESTA FINAL como un MENSAJE DE TEXTO (sin más tool_use) con un objeto JSON único:
{
  "resumen_caso": str,
  "respuestas": [{"pregunta_id":"C1","pregunta":str,"respuesta":str,"confianza":float,"citas":[...]}],
  "info_faltante": [{"id":"Q1","pregunta":str,"motivo":str,"prioridad":"bloqueante|recomendable|mejora","afecta_a":["C1"]}],
  "confianza_global": float
}
Sin markdown, sin comentarios fuera del JSON.

Tono: pericial, conciso, español de España.
"""


def _payload_inicial(caso: Caso) -> dict:
    return {
        "encargo": caso.encargo.model_dump(mode="json") if caso.encargo else None,
        "siniestro": {
            "fecha": caso.fecha_accidente.isoformat() if caso.fecha_accidente else None,
            "tipo_colision": caso.tipo_colision.value if caso.tipo_colision else None,
            "ubicacion": caso.ubicacion.model_dump(mode="json") if caso.ubicacion else None,
        },
        "vehiculos_identificacion": [
            v.model_dump(mode="json") for v in caso.vehiculos_identificacion
        ],
        "hechos_atestado": (
            caso.hechos_atestado.model_dump(mode="json") if caso.hechos_atestado else None
        ),
        "lesiones": [l.model_dump(mode="json") for l in caso.lesiones],
        "imagenes_perito": [
            {"url": f.url, "descripcion": f.descripcion or "foto subida por el perito"}
            for f in caso.fotos if f.url
        ],
        "chat_previo": [
            {"rol": m.rol, "contenido": m.contenido}
            for m in (caso.informe.chat if caso.informe else [])
        ],
    }


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


async def coordinar(caso: Caso) -> dict:
    """Devuelve {informe_data, tool_calls, imagenes_recopiladas}.

    `informe_data` es el JSON tal como lo emite el Perito (con citas).
    `tool_calls` es la lista de ToolCallLog que se persistirá en el InformePericial.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        return {
            "informe_data": None,
            "tool_calls": [],
            "imagenes_recopiladas": [],
            "error": "ANTHROPIC_API_KEY no configurada",
        }

    client = get_claude()
    payload = _payload_inicial(caso)
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": (
            "Estos son los datos del caso. Investiga con tus herramientas y "
            "responde a las preguntas del encargo:\n\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
        )},
    ]

    tool_calls_log: list[ToolCallLog] = []
    imagenes_recopiladas: list[ImagenAnalizada] = []
    final_json: dict | None = None
    error: str | None = None

    for turn in range(MAX_TURNS):
        try:
            resp = await client.messages.create(
                model=MODEL_PERITO_DEFAULT,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except APIError as e:
            # Si Opus no está disponible, fallback a Sonnet
            if turn == 0 and "model" in str(e).lower():
                try:
                    resp = await client.messages.create(
                        model=settings.model_sonnet,
                        max_tokens=4096,
                        system=SYSTEM_PROMPT,
                        tools=TOOLS,
                        messages=messages,
                    )
                except APIError as e2:
                    error = str(e2)
                    break
            else:
                error = str(e)
                break

        # Persistir el turno del asistente para mantener contexto
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "tool_use":
            tool_results = []
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use":
                    name = block.name
                    args = block.input or {}
                    try:
                        out = await dispatch(name, args)
                    except Exception as e:
                        out = {"datos": {"error": f"excepción en tool: {e}"}, "_log": None}

                    log: ToolCallLog | None = out.get("_log")
                    if log:
                        tool_calls_log.append(log)
                        imagenes_recopiladas.extend(log.imagenes)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(_clean_for_serialize(out.get("datos", {})),
                                              ensure_ascii=False)[:8000],
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        # stop_reason == "end_turn" → buscamos JSON final en los bloques de texto
        text_out = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        try:
            final_json = _extract_json(text_out)
        except Exception:
            # Forzar un turno final pidiendo SOLO el JSON
            final_json = await _forzar_json_final(client, settings, messages)
            if final_json is None:
                error = "El Perito no devolvió un JSON parseable tras forzar el cierre."
        break
    else:
        # Tope de turnos alcanzado — pedimos JSON con los datos recopilados
        final_json = await _forzar_json_final(client, settings, messages)
        if final_json is None:
            error = f"Se alcanzó el límite de {MAX_TURNS} turnos sin respuesta final."

    return {
        "informe_data": final_json,
        "tool_calls": tool_calls_log,
        "imagenes_recopiladas": imagenes_recopiladas,
        "error": error,
    }


async def _forzar_json_final(client, settings, messages: list[dict]) -> dict | None:
    """Llamada de cierre SIN tools, pidiendo solo el JSON estructurado."""
    closing = list(messages) + [{
        "role": "user",
        "content": (
            "Cierra el informe AHORA. Devuelve EXCLUSIVAMENTE un objeto JSON con esta forma "
            "(sin markdown, sin texto antes ni después):\n\n"
            '{\n'
            '  "resumen_caso": "...",\n'
            '  "respuestas": [{"pregunta_id":"C1","pregunta":"...","respuesta":"...","confianza":0.7,"citas":[]}],\n'
            '  "info_faltante": [{"id":"Q1","pregunta":"...","motivo":"...","prioridad":"recomendable","afecta_a":["C1"]}],\n'
            '  "confianza_global": 0.7\n'
            '}'
        ),
    }]
    for model in (MODEL_PERITO_DEFAULT, settings.model_sonnet):
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=closing,
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
            return _extract_json(text)
        except (APIError, ValueError, json.JSONDecodeError):
            continue
    return None


def _clean_for_serialize(o: Any) -> Any:
    """Convierte objetos Pydantic/anidados a JSON serializable."""
    if hasattr(o, "model_dump"):
        return o.model_dump(mode="json")
    if isinstance(o, dict):
        return {k: _clean_for_serialize(v) for k, v in o.items() if not k.startswith("_log")}
    if isinstance(o, (list, tuple)):
        return [_clean_for_serialize(x) for x in o]
    return o


# ── Construcción del InformePericial a partir de la salida del Perito ──────

def construir_informe(
    coord_out: dict,
    fichas_recopiladas: list[FichaTecnicaVehiculo],
    normativa_recopilada: list[FuenteNormativa],
    bibliografia_recopilada: list[str],
    calculos_recopilados: list[CalculoFisico],
    chat_previo: list,
) -> InformePericial:
    """Funde el JSON del Perito + las fuentes acumuladas en un InformePericial."""
    data = coord_out.get("informe_data") or {}

    respuestas = [
        RespuestaPregunta(
            pregunta_id=r.get("pregunta_id", f"C{i+1}"),
            pregunta=r.get("pregunta", ""),
            respuesta=r.get("respuesta", ""),
            confianza=float(r.get("confianza", 0.0)),
            citas=[Cita(**c) for c in r.get("citas", [])],
        )
        for i, r in enumerate(data.get("respuestas", []))
    ]
    info = [
        InfoFaltante(
            id=q.get("id", f"Q{i+1}"),
            pregunta=q.get("pregunta", ""),
            motivo=q.get("motivo", ""),
            prioridad=PrioridadInfoFaltante(q.get("prioridad", "recomendable")),
            afecta_a=q.get("afecta_a", []),
        )
        for i, q in enumerate(data.get("info_faltante", []))
    ]

    return InformePericial(
        resumen_caso=data.get("resumen_caso", "") or coord_out.get("error", "Informe no generado."),
        fichas_tecnicas=fichas_recopiladas,
        normativa_aplicable=normativa_recopilada,
        bibliografia=bibliografia_recopilada,
        calculos=calculos_recopilados,
        respuestas=respuestas,
        info_faltante=info,
        chat=chat_previo,
        tool_calls=coord_out.get("tool_calls", []),
        imagenes=coord_out.get("imagenes_recopiladas", []),
        confianza_global=float(data.get("confianza_global", 0.0)),
    )

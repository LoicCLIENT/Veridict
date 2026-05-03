"""LegalAgent — selección de normativa aplicable razonada por LLM.

NO usa filtro por matching de strings. Le entrega al LLM el corpus completo
de normativa para el tipo de encargo y le pide que escoja los artículos
realmente aplicables al caso descrito, ordenados por relevancia, con cita
y consolidación BOE/EUR-Lex.
"""

from __future__ import annotations

import json
import re
import time
from datetime import date, datetime
from typing import Optional

from anthropic import APIError

from config import get_claude, get_settings
from models import TipoEncargo, ToolCallLog
from services.external.boe import texto_consolidado
from services.research import bibliografia_para, normativa_para


SYSTEM_LEGAL = """Eres el AGENTE JURÍDICO del equipo pericial VERIDICT, especializado en seguridad vial española.

Tu cometido: dado un caso (encargo, descripción, fecha del siniestro) y un CORPUS de normativa española e internacional que se te entrega como conocimiento, seleccionar los artículos que el perito firmante DEBERÍA citar en el informe, ordenados por relevancia descendente.

PRINCIPIOS:
1. La aplicabilidad la determina la conducta a calificar y la fecha de vigencia. Comprueba siempre que la norma estaba en vigor a la fecha del siniestro.
2. Prioriza los artículos que dan soporte directo a las preguntas del encargo. Descarta los tangenciales.
3. En atropellos a vulnerables (peatón, ciclista) son típicamente concurrentes: deber de diligencia y prudencia (Art. 3 RGC), adecuación de velocidad (Art. 45/19 LSV), moderación ante peatones/ciclistas (Art. 46), pasos para peatones (Art. 54.1) y, jurisprudencialmente, el principio de confianza.
4. En seguridad pasiva: ECE-R12, ECE-R94, FMVSS-208, RD 2822/1998 (RGV) en lo relativo a sistemas obligatorios.
5. Si una norma del corpus NO es aplicable al caso, NO la incluyas aunque pertenezca al tipo de encargo.

RESTRICCIONES:
- NO inventes artículos fuera del corpus aportado.
- Mantén la `referencia` y `boe` exactos del corpus.
- En `motivo_aplicabilidad` razona por qué este artículo aplica AL CASO concreto (1-2 frases), no parafrasees el título.

DEVUELVE EXCLUSIVAMENTE UN JSON con esta forma (sin markdown, sin texto antes ni después):

{
  "normativa_seleccionada": [
    {
      "referencia": "<copiada literal del corpus>",
      "titulo": "<copiada literal del corpus>",
      "boe": "<copiada literal del corpus>",
      "extracto": "<copiada literal del corpus o null>",
      "motivo_aplicabilidad": "Por qué este artículo soporta una conclusión concreta del informe en este caso particular (1-2 frases).",
      "relevancia": "primaria|secundaria|complementaria"
    }
  ],
  "advertencia_temporal": "Texto si la fecha del siniestro afecta a la vigencia de alguna norma (ej. límite genérico 30 km/h pre-RD 970/2020); o null."
}

Idioma: español de España. JSON puro, sin texto fuera del objeto."""


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


async def consultar_legal(
    tipo_encargo: str,
    fecha_siniestro_iso: Optional[str] = None,
    palabras_clave: Optional[list[str]] = None,
    descripcion_caso: Optional[str] = None,
    preguntas_encargo: Optional[list[str]] = None,
) -> dict:
    """Devuelve {datos, _log}. El LLM selecciona los artículos aplicables del corpus.

    `palabras_clave` y `descripcion_caso` son pistas opcionales que el Perito puede
    aportar para orientar al agente jurídico sobre qué partes del caso son relevantes.
    """
    t0 = time.time()
    try:
        tipo = TipoEncargo(tipo_encargo)
    except ValueError:
        tipo = TipoEncargo.RESPONSABILIDAD_TRAFICO

    fecha = None
    if fecha_siniestro_iso:
        try:
            fecha = datetime.fromisoformat(str(fecha_siniestro_iso).replace("Z", "")).date()
        except ValueError:
            fecha = None

    corpus = normativa_para(tipo)              # lista de FuenteNormativa Pydantic
    biblio = bibliografia_para(tipo)
    corpus_dump = [n.model_dump(mode="json") for n in corpus]

    out_norm: list[dict] = []
    advertencia = None
    error = None

    settings = get_settings()
    if settings.anthropic_api_key and corpus_dump:
        payload = {
            "tipo_encargo": tipo.value,
            "fecha_siniestro": fecha.isoformat() if fecha else None,
            "descripcion_caso": descripcion_caso,
            "preguntas_encargo": preguntas_encargo or [],
            "palabras_clave_orientativas": palabras_clave or [],
            "corpus_normativa_disponible": corpus_dump,
        }
        client = get_claude()
        user_msg = (
            "Selecciona del corpus los artículos aplicables al caso, ordenados por relevancia:\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n\nDevuelve SOLO el JSON especificado."
        )
        try:
            resp = await client.messages.create(
                model=settings.model_sonnet,
                max_tokens=2048,
                system=SYSTEM_LEGAL,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = "".join(b.text for b in resp.content if hasattr(b, "text"))
            llm_data = _extract_json(text)
            out_norm = llm_data.get("normativa_seleccionada") or []
            advertencia = llm_data.get("advertencia_temporal")
        except (APIError, ValueError, json.JSONDecodeError) as e:
            error = str(e)
    elif not corpus_dump:
        error = f"No hay corpus normativo seed para tipo={tipo.value}"

    # Fallback si el LLM falla o no hay key: corpus completo, marcado como sin filtrar
    if not out_norm:
        out_norm = [
            {
                **n,
                "motivo_aplicabilidad": "Selección no filtrada (LLM no disponible).",
                "relevancia": "secundaria",
            }
            for n in corpus_dump
        ]

    # Enriquecer con URL BOE consolidada
    enriquecida: list[dict] = []
    for n in out_norm:
        consolidado = texto_consolidado(n.get("referencia", ""), fecha)
        d = dict(n)
        d["url_boe"] = consolidado["url_boe"]
        d["norma_madre"] = consolidado["norma_madre"]
        enriquecida.append(d)

    log = ToolCallLog(
        agente="LegalAgent",
        pregunta=f"Selección normativa LLM para encargo='{tipo.value}' (fecha {fecha_siniestro_iso or '?'})",
        inputs={
            "tipo_encargo": tipo.value,
            "fecha": fecha_siniestro_iso,
            "palabras_clave": palabras_clave or [],
            "n_corpus": len(corpus_dump),
            "n_seleccionados": len(enriquecida),
        },
        resultado_resumen=(
            f"{len(enriquecida)} artículos seleccionados (de {len(corpus_dump)} disponibles), "
            f"{len(biblio)} referencias bibliográficas"
            + (f". Advertencia temporal: {advertencia[:120]}" if advertencia else "")
        ),
        fuentes_consultadas=[
            "Claude Sonnet (razonamiento jurídico)",
            "Veridict normativa seed",
            "BOE/EUR-Lex (URLs consolidadas)",
        ],
        falta_info=error,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": {"normativa": enriquecida, "bibliografia": biblio,
                      "advertencia_temporal": advertencia}, "_log": log}

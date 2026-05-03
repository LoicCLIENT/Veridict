"""ConformidadAtestadoAgent — auditoría metodológica del atestado por LLM.

NO usa reglas regex. Delega al LLM Claude la lectura del texto del atestado
(declaraciones + observaciones) y el cruce con el resto de evidencia para
detectar incongruencias y omisiones, aplicando un manual pericial entregado
como conocimiento autoritativo en el system prompt.
"""

from __future__ import annotations

import json
import re
import time
from typing import Optional

from anthropic import APIError

from config import get_claude, get_settings
from models import ToolCallLog


SYSTEM_CONFORMIDAD = """Eres el AGENTE DE CONFORMIDAD DOCUMENTAL del equipo pericial VERIDICT.

Tu cometido es auditar metodológicamente un atestado policial detectando incongruencias internas, contradicciones con la evidencia física, errores de marco normativo y omisiones obligatorias del expediente.

NO atribuyes culpa. NO valoras la conducta del conductor. SOLO juzgas la calidad técnica del atestado.

═══════════════════════════════════════════════════════════════════════════════
MANUAL PERICIAL — checklist crítico que debes aplicar a TODO atestado
═══════════════════════════════════════════════════════════════════════════════

A. MARCO NORMATIVO Y FECHAS
  - Compara los límites de velocidad citados con la normativa vigente A FECHA del siniestro.
    · El RD 970/2020 introdujo el límite genérico urbano de 30 km/h y entró en vigor el 11/05/2021.
    · Antes de esa fecha el límite genérico urbano era 50 km/h.
    · Si el atestado afirma o asume 30 km/h genérico antes del 11/05/2021 → INCONGRUENCIA ALTA.
  - Si el atestado cita una norma derogada o no vigente a la fecha → INCONGRUENCIA ALTA.

B. COHERENCIA DECLARACIÓN-EVIDENCIA FÍSICA
  - Si el conductor declara haber accionado el freno al máximo (o frenada plena) Y el atestado constata que NO HAY HUELLAS de frenada del vehículo en calzada seca con asfalto en buen estado → INCONGRUENCIA ALTA. Una frenada plena con neumáticos bloqueados deja huella visible.
  - Si la velocidad declarada y la velocidad calculada (que se te aporta como dato) difieren más del 20% → INCONGRUENCIA ALTA.
  - Si el atestado describe un retroceso post-impacto del vehículo de mayor masa frente a uno de mucha menor masa (peatón/ciclista/moto) → INCONGRUENCIA MEDIA: por conservación del momento, lo físicamente esperable es que el vehículo continúe avanzando.

C. ELEMENTOS OBLIGATORIOS QUE SUELEN OMITIRSE
  - En siniestros con resultado letal o lesiones graves: pruebas de detección de alcohol y otras drogas (art. 379 CP). Si no se mencionan → OMISIÓN.
  - Cálculo de velocidad por metodología reconocida (Stannard-Baker, CRASH3, EBS) cuando hay huellas o daños cuantificables. Si no se aporta → OMISIÓN.
  - Croquis a escala y acotado. Si el atestado refiere croquis "sin escala", "desproporcionado" o "sin acotaciones" → INCONGRUENCIA MEDIA.
  - En atropellos: posicionamiento del PDI (punto de impacto), posición final del vehículo y de la víctima, cota lateral de huellas respecto al borde de la vía. Si faltan → OMISIÓN.
  - En siniestros con velocidad relevante: estado de neumáticos y dispositivos de retención del vehículo.

D. CALIDAD METODOLÓGICA
  - Conclusiones del atestado expresadas como hipótesis sin sustento técnico ("podría circular más próximo", "se estima") cuando el dato es desconocido → OMISIÓN.
  - Apriorismos no justificados de posición o trayectoria → INCONGRUENCIA MEDIA.

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES DE SALIDA
═══════════════════════════════════════════════════════════════════════════════

1. Lee el atestado entero (declaraciones + observaciones) que se te aporta.
2. Cruza con la fecha del siniestro y con las velocidades declarada y calculada.
3. Para cada hallazgo: cita LITERALMENTE el fragmento del atestado que lo motiva (entre comillas) y razónalo.
4. Asigna severidad: "alta" (afecta gravemente a la valoración judicial), "media" (debilita la prueba), "baja" (defecto formal).
5. Valoración global:
   · "satisfactorio": ninguna alta y a lo sumo 1 omisión.
   · "incompleto": 0-1 alta y/o 2-3 medias/omisiones.
   · "deficiente": ≥1 alta crítica O ≥2 altas O ≥4 medias/omisiones.

DEVUELVE EXCLUSIVAMENTE UN JSON con esta forma (sin markdown, sin texto antes ni después):

{
  "incongruencias": [
    {"severidad": "alta|media|baja",
     "titulo": "Título corto y operativo (máx 12 palabras)",
     "descripcion": "Cita literal entre comillas + por qué es incongruente, 40-80 palabras."}
  ],
  "elementos_omitidos": [
    "Texto autocontenido describiendo la omisión y la norma o práctica que la exige (40-70 palabras)."
  ],
  "valoracion_global": "satisfactorio|incompleto|deficiente",
  "recomendaciones": ["Acción concreta para subsanar (1-2 frases)..."]
}

REGLAS DURAS:
- Idioma: español de España, registro pericial.
- NO inventes incongruencias que no estén respaldadas por el texto aportado.
- NO repitas la lista del manual: APLÍCALA.
- Si el atestado no presenta defectos relevantes, devuelve listas vacías y valoracion_global="satisfactorio".
- JSON puro."""


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


async def analizar_conformidad(
    hechos: dict,
    lesiones: Optional[list[dict]] = None,
    fecha_siniestro_iso: Optional[str] = None,
    velocidad_declarada_kmh: Optional[float] = None,
    velocidad_calculada_kmh: Optional[float] = None,
    es_atropello: bool = False,
) -> dict:
    """Devuelve {datos, _log}. La estructura de `datos` es la que devuelve el LLM."""
    t0 = time.time()
    settings = get_settings()

    payload = {
        "fecha_siniestro_iso": fecha_siniestro_iso,
        "es_atropello": es_atropello,
        "atestado": {
            "numero_atestado": hechos.get("numero_atestado"),
            "cuerpo_actuante": hechos.get("cuerpo_actuante"),
            "hay_huellas_frenada_vehiculo": hechos.get("hay_huellas_frenada"),
            "estado_calzada": hechos.get("estado_calzada"),
            "visibilidad": hechos.get("visibilidad"),
            "condiciones_meteorologicas": hechos.get("condiciones_meteorologicas"),
            "velocidades_declaradas": hechos.get("velocidades_declaradas") or [],
            "declaraciones_textuales": hechos.get("declaraciones"),
            "observaciones_atestado": hechos.get("observaciones"),
        },
        "lesiones": lesiones or [],
        "contraste_velocidad": {
            "velocidad_declarada_kmh": velocidad_declarada_kmh,
            "velocidad_calculada_kmh": velocidad_calculada_kmh,
        },
    }

    out_data = None
    error = None

    if settings.anthropic_api_key:
        client = get_claude()
        user_msg = (
            "Audita el siguiente atestado siguiendo el manual pericial:\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n\nDevuelve SOLO el JSON especificado en las instrucciones."
        )
        try:
            resp = await client.messages.create(
                model=settings.model_sonnet,
                max_tokens=2048,
                system=SYSTEM_CONFORMIDAD,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = "".join(b.text for b in resp.content if hasattr(b, "text"))
            out_data = _extract_json(text)
        except (APIError, ValueError, json.JSONDecodeError) as e:
            error = str(e)
    else:
        error = "ANTHROPIC_API_KEY no configurada — no se pudo invocar el LLM."

    if not out_data:
        out_data = {
            "incongruencias": [],
            "elementos_omitidos": [],
            "valoracion_global": "no_evaluado",
            "recomendaciones": ([f"Error en el LLM: {error}"] if error else []),
        }

    n_alta = sum(1 for i in out_data.get("incongruencias", []) if i.get("severidad") == "alta")
    n_media = sum(1 for i in out_data.get("incongruencias", []) if i.get("severidad") == "media")
    n_om = len(out_data.get("elementos_omitidos", []))
    valoracion = out_data.get("valoracion_global", "no_evaluado")

    resumen = (f"Valoración: {valoracion}. {n_alta + n_media + sum(1 for i in out_data.get('incongruencias', []) if i.get('severidad') == 'baja')} "
               f"incongruencias ({n_alta} altas, {n_media} medias), {n_om} omisiones.")

    log = ToolCallLog(
        agente="ConformidadAtestadoAgent",
        pregunta=f"Auditoría LLM del atestado ({hechos.get('cuerpo_actuante', 'desconocido')})",
        inputs={
            "es_atropello": es_atropello,
            "fecha": fecha_siniestro_iso,
            "v_declarada": velocidad_declarada_kmh,
            "v_calculada": velocidad_calculada_kmh,
            "n_lesiones": len(lesiones or []),
        },
        resultado_resumen=resumen,
        fuentes_consultadas=[
            "Claude Sonnet (razonamiento pericial)",
            "Manual pericial AEIAT/IURGI (en system prompt)",
            "RD 970/2020", "Art. 379 CP",
        ],
        falta_info=error,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out_data, "_log": log}

"""CronologiaAgent — produce la cronología pericial del siniestro y la enlaza
con la EscenaSimulacionData para attachear un snapshot visual a cada evento.

Funcionamiento:
1. LLM (Opus 4.7, fallback Sonnet) recibe la EscenaSimulacionData ya
   reconstruida + datos de los specialists (escena, meteo, biomecánica, física).
2. Devuelve una lista ordenada de eventos `{t_simulacion_s, descripcion,
   descripcion_visual, actor_principal_id}` cubriendo aproximación, frenada
   (si la hay), impacto, fase de proyección, posiciones finales.
3. Por cada evento se invoca `snapshot_escena.capturar_instante(t)` para
   generar el SVG estático y rellenar `frame_url`.
4. Devuelve `list[Evento]` lista para hidratar `InformePericial.cronologia`.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from anthropic import APIError

from agents.specialists import snapshot_escena
from config import get_claude, get_settings
from models import EscenaSimulacionData, Evento, ToolCallLog


MODEL = "claude-opus-4-20250514"


SYSTEM_PROMPT = """Eres VERIDICT-CRONOLOGIA, un perito que escribe la línea de tiempo del siniestro.

Recibes:
- La EscenaSimulacionData ya reconstruida (con actores, trayectorias, impacto, duracion_s).
- Los datos producidos por los specialists del Perito (escena, biomecánica, física, hechos del atestado, lesiones).

Tu tarea: emitir una lista ORDENADA de 4 a 7 eventos que cubran toda la dinámica del siniestro, alineados temporalmente con el scrubber de la simulación (t en segundos, 0 ≤ t ≤ duracion_s).

REGLAS DURAS
1. Cada evento DEBE tener `t_simulacion_s` ≥ 0 y ≤ duracion_s. El orden de la lista debe respetar t creciente.
2. Cubre como mínimo: aproximación, instante crítico (frenada / pérdida control / inicio del giro), impacto, post-impacto / posiciones finales. Añade más si la dinámica lo justifica (p.ej. salida de curva, proyección del peatón, segundo impacto).
3. La `descripcion` es la frase pericial OBJETIVA del evento (qué pasa: posiciones, velocidades, dinámica). 1-2 frases.
4. La `descripcion_visual` es lo que se VE en el snapshot: qué actor está dónde, hacia dónde mira, si frena. Sirve de pie de foto.
5. `actor_principal_id` es el id del actor protagonista del evento (uno de los actores de la simulación), si lo hay.
6. NO INVENTES velocidades ni posiciones. Usa las que están en la trayectoria de la simulación o las velocidades validadas por physics/biomecanica.
7. Para el evento "impacto", `t_simulacion_s` debe coincidir con `escena.impacto.t` si existe.
8. Si la duración de la simulación es 4 s y el impacto ocurre en t=2.8 s, eventos típicos son:
   - t=0.5 s aproximación inicial
   - t=2.0 s primer indicio (frenada / desviación)
   - t=2.8 s impacto
   - t=3.5 s post-impacto (proyección)
   - t=4.0 s posiciones finales

FORMATO DE SALIDA — DEVUELVE EXCLUSIVAMENTE JSON, sin markdown:

{
  "eventos": [
    {
      "t_simulacion_s": 0.5,
      "descripcion": "El SEAT Ibiza asciende por la BI-3242 a 45 km/h en aproximación a la curva derecha; la bicicleta Orbea desciende por su mitad de calzada a 22 km/h.",
      "descripcion_visual": "Vista cenital con turismo y ciclista todavía separados ~25 m. Ninguno frena.",
      "actor_principal_id": "turismo_seat"
    },
    ...
  ]
}

Responde SOLO con el JSON. Nada más."""


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
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


def _resumen_input(
    escena: EscenaSimulacionData,
    datos_por_tool: dict,
    caso_basico: dict,
) -> dict:
    """Empaqueta lo que el LLM necesita: la escena (compacta) + datos clave."""
    actores_compact = []
    for a in escena.actores or []:
        traj = a.trayectoria or []
        actores_compact.append({
            "id": a.id,
            "tipo": a.tipo.value if hasattr(a.tipo, "value") else str(a.tipo),
            "etiqueta": a.etiqueta,
            "velocidad_inicial_kmh": a.velocidad_inicial_kmh,
            "velocidad_impacto_kmh": a.velocidad_impacto_kmh,
            "frena_desde_t": a.frena_desde_t,
            "trayectoria_resumen": [
                {"t": p.t, "x": round(p.x, 2), "y": round(p.y, 2),
                 "v_kmh": round(p.v_kmh, 1)}
                for p in traj
            ],
        })
    interesantes = [
        "consultar_escena", "consultar_meteo", "calcular_fisica",
        "analizar_biomecanica", "verificar_atestado",
    ]
    datos_compact = {
        k: _recortar(datos_por_tool.get(k))
        for k in interesantes if k in datos_por_tool
    }
    return {
        "caso_basico": caso_basico,
        "escena": {
            "via": escena.via.model_dump(mode="json"),
            "duracion_s": escena.duracion_s,
            "impacto": (escena.impacto.model_dump(mode="json")
                        if escena.impacto else None),
            "actores": actores_compact,
            "descripcion": escena.descripcion,
        },
        "datos_specialists": datos_compact,
    }


def _recortar(value: Any, max_str: int = 500, max_list: int = 8) -> Any:
    if isinstance(value, dict):
        return {k: _recortar(v, max_str, max_list) for k, v in value.items()}
    if isinstance(value, list):
        return [_recortar(v, max_str, max_list) for v in value[:max_list]]
    if isinstance(value, str) and len(value) > max_str:
        return value[:max_str] + "…"
    return value


async def construir_cronologia(
    caso,
    escena: EscenaSimulacionData | None,
    datos_por_tool: dict,
) -> dict:
    """Devuelve {datos: list[Evento], _log: ToolCallLog, _sub_logs: list[ToolCallLog]}.

    Si no hay `escena`, devuelve cronología vacía (no es bloqueante).
    """
    t0 = time.time()
    sub_logs: list[ToolCallLog] = []
    settings = get_settings()

    if escena is None or not escena.actores:
        return {
            "datos": [],
            "_log": ToolCallLog(
                agente="CronologiaAgent",
                pregunta="construir_cronologia",
                inputs={"caso_id": caso.id},
                resultado_resumen="omitido — no hay simulación",
                duracion_ms=int((time.time() - t0) * 1000),
            ),
            "_sub_logs": [],
        }

    if not settings.anthropic_api_key:
        return {
            "datos": [],
            "_log": ToolCallLog(
                agente="CronologiaAgent",
                pregunta="construir_cronologia",
                inputs={"caso_id": caso.id},
                resultado_resumen="error",
                falta_info="ANTHROPIC_API_KEY no configurada",
                duracion_ms=int((time.time() - t0) * 1000),
            ),
            "_sub_logs": [],
        }

    caso_basico = {
        "fecha": caso.fecha_accidente.isoformat() if caso.fecha_accidente else None,
        "tipo_colision": caso.tipo_colision.value if caso.tipo_colision else None,
        "encargo_tipo": caso.encargo.tipo.value if caso.encargo else None,
        "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
        "hechos_atestado": (
            caso.hechos_atestado.model_dump(mode="json")
            if caso.hechos_atestado else None
        ),
    }
    payload = _resumen_input(escena, datos_por_tool or {}, caso_basico)
    user_msg = (
        "Construye la cronología del siniestro a partir de esta evidencia:\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
    )

    client = get_claude()
    raw_text = ""
    fuentes = []
    try:
        resp = await client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw_text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        )
        fuentes.append(f"LLM:{MODEL}")
    except APIError:
        try:
            resp = await client.messages.create(
                model=settings.model_sonnet,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw_text = "".join(
                getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
            )
            fuentes.append(f"LLM:{settings.model_sonnet}")
        except APIError as e2:
            return {
                "datos": [],
                "_log": ToolCallLog(
                    agente="CronologiaAgent",
                    pregunta="construir_cronologia",
                    inputs={"caso_id": caso.id},
                    resultado_resumen="error",
                    fuentes_consultadas=fuentes,
                    falta_info=f"Error LLM: {e2}",
                    duracion_ms=int((time.time() - t0) * 1000),
                ),
                "_sub_logs": [],
            }

    try:
        data = _extract_json(raw_text)
    except Exception as e:
        return {
            "datos": [],
            "_log": ToolCallLog(
                agente="CronologiaAgent",
                pregunta="construir_cronologia",
                inputs={"caso_id": caso.id},
                resultado_resumen="error",
                fuentes_consultadas=fuentes,
                falta_info=f"JSON no parseable: {e}",
                duracion_ms=int((time.time() - t0) * 1000),
            ),
            "_sub_logs": [],
        }

    eventos_raw = data.get("eventos") or []
    duracion = float(escena.duracion_s or 4.0)
    eventos: list[Evento] = []

    for e in eventos_raw:
        try:
            t_sim = float(e.get("t_simulacion_s") or 0.0)
        except (TypeError, ValueError):
            t_sim = 0.0
        t_sim = max(0.0, min(t_sim, duracion))
        descripcion = str(e.get("descripcion") or "").strip()
        if not descripcion:
            continue
        desc_visual = str(e.get("descripcion_visual") or "").strip() or None
        actor_id = e.get("actor_principal_id") or None

        # Generar snapshot SVG para este evento
        snap = await snapshot_escena.capturar_instante(
            escena=escena,
            t_segundos=t_sim,
            descripcion=descripcion,
            actor_principal_id=actor_id,
        )
        if snap.get("_log"):
            sub_logs.append(snap["_log"])
        frame_url = (snap.get("datos") or {}).get("frame_url")

        eventos.append(Evento(
            timestamp=t_sim,
            descripcion=descripcion,
            t_simulacion_s=t_sim,
            frame_url=frame_url,
            descripcion_visual=desc_visual,
            actor_principal_id=actor_id,
        ))

    eventos.sort(key=lambda ev: ev.t_simulacion_s or ev.timestamp or 0.0)

    resumen = (
        f"{len(eventos)} eventos generados con frames "
        f"({sum(1 for e in eventos if e.frame_url)} con snapshot)."
    )
    return {
        "datos": eventos,
        "_log": ToolCallLog(
            agente="CronologiaAgent",
            pregunta="construir_cronologia",
            inputs={"caso_id": caso.id, "duracion_s": duracion},
            resultado_resumen=resumen,
            fuentes_consultadas=fuentes + ["snapshot_escena"],
            duracion_ms=int((time.time() - t0) * 1000),
        ),
        "_sub_logs": sub_logs,
    }

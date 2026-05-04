"""SimulationAgent (LLM) — reconstruye la escena del siniestro como JSON animable.

A diferencia del antiguo `SimulacionAgent` (`simulacion.py`), que es un wrapper
sin LLM sobre `physics/reconstruction.py` y produce un SVG estático cenital,
este specialist USA UN LLM (Claude Opus 4.7) para extraer del caso y de los
datos ya producidos por los demás specialists del Perito un objeto
`EscenaSimulacionData` con:

- Vía (tipo, anchura, pendiente, límite).
- Actores arbitrarios (turismo, bicicleta, peatón, motocicleta, mobiliario).
- Trayectorias por puntos `(x, y, t, v_kmh)` que el frontend interpola.
- Punto de impacto, obstáculos (edificios, zonas terrizas) y meta.

Se ejecuta como POST-STEP tras el `Perito.coordinar()`: lee `datos_por_tool`
para no repetir tool calls (cache) y, si le faltan datos críticos, invoca
`dispatch()` directamente. Devuelve `{datos: EscenaSimulacionData, _log}`.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from anthropic import APIError
from pydantic import ValidationError

from config import get_claude, get_settings
from models import (
    Caso,
    EscenaSimulacionData,
    ToolCallLog,
)


MODEL = "claude-opus-4-20250514"


SYSTEM_PROMPT = """Eres VERIDICT-SIMULATION, un reconstructor cenital 2D de escenas de tráfico.

Tu salida ES UN OBJETO JSON que ALIMENTA UN MOTOR DE ANIMACIÓN frontend con scrubber temporal.

CONVENCIONES DE COORDENADAS
- Vista cenital, eje +X = este (avance "natural" de la lectura), +Y = norte.
- Unidades: metros para posiciones, segundos para tiempos, km/h para velocidades.
- El instante t=0 es el inicio de la animación. El impacto ocurre típicamente entre t=2.5 y t=4.0 s.
- Para cada actor, su trayectoria debe tener entre 6 y 14 puntos cubriendo desde 1-2 s antes del impacto hasta la posición final post-impacto, con paso de 0,2-0,5 s.
- `rotation_deg` es el heading del actor (dirección a la que mira), 0° = +X (este), 90° = +Y (norte).

REGLAS DURAS
1. Un actor por interviniente real. Tipos válidos:
   turismo | motocicleta | bicicleta | peaton | ciclomotor | camion | autobus | mobiliario_urbano.
2. La GEOMETRÍA debe ser COHERENTE con los datos físicos ya calculados:
   - Si `simular_fisica`/`generar_frame_simulacion` fija velocidades pre/post o posiciones finales, RESPÉTALAS.
   - Si `consultar_escena` da `pendiente_pct`, anchura, num_carriles, velocidad máxima → úsalos en `via`.
   - Si `consultar_ficha_tecnica` da masa, longitud, ancho del vehículo → úsalos en el actor.
   - Si `analizar_biomecanica` da WAD y velocidad mínima por daños altos en parabrisas/techo, usa esa velocidad pre-impacto del vehículo.
3. La trayectoria del impacto: el primer actor (vehículo grande) y el segundo (peatón/ciclista) deben CRUZAR sus trayectorias en un punto que esté EN su trayectoria con un `t` cercano (margen 0,1 s).
4. Calzada estrecha urbana (<4 m, p.ej. caso IURGI): tipo "urbana_estrecha", `ancho_total_m=anchura_real`, `carriles=1`. NO inventes 4 carriles si la vía es de 3,10 m.
5. NO INVENTES posiciones ni velocidades. Si falta un dato crítico:
   - Estima razonablemente solo si tienes 1-2 anclas (ej.: con velocidad ~50 km/h y rumbo recto puedes generar la trayectoria).
   - Si no tienes ninguna ancla, añade una entrada en `falta_info` con la pregunta concreta.
6. Si solo hay un vehículo y un peatón/ciclista: incluye AMBOS como actores (no fuerces un coche B falso).
7. Pendientes: si la pendiente es ascendente para el sentido del turismo, ajusta `via.pendiente_pct` con signo + (si va en +X) o − (si va en −X). El frontend pinta un gradiente coherente.
8. Obstáculos: si la escena tiene un edificio que limita visibilidad o una zona terriza adyacente, descríbelos en `obstaculos[]` con un polígono simple de 4 puntos.
9. **EJE DE LA VÍA — CRÍTICO PARA CURVAS.** Cuando la vía NO sea recta (curva, trazado sinuoso, urbana estrecha en pendiente con curvatura, intersección con brazo curvo), DEBES rellenar `via.eje_via` con 5-12 puntos `[x, y]` que describan la LÍNEA MEDIA de la calzada. Los puntos deben:
   - Cubrir todo el rango espacial donde se mueven los actores (extiende el eje 5-15 m antes y después de las trayectorias para que la calzada no se "corte" en pantalla).
   - Estar ordenados a lo largo del sentido de circulación.
   - Ser COHERENTES con las trayectorias: el turismo y la víctima circulan POR DENTRO de la franja `±ancho_total_m/2` en torno al eje. Si el turismo gira a la derecha en una curva, el eje también gira a la derecha.
   - Para curvas suaves: 5-7 puntos. Para curvas cerradas o trazados sinuosos: 8-12 puntos.
   - Para vías rectas (`tipo: "recta"`, `tipo: "autovia"` sin curvatura), DEJA `eje_via` vacío `[]`. El frontend dibuja una recta horizontal por defecto.
   En el caso IURGI Aulestia: la vía es urbana estrecha en CURVA con pendiente, así que `eje_via` debe tener ~7-10 puntos describiendo esa curva, y el SEAT Ibiza ascendiendo y la bicicleta descendiendo siguen ese eje.

FORMATO DE SALIDA — DEVUELVE EXCLUSIVAMENTE UN OBJETO JSON, sin markdown, sin texto antes/después.

{
  "via": {
    "tipo": "urbana_estrecha"|"recta"|"curva"|"interseccion"|"autovia",
    "carriles": int, "ancho_carril_m": float, "ancho_total_m": float|null,
    "limite_kmh": int, "pendiente_pct": float|null, "superficie": str|null,
    "sentido_unico": bool|null
  },
  "actores": [
    {
      "id": "turismo_1"|"ciclista_iurgi"|"peaton_1"|...,
      "tipo": "turismo"|"bicicleta"|"peaton"|...,
      "etiqueta": "SEAT Ibiza 3526-BKL",
      "color": "#3B82F6"|null, "largo_m": float, "ancho_m": float, "masa_kg": float|null,
      "velocidad_inicial_kmh": float|null, "velocidad_impacto_kmh": float|null,
      "frena_desde_t": float|null,
      "trayectoria": [
        {"x": float, "y": float, "t": float, "v_kmh": float, "rotation_deg": float|null, "frenando": bool|null},
        ...
      ]
    }
  ],
  "impacto": {
    "x": float, "y": float, "t": float, "angulo_deg": float,
    "delta_v_por_actor": {"turismo_1": float, "ciclista_iurgi": float}
  },
  "obstaculos": [
    {"tipo": "edificio"|"zona_terriza"|..., "poligono": [[x,y],[x,y],[x,y],[x,y]],
     "altura_m": float|null, "limita_visibilidad": bool, "descripcion": str|null}
  ],
  "huellas": [
    {"actor_id": str|null, "tipo": "frenada"|"derrape"|"arrastre",
     "inicio": [x,y], "fin": [x,y], "longitud_m": float|null}
  ],
  "meta": {
    "meteo": str|null, "condicion_calzada": str|null, "visibilidad_m": float|null,
    "direccion": str|null, "lat": float|null, "lon": float|null, "es_dia": bool|null
  },
  "duracion_s": float,
  "falta_info": ["string concreto", ...],
  "descripcion": "1-2 frases describiendo la escena reconstruida"
}

Responde SOLO con el JSON. Nada más."""


_OBSTACULO_VALIDOS = {
    "edificio", "muro", "zona_terriza", "talud", "poste", "farola",
    "senal", "vegetacion", "acera", "bordillo", "quitamiedos", "barrera", "otro",
}
_OBSTACULO_ALIAS = {
    "talud_lateral": "talud", "talud_derecho": "talud", "talud_izquierdo": "talud",
    "ladera": "talud", "pendiente_lateral": "talud", "desnivel": "talud",
    "señal": "senal", "señal_trafico": "senal", "senal_trafico": "senal",
    "arbol": "vegetacion", "arboles": "vegetacion", "seto": "vegetacion",
    "arbusto": "vegetacion", "matorral": "vegetacion", "hierba": "vegetacion",
    "casa": "edificio", "vivienda": "edificio", "construccion": "edificio",
    "valla": "barrera", "guardarrail": "quitamiedos", "guardrail": "quitamiedos",
    "zona_de_tierra": "zona_terriza", "tierra": "zona_terriza",
    "arcen_terrizo": "zona_terriza", "arcen": "zona_terriza",
}

_VIA_VALIDOS = {"recta", "curva", "interseccion", "urbana_estrecha", "autovia"}
_VIA_ALIAS = {
    "rural_estrecha": "urbana_estrecha", "calle_estrecha": "urbana_estrecha",
    "calle": "urbana_estrecha", "via_urbana": "urbana_estrecha",
    "carretera": "recta", "autopista": "autovia", "cruce": "interseccion",
    "rotonda": "interseccion", "glorieta": "interseccion",
}

_ACTOR_VALIDOS = {
    "turismo", "motocicleta", "bicicleta", "peaton", "ciclomotor",
    "camion", "autobus", "mobiliario_urbano",
}
_ACTOR_ALIAS = {
    "coche": "turismo", "auto": "turismo", "vehiculo": "turismo",
    "ciclista": "bicicleta", "moto": "motocicleta",
    "peatón": "peaton", "viandante": "peaton",
    "furgoneta": "turismo", "suv": "turismo",
}


def _coerce_enum(value: str | None, validos: set[str], alias: dict[str, str], default: str) -> str:
    if not value:
        return default
    v = str(value).strip().lower()
    if v in validos:
        return v
    if v in alias:
        return alias[v]
    return default


def _normalizar_enums(data: dict) -> None:
    """Repara enums fuera del catálogo antes de validar con Pydantic."""
    via = data.get("via")
    if isinstance(via, dict):
        via["tipo"] = _coerce_enum(via.get("tipo"), _VIA_VALIDOS, _VIA_ALIAS, "recta")
    for actor in data.get("actores") or []:
        if isinstance(actor, dict):
            actor["tipo"] = _coerce_enum(actor.get("tipo"), _ACTOR_VALIDOS, _ACTOR_ALIAS, "turismo")
    for ob in data.get("obstaculos") or []:
        if isinstance(ob, dict):
            ob["tipo"] = _coerce_enum(ob.get("tipo"), _OBSTACULO_VALIDOS, _OBSTACULO_ALIAS, "otro")


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


def _resumen_evidencia(caso: Caso, datos_por_tool: dict) -> dict:
    """Compacta todo lo que sabemos del caso + lo que han producido los specialists.

    El LLM consume este dict como input. Mantenemos el formato compacto y
    en español para reducir tokens.
    """
    encargo = caso.encargo
    hechos = caso.hechos_atestado
    out: dict[str, Any] = {
        "caso_basico": {
            "fecha": caso.fecha_accidente.isoformat() if caso.fecha_accidente else None,
            "tipo_colision": caso.tipo_colision.value if caso.tipo_colision else None,
            "ubicacion": caso.ubicacion.model_dump(mode="json") if caso.ubicacion else None,
            "encargo_tipo": encargo.tipo.value if encargo else None,
            "preguntas": (encargo.preguntas if encargo else []) or [],
        },
        "vehiculos_identificacion": [
            v.model_dump(mode="json") for v in (caso.vehiculos_identificacion or [])
        ],
        "hechos_atestado": hechos.model_dump(mode="json") if hechos else None,
        "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
    }

    # Datos ya producidos por los specialists (acotados; lo grande se omite).
    interesantes = [
        "consultar_escena",
        "consultar_meteo",
        "consultar_ficha_tecnica",
        "calcular_fisica",
        "simular_fisica",                  # alias deprecado
        "generar_frame_simulacion",
        "obtener_frame_simulacion",        # alias deprecado
        "analizar_biomecanica",
        "verificar_atestado",
        "analizar_imagen_dano",
    ]
    out["datos_specialists"] = {
        nombre: _recortar(datos_por_tool[nombre])
        for nombre in interesantes
        if nombre in (datos_por_tool or {})
    }
    return out


def _recortar(value: Any, max_str: int = 600, max_list: int = 12) -> Any:
    if isinstance(value, dict):
        return {k: _recortar(v, max_str, max_list) for k, v in value.items()}
    if isinstance(value, list):
        return [_recortar(v, max_str, max_list) for v in value[:max_list]]
    if isinstance(value, str) and len(value) > max_str:
        return value[:max_str] + "…"
    return value


async def _completar_lagunas(
    caso: Caso,
    datos_por_tool: dict,
    contexto: dict,
) -> dict:
    """Si faltan datos críticos para reconstruir la escena, los pide a los
    specialists vía dispatch. Reusa la cache (no duplica trabajo del Perito).
    """
    from agents.tools import dispatch  # importación tardía para evitar ciclos

    extra: dict[str, Any] = {}

    # Escena: si el Perito no la consultó, la pedimos con la ubicación del caso.
    if "consultar_escena" not in datos_por_tool and caso.ubicacion:
        try:
            out = await dispatch(
                "consultar_escena",
                {"lat": caso.ubicacion.lat, "lon": caso.ubicacion.lon, "radio_m": 100},
                contexto=contexto,
            )
            extra["consultar_escena"] = out.get("datos", {})
        except Exception:
            pass

    # Ficha técnica: una llamada por vehículo identificado, si no la tenemos.
    if "consultar_ficha_tecnica" not in datos_por_tool:
        for v in (caso.vehiculos_identificacion or [])[:2]:
            if not v.marca or not v.modelo:
                continue
            try:
                out = await dispatch(
                    "consultar_ficha_tecnica",
                    {"marca": v.marca, "modelo": v.modelo, "anio": v.anio or 0},
                    contexto=contexto,
                )
                extra.setdefault("consultar_ficha_tecnica", {})
                extra["consultar_ficha_tecnica"][v.id] = out.get("datos", {})
            except Exception:
                pass

    return extra


def _fallback_minimo(caso: Caso, motivo: str) -> EscenaSimulacionData:
    """Escena vacía con `falta_info` para que el frontend pinte un placeholder."""
    return EscenaSimulacionData(
        falta_info=[motivo],
        descripcion="Reconstrucción no disponible — datos insuficientes.",
    )


async def reconstruir_escena(
    caso: Caso,
    datos_por_tool: dict,
    contexto: dict | None = None,
) -> dict:
    """Devuelve {datos: EscenaSimulacionData (model_dump), _log: ToolCallLog}.

    Args:
        caso: el Caso completo recibido por el Perito.
        datos_por_tool: el dict `datos_por_tool` que devolvió `coordinar()`.
        contexto: contexto lateral (caso_id, fotos, hechos, lesiones).
    """
    t0 = time.time()
    settings = get_settings()
    contexto = contexto or {}
    fuentes_log: list[str] = []

    if not settings.anthropic_api_key:
        falta = "ANTHROPIC_API_KEY no configurada — escena no reconstruida"
        return {
            "datos": _fallback_minimo(caso, falta).model_dump(mode="json"),
            "_log": ToolCallLog(
                agente="SimulationAgent",
                pregunta="reconstruir_escena",
                inputs={"caso_id": caso.id},
                resultado_resumen="error",
                falta_info=falta,
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    # 1) Completar lagunas críticas vía dispatch (cache reutilizada)
    extra = await _completar_lagunas(caso, datos_por_tool, contexto)
    if extra:
        fuentes_log.extend(f"dispatch:{k}" for k in extra.keys())
        datos_por_tool = {**datos_por_tool, **extra}

    # 2) Componer evidencia y pedir el JSON al LLM
    evidencia = _resumen_evidencia(caso, datos_por_tool)
    user_msg = (
        "Reconstruye la escena cenital animable a partir de esta evidencia:\n\n"
        f"```json\n{json.dumps(evidencia, ensure_ascii=False, indent=2)}\n```"
    )

    client = get_claude()
    raw_text: str = ""
    try:
        resp = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw_text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        )
        fuentes_log.append(f"LLM:{MODEL}")
    except APIError as e:
        # Fallback a Sonnet si Opus está caído
        try:
            resp = await client.messages.create(
                model=settings.model_sonnet,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw_text = "".join(
                getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
            )
            fuentes_log.append(f"LLM:{settings.model_sonnet}")
        except APIError as e2:
            falta = f"Error invocando LLM: {e2}"
            return {
                "datos": _fallback_minimo(caso, falta).model_dump(mode="json"),
                "_log": ToolCallLog(
                    agente="SimulationAgent",
                    pregunta="reconstruir_escena",
                    inputs={"caso_id": caso.id},
                    resultado_resumen="error",
                    fuentes_consultadas=fuentes_log,
                    falta_info=falta,
                    duracion_ms=int((time.time() - t0) * 1000),
                ),
            }

    # 3) Parsear y validar
    try:
        data = _extract_json(raw_text)
        _normalizar_enums(data)
    except Exception as e:
        falta = f"LLM devolvió JSON no parseable: {e}"
        return {
            "datos": _fallback_minimo(caso, falta).model_dump(mode="json"),
            "_log": ToolCallLog(
                agente="SimulationAgent",
                pregunta="reconstruir_escena",
                inputs={"caso_id": caso.id},
                resultado_resumen="error",
                fuentes_consultadas=fuentes_log,
                falta_info=falta,
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    try:
        escena = EscenaSimulacionData.model_validate(data)
    except ValidationError as e:
        falta = f"Escena inválida (no pasa schema Pydantic): {e}"
        return {
            "datos": _fallback_minimo(caso, falta).model_dump(mode="json"),
            "_log": ToolCallLog(
                agente="SimulationAgent",
                pregunta="reconstruir_escena",
                inputs={"caso_id": caso.id, "raw_keys": list((data or {}).keys())},
                resultado_resumen="schema_invalid",
                fuentes_consultadas=fuentes_log,
                falta_info=falta,
                duracion_ms=int((time.time() - t0) * 1000),
            ),
        }

    n_actores = len(escena.actores)
    impacto_t = escena.impacto.t if escena.impacto else None
    resumen = (
        f"Escena reconstruida: {n_actores} actor(es)"
        + (f", impacto en t={impacto_t:.2f}s" if impacto_t is not None else "")
        + f", vía {escena.via.tipo.value} ({escena.via.ancho_total_m or escena.via.ancho_carril_m * escena.via.carriles:.1f} m)."
    )

    return {
        "datos": escena.model_dump(mode="json"),
        "_log": ToolCallLog(
            agente="SimulationAgent",
            pregunta="reconstruir_escena",
            inputs={"caso_id": caso.id, "n_specialists_consultados": len(datos_por_tool)},
            resultado_resumen=resumen,
            fuentes_consultadas=fuentes_log,
            falta_info=("; ".join(escena.falta_info) if escena.falta_info else None),
            duracion_ms=int((time.time() - t0) * 1000),
        ),
    }

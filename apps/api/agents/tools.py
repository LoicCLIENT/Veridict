"""Definiciones de tools en formato Anthropic.

Cada tool corresponde a una función exportada por un specialist. El Perito
coordinador (Opus 4.7) decide a cuáles llamar y con qué inputs.
"""

from __future__ import annotations

from typing import Any

from agents.specialists import atestado as atestado_spec
from agents.specialists import escena as escena_spec
from agents.specialists import ficha as ficha_spec
from agents.specialists import legal as legal_spec
from agents.specialists import meteo as meteo_spec
from agents.specialists import simulacion as simulacion_spec


# ── Schemas de tools que se envían a Anthropic ─────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "consultar_escena",
        "description": (
            "EscenaAgent — Devuelve la geometría real de la vía en un punto: "
            "anchura, número de carriles, velocidad máxima publicada, señales "
            "cercanas (stop, ceda, semáforos, pasos peatones), si hay carril "
            "bici, pendiente del terreno y, si están disponibles, imágenes "
            "ground-level Mapillary. Usa esta tool cuando necesites caracterizar "
            "la vía, identificar limitación de velocidad, evaluar visibilidad "
            "o señales reglamentarias del lugar."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "radio_m": {"type": "integer", "default": 50,
                            "description": "Radio en metros para buscar elementos cercanos."},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "consultar_meteo",
        "description": (
            "MeteoAgent — Devuelve meteorología histórica del momento del "
            "siniestro (precipitación, temperatura, viento, estado calzada "
            "estimado, día/noche, hora de amanecer/atardecer). Fuente: "
            "Open-Meteo Archive (ECMWF ERA5). Llámala si la visibilidad, "
            "lluvia o luz es relevante para el encargo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "fecha_iso": {"type": "string",
                              "description": "Fecha+hora ISO 8601 del siniestro."},
            },
            "required": ["lat", "lon", "fecha_iso"],
        },
    },
    {
        "name": "consultar_ficha_tecnica",
        "description": (
            "FichaAgent — Ficha técnica del vehículo: masa, dimensiones, "
            "altura del parachoques y de los largueros, rigidez CRASH3 y "
            "sistemas de seguridad de serie/opcional. Llámala una vez por "
            "vehículo implicado."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "marca": {"type": "string"},
                "modelo": {"type": "string"},
                "anio": {"type": "integer"},
                "vehiculo_id": {"type": "string", "default": "A"},
            },
            "required": ["marca", "modelo"],
        },
    },
    {
        "name": "consultar_legal",
        "description": (
            "LegalAgent — Normativa aplicable al encargo, con enlace BOE/EUR-Lex "
            "y bibliografía. Filtra por tipo de encargo y opcionalmente por "
            "palabras clave (p.ej. ['airbag','antiempotramiento'])."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tipo_encargo": {
                    "type": "string",
                    "enum": ["responsabilidad_trafico", "velocidad_impacto",
                             "seguridad_pasiva", "mecanica_fallo", "atropello",
                             "cuantia_danos", "otro"],
                },
                "fecha_siniestro_iso": {"type": "string"},
                "palabras_clave": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["tipo_encargo"],
        },
    },
    {
        "name": "simular_fisica",
        "description": (
            "SimulacionAgent — Ejecuta un cálculo físico determinista. Modelos:\n"
            "- 'balance_momento_alcance': dado v_a_kmh, v_b_kmh, m_a_kg, m_b_kg → Δv, energía, frames T+0…T+N ms.\n"
            "- 'velocidad_por_huella': dado distancia_m (huella), opcional coef_friccion, pendiente_pct → velocidad mínima.\n"
            "- 'distancia_detencion': dado v_kmh, opcional coef_friccion, pendiente_pct, t_reaccion_s → distancia y tiempo de parada.\n"
            "- 'atropello_throw': dado distancia_proyeccion_m, opcional coef_friccion_peaton → velocidad mínima (Searle)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "modelo": {"type": "string",
                           "enum": ["balance_momento_alcance", "velocidad_por_huella",
                                    "distancia_detencion", "atropello_throw"]},
                "parametros": {"type": "object", "description": "Inputs específicos del modelo (ver descripción)."},
            },
            "required": ["modelo", "parametros"],
        },
    },
    {
        "name": "verificar_atestado",
        "description": (
            "AtestadoAgent — Contrasta una declaración del atestado contra una "
            "velocidad calculada. Devuelve compatibilidad ±15% y la diferencia."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "declaracion": {"type": "string"},
                "velocidad_calculada_kmh": {"type": "number"},
                "velocidad_declarada_kmh": {"type": "number"},
            },
            "required": ["velocidad_calculada_kmh", "velocidad_declarada_kmh"],
        },
    },
    {
        "name": "analizar_imagen_dano",
        "description": (
            "AtestadoAgent.vision — Pide al modelo de visión que describa una "
            "imagen de daño del vehículo o de la escena (URL pública). Útil "
            "para identificar pieza dañada, lado, altura del impacto y otros "
            "indicios objetivos. Devuelve descripción técnica."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string"},
                "contexto": {"type": "string",
                             "description": "Pista de qué buscar (p.ej. 'altura del impacto en parabrisas')."},
            },
            "required": ["image_url"],
        },
    },
]


# ── Despacho: nombre → coroutine ────────────────────────────────────────────

async def dispatch(name: str, args: dict[str, Any]) -> dict:
    """Invoca el specialist correspondiente; devuelve {datos, _log, ...}."""
    if name == "consultar_escena":
        return await escena_spec.analizar_escena(**args)
    if name == "consultar_meteo":
        return await meteo_spec.consultar_meteo(**args)
    if name == "consultar_ficha_tecnica":
        return await ficha_spec.consultar_ficha(**args)
    if name == "consultar_legal":
        return await legal_spec.consultar_legal(**args)
    if name == "simular_fisica":
        return await simulacion_spec.simular(**args)
    if name == "verificar_atestado":
        return await atestado_spec.verificar_declaraciones(**args)
    if name == "analizar_imagen_dano":
        return await atestado_spec.analizar_imagen_dano(**args)
    return {"datos": {"error": f"tool desconocida: {name}"}, "_log": None}

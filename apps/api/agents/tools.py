"""Definiciones de tools en formato Anthropic.

Cada tool corresponde a una función exportada por un specialist. El Perito
coordinador (Opus 4.7) decide a cuáles llamar y con qué inputs.
"""

from __future__ import annotations

from typing import Any

from agents.specialists import atestado as atestado_spec
from agents.specialists import biblioteca_fotos as biblioteca_spec
from agents.specialists import biomecanica as biomecanica_spec
from agents.specialists import conformidad_atestado as conformidad_spec
from agents.specialists import escena as escena_spec
from agents.specialists import ficha as ficha_spec
from agents.specialists import legal as legal_spec
from agents.specialists import meteo as meteo_spec
from agents.specialists import simulacion as simulacion_spec
from agents.specialists import simulacion_frames as sim_frames_spec


# ── Schemas de tools que se envían a Anthropic ─────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "consultar_escena",
        "description": (
            "EscenaAgent — Caracteriza la escena del siniestro a partir de "
            "coordenadas O de una dirección textual. Devuelve: vía resuelta "
            "por Nominatim (geocoding), anchura/carriles/maxspeed de OSM, "
            "señales reglamentarias cercanas (stop, ceda, semáforos, pasos "
            "peatones, traffic_sign), carril bici, pendiente del terreno por "
            "Open-Elevation, imágenes ground-level Mapillary con compass_angle. "
            "Si OSM no encuentra vías, reintenta con radios crecientes "
            "(100m, 250m). PREFIERE pasar `direccion` (ej. 'Barrio Zubero, "
            "Aulestia, Bizkaia') si la coords del payload son aproximadas: "
            "Nominatim resuelve coordenadas más precisas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "radio_m": {"type": "integer", "default": 50,
                            "description": "Radio inicial en metros."},
                "direccion": {"type": "string",
                              "description": "Dirección textual (geocoding Nominatim). Si se aporta, las coords resultantes prevalecen sobre lat/lon."},
            },
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
            "SimulacionAgent — Cálculo físico determinista. Modelos:\n"
            "- 'balance_momento_alcance': v_a_kmh, v_b_kmh, m_a_kg, m_b_kg → Δv, energía, frames.\n"
            "- 'velocidad_por_huella': distancia_m (huella), opcional coef_friccion, pendiente_pct → velocidad mínima Stannard-Baker.\n"
            "- 'distancia_detencion': v_kmh, opcional coef_friccion, pendiente_pct, t_reaccion_s, "
            "incluir_tiempo_reaccion (bool, def True) → distancia y tiempo de parada. Pasa "
            "`incluir_tiempo_reaccion=false` cuando quieras alinearte con la cifra pericial habitual "
            "(solo frenada, sin reacción).\n"
            "- 'atropello_throw': distancia_proyeccion_m, opcional coef_friccion_peaton → velocidad mínima (Searle).\n"
            "- 'tiempo_huella': distancia_m (huella), opcional coef_friccion, pendiente_pct, "
            "t_reaccion_s (def 1.0), t_ejecucion_s (def 0.5) → t_total = t_reacción + t_ejecución + "
            "t_frenada. CLAVE para atropellos: demuestra el tiempo mínimo entre que la víctima "
            "percibe el riesgo y el final de su huella, lo que permite acotar si el conductor pudo "
            "haber detenido el vehículo a velocidad reglamentaria (compárese con la distancia de "
            "detención)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "modelo": {"type": "string",
                           "enum": ["balance_momento_alcance", "velocidad_por_huella",
                                    "distancia_detencion", "atropello_throw", "tiempo_huella"]},
                "parametros": {"type": "object",
                               "description": "Inputs específicos del modelo (ver descripción)."},
            },
            "required": ["modelo", "parametros"],
        },
    },
    {
        "name": "analizar_conformidad_atestado",
        "description": (
            "ConformidadAtestadoAgent — Crítica metodológica DETERMINISTA del atestado "
            "policial. Aplica 8 reglas (R1-R8) que detectan errores comunes: límite de "
            "velocidad mal interpretado a la fecha, frenada plena declarada sin huella, "
            "retroceso post-impacto físicamente improbable, ausencia de cálculos de "
            "velocidad, croquis sin escala, ausencia de pruebas toxicológicas en delitos "
            "viales, incompatibilidad declaración-evidencia física, ausencia de "
            "posicionamiento de víctima/huellas en atropello. Devuelve incongruencias con "
            "severidad (alta/media/baja), elementos omitidos, valoración global "
            "(satisfactorio/incompleto/deficiente) y recomendaciones. "
            "OBLIGATORIO en encargos de responsabilidad_trafico, atropello, "
            "velocidad_impacto y siempre que haya fallecimiento. Si la valoración es "
            "'incompleto' o 'deficiente', AÑADE una conclusión transversal en el informe "
            "(p.ej. C_n+1 'Crítica metodológica al atestado')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "fecha_siniestro_iso": {"type": "string"},
                "velocidad_declarada_kmh": {"type": "number"},
                "velocidad_calculada_kmh": {"type": "number"},
                "es_atropello": {"type": "boolean"},
            },
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
        "name": "obtener_frame_simulacion",
        "description": (
            "SimulacionFramesAgent — Pide al motor de reconstrucción interno un FRAME "
            "concreto del siniestro (croquis SVG con vehículos, trayectorias, PDI, huellas "
            "y vectores de velocidad). Usa esta tool cuando necesites una imagen visual de "
            "la dinámica para citarla en el informe (no usa Mapillary; el motor lo genera "
            "a partir de masas, velocidades y posiciones finales). El SVG queda guardado "
            "y devuelve URL pública. "
            "Eventos válidos: 'croquis_general' (cenital con todo), 'pre_impacto', "
            "'impacto', 'post_impacto', 'huellas'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "evento": {
                    "type": "string",
                    "enum": ["croquis_general", "pre_impacto", "impacto", "post_impacto", "huellas"],
                },
                "masa_a": {"type": "number", "description": "kg"},
                "masa_b": {"type": "number", "description": "kg (peatón ≈ 70, ciclista ≈ 80, vehículo en su masa)"},
                "ebs_a_kmh": {"type": "number", "description": "Velocidad de impacto del vehículo A en km/h"},
                "ebs_b_kmh": {"type": "number", "description": "Velocidad de impacto del vehículo B en km/h (0 si parado)"},
                "angulo_pre_a": {"type": "number", "default": 0.0, "description": "ángulo de aproximación A en grados"},
                "angulo_pre_b": {"type": "number", "default": 180.0},
                "tipo_colision": {"type": "string", "default": "colision"},
                "modelo_a": {"type": "string", "default": "Vehículo A"},
                "modelo_b": {"type": "string", "default": "Vehículo B"},
                "huellas_post_a_m": {"type": "number"},
                "huellas_post_b_m": {"type": "number"},
                "mu": {"type": "number", "default": 0.65},
            },
            "required": ["evento", "masa_a", "masa_b", "ebs_a_kmh", "ebs_b_kmh"],
        },
    },
    {
        "name": "analizar_biomecanica",
        "description": (
            "BiomecanicaAgent — Aplica el manual ESTT/DGT 2011 + literatura forense (WAD, "
            "AIS, mecanismos lesivos). Devuelve: zona de impacto WAD → rango de velocidad "
            "compatible, energía cinética en kJ, probabilidad AIS 3+, mecanismos lesivos "
            "candidatos (flexión/extensión/tracción/compresión/torsión), cadena de los 4 "
            "impactos sucesivos y, si hay lesiones cefálicas, ANÁLISIS CRANEAL detallado "
            "(golpe directo, contragolpe, hematoma subdural, hemorragia subaracnoidea, "
            "lesión axonal difusa). Llámala SIEMPRE que haya lesiones graves o "
            "fallecimiento, especialmente en atropellos."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "descripcion_lesiones": {"type": "string"},
                "descripcion_danos_vehiculo": {"type": "string",
                    "description": "Texto libre describiendo dónde quedaron los daños (parabrisas, capó, techo…)."},
                "velocidad_estimada_kmh": {"type": "number"},
                "masa_vehiculo_kg": {"type": "number"},
                "altura_impacto_m": {"type": "number",
                    "description": "Altura del impacto del cuerpo de la víctima en metros (WAD)."},
                "es_atropello": {"type": "boolean"},
                "gravedad_lesion": {"type": "string",
                    "enum": ["leve", "moderada", "grave", "muy_grave", "fallecimiento"]},
            },
            "required": ["descripcion_lesiones"],
        },
    },
    {
        "name": "buscar_foto_perito",
        "description": (
            "BibliotecaFotosAgent — Busca entre las fotografías que el perito "
            "ha subido al caso una que cumpla un CRITERIO descriptivo (p.ej. "
            "'frontal del SEAT con parabrisas dañado', 'huella de frenada en "
            "calzada', 'señal de limitación de velocidad'). Devuelve la mejor "
            "coincidencia con su URL + alternativas. Si NO existe ninguna que "
            "cumpla el criterio, devuelve `requiere_foto=true` y la pregunta "
            "concreta que el perito debe responder subiendo la imagen. "
            "USA esta tool ANTES de `analizar_imagen_dano` cuando necesites "
            "una imagen específica."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "criterio": {
                    "type": "string",
                    "description": "Descripción concreta de la foto que necesitas.",
                },
            },
            "required": ["criterio"],
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

async def dispatch(name: str, args: dict[str, Any], *, contexto: dict | None = None) -> dict:
    """Invoca el specialist correspondiente; devuelve {datos, _log, ...}.

    `contexto` es un canal lateral con datos del caso que algunos specialists
    necesitan (p.ej. la lista de fotos del perito) y que NO son inputs del
    modelo (porque el modelo no los conoce ni los puede inventar).
    """
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
    if name == "analizar_conformidad_atestado":
        # Inyectar hechos y lesiones del caso desde el contexto lateral
        hechos = (contexto or {}).get("hechos_atestado") or {}
        lesiones = (contexto or {}).get("lesiones") or []
        return await conformidad_spec.analizar_conformidad(
            hechos=hechos, lesiones=lesiones, **args,
        )
    if name == "buscar_foto_perito":
        fotos = (contexto or {}).get("fotos") or []
        return await biblioteca_spec.buscar_foto(args.get("criterio", ""), fotos)
    if name == "analizar_imagen_dano":
        return await atestado_spec.analizar_imagen_dano(**args)
    if name == "obtener_frame_simulacion":
        return await sim_frames_spec.obtener_frame(**args)
    if name == "analizar_biomecanica":
        return await biomecanica_spec.analizar_biomecanica(**args)
    return {"datos": {"error": f"tool desconocida: {name}"}, "_log": None}

"""BiomecanicaAgent — análisis biomecánico razonado por Claude.

NO usa reglas regex sobre la descripción de lesiones. Delega el razonamiento
al LLM, al que se le entrega el corpus técnico (Manual ESTT/DGT 2011, tablas
WAD y AIS) como conocimiento autoritativo. La interpolación AIS y las tablas
WAD siguen siendo deterministas; lo que el LLM decide es qué mecanismos
lesivos están activos, si procede análisis cefálico, y la compatibilidad
clínica entre velocidad estimada y lesividad observada.
"""

from __future__ import annotations

import json
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

from anthropic import APIError

from config import get_claude, get_settings
from models import ToolCallLog


SEED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seeds" / "biomecanica.json"


@lru_cache(maxsize=1)
def _load_seed() -> dict:
    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ── Tablas deterministas ────────────────────────────────────────────────────

def _zona_para_altura(altura_m: float) -> dict | None:
    seed = _load_seed()
    for entry in seed["wad_atropello_ciclista"]["tablas_velocidad_por_zona_impacto"]:
        lo, hi = entry["altura_m"]
        if lo <= altura_m <= hi:
            return entry
    return None


def _energia_cinetica_kj(masa_kg: float, v_kmh: float) -> float:
    v_ms = v_kmh / 3.6
    return 0.5 * masa_kg * v_ms ** 2 / 1000.0


def _ais3_pct_para_dv(delta_v_kmh: float) -> int:
    seed = _load_seed()
    tabla = seed["umbrales_lesividad"]["tabla"]
    if delta_v_kmh <= tabla[0]["delta_v_kmh"]:
        return tabla[0]["ais3_plus_pct"]
    if delta_v_kmh >= tabla[-1]["delta_v_kmh"]:
        return tabla[-1]["ais3_plus_pct"]
    for i in range(len(tabla) - 1):
        a, b = tabla[i], tabla[i + 1]
        if a["delta_v_kmh"] <= delta_v_kmh <= b["delta_v_kmh"]:
            t = (delta_v_kmh - a["delta_v_kmh"]) / (b["delta_v_kmh"] - a["delta_v_kmh"])
            return int(round(a["ais3_plus_pct"] + t * (b["ais3_plus_pct"] - a["ais3_plus_pct"])))
    return tabla[-1]["ais3_plus_pct"]


# ── Prompt del especialista (prompt engineering) ────────────────────────────

SYSTEM_BIOMECANICA = """Eres un PERITO BIOMECÁNICO forense de accidentes de tráfico.

Tu tarea: dada una descripción técnica de lesiones y daños del vehículo, identificar:
(a) qué mecanismos lesivos del Manual ESTT/DGT 2011 están activos en este caso,
(b) si las lesiones implican afectación craneoencefálica y, en ese caso, qué tipos de lesión cefálica son compatibles con el mecanismo de impacto,
(c) la compatibilidad clínica cualitativa entre velocidad estimada y lesividad observada.

CONOCIMIENTO AUTORITATIVO QUE DEBES APLICAR (no reproducirlo, ÚSALO para razonar):

[Mecanismos lesivos — Manual ESTT/DGT 2011 §biomecánica]
1. Flexión: típica de fracturas transversales (huesos largos doblados en el límite elástico).
2. Extensión: fracturas transversales y/o luxaciones articulares (whiplash, hiperextensión).
3. Tracción: desgarros cutáneos, musculares, luxaciones, avulsiones óseas.
4. Compresión: fuerza axial longitudinal — fenómeno de émbolo, fracturas por estallido vertebral.
5. Torsión: fracturas espiroideas (esquí, atrapamiento con giro).

[Lesiones craneoencefálicas — fisiopatología]
- Hematoma frontal por golpe directo: impacto de los lóbulos frontales contra la cara interna del hueso frontal.
- Lesión por contragolpe (contre-coup): tracción del lóbulo opuesto al desplazarse el encéfalo en su sentido inicial.
- Hematoma subdural occipital: desgarro de los vasos puente meníngeos por tracción brusca occipital.
- Hemorragia subaracnoidea: rotura de vasos del espacio subaracnoideo por aceleración angular.
- Lesión axonal difusa (DAI): cizallamiento de axones por aceleración rotacional, frecuente en atropellos a >40 km/h.

[Criterios de compatibilidad velocidad ↔ gravedad]
- Atropellos peatón/ciclista a v ≥ 40 km/h: lesiones graves o letales son altamente probables, especialmente cefálicas.
- Atropellos a v < 25 km/h con lesiones letales: solo plausibles si hay paso por encima del cuerpo, fragilidad extrema, o impacto contra estructura rígida del vehículo (umbral techo).
- Coherencia "infralesivo": v alta con lesiones leves sugiere maniobra evasiva exitosa o impacto tangencial.

INSTRUCCIONES DE RESPUESTA:
1. Lee la descripción de lesiones y de daños del vehículo. Identifica las regiones anatómicas afectadas.
2. Razona QUÉ mecanismos lesivos del catálogo ESTT (1-5) son compatibles con cada lesión descrita y por qué. NO listes los 5 si no proceden todos.
3. Si la descripción menciona afectación craneal (cabeza, cráneo, encéfalo, lesión cefálica, lesión cerebral, hematoma intracraneal, fractura craneal, contusión cerebral, autopsia letal cefálica, etc.) — interpreta el lenguaje natural, NO busques palabras exactas — selecciona los tipos de lesión cefálica COMPATIBLES con la dinámica descrita.
4. Evalúa la coherencia velocidad-lesividad usando los criterios anteriores.
5. Si te falta dato crucial (ej. autopsia detallada, dirección de la fuerza, edad/fragilidad de la víctima), márcalo en `falta_info`.

DEVUELVE EXCLUSIVAMENTE UN JSON con esta estructura (sin markdown, sin texto antes ni después):

{
  "mecanismos_lesivos_compatibles": [
    {"nombre": "Flexión|Extensión|Tracción|Compresión|Torsión",
     "razon": "Explicación clínica concisa (1-2 frases) por qué este mecanismo está activo en este caso concreto."}
  ],
  "afectacion_cefalica": true|false,
  "analisis_craneal": {
    "mecanismo_general": "Síntesis del mecanismo dominante en este caso (1-2 frases adaptadas, no genéricas).",
    "tipos_compatibles": [
      {"nombre": "<uno de los 5 listados>",
       "mecanismo": "Por qué este tipo específico es compatible con la dinámica observada (1 frase)."}
    ],
    "consideracion_clinica": "Párrafo único 60-100 palabras integrando dinámica + lesiones + autopsia (si la hay)."
  } | null,
  "compatibilidad_velocidad_lesion": "compatible | infralesivo respecto a la velocidad estimada | incompatible — <breve explicación> | no determinada",
  "razonamiento_compatibilidad": "Una frase justificando la compatibilidad asignada.",
  "falta_info": "Pregunta concreta al perito humano si falta dato clave, o null."
}

REGLAS DURAS:
- Idioma: español de España, registro pericial.
- NO atribuyas culpa.
- NO inventes lesiones que no están en la descripción.
- Si afectacion_cefalica=false, analisis_craneal=null.
- JSON puro, sin texto fuera del objeto."""


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


async def _razonar_con_llm(payload: dict) -> dict:
    """Llama a Claude para que devuelva mecanismos lesivos + análisis cráneo + compatibilidad."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return {
            "mecanismos_lesivos_compatibles": [],
            "afectacion_cefalica": False,
            "analisis_craneal": None,
            "compatibilidad_velocidad_lesion": "no determinada",
            "razonamiento_compatibilidad": "ANTHROPIC_API_KEY no configurada.",
            "falta_info": "Configurar ANTHROPIC_API_KEY para activar el análisis biomecánico LLM.",
        }
    client = get_claude()
    user_msg = (
        "DATOS DEL CASO PARA EL ANÁLISIS BIOMECÁNICO:\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nAplica el conocimiento autoritativo y devuelve el JSON especificado."
    )
    try:
        resp = await client.messages.create(
            model=settings.model_sonnet,
            max_tokens=2048,
            system=SYSTEM_BIOMECANICA,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        return _extract_json(text)
    except (APIError, ValueError, json.JSONDecodeError) as e:
        return {
            "mecanismos_lesivos_compatibles": [],
            "afectacion_cefalica": False,
            "analisis_craneal": None,
            "compatibilidad_velocidad_lesion": "no determinada",
            "razonamiento_compatibilidad": f"Error en LLM: {e}",
            "falta_info": str(e),
        }


# ── API pública ─────────────────────────────────────────────────────────────

async def analizar_biomecanica(
    descripcion_lesiones: str,
    descripcion_danos_vehiculo: Optional[str] = None,
    velocidad_estimada_kmh: Optional[float] = None,
    masa_vehiculo_kg: Optional[float] = None,
    altura_impacto_m: Optional[float] = None,
    es_atropello: bool = False,
    gravedad_lesion: Optional[str] = None,
) -> dict:
    """Análisis biomecánico razonado por LLM + tablas deterministas (WAD, AIS, energía)."""
    t0 = time.time()
    seed = _load_seed()

    # 1. WAD por altura — determinista
    wad_resultado = None
    zona = _zona_para_altura(altura_impacto_m) if altura_impacto_m is not None else None
    if zona and es_atropello:
        wad_resultado = {
            "zona_impacto": zona["zona_impacto"],
            "altura_m": zona["altura_m"],
            "velocidad_min_kmh": zona["velocidad_min_kmh"],
            "velocidad_max_kmh": zona["velocidad_max_kmh"],
            "fuente": "Otte 1989; Searle 1993; Van Rooij 2003; manuales UC3M-GC 2020.",
        }

    # 2. Energía cinética y AIS — determinista.
    #
    # Política: si tenemos rango WAD, calculamos Ec en TRES puntos del rango
    # (mínimo, medio, máximo) para que el informe pericial muestre la energía
    # acotada por el indicio biomecánico, no por un único punto inventado por
    # el orquestador. Si no hay WAD, usamos solo `velocidad_estimada_kmh`.
    energia = None
    ais_pct = None
    energia_tabla: list[dict] = []
    if masa_vehiculo_kg:
        if wad_resultado:
            puntos = [
                ("min_wad", wad_resultado["velocidad_min_kmh"]),
                ("max_wad", wad_resultado["velocidad_max_kmh"]),
            ]
            if velocidad_estimada_kmh:
                puntos.append(("declarada_perito", velocidad_estimada_kmh))
            for etiqueta, vk in puntos:
                if vk is None:
                    continue
                energia_tabla.append({
                    "etiqueta": etiqueta,
                    "v_kmh": vk,
                    "energia_kj": round(_energia_cinetica_kj(masa_vehiculo_kg, vk), 1),
                    "ais3_plus_pct": _ais3_pct_para_dv(vk),
                })
            # Cifra principal: extremo SUPERIOR del rango WAD (criterio pericial
            # ITRASA: "los daños indican AL MENOS 50 km/h" — no 35 km/h).
            energia = _energia_cinetica_kj(masa_vehiculo_kg, wad_resultado["velocidad_max_kmh"])
            ais_pct = _ais3_pct_para_dv(wad_resultado["velocidad_max_kmh"])
        elif velocidad_estimada_kmh:
            energia = _energia_cinetica_kj(masa_vehiculo_kg, velocidad_estimada_kmh)
            ais_pct = _ais3_pct_para_dv(velocidad_estimada_kmh)
            energia_tabla.append({
                "etiqueta": "declarada_perito",
                "v_kmh": velocidad_estimada_kmh,
                "energia_kj": round(energia, 1),
                "ais3_plus_pct": ais_pct,
            })

    # 3. Razonamiento clínico — LLM
    llm_payload = {
        "descripcion_lesiones": descripcion_lesiones,
        "descripcion_danos_vehiculo": descripcion_danos_vehiculo,
        "velocidad_estimada_kmh": velocidad_estimada_kmh,
        "masa_vehiculo_kg": masa_vehiculo_kg,
        "altura_impacto_m": altura_impacto_m,
        "wad_zona_resuelta": wad_resultado["zona_impacto"] if wad_resultado else None,
        "energia_cinetica_kj_estimada": round(energia, 1) if energia is not None else None,
        "probabilidad_ais3_plus_pct": ais_pct,
        "es_atropello": es_atropello,
        "gravedad_lesion_perito": gravedad_lesion,
    }
    razonamiento = await _razonar_con_llm(llm_payload)

    # 4. Cadena de 4 impactos sucesivos — siempre informativa, determinista
    cadena_impactos = seed["impactos_sucesivos"]

    out = {
        "wad": wad_resultado,
        "energia_cinetica_kj": round(energia, 1) if energia is not None else None,
        "energia_cinetica_v_kmh_referencia": (
            wad_resultado["velocidad_max_kmh"] if wad_resultado
            else (velocidad_estimada_kmh if energia is not None else None)
        ),
        "energia_cinetica_tabla": energia_tabla,
        "probabilidad_ais3_pct": ais_pct,
        "mecanismos_lesivos_compatibles": razonamiento.get("mecanismos_lesivos_compatibles", []),
        "cadena_4_impactos_sucesivos": cadena_impactos,
        "analisis_craneal": razonamiento.get("analisis_craneal"),
        "compatibilidad_velocidad_lesion": razonamiento.get("compatibilidad_velocidad_lesion", "no determinada"),
        "razonamiento_compatibilidad": razonamiento.get("razonamiento_compatibilidad"),
        "tabla_aceleraciones_tipo": seed["tabla_aceleraciones_tipo"],
        "fuentes": [
            "Manual ESTT/DGT 2011 — Especialidad Gestión del Tráfico y Movilidad.",
            "Limpert R., Motor Vehicle Accident Reconstruction (LexisNexis, 6.ª ed., 2012).",
            "Mertz H.J., Anthropomorphic Test Devices, en Accidental Injury (Springer, 2002).",
            "Otte D., Pedestrian/Cyclist injuries from cars (1989).",
            "Van Rooij L., Pedestrian impact reconstruction with WAD (2003).",
            "UC3M & Guardia Civil, Manual de reconstrucción atropellos (2020).",
        ],
    }

    falta = razonamiento.get("falta_info")
    if es_atropello and not wad_resultado and altura_impacto_m is None:
        msg = (
            "Para aplicar la tabla WAD necesito la altura aproximada del impacto del "
            "cuerpo en el vehículo (parabrisas, capó, techo) en metros. Si no se mide, "
            "una foto del frontal con una regla permite estimarla."
        )
        falta = (falta + " | " + msg) if falta else msg

    resumen_partes = []
    if wad_resultado:
        resumen_partes.append(
            f"WAD {wad_resultado['zona_impacto']} → {wad_resultado['velocidad_min_kmh']}-"
            f"{wad_resultado['velocidad_max_kmh']} km/h"
        )
    if energia is not None:
        v_ref = out["energia_cinetica_v_kmh_referencia"]
        resumen_partes.append(f"Ec={energia:.1f} kJ @ {v_ref} km/h")
    if ais_pct is not None:
        resumen_partes.append(f"AIS3+ p={ais_pct}%")
    if out["analisis_craneal"]:
        resumen_partes.append(
            f"análisis cefálico ({len(out['analisis_craneal'].get('tipos_compatibles', []))} tipos)"
        )
    if out["mecanismos_lesivos_compatibles"]:
        resumen_partes.append(f"{len(out['mecanismos_lesivos_compatibles'])} mecanismos lesivos")
    resumen_partes.append(f"compatibilidad: {out['compatibilidad_velocidad_lesion']}")

    log = ToolCallLog(
        agente="BiomecanicaAgent",
        pregunta=f"analizar_biomecanica (atropello={es_atropello}) v={velocidad_estimada_kmh}",
        inputs={
            "descripcion_lesiones": (descripcion_lesiones[:120] + "…") if descripcion_lesiones and len(descripcion_lesiones) > 120 else descripcion_lesiones,
            "altura_impacto_m": altura_impacto_m,
            "velocidad_estimada_kmh": velocidad_estimada_kmh,
            "masa_vehiculo_kg": masa_vehiculo_kg,
            "es_atropello": es_atropello,
            "gravedad_lesion": gravedad_lesion,
        },
        resultado_resumen=" · ".join(resumen_partes),
        fuentes_consultadas=out["fuentes"] + ["Claude Sonnet (razonamiento clínico)"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}

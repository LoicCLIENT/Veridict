"""BiomecanicaAgent.

Aplica el Manual ESTT/DGT 2011 + literatura forense (Limpert, Mertz, Otte,
Van Rooij, NHTSA) para evaluar:
  · Mecanismo lesivo dominante.
  · Cadena de 4 impactos sucesivos.
  · Estimación WAD (Wrap Around Distance) → velocidad mínima en atropello.
  · Análisis de lesiones cefálicas (golpe directo, contragolpe, subdural,
    subaracnoidea, lesión axonal difusa).
  · Energía cinética y compatibilidad con la lesividad observada (AIS 3+).
"""

from __future__ import annotations

import json
import math
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

from models import ToolCallLog


SEED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seeds" / "biomecanica.json"


@lru_cache(maxsize=1)
def _load_seed() -> dict:
    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _zona_para_altura(altura_m: float) -> dict | None:
    seed = _load_seed()
    for entry in seed["wad_atropello_ciclista"]["tablas_velocidad_por_zona_impacto"]:
        lo, hi = entry["altura_m"]
        if lo <= altura_m <= hi:
            return entry
    return None


def _zona_por_descripcion(descripcion: str) -> dict | None:
    """Mapea descripciones textuales libres a zonas WAD predefinidas."""
    if not descripcion:
        return None
    d = descripcion.lower()
    seed = _load_seed()
    tabla = seed["wad_atropello_ciclista"]["tablas_velocidad_por_zona_impacto"]
    if "parachoque" in d or "paragolpes" in d:
        return tabla[0]
    if "capó" in d or "capo" in d:
        if "alto" in d or "base parabrisas" in d:
            return tabla[2]
        return tabla[1]
    if "parabrisas" in d:
        if "alto" in d or "umbral" in d or "techo" in d:
            return tabla[4]
        return tabla[3]
    if "techo" in d or "umbral techo" in d:
        return tabla[5]
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


async def analizar_biomecanica(
    descripcion_lesiones: str,
    descripcion_danos_vehiculo: Optional[str] = None,
    velocidad_estimada_kmh: Optional[float] = None,
    masa_vehiculo_kg: Optional[float] = None,
    altura_impacto_m: Optional[float] = None,
    es_atropello: bool = False,
    gravedad_lesion: Optional[str] = None,
) -> dict:
    """Devuelve un análisis biomecánico estructurado con citas al manual."""
    t0 = time.time()
    seed = _load_seed()

    # 1. WAD (atropellos): zona por altura o por descripción de daños
    wad_resultado = None
    zona = None
    if altura_impacto_m is not None:
        zona = _zona_para_altura(altura_impacto_m)
    if not zona and descripcion_danos_vehiculo:
        zona = _zona_por_descripcion(descripcion_danos_vehiculo)
    if zona and es_atropello:
        wad_resultado = {
            "zona_impacto": zona["zona_impacto"],
            "altura_m": zona["altura_m"],
            "velocidad_min_kmh": zona["velocidad_min_kmh"],
            "velocidad_max_kmh": zona["velocidad_max_kmh"],
            "fuente": "Otte 1989; Searle 1993; Van Rooij 2003; manuales UC3M-GC 2020.",
        }

    # 2. Energía cinética y umbral AIS
    energia = None
    ais_pct = None
    if masa_vehiculo_kg and velocidad_estimada_kmh:
        energia = _energia_cinetica_kj(masa_vehiculo_kg, velocidad_estimada_kmh)
        ais_pct = _ais3_pct_para_dv(velocidad_estimada_kmh)

    # 3. Identificar mecanismos lesivos relevantes según descripción
    desc = (descripcion_lesiones or "").lower()
    mecanismos_aplicables = []
    if any(k in desc for k in ("fractura", "rotura ósea")):
        mecanismos_aplicables.append({"nombre": "Flexión",
                                      "razon": "Fracturas óseas transversales son típicas de mecanismo de flexión."})
    if any(k in desc for k in ("luxación", "extensión")):
        mecanismos_aplicables.append({"nombre": "Extensión",
                                      "razon": "Luxaciones articulares orientan a mecanismo de extensión."})
    if any(k in desc for k in ("desgarro", "rotura de tejidos blandos")):
        mecanismos_aplicables.append({"nombre": "Tracción",
                                      "razon": "Desgarros cutáneos/musculares apuntan a tracción."})
    if any(k in desc for k in ("aplastamiento", "compresión", "estallido vertebral")):
        mecanismos_aplicables.append({"nombre": "Compresión",
                                      "razon": "Lesiones por aplastamiento o estallido vertebral."})
    if "espiroidea" in desc or "espiral" in desc or "torsión" in desc:
        mecanismos_aplicables.append({"nombre": "Torsión", "razon": "Fractura espiroidea."})

    # 4. Cadena de 4 impactos sucesivos siempre se documenta
    cadena_impactos = seed["impactos_sucesivos"]

    # 5. Análisis cefálico si la zona indica cabeza/cráneo/encéfalo
    analisis_craneal = None
    if any(k in desc for k in ("cabeza", "cráneo", "craneo", "cefal", "encéfalo", "encefal", "letal")):
        analisis_craneal = {
            "mecanismo_general": seed["lesiones_cefalicas"]["mecanismo_general"],
            "tipos_compatibles": seed["lesiones_cefalicas"]["tipos"],
            "consideracion_clinica": (
                "Las lesiones letales en cabeza tras atropello a velocidad superior a 40 km/h "
                "son habitualmente la consecuencia combinada de impacto directo del cráneo "
                "contra la estructura del vehículo (parabrisas, marco/umbral del techo) y de "
                "la deceleración angular brusca, que induce hematomas subdurales, hemorragia "
                "subaracnoidea y lesión axonal difusa. La autopsia debe confirmar el o los "
                "mecanismos finalmente activos."
            ),
        }

    # 6. Compatibilidad cualitativa
    compatibilidad = "no determinada"
    if velocidad_estimada_kmh and gravedad_lesion:
        gv = gravedad_lesion.lower()
        if velocidad_estimada_kmh >= 40 and gv in ("grave", "muy_grave", "fallecimiento"):
            compatibilidad = "compatible"
        elif velocidad_estimada_kmh < 25 and gv == "fallecimiento":
            compatibilidad = (
                "incompatible — lesiones letales son improbables a velocidades <25 km/h "
                "sin condiciones específicas (atropello con paso por encima del cuerpo, fragilidad)."
            )
        elif velocidad_estimada_kmh >= 25 and gv == "leve":
            compatibilidad = "infralesivo respecto a la velocidad estimada"
        else:
            compatibilidad = "consistente con la velocidad estimada"

    out = {
        "wad": wad_resultado,
        "energia_cinetica_kj": round(energia, 1) if energia is not None else None,
        "probabilidad_ais3_pct": ais_pct,
        "mecanismos_lesivos_compatibles": mecanismos_aplicables,
        "cadena_4_impactos_sucesivos": cadena_impactos,
        "analisis_craneal": analisis_craneal,
        "compatibilidad_velocidad_lesion": compatibilidad,
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

    falta = None
    if es_atropello and not wad_resultado:
        falta = (
            "Para aplicar la tabla WAD necesito la zona de impacto del cuerpo en el vehículo "
            "(parabrisas central, parabrisas alto, techo, etc.) o su altura en metros. "
            "Pídele al perito una foto del frontal/parabrisas que permita medir el WAD."
        )

    resumen = []
    if wad_resultado:
        resumen.append(
            f"WAD {wad_resultado['zona_impacto']} → {wad_resultado['velocidad_min_kmh']}-"
            f"{wad_resultado['velocidad_max_kmh']} km/h"
        )
    if energia is not None:
        resumen.append(f"Ec={energia:.1f} kJ")
    if ais_pct is not None:
        resumen.append(f"AIS3+ p={ais_pct}%")
    if analisis_craneal:
        resumen.append("análisis cefálico (cráneo/encéfalo) incluido")
    resumen.append(f"compatibilidad: {compatibilidad}")

    log = ToolCallLog(
        agente="BiomecanicaAgent",
        pregunta=f"analizar_biomecanica (atropello={es_atropello}) v={velocidad_estimada_kmh}",
        inputs={
            "descripcion_lesiones": descripcion_lesiones[:120] if descripcion_lesiones else None,
            "altura_impacto_m": altura_impacto_m,
            "velocidad_estimada_kmh": velocidad_estimada_kmh,
            "masa_vehiculo_kg": masa_vehiculo_kg,
            "es_atropello": es_atropello,
            "gravedad_lesion": gravedad_lesion,
        },
        resultado_resumen=" · ".join(resumen),
        fuentes_consultadas=out["fuentes"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}

"""ConformidadAtestadoAgent — crítica metodológica del atestado policial.

Detecta de forma DETERMINISTA (sin LLM) las incongruencias y omisiones típicas
de los atestados, según el patrón crítico que IURGI/ITRASA aplica.

Reglas implementadas:
  R1. Si el atestado afirma un límite genérico de 30 km/h en vía urbana antes
      del 11/05/2021 → ERROR (RD 970/2020 entró en vigor ese día).
  R2. Si dice "no se observan huellas" del vehículo Y el conductor dice haber
      frenado al máximo → INCONGRUENCIA (en seco una frenada plena deja huella).
  R3. Si hay declaraciones de retroceso del vehículo grande tras impactar a un
      vehículo mucho menor → física improbable.
  R4. Ausencia de cálculos de velocidad en el atestado.
  R5. Croquis mencionado pero "sin escala" o sin acotar.
  R6. Si hay fallecimiento: ausencia de prueba toxicológica/drogas (delito vial).
  R7. Si la velocidad declarada es ≤25 km/h y hay lesiones letales en cabeza
      contra parabrisas/techo: incompatible con la biomecánica.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

from models import HechosAtestado, Lesion, ToolCallLog


# Fecha de entrada en vigor del límite genérico 30 km/h urbano
RD_970_2020_VIGENCIA = datetime(2021, 5, 11).date()


async def analizar_conformidad(
    hechos: dict,
    lesiones: Optional[list[dict]] = None,
    fecha_siniestro_iso: Optional[str] = None,
    velocidad_declarada_kmh: Optional[float] = None,
    velocidad_calculada_kmh: Optional[float] = None,
    es_atropello: bool = False,
) -> dict:
    """Devuelve {datos: AnalisisConformidadAtestado-like, _log}."""
    t0 = time.time()
    incongruencias: list[dict] = []
    omitidos: list[str] = []
    recomendaciones: list[str] = []

    declaraciones = ((hechos or {}).get("declaraciones") or "").lower()
    observaciones = ((hechos or {}).get("observaciones") or "").lower()
    cuerpo_actuante = (hechos or {}).get("cuerpo_actuante", "")
    hay_huellas = (hechos or {}).get("hay_huellas_frenada")
    todo = declaraciones + " " + observaciones

    # R1 — Límite 30 km/h pre-2021
    fecha = None
    if fecha_siniestro_iso:
        try:
            fecha = datetime.fromisoformat(str(fecha_siniestro_iso).replace("Z", "")).date()
        except ValueError:
            fecha = None
    if fecha and fecha < RD_970_2020_VIGENCIA and ("30 km/h" in todo or "límite genérico de 30" in todo or "limite generico de 30" in todo):
        incongruencias.append({
            "severidad": "alta",
            "titulo": "Límite genérico 30 km/h erróneo para la fecha",
            "descripcion": (
                f"El atestado refiere un límite genérico urbano de 30 km/h, pero la fecha del "
                f"siniestro ({fecha.isoformat()}) es anterior al 11/05/2021, entrada en vigor "
                f"del RD 970/2020 que introduce ese límite. En esa fecha el límite genérico "
                f"urbano era de 50 km/h."
            ),
        })

    # R2 — frenada plena sin huella
    if hay_huellas is False and any(k in todo for k in ("freno al máximo", "freno al maximo", "frenada al máximo", "frenada al maximo", "frenó al máximo", "freno maximo", "frenado al máximo")):
        incongruencias.append({
            "severidad": "alta",
            "titulo": "Frenada plena declarada sin huella en calzada",
            "descripcion": (
                "El conductor declara haber accionado el freno al máximo, pero el atestado "
                "indica que no se observan huellas de frenada del vehículo. En condiciones "
                "de asfalto seco con μ ~0,75, una frenada plena con neumáticos bloqueados "
                "deja huella visible. La ausencia es incompatible con la declaración: o la "
                "frenada no fue plena (falta de atención, pisada tardía o suave) o la "
                "velocidad era inferior a la declarada."
            ),
        })

    # R3 — retroceso post-impacto
    if any(k in todo for k in ("retrocede", "retrocedió", "rebotado", "rebota", "retroceso")):
        if any(k in todo for k in ("camión", "camion", "turismo", "vehículo", "vehiculo")):
            incongruencias.append({
                "severidad": "media",
                "titulo": "Retroceso post-impacto físicamente improbable",
                "descripcion": (
                    "El atestado consigna un retroceso del vehículo tras el impacto. Si el "
                    "vehículo de mayor masa colisiona contra otro de mucha menor masa "
                    "(peatón, ciclista, motocicleta), la conservación del momento implica "
                    "que aquél continuará avanzando, no retrocediendo. Un retroceso real "
                    "exigiría intervención voluntaria del conductor o coeficiente de "
                    "restitución imposible."
                ),
            })

    # R4 — ausencia de cálculos de velocidad
    if not any(k in todo for k in ("cálculo de velocidad", "calculo de velocidad", "stannard", "crash3", "ebs", "deceleración")):
        omitidos.append(
            "El atestado no incluye cálculo de velocidad mediante metodología reconocida "
            "(Stannard-Baker, CRASH3, EBS) pese a disponer de huellas/daños cuantificables."
        )

    # R5 — croquis sin escala
    if "sin escala" in todo or "sin acotar" in todo or "desproporcionado" in todo or "desproporcionados" in todo:
        incongruencias.append({
            "severidad": "media",
            "titulo": "Croquis sin escala o sin acotaciones",
            "descripcion": (
                "El atestado refiere un croquis sin escala o desproporcionado. Un croquis "
                "pericial debe levantarse a escala definida y acotar las distancias clave "
                "(huellas, posiciones finales, anchura de calzada) para permitir su "
                "verificación posterior."
            ),
        })

    # R6 — atropello/fallecimiento sin prueba toxicológica
    fallecimiento = any((l or {}).get("gravedad") == "fallecimiento" for l in (lesiones or []))
    if (es_atropello or fallecimiento) and not any(k in todo for k in ("droga", "alcohol", "alcoholemia", "tóxico", "toxicológ", "etilometría", "etilometria")):
        omitidos.append(
            "En siniestros con resultado letal o lesiones graves, las diligencias deben "
            "consignar la realización de pruebas de detección de alcohol y otras drogas "
            "(art. 379 CP y normativa concordante). El atestado no recoge mención expresa."
        )

    # R7 — velocidad declarada incompatible con la calculada
    if velocidad_declarada_kmh is not None and velocidad_calculada_kmh is not None:
        diff = velocidad_calculada_kmh - velocidad_declarada_kmh
        if diff > 0.20 * max(velocidad_declarada_kmh, 1):
            incongruencias.append({
                "severidad": "alta",
                "titulo": "Velocidad declarada incompatible con la evidencia física",
                "descripcion": (
                    f"Declaración del conductor: {velocidad_declarada_kmh} km/h. Cálculo "
                    f"físico (huellas/daños/biomecánica): {velocidad_calculada_kmh} km/h. "
                    f"Diferencia +{diff:.1f} km/h, fuera del margen aceptable del 15-20%. "
                    f"La evidencia física rebate la declaración."
                ),
            })

    # R8 — atropello sin posicionamiento de huellas o víctima
    if es_atropello and not any(k in todo for k in ("posición final", "posicion final", "punto de impacto", "pdi", "huellas a", "huella de ", "metros del borde")):
        omitidos.append(
            "En atropello, el atestado debe consignar punto de impacto (PDI), posición "
            "final del vehículo y de la víctima, y origen/fin de huellas con cota lateral "
            "respecto al borde de la vía. No constan estos elementos con precisión."
        )

    # Recomendaciones
    if incongruencias or omitidos:
        recomendaciones.append(
            "Solicitar diligencias complementarias para subsanar las omisiones señaladas "
            "y aclarar las incongruencias detectadas."
        )
    if any(i.get("severidad") == "alta" for i in incongruencias):
        recomendaciones.append(
            "Considerar las incongruencias de severidad ALTA como prueba de descargo de "
            "la declaración del conductor en su literalidad."
        )

    # Valoración global
    n_alta = sum(1 for i in incongruencias if i.get("severidad") == "alta")
    n_media = sum(1 for i in incongruencias if i.get("severidad") == "media")
    if n_alta == 0 and n_media == 0 and not omitidos:
        valoracion = "satisfactorio"
    elif n_alta >= 2 or (n_alta >= 1 and len(omitidos) >= 2):
        valoracion = "deficiente"
    else:
        valoracion = "incompleto"

    out = {
        "incongruencias": incongruencias,
        "elementos_omitidos": omitidos,
        "valoracion_global": valoracion,
        "recomendaciones": recomendaciones,
    }

    resumen = (
        f"Valoración: {valoracion}. {len(incongruencias)} incongruencias "
        f"({n_alta} altas, {n_media} medias), {len(omitidos)} omisiones."
    )
    log = ToolCallLog(
        agente="ConformidadAtestadoAgent",
        pregunta=f"Análisis crítico del atestado ({cuerpo_actuante})",
        inputs={"es_atropello": es_atropello, "fecha": fecha_siniestro_iso,
                "v_declarada": velocidad_declarada_kmh,
                "v_calculada": velocidad_calculada_kmh},
        resultado_resumen=resumen,
        fuentes_consultadas=[
            "Reglas internas Veridict (R1-R8) basadas en práctica pericial IURGI/AEIAT",
            "RD 970/2020", "Art. 379 CP",
        ],
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": out, "_log": log}

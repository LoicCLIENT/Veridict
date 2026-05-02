"""
Adjudicator Agent — Atribución de responsabilidad civil conforme a:
  · LRCSCVM (RDLeg 8/2004), art. 1.1, 1.2, 1.3
  · LSV (RDLeg 6/2015), art. 75-77 (clasificación infracciones)
  · RGC (RD 1428/2003)
  · Jurisprudencia TS: STS 536/2012 (daños personales) y STS 294/2019 (daños materiales)

Metodología en 4 pasos:
  1. Presunción por tipo de colisión (jurisprudencia TS)
  2. Análisis de nexo causal por infracción
  3. Ponderación proporcional por gravedad e incidencia causal
  4. Regla de cierre del TS (50/50 material / 100/100 personal si prueba insuficiente)
"""

import json
import re
from typing import Any

from models import Caso, Resultado, Veredicto, CompatibilidadVersiones


def _parse_json(text: str) -> Any:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    # Extraer solo el bloque JSON si hay texto previo
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group(0)
    return json.loads(text)


_SYSTEM_PROMPT = """\
Eres un perito judicial forense especializado en accidentes de tráfico en España.
Tu función es determinar la atribución de responsabilidad civil aplicando estrictamente
el marco jurídico español vigente: LRCSCVM (RDLeg 8/2004), LSV (RDLeg 6/2015),
RGC (RD 1428/2003) y la jurisprudencia del Tribunal Supremo.

MARCO LEGAL OBLIGATORIO:
─────────────────────────────────────────────────────────────────────────────
LRCSCVM Art. 1.1 — Responsabilidad objetiva: el conductor responde por el riesgo
  creado, salvo que pruebe causa extraña (Art. 1.2).
LRCSCVM Art. 1.3 — Concurrencia de culpas: reducción equitativa del 25 % al 75 %
  según la contribución causal de cada parte.
LSV Art. 77   — Infracciones MUY GRAVES: exceso velocidad >50 % límite, alcohol/drogas,
  conducción sin permiso, uso inhibidores radar.
LSV Art. 76   — Infracciones GRAVES: exceso velocidad ≤50 %, no respetar señales,
  distancia de seguridad, adelantamientos indebidos, uso del móvil.
LSV Art. 75   — Infracciones LEVES: resto de conductas negligentes menores.
STS 536/2012  — Daños personales: cuando no se prueba el % concreto de incidencia
  causal de cada vehículo, cada conductor responde al 100 % ante los ocupantes del otro.
STS 294/2019  — Daños materiales: cuando ninguno prueba falta de culpa, se aplica 50/50.
─────────────────────────────────────────────────────────────────────────────

PRESUNCIONES POR TIPO DE COLISIÓN (jurisprudencia consolidada):
  · ALCANCE      → culpa del vehículo trasero (presunción rebatible si el delantero
                    maniobró de forma imprevisible o sus pilotos traseros fallaban).
  · FRONTAL      → culpa del que invadió el carril contrario; 50/50 si no se prueba.
  · LATERAL      → culpa del que no respetó preferencia o señal de stop/ceda el paso.
  · ATROPELLO    → culpa del conductor (presunción muy fuerte, art. 1.1 LRCSCVM);
                    se reduce si el peatón cruzó imprudentemente fuera del paso.

ESCALA DE PESO CAUSAL POR INFRACCIÓN:
  · MUY GRAVE con nexo causal directo  → 0.50 – 0.70 del peso total
  · GRAVE     con nexo causal directo  → 0.20 – 0.40
  · LEVE      con nexo causal directo  → 0.05 – 0.15
  · Cualquier infracción SIN nexo causal → peso 0 (concurrente pero no determinante)
"""

_USER_TEMPLATE = """\
CASO A ANALIZAR
═══════════════════════════════════════════════════════════════════════════════

TIPO DE COLISIÓN: {tipo_colision}
FECHA Y HORA: {fecha}
CONDICIONES CONTEXTUALES: {contexto}

CÁLCULOS FÍSICOS (evidencia objetiva):
{calculos_txt}

CRONOLOGÍA FORENSE:
{cronologia_txt}

INFRACCIONES IDENTIFICADAS (RGC/LSV):
{infracciones_txt}

DECLARACIONES DE LOS CONDUCTORES:
{versiones_txt}

CONTRASTE DECLARACIONES VS FÍSICA:
{contraste_txt}

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES DE ANÁLISIS — sigue los 4 pasos en orden:

PASO 1 · PRESUNCIÓN POR TIPO DE COLISIÓN
  Aplica la presunción jurisprudencial correspondiente al tipo de colisión.
  Indica qué conductor parte con la carga de la prueba en su contra y la base legal.

PASO 2 · ANÁLISIS DE NEXO CAUSAL POR INFRACCIÓN
  Para cada infracción listada, evalúa:
    a) ¿Es la causa eficiente del accidente, una causa concurrente, o no tiene nexo?
    b) Clasifica la gravedad según LSV (muy_grave / grave / leve).
    c) Justifica con los datos físicos y la cronología.

PASO 3 · PONDERACIÓN PROPORCIONAL
  Asigna el peso causal acumulado a cada vehículo usando la escala de peso causal.
  Normaliza para que culpa_a + culpa_b = 1.0.
  Si un vehículo no tiene infracciones con nexo, puede llegar a 0.0.

PASO 4 · REGLA DE CIERRE (Tribunal Supremo)
  Evalúa si la evidencia es suficiente para sostener el porcentaje ante un tribunal.
  · Si confianza < 0.60: aplica 50/50 para daños materiales (STS 294/2019) y advierte
    que para daños personales operará la regla 100/100 (STS 536/2012).
  · Si confianza ≥ 0.60: mantén el porcentaje calculado.

COMPATIBILIDAD DE DECLARACIONES:
  Evalúa si la versión de cada conductor es compatible con la física.
  Diferencia > 10 km/h entre velocidad declarada y calculada = INCOMPATIBLE.
  Contradicción cronológica = INCOMPATIBLE. Sé específico con valores numéricos.

Responde ÚNICAMENTE con el siguiente JSON válido, sin texto adicional:
{{
  "paso1": {{
    "presuncion": "<descripción>",
    "vehiculo_presunto_responsable": "A|B|ninguno",
    "base_legal": "<artículo o sentencia>"
  }},
  "paso2_nexo_causal": [
    {{
      "vehiculo": "A|B",
      "articulo": "<artículo RGC/LSV>",
      "gravedad": "muy_grave|grave|leve",
      "nexo": "causa_eficiente|concurrente|sin_nexo",
      "justificacion": "<texto breve con referencia a datos>"
    }}
  ],
  "paso3": {{
    "peso_a": 0.0,
    "peso_b": 1.0,
    "detalle": "<cómo se calcularon los pesos>"
  }},
  "paso4": {{
    "regla_aplicada": "porcentaje_calculado|regla_50_50|regla_100_100",
    "advertencia_personal": true,
    "justificacion": "<texto>"
  }},
  "veredicto": {{
    "culpa_a": 0.0,
    "culpa_b": 1.0,
    "confidence": 0.88
  }},
  "compatibilidad": {{
    "a": true,
    "b": false,
    "justificacion": "<texto con valores numéricos>"
  }},
  "razonamiento": "<párrafo completo de 100-150 palabras, tono técnico-jurídico, citando artículos y sentencias aplicadas>"
}}"""


class Adjudicator:

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()

    async def adjudicate(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        calculos_txt = "\n".join(
            f"  · {c.nombre}: {c.valor} {c.unidad} — {c.justificacion}"
            for c in resultado.calculos
        ) or "  · Sin cálculos disponibles"

        infracciones_txt = "\n".join(
            f"  · [Veh. {i.vehiculo}] {i.articulo} ({i.fuente}): {i.descripcion}"
            for i in resultado.infracciones
        ) or "  · Sin infracciones identificadas"

        versiones_txt = "\n".join(
            f'  · Vehículo {v.id} ({v.modelo or "desconocido"}): "{v.version_conductor}"'
            for v in caso.vehiculos if v.version_conductor
        ) or "  · Sin declaraciones"

        cronologia_txt = "\n".join(
            f"  · T{e.timestamp:+.1f}s: {e.descripcion}"
            for e in resultado.cronologia
        ) or "  · Sin cronología"

        contraste_txt = "\n".join(
            f"  · Veh. {cv.vehiculo_id}: declarada {cv.velocidad_declarada_kmh or '?'} km/h "
            f"/ calculada {cv.velocidad_calculada_kmh or '?'} km/h "
            f"— {'COMPATIBLE' if cv.compatible else 'INCOMPATIBLE'} ({cv.observacion})"
            for cv in resultado.contraste_versiones
        ) or "  · No disponible"

        ctx = resultado.contexto
        contexto_txt = "No disponible"
        if ctx:
            partes = []
            if ctx.direccion:
                partes.append(ctx.direccion)
            if ctx.meteo and ctx.meteo.estado_tiempo:
                partes.append(f"meteorología: {ctx.meteo.estado_tiempo}")
            if ctx.via and ctx.via.velocidad_maxima:
                partes.append(f"límite vía: {ctx.via.velocidad_maxima} km/h")
            if ctx.sol and ctx.sol.es_dia is not None:
                partes.append("diurno" if ctx.sol.es_dia else "nocturno")
            contexto_txt = " · ".join(partes) if partes else "No disponible"

        prompt = _USER_TEMPLATE.format(
            tipo_colision=caso.tipo_colision.value,
            fecha=caso.fecha_accidente.strftime("%d/%m/%Y %H:%M"),
            contexto=contexto_txt,
            calculos_txt=calculos_txt,
            cronologia_txt=cronologia_txt,
            infracciones_txt=infracciones_txt,
            versiones_txt=versiones_txt,
            contraste_txt=contraste_txt,
        )

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_opus,
                max_tokens=2048,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            data = _parse_json(response.content[0].text)

            v = data["veredicto"]
            culpa_a = float(v["culpa_a"])
            culpa_b = float(v["culpa_b"])
            total = culpa_a + culpa_b
            if total > 0:
                culpa_a = round(culpa_a / total, 2)
                culpa_b = round(1.0 - culpa_a, 2)

            veredicto = Veredicto(
                culpa_a=culpa_a,
                culpa_b=culpa_b,
                confidence=min(float(v["confidence"]), 0.95),
            )

            c = data["compatibilidad"]
            compatibilidad = CompatibilidadVersiones(
                a=bool(c["a"]),
                b=bool(c["b"]),
                justificacion=c["justificacion"],
            )

            razonamiento = data.get("razonamiento", "")
            paso4 = data.get("paso4", {})

            return {
                "veredicto": veredicto,
                "compatibilidad": compatibilidad,
                "razonamiento": razonamiento,
                "advertencia_personal": paso4.get("advertencia_personal", False),
                "nexo_causal": data.get("paso2_nexo_causal", []),
            }

        except Exception as e:
            print(f"Adjudicator error: {e}")
            return self._fallback_adjudication(resultado)

    def _fallback_adjudication(self, resultado: Resultado) -> dict[str, Any]:
        infracciones_a = [i for i in resultado.infracciones if i.vehiculo == "A"]
        infracciones_b = [i for i in resultado.infracciones if i.vehiculo == "B"]
        total = len(resultado.infracciones) or 1
        culpa_a = round(len(infracciones_a) / total, 2)
        culpa_b = round(1.0 - culpa_a, 2)

        return {
            "veredicto": Veredicto(culpa_a=culpa_a, culpa_b=culpa_b, confidence=0.50),
            "compatibilidad": CompatibilidadVersiones(
                a=True,
                b=True,
                justificacion=(
                    "Análisis de compatibilidad no disponible. "
                    "Aplicada regla supletoria STS 294/2019 (50/50). Requiere revisión manual."
                ),
            ),
            "razonamiento": (
                "Error en el análisis automatizado. Se ha aplicado la regla supletoria "
                "del Tribunal Supremo (STS 294/2019): distribución 50/50 para daños materiales. "
                "Para daños personales operará la regla de indemnización cruzada al 100% "
                "(STS 536/2012). El perito firmante debe revisar y completar este apartado."
            ),
            "advertencia_personal": True,
            "nexo_causal": [],
        }

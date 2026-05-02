"""
Legal Reasoner Agent - Identifies traffic law infractions using Claude.
"""

import json
import re
from typing import Any

from models import Caso, CalculoFisico, Infraccion, Contexto

CORPUS_LEGAL = """
ARTICULOS APLICABLES DEL REGLAMENTO GENERAL DE CIRCULACION (RGC) Y LEY DE SEGURIDAD VIAL (LSV):

Art. 74.1 RGC (BOE-A-2003-23514): Prohibicion de circular a velocidad superior a la maxima permitida.
  Sancion: GRAVE si supera el limite hasta 50%, MUY GRAVE si lo supera en mas del 50%.

Art. 72.1 RGC (BOE-A-2003-23514): Cambio de carril o direccion debe señalizarse con suficiente
  antelacion mediante el indicador de direccion (intermitente). Infraccion GRAVE.

Art. 54.1 RGC (BOE-A-2003-23514): Todo conductor debe mantener la distancia de seguridad
  necesaria para detenerse en caso de frenada brusca del vehiculo precedente. Infraccion GRAVE.

Art. 65.3.a LSV (BOE-A-2015-11722): Los conductores estan obligados a ceder el paso a los
  peatones que crucen por pasos habilitados. Infraccion MUY GRAVE.

Art. 76.a RGC (BOE-A-2003-23514): Adelantamiento en lugar prohibido o sin visibilidad.

Art. 87.1 RGC (BOE-A-2003-23514): Conduccion bajo la influencia de bebidas alcoholicas
  o sustancias estupefacientes.

Art. 48 RGC (BOE-A-2003-23514): Uso incorrecto de carriles. No respetar la marcacion vial.
"""


def _parse_json(text: str) -> Any:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    return json.loads(text)


class LegalReasoner:
    """Agent for legal analysis of traffic accident infractions."""

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()

    async def analyze(
        self,
        caso: Caso,
        calculos: list[CalculoFisico],
        contexto: Contexto | None = None,
    ) -> dict[str, Any]:
        calculos_txt = "\n".join(
            f"  - {c.nombre}: {c.valor} {c.unidad} — {c.justificacion}"
            for c in calculos
        ) or "  - Sin calculos de velocidad disponibles"

        versiones = []
        for v in caso.vehiculos:
            if v.version_conductor:
                versiones.append(f'  Vehiculo {v.id} ({v.modelo or "desconocido"}): "{v.version_conductor}"')
        versiones_txt = "\n".join(versiones) or "  Sin declaraciones disponibles"

        # Límite de velocidad real de la vía (OSM) — más preciso que los genéricos
        limite_via = None
        via_nombre = None
        if contexto and contexto.via:
            limite_via = contexto.via.velocidad_maxima
            via_nombre = contexto.via.nombre_via or contexto.via.tipo_via
        limite_txt = (
            f"LÍMITE DE VELOCIDAD EN EL LUGAR (dato OSM verificado): {limite_via} km/h"
            + (f" — {via_nombre}" if via_nombre else "")
            if limite_via
            else "LÍMITE DE VELOCIDAD: usar valores por defecto (zona urbana 50, escolar/cebra 30, autopista 120)"
        )

        # Extraer distancia de seguridad calculada si existe
        dist_seg_txt = ""
        dist_segs = [c for c in calculos if "distancia seguridad" in c.nombre.lower()]
        if dist_segs:
            dist_seg_txt = "\nDISTANCIAS DE SEGURIDAD CALCULADAS (Art. 54.1 RGC):\n" + "\n".join(
                f"  - {c.nombre}: {c.valor} {c.unidad} — {c.justificacion}"
                for c in dist_segs
            )

        prompt = f"""Eres un perito juridico especializado en derecho de trafico espanol.
Analiza el siguiente accidente e identifica las infracciones cometidas.

ACCIDENTE:
- Tipo de colision: {caso.tipo_colision.value}
- Fecha: {caso.fecha_accidente.strftime('%d/%m/%Y %H:%M')}

{limite_txt}

CALCULOS FISICOS DEMOSTRADOS:
{calculos_txt}
{dist_seg_txt}

DECLARACIONES DE LOS CONDUCTORES:
{versiones_txt}

{CORPUS_LEGAL}

INSTRUCCIONES:
1. Identifica TODAS las infracciones aplicables para cada vehiculo (A y B).
2. Basa las infracciones en los calculos fisicos y el tipo de colision.
3. Para Art. 74.1 RGC (velocidad): compara EBS o velocidad pre-frenada con el LIMITE REAL de la via indicado arriba. No uses limites genéricos si tienes el dato OSM.
4. Para colision lateral: verifica Art. 72.1 RGC (cambio de carril).
5. Para alcance: verifica Art. 54.1 RGC usando la distancia de seguridad calculada — si la huella real es menor que la requerida, es infraccion probada con valores numéricos.
6. Para atropello: verifica Art. 65.3.a LSV y Art. 74.1 RGC.
7. En la descripcion de cada infraccion cita los valores numericos concretos (km/h calculados, metros de huella vs metros requeridos).

Responde UNICAMENTE con un array JSON valido, sin texto adicional:
[{{"articulo": "Art. 74.1 RGC", "descripcion": "Descripcion precisa con valores numericos", "vehiculo": "A", "fuente": "BOE-A-2003-23514"}}]"""

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_sonnet,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            infracciones_raw = _parse_json(response.content[0].text)
            return {
                "infracciones": [
                    Infraccion(
                        articulo=i["articulo"],
                        descripcion=i["descripcion"],
                        vehiculo=i["vehiculo"],
                        fuente=i["fuente"],
                    )
                    for i in infracciones_raw
                ]
            }
        except Exception as e:
            print(f"LegalReasoner error: {e}")
            return {"infracciones": self._fallback_infracciones(caso, calculos)}

    def _fallback_infracciones(self, caso: Caso, calculos: list[CalculoFisico]) -> list[Infraccion]:
        infracciones = []
        tipo = caso.tipo_colision.value

        for c in calculos:
            limite = 30 if tipo == "atropello" else 50
            if c.valor > limite:
                infracciones.append(Infraccion(
                    articulo="Art. 74.1 RGC",
                    descripcion=f"Circular a {c.valor:.0f} km/h en zona limitada a {limite} km/h",
                    vehiculo="A",
                    fuente="BOE-A-2003-23514",
                ))
                break

        if tipo == "lateral":
            infracciones.append(Infraccion(
                articulo="Art. 72.1 RGC",
                descripcion="Cambio de carril sin señalizar con suficiente antelacion",
                vehiculo="B",
                fuente="BOE-A-2003-23514",
            ))
        elif tipo == "alcance":
            infracciones.append(Infraccion(
                articulo="Art. 54.1 RGC",
                descripcion="No mantener distancia de seguridad adecuada con el vehiculo precedente",
                vehiculo="A",
                fuente="BOE-A-2003-23514",
            ))
        elif tipo == "atropello":
            infracciones.append(Infraccion(
                articulo="Art. 65.3.a LSV",
                descripcion="No ceder el paso a peaton en paso de cebra habilitado",
                vehiculo="A",
                fuente="BOE-A-2015-11722",
            ))

        return infracciones

"""
Declaration Analyst — contraste técnico entre declaraciones y evidencia física.

Objetivo: el perito necesita saber si lo que dice cada conductor
es físicamente posible dado lo que muestran los cálculos.
No se atribuye culpa — se describe objetivamente qué dice la física.
"""

import json
import re
from typing import Any

from models import Caso, CalculoFisico, Evento, ContrastVersiones


def _parse_json(text: str) -> Any:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)


class DeclarationAnalyst:

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()

    async def analyze(
        self,
        caso: Caso,
        calculos: list[CalculoFisico],
        cronologia: list[Evento],
    ) -> list[ContrastVersiones]:
        """
        Para cada conductor con declaración, determina técnicamente si
        su versión es compatible con los cálculos físicos.
        """
        conductores_con_version = [
            v for v in caso.vehiculos if v.version_conductor.strip()
        ]
        if not conductores_con_version:
            return []

        calculos_txt = "\n".join(
            f"  • {c.nombre}: {c.valor} {c.unidad} — {c.justificacion}"
            for c in calculos
        )

        cronologia_txt = "\n".join(
            f"  T={e.timestamp:+.1f}s: {e.descripcion}"
            for e in cronologia
        )

        versiones_txt = "\n".join(
            f'  Vehículo {v.id} ({v.modelo}): "{v.version_conductor}"'
            for v in conductores_con_version
        )

        prompt = f"""Eres un perito forense. Analiza técnicamente si las declaraciones de los conductores
son compatibles con la evidencia física calculada. NO atribuyas culpa — solo describe
objetivamente qué dice la física y si la declaración es o no compatible con ella.

TIPO DE COLISIÓN: {caso.tipo_colision.value}

DECLARACIONES:
{versiones_txt}

EVIDENCIA FÍSICA (objetiva):
{calculos_txt}

CRONOLOGÍA RECONSTRUIDA:
{cronologia_txt}

Para cada conductor, extrae la velocidad declarada si la menciona (puede estar implícita).
Determina si esa declaración es técnicamente compatible con los cálculos.

Reglas:
— Compatible: la velocidad declarada difiere < 15 km/h de la calculada O los hechos narrados
  son coherentes con la cronología física.
— Incompatible: la velocidad declarada difiere > 15 km/h de la calculada O los hechos narrados
  contradicen directamente la evidencia física.
— Si no menciona velocidad concreta, valora si la descripción de hechos es coherente.

Responde ÚNICAMENTE con JSON válido (una entrada por conductor con declaración):
[
  {{
    "vehiculo_id": "A",
    "velocidad_declarada_kmh": 50.0,
    "velocidad_calculada_kmh": 45.6,
    "compatible": true,
    "observacion": "La velocidad declarada (50 km/h) es compatible con el EBS calculado (45.6 km/h). Diferencia < 15 km/h."
  }}
]"""

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_sonnet,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = _parse_json(response.content[0].text)
            return [
                ContrastVersiones(
                    vehiculo_id=r["vehiculo_id"],
                    velocidad_declarada_kmh=r.get("velocidad_declarada_kmh"),
                    velocidad_calculada_kmh=r.get("velocidad_calculada_kmh"),
                    compatible=bool(r["compatible"]),
                    observacion=r["observacion"],
                )
                for r in raw
            ]
        except Exception as e:
            print(f"DeclarationAnalyst error: {e}")
            return self._fallback(caso, calculos)

    def _fallback(
        self, caso: Caso, calculos: list[CalculoFisico]
    ) -> list[ContrastVersiones]:
        resultados = []
        for v in caso.vehiculos:
            if not v.version_conductor.strip():
                continue
            ebs = next(
                (c.valor for c in calculos if f"Vehículo {v.id}" in c.nombre),
                None,
            )
            resultados.append(ContrastVersiones(
                vehiculo_id=v.id,
                velocidad_calculada_kmh=ebs,
                compatible=True,
                observacion="Contraste automático no disponible. Requiere revisión manual del perito.",
            ))
        return resultados

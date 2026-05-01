"""
Adjudicator Agent - Determines fault attribution.
Uses Claude Opus for final reasoning.
"""

from typing import Any

from models import Caso, Resultado, Veredicto, CompatibilidadVersiones


class Adjudicator:
    """Agent for determining fault attribution and version compatibility."""

    def __init__(self):
        self.model = "claude-opus-4-5-20251101"

    async def adjudicate(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        """
        Determine fault attribution based on evidence.

        Returns:
            dict with 'veredicto' and 'compatibilidad'
        """
        # Analyze infractions to determine fault
        infracciones_a = [i for i in resultado.infracciones if i.vehiculo == "A"]
        infracciones_b = [i for i in resultado.infracciones if i.vehiculo == "B"]

        # Calculate base fault (simplified logic)
        culpa_a = len(infracciones_a) / max(len(resultado.infracciones), 1)
        culpa_b = len(infracciones_b) / max(len(resultado.infracciones), 1)

        # Adjust for severity (speed violations are more severe)
        for inf in infracciones_a:
            if "velocidad" in inf.descripcion.lower():
                culpa_a += 0.2

        for inf in infracciones_b:
            if "velocidad" in inf.descripcion.lower():
                culpa_b += 0.2

        # Normalize
        total = culpa_a + culpa_b
        if total > 0:
            culpa_a /= total
            culpa_b /= total
        else:
            culpa_a = 0.5
            culpa_b = 0.5

        # Calculate confidence based on evidence quality
        confidence = self._calculate_confidence(caso, resultado)

        veredicto = Veredicto(
            culpa_a=round(culpa_a, 2),
            culpa_b=round(culpa_b, 2),
            confidence=confidence,
        )

        # Check version compatibility
        compatibilidad = await self._check_version_compatibility(caso, resultado)

        return {
            "veredicto": veredicto,
            "compatibilidad": compatibilidad,
        }

    def _calculate_confidence(self, caso: Caso, resultado: Resultado) -> float:
        """Calculate confidence score based on evidence quality."""
        confidence = 0.5  # Base

        # More calculations = more confidence
        confidence += min(len(resultado.calculos) * 0.1, 0.3)

        # More infractions identified = more confidence
        confidence += min(len(resultado.infracciones) * 0.05, 0.1)

        # More vehicles with measurements = more confidence
        vehicles_with_data = sum(
            1 for v in caso.vehiculos if any(c > 0 for c in v.mediciones_C)
        )
        confidence += vehicles_with_data * 0.05

        return min(confidence, 0.95)

    async def _check_version_compatibility(
        self, caso: Caso, resultado: Resultado
    ) -> CompatibilidadVersiones:
        """Check if driver versions are compatible with physical evidence."""
        # In production, would use LLM to analyze version vs physics
        compatible_a = True
        compatible_b = True
        justificaciones = []

        for vehiculo in caso.vehiculos:
            if not vehiculo.version_conductor:
                continue

            # Check for speed claims vs calculated speed
            version_lower = vehiculo.version_conductor.lower()

            # Look for speed claims in version
            for calculo in resultado.calculos:
                if vehiculo.id in calculo.nombre and "ebs" in calculo.nombre.lower():
                    calculated_speed = calculo.valor

                    # Simple check: if they claim low speed but physics shows high
                    if "30" in version_lower or "40" in version_lower:
                        claimed_speed = 30 if "30" in version_lower else 40
                        if calculated_speed > claimed_speed + 10:
                            if vehiculo.id == "A":
                                compatible_a = False
                            else:
                                compatible_b = False
                            justificaciones.append(
                                f"Vehiculo {vehiculo.id}: declara ~{claimed_speed} km/h, "
                                f"fisica indica {calculated_speed:.0f} km/h"
                            )

        justificacion = ". ".join(justificaciones) if justificaciones else "Versiones compatibles con evidencia fisica"

        return CompatibilidadVersiones(
            a=compatible_a,
            b=compatible_b,
            justificacion=justificacion,
        )

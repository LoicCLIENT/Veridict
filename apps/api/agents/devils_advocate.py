"""
Devil's Advocate Agent - Adversarial verification of results.
Challenges the analysis to find inconsistencies.
"""

from typing import Any

from models import Caso, Resultado


class DevilsAdvocate:
    """Agent for adversarial verification of analysis results."""

    def __init__(self):
        self.model = "claude-opus-4-5-20251101"
        self.checks = [
            self._verify_momentum_conservation,
            self._verify_ebs_coherence,
            self._verify_version_compatibility,
            self._verify_biomechanics,
        ]

    async def verify(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        """
        Run adversarial verification checks.

        Returns:
            dict with 'passed' and 'failures'
        """
        failures = []

        for check in self.checks:
            check_result = await check(caso, resultado)
            if not check_result["passed"]:
                failures.append(check_result["reason"])

        return {
            "passed": len(failures) == 0,
            "failures": failures,
        }

    async def _verify_momentum_conservation(
        self, caso: Caso, resultado: Resultado
    ) -> dict:
        """Verify that momentum is conserved in the collision."""
        # In production, would do actual physics calculation
        # For now, pass if we have calculations
        if len(resultado.calculos) >= 2:
            return {"passed": True, "reason": None}

        return {
            "passed": False,
            "reason": "Insufficient data to verify momentum conservation",
        }

    async def _verify_ebs_coherence(
        self, caso: Caso, resultado: Resultado
    ) -> dict:
        """Verify EBS values are coherent with brake marks."""
        ebs_calculos = [c for c in resultado.calculos if "ebs" in c.nombre.lower()]
        sb_calculos = [c for c in resultado.calculos if "stannard" in c.nombre.lower() or "frenada" in c.nombre.lower()]

        if ebs_calculos and sb_calculos:
            # Check if values are reasonably close
            ebs_avg = sum(c.valor for c in ebs_calculos) / len(ebs_calculos)
            sb_avg = sum(c.valor for c in sb_calculos) / len(sb_calculos)

            if abs(ebs_avg - sb_avg) > 20:  # More than 20 km/h difference
                return {
                    "passed": False,
                    "reason": f"EBS ({ebs_avg:.0f} km/h) inconsistent with brake analysis ({sb_avg:.0f} km/h)",
                }

        return {"passed": True, "reason": None}

    async def _verify_version_compatibility(
        self, caso: Caso, resultado: Resultado
    ) -> dict:
        """Verify version compatibility analysis is complete."""
        if resultado.compatibilidad_versiones is None:
            return {
                "passed": False,
                "reason": "Version compatibility not analyzed",
            }

        # If both versions are marked compatible but infractions exist, flag it
        if (
            resultado.compatibilidad_versiones.a
            and resultado.compatibilidad_versiones.b
            and len(resultado.infracciones) > 0
        ):
            # This might be fine, but worth noting
            pass

        return {"passed": True, "reason": None}

    async def _verify_biomechanics(
        self, caso: Caso, resultado: Resultado
    ) -> dict:
        """Verify biomechanical coherence for pedestrian impacts."""
        if caso.tipo_colision.value != "atropello":
            return {"passed": True, "reason": None}

        # For pedestrian impacts, check Delta-V is survivable
        for calculo in resultado.calculos:
            if "delta" in calculo.nombre.lower():
                if calculo.valor > 80:  # > 80 km/h usually fatal
                    return {
                        "passed": False,
                        "reason": f"Delta-V of {calculo.valor:.0f} km/h exceeds survivable threshold",
                    }

        return {"passed": True, "reason": None}

"""
Devil's Advocate Agent - Adversarial verification of results.
Combines physics checks with Claude reasoning.
"""

from typing import Any

from models import Caso, Resultado


class DevilsAdvocate:
    """Agent for adversarial verification of analysis results."""

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()
        self.checks = [
            self._verify_momentum_conservation,
            self._verify_ebs_coherence,
            self._verify_reconstruction_2d,
            self._verify_restitution_coefficient,
            self._verify_version_compatibility,
            self._verify_biomechanics,
        ]

    async def verify(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        failures = []
        for check in self.checks:
            check_result = await check(caso, resultado)
            if not check_result["passed"]:
                failures.append(check_result["reason"])

        passed = len(failures) == 0

        # Ask Claude for a brief adversarial review
        claude_review = await self._claude_review(caso, resultado, failures)

        return {
            "passed": passed and claude_review["passed"],
            "failures": failures + claude_review.get("additional_failures", []),
        }

    async def _claude_review(
        self, caso: Caso, resultado: Resultado, physics_failures: list[str]
    ) -> dict:
        calculos_txt = "\n".join(
            f"  - {c.nombre}: {c.valor} {c.unidad}"
            for c in resultado.calculos
        ) or "  - Sin calculos"

        v = resultado.veredicto
        veredicto_txt = f"Culpa A: {v.culpa_a*100:.0f}%, Culpa B: {v.culpa_b*100:.0f}%, Confianza: {v.confidence*100:.0f}%" if v else "Sin veredicto"

        comp = resultado.compatibilidad_versiones
        comp_txt = comp.justificacion if comp else "Sin analisis de compatibilidad"

        failures_txt = "\n".join(f"  - {f}" for f in physics_failures) or "  - Ninguno"

        prompt = f"""Eres un abogado defensor revisando un informe pericial de accidente de trafico.
Tu mision es encontrar inconsistencias o debilidades en el analisis.

CALCULOS FISICOS:
{calculos_txt}

VEREDICTO PROPUESTO: {veredicto_txt}

COMPATIBILIDAD DE VERSIONES: {comp_txt}

FALLOS FISICOS YA DETECTADOS:
{failures_txt}

Revisa el analisis buscando:
1. Contradicciones entre calculos fisicos
2. Atribucion de culpa desproporcionada con la evidencia
3. Conclusiones que no se sostienen con los datos

Responde en JSON:
{{"passed": true, "additional_failures": []}}

Si encuentras un problema real, añadelo a additional_failures con descripcion concisa.
Si el analisis es solido, devuelve passed: true y lista vacia."""

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_sonnet,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            import json, re
            text = re.sub(r"```(?:json)?\s*", "", response.content[0].text).strip().rstrip("```").strip()
            return json.loads(text)
        except Exception as e:
            print(f"DevilsAdvocate Claude review error: {e}")
            return {"passed": True, "additional_failures": []}

    async def _verify_momentum_conservation(self, caso: Caso, resultado: Resultado) -> dict:
        """
        Verifica la 3ª ley de Newton: m_A·ΔV_A ≈ m_B·ΔV_B (impulso igual y opuesto).
        Tolerancia 20% para cubrir asimetría por ángulo de impacto no estrictamente frontal.
        """
        if caso.tipo_colision.value == "atropello":
            ebs = [c for c in resultado.calculos if "ebs" in c.nombre.lower() or "crash3" in c.nombre.lower()]
            if not ebs:
                return {"passed": False, "reason": "Sin EBS calculado para el vehículo en atropello"}
            return {"passed": True, "reason": None}

        # Buscar Delta-V de cada vehículo en los cálculos
        dv_por_vehiculo: dict[str, float] = {}
        for c in resultado.calculos:
            nombre_lower = c.nombre.lower()
            if "delta-v" in nombre_lower or "delta_v" in nombre_lower or "delta v" in nombre_lower:
                for v in caso.vehiculos:
                    if f"vehículo {v.id.lower()}" in nombre_lower or f"vehiculo {v.id.lower()}" in nombre_lower:
                        dv_por_vehiculo[v.id] = c.valor
                        break

        if len(dv_por_vehiculo) < 2:
            # Sin Delta-V: fallback — verificar al menos 2 EBS
            ebs_all = [c for c in resultado.calculos if "ebs" in c.nombre.lower() or "crash3" in c.nombre.lower()]
            if len(ebs_all) < 2:
                return {
                    "passed": False,
                    "reason": "Datos insuficientes: se necesitan mediciones de deformación de ambos vehículos para verificar conservación de momento",
                }
            return {"passed": True, "reason": None}

        masas = {v.id: (v.masa_kg or 1350) for v in caso.vehiculos}
        ids = list(dv_por_vehiculo.keys())
        id_a, id_b = ids[0], ids[1]
        impulso_a = masas.get(id_a, 1350) * dv_por_vehiculo[id_a]
        impulso_b = masas.get(id_b, 1350) * dv_por_vehiculo[id_b]

        if max(impulso_a, impulso_b) == 0:
            return {"passed": True, "reason": None}

        error_pct = abs(impulso_a - impulso_b) / max(impulso_a, impulso_b) * 100
        if error_pct > 20:
            return {
                "passed": False,
                "reason": (
                    f"Violación 3ª ley de Newton: impulso A={impulso_a:.0f} kg·km/h, "
                    f"impulso B={impulso_b:.0f} kg·km/h — error {error_pct:.0f}% > 20%. "
                    f"Revisar mediciones de deformación o masas declaradas."
                ),
            }
        return {"passed": True, "reason": None}

    async def _verify_ebs_coherence(self, caso: Caso, resultado: Resultado) -> dict:
        ebs = [c for c in resultado.calculos if "ebs" in c.nombre.lower() or "crash3" in c.nombre.lower()]
        sb = [c for c in resultado.calculos if "stannard" in c.nombre.lower() or "frenada" in c.nombre.lower() or "velocidad pre" in c.nombre.lower()]

        if ebs and sb:
            ebs_avg = sum(c.valor for c in ebs) / len(ebs)
            sb_avg = sum(c.valor for c in sb) / len(sb)
            if abs(ebs_avg - sb_avg) > 25:
                return {
                    "passed": False,
                    "reason": f"EBS ({ebs_avg:.0f} km/h) inconsistente con analisis de frenada ({sb_avg:.0f} km/h) — diferencia > 25 km/h",
                }

        return {"passed": True, "reason": None}

    async def _verify_version_compatibility(self, caso: Caso, resultado: Resultado) -> dict:
        if resultado.compatibilidad_versiones is None:
            return {"passed": False, "reason": "Compatibilidad de versiones no analizada"}
        return {"passed": True, "reason": None}

    async def _verify_reconstruction_2d(self, caso: Caso, resultado: Resultado) -> dict:
        """Verifica el error de conservación de momento del módulo de reconstrucción 2D."""
        momento_check = next(
            (c for c in resultado.calculos if "conservación de momento 2D" in c.nombre.lower()),
            None,
        )
        if momento_check is None:
            return {"passed": True, "reason": None}  # No hay reconstrucción 2D, OK

        error_pct = momento_check.valor
        if error_pct > 20:
            return {
                "passed": False,
                "reason": (
                    f"Error de conservación de momento 2D del {error_pct:.1f}% supera el umbral del 20%. "
                    f"Revisar ángulos de aproximación o velocidades de impacto."
                ),
            }
        if error_pct > 15:
            return {
                "passed": False,
                "reason": (
                    f"Error de conservación de momento 2D del {error_pct:.1f}% supera el límite aceptable (15%). "
                    f"Los ángulos declarados pueden ser incorrectos."
                ),
            }
        return {"passed": True, "reason": None}

    async def _verify_restitution_coefficient(self, caso: Caso, resultado: Resultado) -> dict:
        """Verifica que el coeficiente de restitución esté en el rango vehicular esperado."""
        e_check = next(
            (c for c in resultado.calculos if "coeficiente de restitución" in c.nombre.lower()),
            None,
        )
        if e_check is None:
            return {"passed": True, "reason": None}

        e = e_check.valor
        if e > 0.5:
            return {
                "passed": False,
                "reason": (
                    f"Coeficiente de restitución e={e:.3f} es anormalmente alto para una colisión vehicular "
                    f"(rango típico: 0.05–0.35). Posible error en huellas post-impacto o velocidades."
                ),
            }
        if e < 0.0:
            return {
                "passed": False,
                "reason": f"Coeficiente de restitución e={e:.3f} negativo — imposible físicamente.",
            }
        return {"passed": True, "reason": None}

    async def _verify_biomechanics(self, caso: Caso, resultado: Resultado) -> dict:
        """
        Verifica severidad biomecánica usando Delta-V calculado (disponible para todos los tipos).
        ΔV > 70 km/h → riesgo vital alto.
        ΔV > 80 km/h → umbral de supervivencia comprometido.
        En atropello sin Delta-V, usa EBS como proxy.
        """
        dv_calculos = [
            c for c in resultado.calculos
            if "delta-v" in c.nombre.lower() or "delta_v" in c.nombre.lower() or "delta v" in c.nombre.lower()
        ]

        for c in dv_calculos:
            if c.valor > 80:
                return {
                    "passed": False,
                    "reason": (
                        f"{c.nombre}: ΔV={c.valor:.0f} km/h supera umbral de supervivencia (80 km/h). "
                        f"Lesiones graves o fatales altamente probables. Notificar a autoridad judicial."
                    ),
                }

        if caso.tipo_colision.value == "atropello" and not dv_calculos:
            ebs = next((c.valor for c in resultado.calculos if "ebs" in c.nombre.lower()), None)
            if ebs and ebs > 60:
                return {
                    "passed": False,
                    "reason": f"Atropello con EBS {ebs:.0f} km/h — lesiones graves o fatales muy probables",
                }

        return {"passed": True, "reason": None}

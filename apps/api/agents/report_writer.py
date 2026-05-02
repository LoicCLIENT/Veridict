"""
Report Writer — conclusión técnica (Claude) + PDF completo (ReportLab).
"""

from typing import Any
from models import Caso, Resultado


class ReportWriter:

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()

    async def generate(self, caso: Caso, resultado: Resultado) -> dict[str, Any]:
        import json
        from reports.pdf_generator import generate_pdf
        from audit.sigstore_signer import sign_document

        conclusion = await self._generate_conclusion(caso, resultado)

        # Firmar los datos del análisis (no el PDF) para poder incrustar el hash en el propio PDF.
        digest_data = {
            "caso_id": caso.id,
            "fecha": caso.fecha_accidente.isoformat(),
            "calculos": [c.model_dump() for c in resultado.calculos],
            "infracciones": [i.model_dump() for i in resultado.infracciones],
            "veredicto": resultado.veredicto.model_dump() if resultado.veredicto else None,
        }
        sigstore_hash = await sign_document(
            json.dumps(digest_data, ensure_ascii=False).encode()
        )
        resultado.sigstore_hash = sigstore_hash

        pdf_bytes = await generate_pdf(caso, resultado, conclusion=conclusion)
        pdf_url = f"/api/casos/{caso.id}/pdf"

        return {"pdf_url": pdf_url, "sigstore_hash": sigstore_hash}

    async def _generate_conclusion(self, caso: Caso, resultado: Resultado) -> str:
        calculos_txt = "\n".join(
            f"  • {c.nombre}: {c.valor} {c.unidad}"
            for c in resultado.calculos
        ) or "  • Sin cálculos disponibles"

        infracciones_txt = ", ".join(
            f"{i.articulo} (Veh. {i.vehiculo})"
            for i in resultado.infracciones
        ) or "ninguna identificada"

        contraste_txt = ""
        for cv in resultado.contraste_versiones:
            compat = "compatible" if cv.compatible else "no compatible"
            contraste_txt += f"\n  • Vehículo {cv.vehiculo_id}: declaración {compat} con la física"

        verificacion_txt = ""
        if resultado.verificacion_adversarial:
            va = resultado.verificacion_adversarial
            if va.passed:
                verificacion_txt = "\n- Verificación adversarial: análisis superado sin incidencias"
            else:
                inc = "; ".join(va.failures[:3])
                verificacion_txt = f"\n- Verificación adversarial: {len(va.failures)} incidencia(s) — {inc}"

        prompt = f"""Redacta el párrafo de CONCLUSIÓN TÉCNICA de un informe pericial de accidente de tráfico español.

DATOS:
- Tipo de colisión: {caso.tipo_colision.value}
- Fecha: {caso.fecha_accidente.strftime('%d/%m/%Y %H:%M')}
- Cálculos físicos:{calculos_txt}
- Artículos aplicables: {infracciones_txt}
{f'- Contraste declaraciones:{contraste_txt}' if contraste_txt else ''}{verificacion_txt}

INSTRUCCIONES:
— Tono técnico-jurídico formal, como un perito colegiado.
— 80-120 palabras en prosa continua (sin viñetas).
— Menciona los métodos utilizados (CRASH3, Stannard Baker si aplica).
— Cita las velocidades calculadas y los artículos identificados.
— Si hay incidencias en la verificación adversarial, indícalo brevemente.
— NO atribuyas porcentajes de culpa ni responsabilidad civil.
— Termina indicando que el informe queda a disposición de las partes."""

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_sonnet,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"ReportWriter conclusion error: {e}")
            return (
                f"Mediante la aplicación de las metodologías CRASH3 y Stannard Baker "
                f"se han obtenido las velocidades equivalentes de barrera y velocidades "
                f"previas a la frenada que constan en el apartado de cálculos físicos. "
                f"Se han identificado los artículos del RGC/LSV aplicables al presente siniestro. "
                f"El presente informe queda a disposición de las partes y del órgano jurisdiccional competente."
            )

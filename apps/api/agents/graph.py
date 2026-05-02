"""
Pipeline de análisis forense — ejecución paralela.

Fases:
  1. PARALELO   → Física (CRASH3/SB) + Contexto externo (meteo, vía, sol, dirección)
  2. PARALELO   → Cronología (Claude) + Infracciones RGC/LSV (Claude)
  3. PARALELO   → Adjudicación culpa % (Claude Opus) + Contraste declaraciones (Claude)
  4. SECUENCIAL → Verificación adversarial (Devil's Advocate)
  5. SECUENCIAL → Generación PDF (Claude + ReportLab)
"""

import asyncio
from typing import Callable, Optional

from models import Caso, Resultado, VerificacionAdversarial, NexoCausal


async def run_analysis_pipeline(
    caso: Caso,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Resultado:

    def update(p: float, msg: str):
        if progress_callback:
            progress_callback(p, msg)

    resultado = Resultado()

    try:
        # ── FASE 1: PARALELO ──────────────────────────────────────────────
        # Contexto primero (meteo, OSM) para que la física use μ real de la calzada.
        update(5, "Obteniendo contexto externo y calculando física...")

        from agents.forensic_analyst import ForensicAnalyst
        from agents.context_fetcher import fetch_full_context

        analyst = ForensicAnalyst()
        contexto = await fetch_full_context(caso)
        resultado.contexto = contexto

        # Física con contexto: μ real, distancia seguridad, Delta-V
        (calculos, _) = await analyst.run_physics(caso, contexto)
        resultado.calculos = calculos

        update(35, "Física y contexto obtenidos")

        # ── FASE 2: PARALELO ──────────────────────────────────────────────
        update(38, "Generando cronología e identificando infracciones...")

        from agents.legal_reasoner import LegalReasoner

        timeline_task = analyst.generate_timeline(caso, calculos, contexto)
        # LegalReasoner recibe contexto para usar límite de velocidad OSM real
        infractions_task = LegalReasoner().analyze(caso, calculos, contexto)

        cronologia, infractions_result = await asyncio.gather(
            timeline_task,
            infractions_task,
        )

        resultado.cronologia = cronologia
        resultado.infracciones = infractions_result.get("infracciones", [])

        update(70, "Cronología e infracciones completadas")

        # ── FASE 3: SECUENCIAL — contraste de declaraciones ───────────────
        # Debe correr ANTES del Adjudicator para que éste tenga el contraste disponible.
        update(72, "Contrastando declaraciones con la evidencia física...")

        from agents.declaration_analyst import DeclarationAnalyst

        contraste = await DeclarationAnalyst().analyze(caso, calculos, resultado.cronologia)
        resultado.contraste_versiones = contraste

        update(78, "Contraste de declaraciones completado")

        # ── FASE 4: ADJUDICACIÓN ──────────────────────────────────────────
        # Ahora resultado.contraste_versiones está disponible para el prompt de Opus.
        update(80, "Adjudicando responsabilidad civil...")

        from agents.adjudicator import Adjudicator

        adjudication_result = await Adjudicator().adjudicate(caso, resultado)

        veredicto = adjudication_result.get("veredicto")
        if veredicto:
            veredicto.razonamiento = adjudication_result.get("razonamiento", "")
            veredicto.advertencia_personal = adjudication_result.get("advertencia_personal", False)
            veredicto.nexo_causal = [
                NexoCausal(**n) for n in adjudication_result.get("nexo_causal", [])
            ]
        resultado.veredicto = veredicto
        resultado.compatibilidad_versiones = adjudication_result.get("compatibilidad")

        update(85, "Veredicto completado")

        # ── FASE 4: VERIFICACIÓN ADVERSARIAL ─────────────────────────────
        update(87, "Verificación adversarial (Devil's Advocate)...")

        from agents.devils_advocate import DevilsAdvocate

        da = await DevilsAdvocate().verify(caso, resultado)
        resultado.verificacion_adversarial = VerificacionAdversarial(
            passed=da["passed"],
            failures=da.get("failures", []),
        )

        if not da["passed"]:
            update(93, f"⚠ Verificación adversarial: {len(da['failures'])} incidencia(s) detectada(s)")
        else:
            update(93, "Verificación adversarial superada ✓")

        # ── FASE 5: INFORME PDF ───────────────────────────────────────────
        update(95, "Generando informe pericial PDF...")

        from agents.report_writer import ReportWriter

        report = await ReportWriter().generate(caso, resultado)
        resultado.pdf_url = report.get("pdf_url")
        resultado.sigstore_hash = report.get("sigstore_hash")

        update(100, "Informe pericial completado")
        return resultado

    except Exception as e:
        print(f"Pipeline error: {e}")
        raise

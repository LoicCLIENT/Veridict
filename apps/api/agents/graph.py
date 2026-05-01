"""
LangGraph orchestration for multi-agent pipeline.

Pipeline:
[Data] -> [Forensic Analyst] -> [Legal Reasoner] -> [Adjudicator]
       -> [Devil's Advocate] -> [Report Writer]
"""

from typing import Callable, Optional
import asyncio

from models import Caso, Resultado, Evento, CalculoFisico, Infraccion, Veredicto, CompatibilidadVersiones


async def run_analysis_pipeline(
    caso: Caso,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Resultado:
    """
    Run the complete multi-agent analysis pipeline.

    Args:
        caso: The case to analyze
        progress_callback: Optional callback for progress updates (progress%, stage_name)

    Returns:
        Resultado with complete analysis
    """
    from agents.forensic_analyst import ForensicAnalyst
    from agents.legal_reasoner import LegalReasoner
    from agents.adjudicator import Adjudicator
    from agents.devils_advocate import DevilsAdvocate
    from agents.report_writer import ReportWriter

    resultado = Resultado()

    def update(progress: float, stage: str):
        if progress_callback:
            progress_callback(progress, stage)

    try:
        # Stage 1: Forensic Analysis (0-30%)
        update(5, "Extrayendo datos contextuales")
        await asyncio.sleep(0.5)  # Simulated API calls

        update(10, "Analizando fotografias con vision AI")
        await asyncio.sleep(0.5)

        update(15, "Ejecutando calculos CRASH3")
        forensic = ForensicAnalyst()
        forensic_result = await forensic.analyze(caso)
        resultado.cronologia = forensic_result.get("cronologia", [])
        resultado.calculos = forensic_result.get("calculos", [])

        update(30, "Analisis forense completado")

        # Stage 2: Legal Reasoning (30-50%)
        update(35, "Buscando articulos aplicables en corpus legal")
        legal = LegalReasoner()
        legal_result = await legal.analyze(caso, resultado.calculos)
        resultado.infracciones = legal_result.get("infracciones", [])

        update(50, "Razonamiento legal completado")

        # Stage 3: Adjudication (50-70%)
        update(55, "Calculando atribucion de culpa")
        adjudicator = Adjudicator()
        adj_result = await adjudicator.adjudicate(caso, resultado)
        resultado.veredicto = adj_result.get("veredicto")
        resultado.compatibilidad_versiones = adj_result.get("compatibilidad")

        update(70, "Adjudicacion completada")

        # Stage 4: Devil's Advocate (70-85%)
        if resultado.veredicto and resultado.veredicto.confidence >= 0.85:
            update(75, "Ejecutando verificacion adversarial")
            devils = DevilsAdvocate()
            devils_result = await devils.verify(caso, resultado)
            resultado.devils_advocate_passed = devils_result.get("passed", False)

            if not resultado.devils_advocate_passed:
                update(85, "Verificacion fallida - requiere revision humana")
                return resultado
        else:
            update(75, "Confianza insuficiente - escalando a humano")
            resultado.devils_advocate_passed = False
            return resultado

        update(85, "Verificacion adversarial completada")

        # Stage 5: Report Generation (85-100%)
        update(90, "Generando informe PDF")
        writer = ReportWriter()
        report_result = await writer.generate(caso, resultado)
        resultado.pdf_url = report_result.get("pdf_url")
        resultado.sigstore_hash = report_result.get("sigstore_hash")

        update(100, "Dictamen completado")

        return resultado

    except Exception as e:
        print(f"Pipeline error: {e}")
        raise


# For standalone testing
if __name__ == "__main__":
    import sys
    import json

    async def main():
        # Load test case
        caso_path = sys.argv[1] if len(sys.argv) > 1 else "data/casos_demo/caso_1_madrid_m30"
        print(f"Running pipeline for: {caso_path}")

        # Mock caso for testing
        from datetime import datetime
        from models import Ubicacion, TipoColision

        caso = Caso(
            id="test-1",
            fecha_accidente=datetime.now(),
            ubicacion=Ubicacion(lat=40.4168, lon=-3.7038),
            tipo_colision=TipoColision.LATERAL,
        )

        def progress(p, s):
            print(f"[{p:.0f}%] {s}")

        resultado = await run_analysis_pipeline(caso, progress)
        print(json.dumps(resultado.model_dump(), indent=2, default=str))

    asyncio.run(main())

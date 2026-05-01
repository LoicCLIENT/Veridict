"""Router for analysis operations."""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks

from models import EstadoCaso, EstadoAnalisis
from routers.casos import casos_db

router = APIRouter()

# In-memory state for analysis progress
analisis_estado: dict[str, EstadoAnalisis] = {}


async def run_pipeline(caso_id: str):
    """Run the multi-agent analysis pipeline."""
    from agents.graph import run_analysis_pipeline

    try:
        # Update state
        analisis_estado[caso_id] = EstadoAnalisis(
            estado="procesando", progreso=0, etapa_actual="Iniciando analisis"
        )

        caso = casos_db[caso_id]
        caso.estado = EstadoCaso.PROCESANDO
        casos_db[caso_id] = caso

        # Run the pipeline
        resultado = await run_analysis_pipeline(
            caso, progress_callback=lambda p, e: update_progress(caso_id, p, e)
        )

        # Update caso with results
        caso.resultado = resultado
        caso.estado = EstadoCaso.COMPLETADO
        casos_db[caso_id] = caso

        analisis_estado[caso_id] = EstadoAnalisis(
            estado="completado", progreso=100, etapa_actual="Finalizado"
        )

    except Exception as e:
        print(f"Error in pipeline: {e}")
        caso = casos_db[caso_id]
        caso.estado = EstadoCaso.ESCALADO_HUMANO
        casos_db[caso_id] = caso

        analisis_estado[caso_id] = EstadoAnalisis(
            estado="error", progreso=0, etapa_actual=str(e)
        )


def update_progress(caso_id: str, progreso: float, etapa: str):
    """Update analysis progress."""
    analisis_estado[caso_id] = EstadoAnalisis(
        estado="procesando", progreso=progreso, etapa_actual=etapa
    )


@router.post("/{caso_id}/analizar")
async def iniciar_analisis(caso_id: str, background_tasks: BackgroundTasks) -> dict:
    """Start the multi-agent analysis pipeline (async)."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    if caso.estado == EstadoCaso.PROCESANDO:
        raise HTTPException(status_code=400, detail="Analysis already in progress")

    # Initialize state
    analisis_estado[caso_id] = EstadoAnalisis(
        estado="iniciando", progreso=0, etapa_actual="Preparando"
    )

    # Run in background
    background_tasks.add_task(run_pipeline, caso_id)

    return {"status": "started", "caso_id": caso_id}


@router.get("/{caso_id}/estado", response_model=EstadoAnalisis)
async def obtener_estado(caso_id: str) -> EstadoAnalisis:
    """Get current analysis state (for polling)."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    if caso_id in analisis_estado:
        return analisis_estado[caso_id]

    caso = casos_db[caso_id]
    return EstadoAnalisis(
        estado=caso.estado.value,
        progreso=100 if caso.estado == EstadoCaso.COMPLETADO else 0,
        etapa_actual=None,
    )

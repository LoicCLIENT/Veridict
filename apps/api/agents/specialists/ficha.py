"""FichaAgent — ficha técnica del vehículo a partir del seed local."""

from __future__ import annotations

import time

from models import IdentificacionVehiculo, ToolCallLog
from services.enrichment import enriquecer_vehiculo


async def consultar_ficha(marca: str, modelo: str, anio: int | None = None,
                          vehiculo_id: str = "A") -> dict:
    t0 = time.time()
    ident = IdentificacionVehiculo(id=vehiculo_id, marca=marca, modelo=modelo, anio=anio)
    ficha = enriquecer_vehiculo(ident)
    falta = None
    if ficha.notas and "default" in (ficha.notas or "").lower():
        falta = (
            f"No tenemos ficha exacta de {marca} {modelo}. "
            f"Pregunta al perito por: masa real (tarjeta ITV), año concreto, "
            f"y si se trata del modelo base o premium."
        )

    log = ToolCallLog(
        agente="FichaAgent",
        pregunta=f"Ficha técnica de {marca} {modelo} ({anio or '?'})",
        inputs={"marca": marca, "modelo": modelo, "anio": anio, "vehiculo_id": vehiculo_id},
        resultado_resumen=(
            f"{marca} {modelo}: {ficha.masa_kg} kg, ancho {ficha.ancho_m} m, "
            f"{len(ficha.sistemas_seguridad)} sistemas seguridad. Fuente: {ficha.fuente}"
        ),
        fuentes_consultadas=[ficha.fuente or "seed local"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": ficha.model_dump(mode="json"), "_log": log}

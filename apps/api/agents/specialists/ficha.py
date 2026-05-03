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
    is_default = ficha.notas and "default" in (ficha.notas or "").lower()
    if is_default:
        if ficha.tipo_vehiculo == "bicicleta":
            falta = (
                f"No tenemos ficha exacta de la bicicleta {marca} {modelo}. "
                f"Pregunta al perito: marca/modelo concretos, masa de la bici (kg), "
                f"masa estimada del ciclista (kg), altura de sillín y anchura de manillar."
            )
        else:
            falta = (
                f"No tenemos ficha exacta de {marca} {modelo}. "
                f"Pregunta al perito por: masa real (tarjeta ITV), año concreto, "
                f"y si se trata del modelo base o premium."
            )
    elif ficha.tipo_vehiculo == "turismo" and not anio:
        # Para turismos cuya ficha tiene `_year_routing` interno, sin año el
        # resultado es una entrada genérica. Pedimos el año al perito.
        falta = (
            f"Has consultado un {marca} {modelo} sin año. La ficha devuelta es "
            f"genérica. Aporta el año del vehículo para resolver la generación "
            f"(p.ej. SEAT Ibiza IV vs V tienen anchura distinta: 1.69 vs 1.78 m)."
        )

    if ficha.tipo_vehiculo == "bicicleta":
        resumen = (
            f"🚲 {marca} {modelo}: bici {ficha.masa_kg} kg, "
            f"sillín {ficha.altura_sillin_m} m, manillar {ficha.anchura_manillar_m} m, "
            f"ciclista estimado {ficha.masa_ciclista_estimada_kg} kg. "
            f"Fuente: {ficha.fuente}"
        )
    else:
        resumen = (
            f"{marca} {modelo}: {ficha.masa_kg} kg, ancho {ficha.ancho_m} m, "
            f"{len(ficha.sistemas_seguridad)} sistemas seguridad. Fuente: {ficha.fuente}"
        )

    log = ToolCallLog(
        agente="FichaAgent",
        pregunta=f"Ficha técnica de {marca} {modelo} ({anio or '?'})",
        inputs={"marca": marca, "modelo": modelo, "anio": anio, "vehiculo_id": vehiculo_id},
        resultado_resumen=resumen,
        fuentes_consultadas=[ficha.fuente or "seed local"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": ficha.model_dump(mode="json"), "_log": log}

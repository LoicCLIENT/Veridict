"""Pre-warm de specialists en cuanto se crea el caso.

Llama en background a las herramientas cuyos resultados solo dependen
del formulario (lat/lon, fecha, vehículos, tipo encargo) y los cachea
en `services.specialist_cache`. Cuando el orquestador los pida después,
los recibe instantáneos.

NUNCA bloquea la respuesta del POST /api/casos: las tareas se lanzan
con `asyncio.create_task` y el endpoint devuelve inmediatamente.
"""
from __future__ import annotations

import asyncio
import traceback
from typing import Any

from agents.tools import dispatch
from models import Caso


async def _safe(name: str, args: dict, contexto: dict) -> None:
    try:
        await dispatch(name, args, contexto=contexto)
        print(f"[prewarm]   ✓ {name}", flush=True)
    except Exception as e:  # nunca rompemos el caso por un fallo de pre-warm
        print(f"[prewarm]   ✗ {name}: {e}", flush=True)
        traceback.print_exc()


async def _prewarm(caso: Caso) -> None:
    contexto = {"caso_id": caso.id}
    print(f"[prewarm] === START caso={caso.id} ===", flush=True)

    tareas: list[asyncio.Task] = []

    # 1. Escena (lat, lon)
    if caso.ubicacion and caso.ubicacion.lat and caso.ubicacion.lon:
        tareas.append(asyncio.create_task(_safe(
            "consultar_escena",
            {"lat": caso.ubicacion.lat, "lon": caso.ubicacion.lon, "radio_m": 100},
            contexto,
        )))

    # 2. Meteo (lat, lon, fecha)
    if caso.ubicacion and caso.fecha_accidente:
        tareas.append(asyncio.create_task(_safe(
            "consultar_meteo",
            {
                "lat": caso.ubicacion.lat,
                "lon": caso.ubicacion.lon,
                "fecha_iso": caso.fecha_accidente.isoformat(),
            },
            contexto,
        )))

    # 3. Ficha técnica de cada vehículo identificado
    for v in caso.vehiculos_identificacion or []:
        if not (v.marca and v.modelo):
            continue
        args: dict[str, Any] = {"marca": v.marca, "modelo": v.modelo}
        if v.anio:
            args["anio"] = v.anio
        tareas.append(asyncio.create_task(_safe("consultar_ficha_tecnica", args, contexto)))

    # 4. Legal (depende del tipo de encargo)
    if caso.encargo and caso.encargo.tipo:
        args = {
            "tipo_encargo": caso.encargo.tipo.value if hasattr(caso.encargo.tipo, "value") else str(caso.encargo.tipo),
        }
        if caso.fecha_accidente:
            args["fecha_iso"] = caso.fecha_accidente.isoformat()
        tareas.append(asyncio.create_task(_safe("consultar_legal", args, contexto)))

    if not tareas:
        print(f"[prewarm] sin tareas para caso={caso.id}", flush=True)
        return

    await asyncio.gather(*tareas, return_exceptions=True)
    print(f"[prewarm] === END caso={caso.id} tareas={len(tareas)} ===", flush=True)


def lanzar_prewarm(caso: Caso) -> None:
    """Dispara el pre-warm en background. No bloquea ni espera."""
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(_prewarm(caso))
    except RuntimeError:
        # No event loop en este hilo (caso raro fuera de FastAPI). Lo ignoramos
        # para no romper la creación del caso.
        print(f"[prewarm] no event loop, skip caso={caso.id}", flush=True)

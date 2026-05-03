"""Trace en vivo del orquestador-perito.

Mientras `coordinar()` está corriendo, va escribiendo aquí el progreso
turno a turno y cada llamada a un specialist. El endpoint
`GET /api/casos/{id}/razonamiento` lo sirve para que el frontend pueda
hacer polling y mostrarlo en directo.

Almacenamiento en memoria (single-process). Suficiente para el hackathon.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

# caso_id → trace dict
_traces: dict[str, dict[str, Any]] = {}


def _now() -> str:
    return datetime.utcnow().isoformat()


def init(caso_id: str) -> None:
    _traces[caso_id] = {
        "estado": "iniciando",
        "mensaje": "Preparando contexto del caso…",
        "started_at": _now(),
        "updated_at": _now(),
        "razonamiento_perito": [],
        "datos_completos": [],
        "n_turnos": 0,
        "n_tool_calls": 0,
        "error": None,
    }


def update(caso_id: str, **patch: Any) -> None:
    if caso_id not in _traces:
        return
    _traces[caso_id].update(patch)
    _traces[caso_id]["updated_at"] = _now()


def append_turno(caso_id: str, turno: dict) -> None:
    if caso_id not in _traces:
        return
    t = _traces[caso_id]
    t["razonamiento_perito"].append(turno)
    t["n_turnos"] = len(t["razonamiento_perito"])
    t["updated_at"] = _now()


def append_tool_call(caso_id: str, dato: dict) -> None:
    if caso_id not in _traces:
        return
    t = _traces[caso_id]
    t["datos_completos"].append(dato)
    t["n_tool_calls"] = len(t["datos_completos"])
    t["updated_at"] = _now()


def get(caso_id: str) -> dict | None:
    return _traces.get(caso_id)


def is_running(caso_id: str) -> bool:
    t = _traces.get(caso_id)
    if not t:
        return False
    return t.get("estado") not in ("completado", "error")


def finalize(caso_id: str, *, estado: str = "completado",
             mensaje: str = "Informe listo", error: str | None = None) -> None:
    if caso_id not in _traces:
        return
    _traces[caso_id]["estado"] = estado
    _traces[caso_id]["mensaje"] = mensaje
    _traces[caso_id]["error"] = error
    _traces[caso_id]["updated_at"] = _now()


def clear(caso_id: str) -> None:
    _traces.pop(caso_id, None)

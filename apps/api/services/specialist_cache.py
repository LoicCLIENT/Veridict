"""Cache de resultados de specialists por caso.

Permite "pre-warmar" en cuanto se crea el caso las consultas que solo
dependen del formulario (escena, meteo, ficha técnica, legal) y servirlas
instantáneas cuando el orquestador las pida más tarde.

Almacenamiento en memoria (single-process). Suficiente para el hackathon.
"""
from __future__ import annotations

import json
from typing import Any

# caso_id → {key_serialized → resultado del specialist}
_cache: dict[str, dict[str, Any]] = {}


def _key(tool: str, args: dict | None) -> str:
    return json.dumps({"tool": tool, "args": args or {}}, sort_keys=True, default=str)


def get(caso_id: str, tool: str, args: dict | None) -> Any | None:
    return _cache.get(caso_id, {}).get(_key(tool, args))


def put(caso_id: str, tool: str, args: dict | None, value: Any) -> None:
    _cache.setdefault(caso_id, {})[_key(tool, args)] = value


def clear(caso_id: str) -> None:
    _cache.pop(caso_id, None)


def stats(caso_id: str) -> dict:
    bucket = _cache.get(caso_id, {})
    return {"caso_id": caso_id, "n_entries": len(bucket)}

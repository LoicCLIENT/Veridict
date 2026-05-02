"""Research Service.

Dado el tipo de encargo, devuelve normativa aplicable y bibliografía relevante.
v0: índice estático en seed JSON. v2: Qdrant vectorial sobre corpus completo.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from models import FuenteNormativa, TipoEncargo


SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "normativa.json"


@lru_cache(maxsize=1)
def _load_seed() -> dict:
    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def normativa_para(tipo: TipoEncargo) -> list[FuenteNormativa]:
    seed = _load_seed()
    bucket = seed.get(tipo.value, seed.get("otro", {}))
    return [FuenteNormativa(**item) for item in bucket.get("normativa", [])]


def bibliografia_para(tipo: TipoEncargo) -> list[str]:
    seed = _load_seed()
    bucket = seed.get(tipo.value, seed.get("otro", {}))
    return bucket.get("bibliografia", [])

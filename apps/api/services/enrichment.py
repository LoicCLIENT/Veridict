"""Data Enrichment Service.

Dado (marca, modelo, año), devuelve la ficha técnica del vehículo.
Para v0 usa un seed JSON; en v2 será scraping/API del fabricante o BBDD ITV.

Routing:
1. Si la marca|modelo coincide y la entrada tiene `_year_routing`, se intenta
   resolver primero por generación (p.ej. SEAT Ibiza IV vs V según el año).
2. Si no hay routing o no coincide, se usa la entrada genérica.
3. Si tampoco existe entrada exacta, se cae al `_default_<tipo>`. Bicicletas
   se detectan por marca/modelo conocidos y palabras clave.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from models import FichaTecnicaVehiculo, IdentificacionVehiculo


SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "vehiculos.json"


@lru_cache(maxsize=1)
def _load_seed() -> dict:
    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


_BICI_MARCAS = {"orbea", "trek", "specialized", "giant", "scott", "merida", "bh", "cannondale",
                "btwin", "decathlon", "canyon", "cube", "focus bikes", "kross", "wilier"}
_BICI_KEYWORDS = ("bicicleta", "bici", "mtb", "mountain bike", "gravel", "ciclo", "carretera",
                  "road bike", "ebike", "e-bike", "fixie", "tandem", "bmx")


def _is_bicycle(marca: str, modelo: str) -> bool:
    m = _normalize(marca)
    mod = _normalize(modelo)
    if m in _BICI_MARCAS:
        return True
    return any(k in mod for k in _BICI_KEYWORDS)


def _classify_default(marca: str, modelo: str) -> str:
    """Heurística sencilla para escoger un perfil por defecto."""
    if _is_bicycle(marca, modelo):
        return "_default_bicicleta"
    m = _normalize(modelo)
    if any(k in m for k in ("cabstar", "trafic", "transit", "vito", "doblo", "kangoo")):
        return "_default_furgoneta"
    if any(k in m for k in ("tgl", "tgm", "tgs", "fmx", "actros", "iveco", "daily 70")):
        return "_default_camion"
    return "_default_turismo"


def _resolve_year_routing(entry: dict, anio: Optional[int], seed: dict) -> dict:
    """Si la entrada tiene `_year_routing` y conocemos el año, devuelve la
    entrada específica de la generación. Si no, devuelve la entrada original."""
    routing = entry.get("_year_routing")
    if not routing or anio is None:
        return entry
    for r in routing:
        try:
            mn = int(r.get("min", 0))
            mx = int(r.get("max", 9999))
        except (TypeError, ValueError):
            continue
        if mn <= anio <= mx:
            specific_key = r.get("key")
            specific = seed.get(specific_key) if specific_key else None
            if specific:
                return specific
    return entry


def enriquecer_vehiculo(ident: IdentificacionVehiculo) -> FichaTecnicaVehiculo:
    """Devuelve la ficha técnica enriquecida; cae a un default si no hay match exacto."""
    seed = _load_seed()
    marca = _normalize(ident.marca)
    modelo = _normalize(ident.modelo)
    key = f"{marca}|{modelo}"

    raw = seed.get(key)
    if raw is not None:
        raw = _resolve_year_routing(raw, ident.anio, seed)
    else:
        # Match por modelo (sin marca)
        for k, v in seed.items():
            if k.startswith("_"):
                continue
            partes = k.split("|")
            if len(partes) >= 2 and partes[1] == modelo:
                raw = _resolve_year_routing(v, ident.anio, seed)
                break

    if raw is None:
        default_key = _classify_default(marca, modelo)
        raw = seed.get(default_key, seed["_default_turismo"])
        notas = (raw.get("notas") or "") + " (Ficha por defecto — no se identificó el modelo concreto.)"
    else:
        notas = raw.get("notas")

    altura_pc = raw.get("altura_parachoques_m")
    altura_pc_t: Optional[tuple[float, float]] = (
        (float(altura_pc[0]), float(altura_pc[1])) if altura_pc else None
    )

    return FichaTecnicaVehiculo(
        vehiculo_id=ident.id,
        marca=ident.marca,
        modelo=ident.modelo,
        anio=ident.anio,
        tipo_vehiculo=raw.get("tipo_vehiculo"),
        masa_kg=raw.get("masa_kg"),
        longitud_m=raw.get("longitud_m"),
        ancho_m=raw.get("ancho_m"),
        altura_m=raw.get("altura_m"),
        altura_parachoques_m=altura_pc_t,
        altura_largueros_m=raw.get("altura_largueros_m"),
        rigidez_a=raw.get("rigidez_a"),
        rigidez_b=raw.get("rigidez_b"),
        sistemas_seguridad=raw.get("sistemas_seguridad", []),
        altura_sillin_m=raw.get("altura_sillin_m"),
        anchura_manillar_m=raw.get("anchura_manillar_m"),
        masa_ciclista_estimada_kg=raw.get("masa_ciclista_estimada_kg"),
        fuente=raw.get("fuente"),
        notas=notas,
    )


def enriquecer_todos(vehiculos: list[IdentificacionVehiculo]) -> list[FichaTecnicaVehiculo]:
    return [enriquecer_vehiculo(v) for v in vehiculos]

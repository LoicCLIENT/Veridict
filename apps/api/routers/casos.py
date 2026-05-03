"""Router for caso CRUD operations."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from db import JsonCasoStore
from models import Caso, CasoCreate, CasoUpdate, EstadoCaso
from services.prewarm import lanzar_prewarm

router = APIRouter()

# Persistencia local en JSON: apps/api/db/casos.json
_DB_PATH = Path(__file__).resolve().parent.parent / "db" / "casos.json"
casos_db: JsonCasoStore = JsonCasoStore(_DB_PATH)


def _build_caso(caso_input: CasoCreate) -> Caso:
    """Construye un Caso a partir de un CasoCreate y guarda el payload original."""
    formulario_origen = json.loads(caso_input.model_dump_json())
    return Caso(
        fecha_accidente=caso_input.fecha_accidente,
        ubicacion=caso_input.ubicacion,
        tipo_colision=caso_input.tipo_colision,
        encargo=caso_input.encargo,
        vehiculos_identificacion=caso_input.vehiculos_identificacion,
        hechos_atestado=caso_input.hechos_atestado,
        lesiones=caso_input.lesiones,
        formulario_origen=formulario_origen,
    )


@router.post("", response_model=Caso)
async def crear_caso(caso_input: CasoCreate) -> Caso:
    """Create a new caso (v2 payload: encargo + identificación + hechos + lesiones)."""
    caso = _build_caso(caso_input)
    casos_db[caso.id] = caso
    # Pre-warm: lanza en background las consultas que no dependen de las fotos
    # (escena, meteo, ficha técnica, legal). Cuando el orquestador las pida
    # más tarde, las recibirá instantáneas desde la cache.
    lanzar_prewarm(caso)
    return caso


@router.post("/import-json", response_model=Caso)
async def importar_caso_json(file: UploadFile = File(...)) -> Caso:
    """Importa un caso desde un fichero JSON con la forma de `CasoCreate`.

    Permite crear casos sin tener que rellenar el formulario a mano.
    """
    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")
    try:
        caso_input = CasoCreate.model_validate(data)
    except Exception as e:  # pydantic ValidationError
        raise HTTPException(status_code=422, detail=f"Estructura inválida: {e}")
    caso = _build_caso(caso_input)
    casos_db[caso.id] = caso
    lanzar_prewarm(caso)
    return caso


@router.get("", response_model=list[Caso])
async def listar_casos() -> list[Caso]:
    """List all casos."""
    return list(casos_db.values())


@router.get("/{caso_id}", response_model=Caso)
async def obtener_caso(caso_id: str) -> Caso:
    """Get a specific caso by ID."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    return casos_db[caso_id]


@router.patch("/{caso_id}", response_model=Caso)
async def actualizar_caso(caso_id: str, updates: CasoUpdate) -> Caso:
    """Update a caso."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    if updates.estado is not None:
        caso.estado = updates.estado
    if updates.vehiculos is not None:
        caso.vehiculos = updates.vehiculos

    casos_db[caso_id] = caso
    return caso


@router.delete("/{caso_id}")
async def eliminar_caso(caso_id: str) -> dict:
    """Delete a caso."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    del casos_db[caso_id]
    return {"status": "deleted", "id": caso_id}
# reload trigger

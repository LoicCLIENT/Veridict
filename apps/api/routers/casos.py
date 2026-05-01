"""Router for caso CRUD operations."""

from fastapi import APIRouter, HTTPException
from typing import Dict

from models import Caso, CasoCreate, CasoUpdate, EstadoCaso

router = APIRouter()

# In-memory storage for demo (replace with database in production)
casos_db: Dict[str, Caso] = {}


@router.post("", response_model=Caso)
async def crear_caso(caso_input: CasoCreate) -> Caso:
    """Create a new caso."""
    caso = Caso(
        fecha_accidente=caso_input.fecha_accidente,
        ubicacion=caso_input.ubicacion,
        tipo_colision=caso_input.tipo_colision,
    )
    casos_db[caso.id] = caso
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

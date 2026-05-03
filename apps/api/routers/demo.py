"""Router for demo operations.

Los casos viven en la base de datos (`casos_db`). Este router solo expone
una vista filtrada de los casos cuyo id empieza por `demo-`, sin precargar
nada hardcodeado.
"""

from fastapi import APIRouter, HTTPException

from models import Caso
from routers.casos import casos_db

router = APIRouter()


@router.get("/casos", response_model=list[Caso])
async def listar_demo_casos() -> list[Caso]:
    return [caso for caso in casos_db.values() if caso.id.startswith("demo-")]


@router.post("/casos/{caso_id}/reset")
async def reset_demo_caso(caso_id: str) -> dict:
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return {"status": "noop", "caso_id": caso_id}

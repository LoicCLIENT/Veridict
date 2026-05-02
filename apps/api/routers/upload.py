"""Router for file upload operations."""

import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from config import get_settings
from models import Documento, Foto, MedicionesInput
from routers.casos import casos_db

router = APIRouter()

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_ROOT.mkdir(exist_ok=True)


def _safe_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "file")
    return name[:120] or "file"


async def _save_file(caso_id: str, kind: str, upload: UploadFile) -> tuple[str, str]:
    """Persiste el archivo en disco. Devuelve (rel_path, public_url)."""
    safe = _safe_filename(upload.filename or "file")
    rel = f"{caso_id}/{kind}/{uuid4().hex[:8]}_{safe}"
    abs_path = UPLOAD_ROOT / rel
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    content = await upload.read()
    abs_path.write_bytes(content)
    base = get_settings().api_base_url.rstrip("/")
    public_url = f"{base}/uploads/{rel}"
    return rel, public_url


@router.post("/{caso_id}/upload/atestado")
async def upload_atestado(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload atestado PDF and run OCR."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    # TODO: Upload to R2/Supabase and run OCR
    # For now, just create a mock document
    _, url = await _save_file(caso_id, "atestado", file)
    doc = Documento(tipo="atestado", url=url, texto_extraido=None)
    caso.documentos.append(doc)
    casos_db[caso_id] = caso

    return {"status": "uploaded", "document_id": doc.id, "url": url, "filename": file.filename}


@router.post("/{caso_id}/upload/parte")
async def upload_parte(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload parte amistoso PDF and run OCR."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    _, url = await _save_file(caso_id, "parte", file)
    doc = Documento(tipo="parte_amistoso", url=url, texto_extraido=None)
    caso.documentos.append(doc)
    casos_db[caso_id] = caso

    return {"status": "uploaded", "document_id": doc.id, "url": url, "filename": file.filename}


@router.post("/{caso_id}/upload/foto")
async def upload_foto(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload foto. Se persiste a disco y queda accesible vía /uploads/...

    El Perito coordinador la verá en `imagenes_disponibles` y podrá llamar a
    `analizar_imagen_dano(url)` con visión Claude.
    """
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]
    _, url = await _save_file(caso_id, "fotos", file)
    foto = Foto(url=url, descripcion=None, analisis=None)
    caso.fotos.append(foto)
    casos_db[caso_id] = caso

    return {"status": "uploaded", "foto_id": foto.id, "url": url, "filename": file.filename}


@router.post("/{caso_id}/mediciones")
async def agregar_mediciones(caso_id: str, mediciones: MedicionesInput) -> dict:
    """Add manual measurements from expert."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    # Find or create vehicle
    vehiculo = next(
        (v for v in caso.vehiculos if v.id == mediciones.vehiculo_id), None
    )
    if vehiculo:
        vehiculo.mediciones_C = mediciones.mediciones_C
        vehiculo.ancho_zona_danada_cm = mediciones.ancho_zona_danada_cm
    else:
        from models import Vehiculo

        vehiculo = Vehiculo(
            id=mediciones.vehiculo_id,
            mediciones_C=mediciones.mediciones_C,
            ancho_zona_danada_cm=mediciones.ancho_zona_danada_cm,
        )
        caso.vehiculos.append(vehiculo)

    casos_db[caso_id] = caso

    return {
        "status": "added",
        "vehiculo_id": mediciones.vehiculo_id,
    }

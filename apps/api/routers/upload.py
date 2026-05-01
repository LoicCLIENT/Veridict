"""Router for file upload operations."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from models import Documento, Foto, MedicionesInput
from routers.casos import casos_db

router = APIRouter()


@router.post("/{caso_id}/upload/atestado")
async def upload_atestado(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload atestado PDF and run OCR."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    # TODO: Upload to R2/Supabase and run OCR
    # For now, just create a mock document
    doc = Documento(
        tipo="atestado",
        url=f"/uploads/{caso_id}/atestado/{file.filename}",
        texto_extraido=None,  # Will be filled by OCR
    )
    caso.documentos.append(doc)
    casos_db[caso_id] = caso

    return {
        "status": "uploaded",
        "document_id": doc.id,
        "filename": file.filename,
    }


@router.post("/{caso_id}/upload/parte")
async def upload_parte(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload parte amistoso PDF and run OCR."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    doc = Documento(
        tipo="parte_amistoso",
        url=f"/uploads/{caso_id}/parte/{file.filename}",
        texto_extraido=None,
    )
    caso.documentos.append(doc)
    casos_db[caso_id] = caso

    return {
        "status": "uploaded",
        "document_id": doc.id,
        "filename": file.filename,
    }


@router.post("/{caso_id}/upload/foto")
async def upload_foto(caso_id: str, file: UploadFile = File(...)) -> dict:
    """Upload foto and analyze with Claude Vision."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    # TODO: Upload to R2/Supabase and analyze with Claude Vision
    foto = Foto(
        url=f"/uploads/{caso_id}/fotos/{file.filename}",
        analisis=None,  # Will be filled by Claude Vision
    )
    caso.fotos.append(foto)
    casos_db[caso_id] = caso

    return {
        "status": "uploaded",
        "foto_id": foto.id,
        "filename": file.filename,
    }


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

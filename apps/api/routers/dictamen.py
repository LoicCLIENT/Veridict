"""Router for dictamen operations."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io

from models import Resultado
from routers.casos import casos_db

router = APIRouter()


@router.get("/{caso_id}/dictamen", response_model=Resultado)
async def obtener_dictamen(caso_id: str) -> Resultado:
    """Get the complete dictamen when analysis is done."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    if caso.resultado is None:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    return caso.resultado


@router.get("/{caso_id}/pdf")
async def descargar_pdf(caso_id: str) -> StreamingResponse:
    """Download the dictamen as PDF in UNE-EN 16775 format."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    if caso.resultado is None:
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    # Generate PDF
    from reports.pdf_generator import generate_pdf

    pdf_bytes = await generate_pdf(caso)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="dictamen_{caso_id}.pdf"'
        },
    )


@router.get("/{caso_id}/audit")
async def obtener_audit(caso_id: str) -> dict:
    """Get the Sigstore audit trail."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    if caso.resultado is None or caso.resultado.sigstore_hash is None:
        raise HTTPException(status_code=400, detail="No audit trail available")

    return {
        "caso_id": caso_id,
        "sigstore_hash": caso.resultado.sigstore_hash,
        "rekor_url": f"https://search.sigstore.dev/?hash={caso.resultado.sigstore_hash}",
    }

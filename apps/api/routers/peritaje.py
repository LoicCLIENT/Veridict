"""Router for the v2 peritaje pipeline (encargo → informe estructurado + chat)."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from agents.peritaje import generar_informe, responder_pregunta_perito
from models import EstadoCaso, InformePericial, RespuestaPeritoInput
from reports.pdf_informe import generar_pdf
from routers.casos import casos_db


router = APIRouter()


_PDF_DIR = Path(__file__).resolve().parent.parent / "uploads" / "_pdfs"
_PDF_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{caso_id}/informe", response_model=InformePericial)
async def generar_o_regenerar_informe(caso_id: str) -> InformePericial:
    """Genera (o regenera) el informe pericial v2 a partir del Caso."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]
    caso.estado = EstadoCaso.PROCESANDO
    casos_db[caso_id] = caso

    informe = await generar_informe(caso)
    caso.informe = informe
    caso.estado = EstadoCaso.COMPLETADO
    casos_db[caso_id] = caso
    return informe


@router.get("/{caso_id}/informe", response_model=InformePericial)
async def obtener_informe(caso_id: str) -> InformePericial:
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    return caso.informe


@router.get("/{caso_id}/informe.pdf")
async def descargar_pdf_informe(caso_id: str):
    """Genera y devuelve el PDF UNE-EN 16775 del informe."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    if not caso.informe:
        raise HTTPException(status_code=404, detail="Informe aún no generado")
    out = _PDF_DIR / f"informe_{caso_id}.pdf"
    generar_pdf(caso.informe, caso, out)
    return FileResponse(out, media_type="application/pdf", filename=f"informe_{caso_id[:8]}.pdf")


@router.post("/{caso_id}/responder", response_model=InformePericial)
async def responder_info_faltante(caso_id: str, body: RespuestaPeritoInput) -> InformePericial:
    """El perito responde a una pregunta de info faltante; se regenera el informe."""
    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")
    caso = casos_db[caso_id]
    informe = await responder_pregunta_perito(caso, body.info_id, body.respuesta)
    caso.informe = informe
    casos_db[caso_id] = caso
    return informe

"""Reconstruye un PDF del atestado policial Ertzaintza a partir de los extractos
visibles en el informe pericial IURGI/ITRASA.

Para cada imagen candidata: pasa visión Claude haciendo OCR literal y compone
un PDF "atestado_aulestia_reconstruido.pdf" en la raíz del proyecto, con las
imágenes embebidas + transcripciones + secciones temáticas (declaración,
mediciones, huellas, conclusiones del atestado).
"""

from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path

from anthropic import APIError
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# Reuso config de la API local
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import get_claude, get_settings  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent.parent.parent
BIBLIOTECA = ROOT / "biblioteca"
OUT_PDF = ROOT / "atestado_aulestia_reconstruido.pdf"


# ── Imágenes candidatas — extractos textuales del atestado dentro del peritaje IURGI ──

EXTRACTOS = [
    # archivo, sección donde lo agrupamos
    ("p13_x110.png", "1. Datos generales y entorno"),
    ("p18_x146.png", "2. Análisis policial del lugar y la velocidad"),
    ("p18_x147.png", "2. Análisis policial del lugar y la velocidad"),
    ("p19_x151.png", "3. Declaración del conductor del turismo"),
    ("p19_x152.png", "3. Declaración del conductor del turismo"),
    ("p22_x165.png", "4. Croquis y posiciones referidas"),
    ("p22_x166.png", "4. Croquis y posiciones referidas"),
    ("p23_x170.png", "5. Huellas y elementos sobre la calzada"),
]


SYSTEM_OCR = """Eres un transcriptor forense de documentos. Recibes una imagen
que contiene un fragmento de un atestado policial español (probablemente de la
Ertzaintza). Devuelve EXCLUSIVAMENTE la transcripción LITERAL del texto visible
en la imagen, conservando saltos de línea, mayúsculas y signos.

REGLAS:
- NO añadas comentarios ni explicaciones.
- NO interpretes; transcribe lo que ves.
- Si una palabra es ilegible, escribe [ilegible].
- Si la imagen no contiene texto del atestado (es una foto, croquis, gráfica), responde EXACTAMENTE: NO_ES_EXTRACTO_TEXTUAL.
- Mantén el idioma original (castellano o euskera)."""


async def transcribir(image_path: Path) -> str:
    """OCR con visión Claude. Devuelve el texto transcrito o NO_ES_EXTRACTO_TEXTUAL."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return "[ANTHROPIC_API_KEY no configurada]"

    data = image_path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        media = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        media = "image/jpeg"
    else:
        media = "image/png"

    client = get_claude()
    try:
        resp = await client.messages.create(
            model=settings.model_sonnet,
            max_tokens=2048,
            system=SYSTEM_OCR,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": media,
                        "data": base64.b64encode(data).decode("ascii"),
                    }},
                    {"type": "text", "text": "Transcribe el texto literal de este extracto."},
                ],
            }],
        )
        return "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    except APIError as e:
        return f"[Error OCR: {e}]"


async def main():
    if not BIBLIOTECA.exists():
        print(f"ERROR: no existe {BIBLIOTECA}")
        sys.exit(1)

    print(f">> OCR con Claude visión sobre {len(EXTRACTOS)} extractos…")
    transcripciones: list[tuple[str, str, str]] = []   # (archivo, seccion, texto)
    for archivo, seccion in EXTRACTOS:
        path = BIBLIOTECA / archivo
        if not path.exists():
            print(f"   - {archivo}: NO encontrado, salto")
            continue
        print(f"   - {archivo} → ocr… ", end="", flush=True)
        texto = await transcribir(path)
        es_texto = texto != "NO_ES_EXTRACTO_TEXTUAL" and not texto.startswith("[Error")
        print(f"{'OK ' + str(len(texto)) + ' chars' if es_texto else 'NO TEXTO / error'}")
        transcripciones.append((archivo, seccion, texto))

    # ── Componer el PDF ──────────────────────────────────────────────────────
    print(f"\n>> Componiendo PDF en {OUT_PDF}…")

    doc = BaseDocTemplate(
        str(OUT_PDF), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=1.8 * cm,
        title="Atestado Ertzaintza Aulestia 21052020 — reconstrucción",
        author="Veridict AI",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")

    def chrome(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(2 * cm, 1.0 * cm,
                          "Reconstrucción a partir del expediente IURGI/ITRASA — uso pericial interno")
        canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"Página {doc.page}")
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="t", frames=frame, onPage=chrome)])

    base = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=base["Title"], fontSize=18, leading=22,
                        alignment=1, textColor=colors.HexColor("#1e3a8a"), spaceAfter=8)
    SUB = ParagraphStyle("SUB", parent=base["Normal"], fontSize=11, leading=14,
                         alignment=1, textColor=colors.HexColor("#475569"), spaceAfter=14)
    H2 = ParagraphStyle("H2", parent=base["Heading2"], fontSize=13, leading=17,
                        textColor=colors.HexColor("#1e3a8a"), spaceBefore=12, spaceAfter=6)
    BODY = ParagraphStyle("BODY", parent=base["BodyText"], fontSize=10, leading=14,
                          alignment=4, spaceAfter=4)
    EXTRACTO_STYLE = ParagraphStyle(
        "EXT", parent=base["BodyText"], fontSize=9.5, leading=13,
        leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6,
        textColor=colors.HexColor("#1f2937"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"), borderWidth=0.5,
        borderPadding=8,
    )
    SMALL = ParagraphStyle("SMALL", parent=base["Normal"], fontSize=8, leading=11,
                           textColor=colors.HexColor("#64748b"))
    NOTE = ParagraphStyle("NOTE", parent=base["BodyText"], fontSize=9, leading=12,
                          textColor=colors.HexColor("#7c2d12"),
                          backColor=colors.HexColor("#fef3c7"),
                          borderColor=colors.HexColor("#f59e0b"),
                          borderWidth=0.6, borderPadding=8, spaceAfter=10)

    story: list = []

    # Portada
    story.append(Paragraph("ATESTADO POLICIAL", H1))
    story.append(Paragraph("Ertzaintza — Diligencias 994/08", SUB))

    rows = [
        ["Hecho", "Atropello mortal a ciclista"],
        ["Fecha", "21 de mayo de 2020 — 20:38 h"],
        ["Lugar", "Barrio Zubero auzoa, Aulestia (Bizkaia)"],
        ["Vehículo A", "SEAT Ibiza, matrícula 3526-BKL — conductor JME (vecino)"],
        ["Vehículo B", "Bicicleta Orbea (n.º bastidor 3773) — ciclista IBU"],
        ["Resultado", "Fallecimiento del ciclista IBU por lesiones cefálicas"],
    ]
    t = Table(rows, colWidths=[4 * cm, 11.5 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "<b>NOTA SOBRE ESTE DOCUMENTO.</b> Este PDF es una <b>reconstrucción no oficial</b> "
        "del atestado policial de la Ertzaintza, elaborada a partir de los extractos textuales "
        "y referencias contenidos en el informe pericial IURGI/ITRASA del caso (autores: "
        "Estibaliz González, Dr. Aitor Ibarra y Pedro Gutiérrez). El atestado original es "
        "un documento del expediente judicial reservado a las partes. Esta reconstrucción se "
        "facilita exclusivamente como input para el sistema asistido VERIDICT, agrupando los "
        "fragmentos disponibles por secciones temáticas. Las transcripciones se han obtenido "
        "mediante OCR asistido por IA sobre las capturas embebidas en el peritaje y pueden "
        "contener errores menores. Para uso forense oficial debe acudirse al original.",
        NOTE))

    story.append(PageBreak())

    # Índice
    story.append(Paragraph("Índice de secciones", H2))
    secciones_unicas = []
    for _, seccion, _ in transcripciones:
        if seccion not in secciones_unicas:
            secciones_unicas.append(seccion)
    for s in secciones_unicas:
        story.append(Paragraph(f"&nbsp;&nbsp;· {s}", BODY))
    story.append(Spacer(1, 16))

    # Secciones
    for s in secciones_unicas:
        story.append(Paragraph(s, H2))
        items = [(a, t) for a, sec, t in transcripciones if sec == s]
        for archivo, texto in items:
            block: list = []
            # Embeber la imagen original del extracto
            img_path = BIBLIOTECA / archivo
            if img_path.exists():
                try:
                    block.append(Image(str(img_path), width=14 * cm, height=8 * cm,
                                       kind="proportional"))
                except Exception:
                    pass
            block.append(Paragraph(f"<i>Fuente: {archivo} · OCR Claude visión</i>", SMALL))
            if texto and texto != "NO_ES_EXTRACTO_TEXTUAL":
                # Convertir saltos de línea en HTML
                texto_html = texto.replace("\n\n", "<br/><br/>").replace("\n", "<br/>")
                block.append(Paragraph(texto_html, EXTRACTO_STYLE))
            else:
                block.append(Paragraph(
                    "<i>(esta imagen no contiene texto del atestado, "
                    "es una captura gráfica o un croquis)</i>", SMALL))
            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

    # Pie
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "<i>Documento generado por VERIDICT AI — reconstrucción a partir del peritaje "
        "IURGI/ITRASA mediante OCR Claude. NO es el atestado original.</i>", SMALL))

    doc.build(story)
    print(f"   PDF guardado en {OUT_PDF}")
    print(f"   Tamaño: {OUT_PDF.stat().st_size // 1024} KB")


if __name__ == "__main__":
    asyncio.run(main())

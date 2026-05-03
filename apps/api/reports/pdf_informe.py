"""Genera un PDF del InformePericial v2 con presentación profesional.

Estructura UNE-EN 16775 + ITRASA-style:
  Portada institucional
  Resumen ejecutivo (caja destacada)
  1. Objeto del informe
  2. Antecedentes y hechos del atestado
  3. Vehículos implicados
  4. Análisis técnico (cálculos)
  5. Marco normativo aplicable
  6. Reconstrucción gráfica (frames SVG del motor + Mapillary)
  7. Estudio biomecánico (cráneo, mecanismos lesivos, AIS)
  8. Conclusiones (respuestas C1, C2…)
  9. Información requerida del perito firmante
  10. Bibliografía técnica
  11. Investigación realizada por los agentes (anexo trazabilidad)
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from reportlab.graphics import renderPDF
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
from svglib.svglib import svg2rlg

from models import Caso, InformePericial


# ── Paleta institucional ─────────────────────────────────────────────────────

PRIMARY = colors.HexColor("#1e3a8a")          # azul Veridict
ACCENT = colors.HexColor("#b45309")           # ámbar para magnitudes
NEUTRAL_BG = colors.HexColor("#f8fafc")       # fondo neutro
RULE = colors.HexColor("#cbd5e1")             # líneas
CITE_BG = colors.HexColor("#eef2ff")          # citas
DANGER = colors.HexColor("#b91c1c")
OK = colors.HexColor("#15803d")


# ── Estilos ──────────────────────────────────────────────────────────────────

def _styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name="Cover", fontName="Helvetica-Bold", fontSize=26, leading=32,
                            alignment=1, spaceAfter=8, textColor=PRIMARY))
    base.add(ParagraphStyle(name="CoverSub", fontName="Helvetica", fontSize=14, leading=18,
                            alignment=1, spaceAfter=20, textColor=colors.HexColor("#475569")))
    base.add(ParagraphStyle(name="CoverMeta", fontName="Helvetica", fontSize=10, leading=14,
                            alignment=1, textColor=colors.HexColor("#475569")))
    base.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=15, leading=20,
                            spaceBefore=14, spaceAfter=6, textColor=PRIMARY))
    base.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=11, leading=15,
                            spaceBefore=8, spaceAfter=3, textColor=PRIMARY))
    base.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9.5, leading=13,
                            spaceAfter=4, alignment=4))  # justified
    base.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=8, leading=11,
                            textColor=colors.HexColor("#64748b")))
    base.add(ParagraphStyle(name="Quote", fontName="Helvetica-Oblique", fontSize=9.2, leading=13,
                            leftIndent=14, rightIndent=10,
                            textColor=colors.HexColor("#334155"),
                            backColor=NEUTRAL_BG, borderPadding=6,
                            borderColor=RULE, borderWidth=0.4))
    base.add(ParagraphStyle(name="Mono", fontName="Courier", fontSize=8.8, leading=11,
                            textColor=colors.HexColor("#475569")))
    base.add(ParagraphStyle(name="Cite", fontName="Helvetica", fontSize=7.5, leading=10,
                            textColor=colors.HexColor("#1e40af"),
                            backColor=CITE_BG, borderPadding=2))
    base.add(ParagraphStyle(name="Highlight", fontName="Helvetica", fontSize=10, leading=14,
                            backColor=NEUTRAL_BG, borderColor=PRIMARY, borderWidth=0.6,
                            borderPadding=10, leftIndent=0, rightIndent=0, spaceAfter=10,
                            alignment=4))
    return base


# ── Plantilla de página ──────────────────────────────────────────────────────

def _draw_chrome(canvas, doc):
    canvas.saveState()
    # Banda superior con marca Veridict
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, A4[1] - 1.2 * cm, A4[0], 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(2 * cm, A4[1] - 0.78 * cm, "VERIDICT AI")
    canvas.setFont("Helvetica", 8.5)
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 0.78 * cm,
                           "Borrador de informe pericial — UNE-EN 16775")
    # Pie
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(2 * cm, 1.0 * cm, "Documento asistido por IA. La calificación final corresponde al perito firmante.")
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"Página {doc.page}")
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
    canvas.restoreState()


def _draw_cover(canvas, doc):
    canvas.saveState()
    # Banda superior larga azul
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, A4[1] - 5 * cm, A4[0], 5 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(2 * cm, A4[1] - 2.0 * cm, "VERIDICT AI")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(2 * cm, A4[1] - 2.6 * cm, "Asistente forense para reconstrucción de accidentes de tráfico")
    # Pie de portada
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.5 * cm, "Borrador asistido por IA — UNE-EN 16775. NO atribuye culpa.")
    canvas.restoreState()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _safe(s) -> str:
    if s is None or s == "":
        return "—"
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _fmt_dt(s) -> str:
    try:
        from datetime import datetime
        return datetime.fromisoformat(str(s).replace("Z", "")).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(s)


def _section_rule(s):
    """Línea fina debajo de un H1 — devuelve un Spacer + Table-rule."""
    t = Table([[""]], colWidths=[16.5 * cm], rowHeights=[1])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, PRIMARY)]))
    return t


def _embed_local_image(url: str, uploads_root: Path, max_w_cm: float = 14, max_h_cm: float = 10):
    """Embebe una imagen local /uploads/... como Image."""
    try:
        p = urlparse(url).path
        if p.startswith("/uploads/"):
            rel = p[len("/uploads/"):]
            local = uploads_root / rel
            if local.exists():
                return Image(str(local), width=max_w_cm * cm, height=max_h_cm * cm,
                             kind="proportional")
    except Exception:
        return None
    return None


def _download_image(url: str) -> Optional[bytes]:
    try:
        with httpx.Client(timeout=8, follow_redirects=True) as c:
            r = c.get(url)
            r.raise_for_status()
            return r.content
    except Exception:
        return None


def _embed_remote_image(url: str, max_w_cm: float = 14, max_h_cm: float = 10):
    data = _download_image(url)
    if not data:
        return None
    try:
        return Image(io.BytesIO(data), width=max_w_cm * cm, height=max_h_cm * cm,
                     kind="proportional")
    except Exception:
        return None


def _embed_svg_local(url: str, uploads_root: Path, max_w_cm: float = 16, max_h_cm: float = 11):
    """Embebe un SVG local convertido a Drawing de ReportLab."""
    try:
        p = urlparse(url).path
        if p.startswith("/uploads/"):
            rel = p[len("/uploads/"):]
            local = uploads_root / rel
            if local.exists():
                drawing = svg2rlg(str(local))
                if drawing is None:
                    return None
                target_w = max_w_cm * cm
                scale = min(target_w / max(drawing.width, 1), (max_h_cm * cm) / max(drawing.height, 1))
                drawing.scale(scale, scale)
                drawing.width *= scale
                drawing.height *= scale
                return drawing
    except Exception:
        return None
    return None


# ── Generación ───────────────────────────────────────────────────────────────

def generar_pdf(informe: InformePericial, caso: Caso, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    uploads_root = Path(__file__).resolve().parent.parent / "uploads"

    doc = BaseDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Veridict — Informe pericial",
        author="Veridict AI",
    )
    cover_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                        id="cover", showBoundary=0)
    body_frame = Frame(doc.leftMargin, doc.bottomMargin + 0.3 * cm,
                       doc.width, doc.height - 0.6 * cm, id="body", showBoundary=0)

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=cover_frame, onPage=_draw_cover),
        PageTemplate(id="main",  frames=body_frame,  onPage=_draw_chrome),
    ])

    s = _styles()
    encargo = caso.encargo
    story: list = []

    # ─────────────────── PORTADA ─────────────────────────────────────────────
    story.append(Spacer(1, 5 * cm))
    titulo = "Informe pericial sobre " + (
        encargo.tipo.value.replace("_", " ") if encargo else "siniestro de tráfico"
    )
    story.append(Paragraph(titulo, s["Cover"]))
    if encargo and encargo.solicitante:
        story.append(Paragraph(_safe(encargo.solicitante), s["CoverSub"]))
    if encargo and encargo.procedimiento:
        story.append(Paragraph(_safe(encargo.procedimiento), s["CoverMeta"]))
    story.append(Spacer(1, 1.4 * cm))

    # Caja con datos clave del siniestro
    veh_str = ", ".join([
        f"{v.id}: {v.marca} {v.modelo}" + (f" ({v.matricula})" if v.matricula else "")
        for v in caso.vehiculos_identificacion
    ]) or "—"
    rows = [
        ["Fecha del siniestro", _fmt_dt(caso.fecha_accidente)],
        ["Tipo de colisión", caso.tipo_colision.value if caso.tipo_colision else "—"],
        ["Vehículos implicados", veh_str],
        ["Confianza global", f"{int(round(informe.confianza_global * 100))}%"],
        ["Agentes consultados", str(len(informe.tool_calls))],
        ["Imágenes recopiladas", str(len(informe.imagenes))],
    ]
    t = Table(rows, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
        ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, PRIMARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t)

    # Fórmula deontológica pericial (estándar)
    story.append(Spacer(1, 1.0 * cm))
    story.append(Paragraph(
        "<i>El/los perito(s) firmante(s) manifiestan, conjunta y solidariamente, "
        "bajo promesa de decir verdad, que han actuado y actuarán con la mayor "
        "objetividad posible, tomando en consideración tanto lo que pueda favorecer "
        "como lo que pueda causar perjuicio a cualquiera de las partes, conociendo "
        "las sanciones penales en las que podrían incurrir si incumplieran el deber "
        "del perito. La calificación última de los hechos corresponde al órgano "
        "judicial; este informe se limita a aportar elementos técnicos objetivos.</i>",
        s["CoverMeta"]))

    story.append(PageBreak())

    # Cambia de plantilla a la de cuerpo
    from reportlab.platypus import NextPageTemplate
    story.append(NextPageTemplate("main"))

    # ─────────────────── RESUMEN EJECUTIVO ───────────────────────────────────
    story.append(Paragraph("Resumen ejecutivo", s["H1"]))
    story.append(_section_rule(s))
    story.append(Spacer(1, 4))
    if informe.resumen_caso:
        story.append(Paragraph(_safe(informe.resumen_caso), s["Highlight"]))

    # ─────────────────── 1. OBJETO ──────────────────────────────────────────
    story.append(Paragraph("1. Objeto del informe", s["H1"]))
    story.append(_section_rule(s))
    if encargo and encargo.preguntas:
        story.append(Paragraph(
            "El presente informe responde a las siguientes cuestiones planteadas por el solicitante:",
            s["Body"]))
        for i, q in enumerate(encargo.preguntas, 1):
            story.append(Paragraph(f"<b>C{i}.</b>&nbsp;&nbsp;{_safe(q)}", s["Body"]))

    # ─────────────────── 2. ANTECEDENTES ────────────────────────────────────
    story.append(Paragraph("2. Antecedentes y hechos del atestado", s["H1"]))
    story.append(_section_rule(s))
    h = caso.hechos_atestado
    if h:
        rows = [
            ["Atestado nº", _safe(h.numero_atestado), "Cuerpo", _safe(h.cuerpo_actuante)],
            ["Huellas frenada",
             ("sí, observadas" if h.hay_huellas_frenada else
              "no se observan" if h.hay_huellas_frenada is False else "no consta"),
             "Calzada", _safe(h.estado_calzada)],
            ["Meteorología", _safe(h.condiciones_meteorologicas),
             "Visibilidad", _safe(h.visibilidad)],
        ]
        t = Table(rows, colWidths=[3 * cm, 5.5 * cm, 2.5 * cm, 5 * cm])
        t.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONT", (2, 0), (2, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
            ("TEXTCOLOR", (2, 0), (2, -1), PRIMARY),
            ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_BG),
            ("BOX", (0, 0), (-1, -1), 0.5, RULE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        if h.velocidades_declaradas:
            story.append(Paragraph("<b>Velocidades registradas:</b>", s["H2"]))
            for v in h.velocidades_declaradas:
                story.append(Paragraph(
                    f"Vehículo <b>{v.vehiculo_id}</b>: {v.valor_kmh} km/h "
                    f"<i>(fuente: {v.fuente.value.replace('_', ' ')})</i>",
                    s["Body"]))
        if h.declaraciones:
            story.append(Paragraph("<b>Declaraciones:</b>", s["H2"]))
            story.append(Paragraph(_safe(h.declaraciones), s["Quote"]))
        if h.observaciones:
            story.append(Paragraph("<b>Observaciones del atestado:</b>", s["H2"]))
            story.append(Paragraph(_safe(h.observaciones), s["Quote"]))

    if caso.lesiones:
        story.append(Paragraph("<b>Lesiones:</b>", s["H2"]))
        for l in caso.lesiones:
            story.append(Paragraph(
                f"<b>{_safe(l.ocupante)}</b> (vehículo {l.vehiculo_id or '—'}): "
                f"{_safe(l.zona_corporal)} — {l.gravedad.value.replace('_', ' ')}"
                + (f", {l.dias_baja} días baja" if l.dias_baja else "")
                + (f". {_safe(l.secuelas)}" if l.secuelas else ""),
                s["Body"]))

    # ─────────────────── 2.bis CONTEXTO METEO/SOL ────────────────────────────
    if informe.contexto_meteo:
        story.append(Paragraph("2.1 Condiciones ambientales en el momento del siniestro", s["H2"]))
        m = informe.contexto_meteo
        rows = [
            ["Estado del tiempo", _safe(m.estado_tiempo), "Temperatura", f"{m.temperatura_c} °C" if m.temperatura_c is not None else "—"],
            ["Precipitación", f"{m.precipitacion_mm} mm" if m.precipitacion_mm is not None else "—",
             "Viento", f"{m.viento_kmh} km/h" if m.viento_kmh is not None else "—"],
            ["Calzada (estimada)", _safe(m.calzada_estimada),
             "Visibilidad", f"{int(m.visibilidad_m)} m" if m.visibilidad_m else "—"],
            ["Iluminación natural", "día" if m.es_dia else "noche" if m.es_dia is False else "—",
             "Amanecer / atardecer", f"{m.amanecer or '—'} / {m.atardecer or '—'}"],
        ]
        t = Table(rows, colWidths=[3.2 * cm, 5 * cm, 3 * cm, 4.8 * cm])
        t.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONT", (2, 0), (2, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
            ("TEXTCOLOR", (2, 0), (2, -1), PRIMARY),
            ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_BG),
            ("BOX", (0, 0), (-1, -1), 0.5, RULE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        if m.fuente:
            story.append(Paragraph(f"<i>Fuente:</i> {_safe(m.fuente)}", s["Small"]))
        story.append(Spacer(1, 6))

    # ─────────────────── 2.ter CARACTERIZACIÓN DE LA VÍA ─────────────────────
    if informe.contexto_escena:
        e = informe.contexto_escena
        story.append(Paragraph("2.2 Caracterización de la vía (OpenStreetMap + Open-Elevation)", s["H2"]))
        if e.direccion_resuelta:
            story.append(Paragraph(
                f"<b>Localización resuelta:</b> {_safe(e.direccion_resuelta)} "
                f"<font size=8 color='#64748b'>({e.lat_resuelta:.5f}, {e.lon_resuelta:.5f})</font>",
                s["Body"]))
        rows = [
            ["Vía", _safe(e.via_principal_nombre or e.via_principal_tipo),
             "Tipo OSM", _safe(e.via_principal_tipo)],
            ["Velocidad máxima OSM", f"{e.velocidad_maxima_kmh} km/h" if e.velocidad_maxima_kmh else "—",
             "Carriles", _safe(e.num_carriles)],
            ["Anchura", f"{e.anchura_m} m" if e.anchura_m else "—",
             "Superficie", _safe(e.superficie)],
            ["Pendiente (DEM)", f"{e.pendiente_pct} %" if e.pendiente_pct is not None else "—",
             "Carril bici", "sí" if e.tiene_carril_bici else "no"],
            ["Pasos de peatones próximos", str(e.pasos_peatones_proximos),
             "Imágenes Mapillary", str(e.n_imagenes_mapillary)],
        ]
        t = Table(rows, colWidths=[4.5 * cm, 3.7 * cm, 3 * cm, 4.8 * cm])
        t.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONT", (2, 0), (2, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
            ("TEXTCOLOR", (2, 0), (2, -1), PRIMARY),
            ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_BG),
            ("BOX", (0, 0), (-1, -1), 0.5, RULE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        if e.senales:
            story.append(Paragraph(
                f"<b>Señales detectadas en {len(e.senales)} elementos:</b> "
                + "; ".join(s_["tipo"] for s_ in e.senales[:8] if s_.get("tipo")),
                s["Small"]))
        if e.fuentes:
            story.append(Paragraph(
                "<i>Fuentes:</i> " + " · ".join(_safe(f) for f in e.fuentes), s["Small"]))
        story.append(Spacer(1, 6))

    # ─────────────────── 3. VEHÍCULOS ───────────────────────────────────────
    story.append(Paragraph("3. Vehículos implicados", s["H1"]))
    story.append(_section_rule(s))
    if not informe.fichas_tecnicas:
        story.append(Paragraph("Sin vehículos identificados.", s["Body"]))
    for f in informe.fichas_tecnicas:
        story.append(Paragraph(
            f"Vehículo {f.vehiculo_id} — {f.marca} {f.modelo}"
            + (f" ({f.anio})" if f.anio else ""), s["H2"]))
        info = []
        if f.masa_kg: info.append(f"masa <b>{f.masa_kg} kg</b>")
        if f.longitud_m: info.append(f"longitud {f.longitud_m} m")
        if f.altura_parachoques_m:
            info.append(f"parachoques {f.altura_parachoques_m[0]}–{f.altura_parachoques_m[1]} m")
        if f.altura_largueros_m: info.append(f"largueros {f.altura_largueros_m} m")
        if info:
            story.append(Paragraph(" · ".join(info), s["Body"]))
        if f.sistemas_seguridad:
            story.append(Paragraph(
                "<b>Sistemas de seguridad:</b> " + "; ".join(f.sistemas_seguridad) + ".",
                s["Body"]))
        if f.fuente:
            story.append(Paragraph(f"<i>Fuente:</i> {_safe(f.fuente)}", s["Small"]))
        story.append(Spacer(1, 4))

    # ─────────────────── 4. ANÁLISIS TÉCNICO ────────────────────────────────
    if informe.calculos:
        story.append(Paragraph("4. Análisis técnico y cálculos", s["H1"]))
        story.append(_section_rule(s))
        for c in informe.calculos:
            story.append(Paragraph(
                f"<b>{_safe(c.nombre)}</b> &nbsp; "
                f"<font color='#b45309'><b>{c.valor} {c.unidad}</b></font>",
                s["Body"]))
            story.append(Paragraph(_safe(c.formula), s["Mono"]))
            story.append(Paragraph(_safe(c.justificacion), s["Small"]))
            story.append(Spacer(1, 4))

    # ─────────────────── 5. MARCO NORMATIVO ─────────────────────────────────
    if informe.normativa_aplicable:
        story.append(Paragraph("5. Marco normativo aplicable", s["H1"]))
        story.append(_section_rule(s))
        for n in informe.normativa_aplicable:
            block = []
            # Construir URL BOE/EUR-Lex consolidada
            ref_lower = (n.referencia or "").lower()
            if "rgc" in ref_lower or "1428/2003" in ref_lower:
                url_consolidada = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514"
            elif "lsv" in ref_lower or "6/2015" in ref_lower:
                url_consolidada = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11722"
            elif "ece-r12" in ref_lower:
                url_consolidada = "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:42010X0327(01)"
            elif "fmvss" in ref_lower:
                url_consolidada = "https://www.ecfr.gov/current/title-49/section-571.208"
            elif "rgv" in ref_lower or "2822/1998" in ref_lower:
                url_consolidada = "https://www.boe.es/buscar/act.php?id=BOE-A-1999-1826"
            elif "8/2004" in ref_lower:
                url_consolidada = "https://www.boe.es/buscar/act.php?id=BOE-A-2004-18911"
            elif "970/2020" in ref_lower:
                url_consolidada = "https://www.boe.es/buscar/act.php?id=BOE-A-2020-13969"
            else:
                url_consolidada = None

            block.append(Paragraph(
                f"<b>{_safe(n.referencia)}</b> &nbsp; "
                f"<font size=8 color='#64748b'>{_safe(n.boe)}</font>", s["H2"]))
            block.append(Paragraph(_safe(n.titulo), s["Body"]))
            if n.extracto:
                block.append(Paragraph("«" + _safe(n.extracto) + "»", s["Quote"]))
            if url_consolidada:
                block.append(Paragraph(
                    f"<font size=8 color='#1e40af'>"
                    f"<link href='{url_consolidada}'>↗ Texto consolidado: {url_consolidada}</link>"
                    f"</font>", s["Small"]))
            block.append(Spacer(1, 3))
            story.append(KeepTogether(block))

    # ─────────────────── 6. RECONSTRUCCIÓN GRÁFICA ──────────────────────────
    frames = [i for i in informe.imagenes if (i.fuente or "").startswith("Simulacion")]
    fotos_perito = [i for i in informe.imagenes if (i.fuente or "").lower() == "perito"]
    mapillary = [i for i in informe.imagenes if (i.fuente or "").lower() == "mapillary"]

    if frames or fotos_perito or mapillary:
        story.append(Paragraph("6. Reconstrucción gráfica del siniestro", s["H1"]))
        story.append(_section_rule(s))

        # 6.1 Frames del motor (SVG)
        if frames:
            story.append(Paragraph("6.1 Frames del motor de reconstrucción Veridict", s["H2"]))
            for fr in frames[:6]:
                if fr.url:
                    drawing = _embed_svg_local(fr.url, uploads_root, max_w_cm=15, max_h_cm=10)
                    if drawing is not None:
                        story.append(drawing)
                if fr.descripcion:
                    story.append(Paragraph(_safe(fr.descripcion), s["Small"]))
                if fr.relevancia:
                    story.append(Paragraph(f"<i>{_safe(fr.relevancia)}</i>", s["Small"]))
                story.append(Spacer(1, 6))

        # 6.2 Fotos del perito
        if fotos_perito:
            story.append(Paragraph("6.2 Fotografías aportadas por el perito", s["H2"]))
            for img in fotos_perito[:8]:
                rl = _embed_local_image(img.url or "", uploads_root, max_w_cm=12, max_h_cm=8)
                if rl is not None:
                    story.append(rl)
                if img.descripcion:
                    story.append(Paragraph(_safe(img.descripcion), s["Quote"]))
                story.append(Spacer(1, 4))

        # 6.3 Imágenes Mapillary descargadas
        if mapillary:
            story.append(Paragraph("6.3 Imágenes ground-level del entorno (Mapillary)", s["H2"]))
            for img in mapillary[:4]:
                rl = _embed_remote_image(img.url or "", max_w_cm=12, max_h_cm=8)
                if rl is not None:
                    story.append(rl)
                meta = []
                if img.compass_angle is not None:
                    meta.append(f"orientación {int(img.compass_angle)}°")
                if img.captured_at:
                    meta.append(f"captura {img.captured_at}")
                if meta:
                    story.append(Paragraph(" · ".join(meta), s["Small"]))
                if img.descripcion:
                    story.append(Paragraph(_safe(img.descripcion), s["Small"]))
                story.append(Spacer(1, 4))

    # ─────────────────── 7. ESTUDIO BIOMECÁNICO ─────────────────────────────
    bio = informe.analisis_biomecanico
    if bio:
        story.append(PageBreak())
        story.append(Paragraph("7. Estudio biomecánico", s["H1"]))
        story.append(_section_rule(s))
        story.append(Paragraph(
            "Análisis biomecánico aplicando el Manual ESTT/DGT 2011, las tablas WAD "
            "(Wrap Around Distance) de Otte 1989, Searle 1993 y Van Rooij 2003 y las curvas "
            "de probabilidad AIS 3+ de Mertz/NHTSA.", s["Body"]))

        # 7.1 KPIs principales en tarjetas (tabla)
        kpi_rows = []
        if bio.wad:
            kpi_rows.append([
                "Zona de impacto (WAD)",
                f"{bio.wad.zona_impacto}\n"
                f"({bio.wad.altura_m[0]:.2f}–{bio.wad.altura_m[1]:.2f} m)",
                "Velocidad mínima compatible",
                f"{bio.wad.velocidad_min_kmh:.0f} – {bio.wad.velocidad_max_kmh:.0f} km/h",
            ])
        if bio.energia_cinetica_kj is not None:
            kpi_rows.append([
                "Energía cinética estimada", f"{bio.energia_cinetica_kj:.1f} kJ",
                "Probabilidad AIS 3+",
                f"{bio.probabilidad_ais3_pct or '—'} %" if bio.probabilidad_ais3_pct is not None else "—",
            ])
        if bio.compatibilidad_velocidad_lesion:
            kpi_rows.append([
                "Compatibilidad velocidad ↔ lesión",
                bio.compatibilidad_velocidad_lesion,
                "", "",
            ])

        if kpi_rows:
            t = Table(kpi_rows, colWidths=[4.5 * cm, 4.5 * cm, 3.5 * cm, 4 * cm])
            t.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONT", (2, 0), (2, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
                ("TEXTCOLOR", (2, 0), (2, -1), PRIMARY),
                ("TEXTCOLOR", (3, 0), (3, -1), ACCENT),
                ("FONT", (3, 0), (3, -1), "Helvetica-Bold"),
                ("FONTSIZE", (3, 0), (3, -1), 10),
                ("BACKGROUND", (0, 0), (-1, -1), NEUTRAL_BG),
                ("BOX", (0, 0), (-1, -1), 0.6, PRIMARY),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
            if bio.wad and bio.wad.fuente:
                story.append(Paragraph(
                    f"<i>Tabla WAD — fuente:</i> {_safe(bio.wad.fuente)}", s["Small"]))
                story.append(Spacer(1, 6))

        # 7.2 Mecanismos lesivos compatibles
        if bio.mecanismos_lesivos_compatibles:
            story.append(Paragraph("7.1 Mecanismos lesivos compatibles", s["H2"]))
            story.append(Paragraph(
                "Tras analizar la descripción de las lesiones, los mecanismos lesivos del "
                "Manual ESTT/DGT 2011 cuya activación es compatible son:", s["Body"]))
            rows = [["Mecanismo", "Razón clínica"]]
            for m in bio.mecanismos_lesivos_compatibles:
                rows.append([
                    Paragraph(f"<b>{_safe(m.nombre)}</b>", s["Small"]),
                    Paragraph(_safe(m.razon or m.descripcion), s["Small"]),
                ])
            t = Table(rows, colWidths=[3.5 * cm, 13 * cm], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), NEUTRAL_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))

        # 7.3 Cadena de 4 impactos sucesivos (siempre informativo)
        if bio.cadena_4_impactos_sucesivos:
            story.append(Paragraph("7.2 Cadena de impactos sucesivos", s["H2"]))
            story.append(Paragraph(
                "Toda colisión genera una secuencia de hasta cuatro impactos sucesivos "
                "(Manual ESTT/DGT 2011). Determinarlos permite explicar la lesividad final:",
                s["Body"]))
            rows = [["#", "Descripción"]]
            for i in bio.cadena_4_impactos_sucesivos:
                rows.append([
                    Paragraph(f"<b>{i.orden}</b>", s["Small"]),
                    Paragraph(_safe(i.descripcion), s["Small"]),
                ])
            t = Table(rows, colWidths=[1.2 * cm, 15.3 * cm], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), NEUTRAL_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))

        # 7.4 Análisis cefálico (cráneo) si aplica
        if bio.analisis_craneal:
            story.append(Paragraph("7.3 Análisis cefálico (lesiones craneoencefálicas)", s["H2"]))
            story.append(Paragraph(_safe(bio.analisis_craneal.mecanismo_general), s["Body"]))
            if bio.analisis_craneal.tipos_compatibles:
                rows = [["Tipo de lesión", "Mecanismo lesivo"]]
                for t_les in bio.analisis_craneal.tipos_compatibles:
                    rows.append([
                        Paragraph(f"<b>{_safe(t_les.nombre)}</b>", s["Small"]),
                        Paragraph(_safe(t_les.mecanismo), s["Small"]),
                    ])
                t = Table(rows, colWidths=[5 * cm, 11.5 * cm], repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), DANGER),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                    ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fef2f2")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
            if bio.analisis_craneal.consideracion_clinica:
                story.append(Paragraph(
                    "<b>Consideración clínica:</b> " + _safe(bio.analisis_craneal.consideracion_clinica),
                    s["Quote"]))
                story.append(Spacer(1, 8))

        # 7.5 Tabla de aceleraciones tipo (referencia)
        if bio.tabla_aceleraciones_tipo:
            story.append(Paragraph("7.4 Tabla de referencia — aceleraciones por tipo de impacto", s["H2"]))
            rows = [["Situación", "Tiempo de parada", "Aceleración (g)", "Fuerza (N) · 1200 kg"]]
            for a in bio.tabla_aceleraciones_tipo:
                rows.append([
                    a.situacion, a.tiempo_parada,
                    f"{a.aceleracion_g:.1f}",
                    f"{a.fuerza_n_1200kg:,.0f}".replace(",", "."),
                ])
            t = Table(rows, colWidths=[5.5 * cm, 3 * cm, 3 * cm, 5 * cm], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 1), (-1, -1), NEUTRAL_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))

        # 7.6 Fuentes
        if bio.fuentes:
            story.append(Paragraph("7.5 Fuentes consultadas", s["H2"]))
            for f in bio.fuentes:
                story.append(Paragraph(f"· {_safe(f)}", s["Small"]))

    # ─────────────────── 8. CONCLUSIONES ────────────────────────────────────
    if informe.respuestas:
        story.append(PageBreak())
        story.append(Paragraph("8. Conclusiones periciales", s["H1"]))
        story.append(_section_rule(s))
        story.append(Paragraph(
            "Respuesta razonada a cada cuestión planteada en el encargo. Las citas remiten "
            "a los cálculos, normativa, fichas técnicas, frames de simulación e imágenes del "
            "expediente.", s["Body"]))
        story.append(Spacer(1, 6))
        for r in informe.respuestas:
            block = []
            block.append(Paragraph(
                f"<font color='{PRIMARY.hexval()}'><b>{_safe(r.pregunta_id)}.</b></font> "
                f"<b>{_safe(r.pregunta)}</b>", s["H2"]))
            block.append(Paragraph(_safe(r.respuesta), s["Body"]))
            if r.citas:
                cit = " &nbsp; ".join(
                    [f"<font color='#1e40af'>[{_safe(c.tipo)}: {_safe(c.referencia)}]</font>"
                     for c in r.citas]
                )
                block.append(Paragraph(cit, s["Cite"]))
            color_conf = OK if r.confianza >= 0.7 else (ACCENT if r.confianza >= 0.5 else DANGER)
            block.append(Paragraph(
                f"<font color='{color_conf.hexval()}'>"
                f"Confianza de la respuesta: <b>{int(round(r.confianza * 100))}%</b></font>",
                s["Small"]))
            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

    # ─────────────────── 8.bis CRÍTICA METODOLÓGICA AL ATESTADO ────────────
    if informe.conformidad_atestado:
        c = informe.conformidad_atestado
        story.append(PageBreak())
        story.append(Paragraph("8.1 Crítica metodológica al atestado policial", s["H1"]))
        story.append(_section_rule(s))
        story.append(Paragraph(
            "Análisis automatizado de la conformidad técnica del atestado, aplicando "
            "ocho reglas (R1–R8) basadas en la práctica pericial reconocida (IURGI/AEIAT, "
            "Brach 2011, Limpert 2012). NO sustituye la valoración judicial.", s["Body"]))

        valoracion_color = OK if c.valoracion_global == "satisfactorio" else (
            ACCENT if c.valoracion_global == "incompleto" else DANGER)
        story.append(Paragraph(
            f"<b>Valoración global:</b> "
            f"<font color='{valoracion_color.hexval()}'>"
            f"<b>{(c.valoracion_global or '—').upper()}</b></font>",
            s["Highlight"]))

        if c.incongruencias:
            story.append(Paragraph("Incongruencias detectadas", s["H2"]))
            rows = [["Severidad", "Título", "Descripción"]]
            for inc in c.incongruencias:
                sev = (inc.severidad or "media").upper()
                color = DANGER if sev == "ALTA" else (ACCENT if sev == "MEDIA" else colors.HexColor("#475569"))
                rows.append([
                    Paragraph(f"<font color='{color.hexval()}'><b>{sev}</b></font>", s["Small"]),
                    Paragraph(f"<b>{_safe(inc.titulo)}</b>", s["Small"]),
                    Paragraph(_safe(inc.descripcion), s["Small"]),
                ])
            t = Table(rows, colWidths=[1.8 * cm, 4.2 * cm, 10.5 * cm], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), NEUTRAL_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))

        if c.elementos_omitidos:
            story.append(Paragraph("Elementos omitidos en el atestado", s["H2"]))
            for o in c.elementos_omitidos:
                story.append(Paragraph(f"&nbsp;&nbsp;· {_safe(o)}", s["Body"]))
            story.append(Spacer(1, 4))

        if c.recomendaciones:
            story.append(Paragraph("Recomendaciones", s["H2"]))
            for r in c.recomendaciones:
                story.append(Paragraph(f"&nbsp;&nbsp;· {_safe(r)}", s["Body"]))

    # ─────────────────── 9. INFO FALTANTE ───────────────────────────────────
    if informe.info_faltante:
        story.append(Paragraph("9. Información requerida del perito firmante", s["H1"]))
        story.append(_section_rule(s))
        for q in informe.info_faltante:
            badge = q.prioridad.value.upper() if hasattr(q.prioridad, 'value') else str(q.prioridad).upper()
            color = DANGER if badge == "BLOQUEANTE" else (ACCENT if badge == "RECOMENDABLE" else colors.HexColor("#475569"))
            tag_foto = "  📷 [REQUIERE FOTO]" if q.requiere_foto else ""
            story.append(Paragraph(
                f"<font color='{color.hexval()}'><b>[{badge}]{tag_foto}</b></font> "
                f"{_safe(q.pregunta)}", s["Body"]))
            story.append(Paragraph(_safe(q.motivo), s["Small"]))
            story.append(Spacer(1, 3))

    # ─────────────────── 10. BIBLIOGRAFÍA ───────────────────────────────────
    if informe.bibliografia:
        story.append(Paragraph("10. Bibliografía técnica", s["H1"]))
        story.append(_section_rule(s))
        for i, b in enumerate(informe.bibliografia, 1):
            story.append(Paragraph(f"{i}. {_safe(b)}", s["Body"]))

    # ─────────────────── 11. ANEXO TRAZABILIDAD AGENTES ─────────────────────
    if informe.tool_calls:
        story.append(PageBreak())
        story.append(Paragraph("11. Anexo de trazabilidad — agentes consultados", s["H1"]))
        story.append(_section_rule(s))
        story.append(Paragraph(
            "Detalle de cada invocación realizada por el perito coordinador (Veridict-Perito) "
            "a sus agentes especialistas. Se documenta agente, pregunta, resultado resumido, "
            "fuentes consultadas y duración.", s["Body"]))
        rows = [["Agente", "Pregunta", "Resultado", "Fuentes", "ms"]]
        for tc in informe.tool_calls:
            rows.append([
                Paragraph(f"<b>{_safe(tc.agente)}</b>", s["Small"]),
                Paragraph(_safe(tc.pregunta)[:120], s["Small"]),
                Paragraph(_safe(tc.resultado_resumen)[:140], s["Small"]),
                Paragraph(_safe("; ".join(tc.fuentes_consultadas))[:120], s["Small"]),
                Paragraph(str(tc.duracion_ms or 0), s["Small"]),
            ])
        t = Table(rows, colWidths=[3 * cm, 3.6 * cm, 4.4 * cm, 4.0 * cm, 1.2 * cm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
            ("BOX", (0, 0), (-1, -1), 0.5, RULE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), NEUTRAL_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

    # Cierre
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "<i>Borrador asistido por Veridict AI — Multi-agente con tool_use real (Claude Opus 4.7). "
        "La calificación última corresponde al perito firmante. Este documento NO constituye "
        "atribución de culpa.</i>", s["Small"]))

    doc.build(story)
    return output_path

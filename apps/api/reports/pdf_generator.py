"""
PDF Generator for UNE-EN 16775 format reports.

Generates professional forensic reports in the standard format
required for Spanish judicial proceedings.
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from models import Caso


async def generate_pdf(caso: Caso) -> bytes:
    """
    Generate PDF report in UNE-EN 16775 format.

    Args:
        caso: The case to generate report for

    Returns:
        PDF bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center
    )
    story.append(Paragraph("INFORME PERICIAL DE ACCIDENTE DE TRAFICO", title_style))
    story.append(Paragraph(f"Caso: {caso.id}", styles["Heading2"]))
    story.append(Spacer(1, 20))

    # Case info
    story.append(Paragraph("1. DATOS DEL ACCIDENTE", styles["Heading2"]))
    info_data = [
        ["Fecha:", caso.fecha_accidente.strftime("%d/%m/%Y %H:%M")],
        ["Ubicacion:", f"{caso.ubicacion.lat:.6f}, {caso.ubicacion.lon:.6f}"],
        ["Tipo de colision:", caso.tipo_colision.value.capitalize()],
    ]
    info_table = Table(info_data, colWidths=[4 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Vehicles
    if caso.vehiculos:
        story.append(Paragraph("2. VEHICULOS IMPLICADOS", styles["Heading2"]))
        for v in caso.vehiculos:
            story.append(Paragraph(f"Vehiculo {v.id}", styles["Heading3"]))
            v_data = [
                ["Matricula:", v.matricula or "N/A"],
                ["Modelo:", v.modelo or "N/A"],
                ["Masa:", f"{v.masa_kg} kg" if v.masa_kg else "N/A"],
            ]
            v_table = Table(v_data, colWidths=[4 * cm, 12 * cm])
            story.append(v_table)
            story.append(Spacer(1, 10))

    # Results
    if caso.resultado:
        # Chronology
        story.append(Paragraph("3. CRONOLOGIA DEL ACCIDENTE", styles["Heading2"]))
        for evento in caso.resultado.cronologia:
            story.append(
                Paragraph(f"T+{evento.timestamp}s: {evento.descripcion}", styles["Normal"])
            )
        story.append(Spacer(1, 20))

        # Calculations
        story.append(Paragraph("4. CALCULOS FISICOS", styles["Heading2"]))
        for calc in caso.resultado.calculos:
            story.append(Paragraph(f"<b>{calc.nombre}</b>", styles["Normal"]))
            story.append(Paragraph(f"Formula: {calc.formula}", styles["Normal"]))
            story.append(
                Paragraph(f"Resultado: {calc.valor} {calc.unidad}", styles["Normal"])
            )
            story.append(Paragraph(f"Justificacion: {calc.justificacion}", styles["Normal"]))
            story.append(Spacer(1, 10))

        # Legal
        story.append(Paragraph("5. INFRACCIONES DETECTADAS", styles["Heading2"]))
        for inf in caso.resultado.infracciones:
            story.append(
                Paragraph(
                    f"<b>{inf.articulo}</b> - Vehiculo {inf.vehiculo}", styles["Normal"]
                )
            )
            story.append(Paragraph(inf.descripcion, styles["Normal"]))
            story.append(Paragraph(f"Fuente: {inf.fuente}", styles["Normal"]))
            story.append(Spacer(1, 10))

        # Verdict
        if caso.resultado.veredicto:
            story.append(Paragraph("6. CONCLUSION", styles["Heading2"]))
            v = caso.resultado.veredicto
            story.append(
                Paragraph(
                    f"Atribucion de responsabilidad: "
                    f"Vehiculo A: {v.culpa_a * 100:.0f}%, "
                    f"Vehiculo B: {v.culpa_b * 100:.0f}%",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(f"Nivel de confianza: {v.confidence * 100:.0f}%", styles["Normal"])
            )

        # Version compatibility
        if caso.resultado.compatibilidad_versiones:
            story.append(Spacer(1, 10))
            comp = caso.resultado.compatibilidad_versiones
            story.append(Paragraph("Compatibilidad de versiones:", styles["Normal"]))
            story.append(Paragraph(comp.justificacion, styles["Normal"]))

    # Footer
    story.append(Spacer(1, 40))
    story.append(
        Paragraph(
            "Informe generado automaticamente por Veridict AI. "
            "Formato UNE-EN 16775.",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        )
    )

    doc.build(story)
    return buffer.getvalue()

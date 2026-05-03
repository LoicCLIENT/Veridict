"""Genera un PDF en formato atestado policial Ertzaintza para el caso Aulestia
21/05/2020. Solo texto estructurado en diligencias, sin imágenes intercaladas.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


OUT = Path(r"c:/Users/javie/OneDrive/Escritorio/Veridict/atestado_ertzaintza_aulestia.pdf")


def _styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("Cabecera", fontName="Helvetica-Bold", fontSize=12, leading=14,
                            alignment=1, textColor=colors.black, spaceAfter=2))
    base.add(ParagraphStyle("CabeceraSub", fontName="Helvetica", fontSize=10, leading=13,
                            alignment=1, textColor=colors.HexColor("#374151"), spaceAfter=2))
    base.add(ParagraphStyle("TituloAtestado", fontName="Helvetica-Bold", fontSize=14, leading=18,
                            alignment=1, spaceBefore=14, spaceAfter=10))
    base.add(ParagraphStyle("Diligencia", fontName="Helvetica-Bold", fontSize=11, leading=14,
                            spaceBefore=12, spaceAfter=4,
                            textColor=colors.HexColor("#0f172a")))
    base.add(ParagraphStyle("BodyAt", fontName="Times-Roman", fontSize=11, leading=15,
                            alignment=4, spaceAfter=5, firstLineIndent=14))
    base.add(ParagraphStyle("BodyAtNoIndent", fontName="Times-Roman", fontSize=11, leading=15,
                            alignment=4, spaceAfter=5))
    base.add(ParagraphStyle("Firma", fontName="Helvetica-Oblique", fontSize=10, leading=13,
                            alignment=1, spaceBefore=24, textColor=colors.HexColor("#374151")))
    base.add(ParagraphStyle("Pie", fontName="Helvetica", fontSize=8, leading=11,
                            textColor=colors.HexColor("#6b7280"), alignment=1))
    return base


def _chrome(canvas, doc):
    canvas.saveState()
    # Cabecera fija con sello Ertzaintza
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#1f2937"))
    canvas.drawString(2 * cm, A4[1] - 1.0 * cm, "ERTZAINTZA · Eusko Jaurlaritza – Gobierno Vasco")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.0 * cm,
                           "Atestado · Diligencias nº 994/2020 · Aulestia")
    canvas.setStrokeColor(colors.HexColor("#9ca3af"))
    canvas.line(2 * cm, A4[1] - 1.2 * cm, A4[0] - 2 * cm, A4[1] - 1.2 * cm)
    # Pie con paginación
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(2 * cm, 1.0 * cm, "ERTZAINTZA · Comisaría de Markina-Xemein")
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"Folio nº {doc.page}")
    canvas.line(2 * cm, 1.2 * cm, A4[0] - 2 * cm, 1.2 * cm)
    canvas.restoreState()


def main():
    doc = BaseDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2.0 * cm, bottomMargin=1.8 * cm,
        title="Atestado Ertzaintza — Aulestia 21052020",
        author="Ertzaintza",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="m")
    doc.addPageTemplates([PageTemplate(id="t", frames=frame, onPage=_chrome)])

    s = _styles()
    story = []

    # ── Cabecera ───────────────────────────────────────────────────────────
    story.append(Paragraph("DEPARTAMENTO DE SEGURIDAD", s["Cabecera"]))
    story.append(Paragraph("Eusko Jaurlaritza — Gobierno Vasco", s["CabeceraSub"]))
    story.append(Paragraph("ERTZAINTZA — Comisaría de Markina-Xemein", s["CabeceraSub"]))
    story.append(Paragraph("Sección de Tráfico — Equipo de Atestados", s["CabeceraSub"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "ATESTADO INSTRUIDO POR HECHOS RELACIONADOS CON LA CIRCULACIÓN VIAL",
        s["TituloAtestado"]))
    story.append(Paragraph(
        "Diligencias nº 994/2020 — Atropello con resultado de muerte",
        ParagraphStyle("subtitulo", parent=s["CabeceraSub"], fontSize=11)))

    # Tabla de datos administrativos
    rows = [
        ["Hecho", "Atropello mortal a ciclista por turismo en zona urbana"],
        ["Fecha", "21 de mayo de 2020"],
        ["Hora", "20:38 h"],
        ["Lugar", "Barrio Zubero auzoa, Aulestia (Bizkaia)"],
        ["Calificación provisional", "Homicidio por imprudencia grave (art. 142 CP) y/o "
                                      "delito contra la seguridad vial (arts. 379 y ss. CP), "
                                      "a determinar por la Autoridad Judicial"],
        ["Juzgado al que se remite", "Juzgado de Instrucción de Markina-Xemein"],
        ["Instructor del atestado", "Agente nº 12.345 — Ertzaintza"],
        ["Secretario", "Agente nº 67.890 — Ertzaintza"],
    ]
    t = Table(rows, colWidths=[4.5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9ca3af")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # ── DILIGENCIA PRIMERA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA PRIMERA.— Para hacer constar la formación del atestado",
        s["Diligencia"]))
    story.append(Paragraph(
        "En la villa de Markina-Xemein (Bizkaia), siendo las 21:15 horas del día 21 de mayo "
        "de 2020, el agente del cuerpo de la Ertzaintza con número profesional 12.345, "
        "actuando como Instructor, asistido por el agente nº 67.890 que actúa como Secretario, "
        "procede a la incoación del presente atestado como consecuencia de los hechos "
        "ocurridos a las 20:38 horas en el Barrio Zubero auzoa de Aulestia (Bizkaia), "
        "que han tenido como resultado el fallecimiento de una persona.", s["BodyAt"]))
    story.append(Paragraph(
        "Se procede a hacer constar las diligencias practicadas, cuyas resultas se reflejan "
        "en los apartados siguientes.", s["BodyAt"]))

    # ── DILIGENCIA SEGUNDA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA SEGUNDA.— Inspección ocular del lugar de los hechos",
        s["Diligencia"]))
    story.append(Paragraph(
        "Personados los actuantes en el lugar de los hechos a las 20:51 horas, se constata "
        "que el siniestro ha tenido lugar en una vía urbana del Barrio Zubero auzoa de "
        "Aulestia, en una zona de pendiente ascendente para el sentido de circulación del "
        "vehículo turismo y descendente para el ciclista, con trazado en curva.", s["BodyAt"]))
    story.append(Paragraph(
        "<b>Características de la vía:</b> calzada de doble sentido sin separación física, "
        "con anchura aproximada de 3,15 metros (medida con cinta métrica entre bordes), "
        "pavimento de asfalto en buen estado de conservación y seco al momento de los "
        "hechos. La pendiente del tramo se estima entre el 9 % y el 11,6 %. Existe en el "
        "margen derecho de la vía, según el sentido de circulación del turismo, una franja "
        "terriza de varios metros de anchura, prácticamente diáfana, con un desnivel máximo "
        "de cuatro centímetros respecto a la calzada.", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Limitación de velocidad en el tramo:</b> según los datos disponibles a estos "
        "instructores, la vía está sujeta a la limitación genérica de 30 km/h propia de las "
        "vías urbanas. No se aporta fotografía de señalización vertical específica.",
        s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Visibilidad:</b> se aprecia desde el sentido de marcha del turismo una "
        "visibilidad limitada por el trazado en curva, estimándose una distancia de "
        "visibilidad efectiva de aproximadamente 20 metros lineales.", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Condiciones meteorológicas:</b> tarde clara, sin precipitaciones, asfalto seco, "
        "iluminación natural diurna suficiente.", s["BodyAtNoIndent"]))

    # ── DILIGENCIA TERCERA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA TERCERA.— Identificación e inspección de los vehículos implicados",
        s["Diligencia"]))
    story.append(Paragraph(
        "<b>Vehículo 1 (turismo):</b> SEAT Ibiza, 5 puertas, color blanco, matrícula "
        "<b>3526-BKL</b>, año de matriculación 2018. Conducido en el momento de los hechos "
        "por D. JME, mayor de edad, vecino del propio Barrio Zubero, en posesión de permiso "
        "de conducción tipo B en vigor. Daños observados: parabrisas delantero fracturado "
        "principalmente en su lado derecho; hendidura en techo extremo derecho; daños "
        "estructurales en paragolpes delantero, principalmente lateral derecho, faltando la "
        "tapa inferior del paragolpes a esa altura; daños menores en capó (impronta visible "
        "compatible con deslizamiento de cuerpo).", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Vehículo 2 (bicicleta):</b> Bicicleta marca Orbea, color rojo, número de "
        "bastidor 3773. Sillín a 79 cm del suelo y manillar de 55 cm de anchura. Conducida "
        "por D. IBU, mayor de edad. Daños: cuadro deformado, marcas de derrape en cubierta "
        "trasera, ruedas desalineadas.", s["BodyAtNoIndent"]))

    story.append(PageBreak())

    # ── DILIGENCIA CUARTA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA CUARTA.— Toma de declaración al conductor del vehículo turismo",
        s["Diligencia"]))
    story.append(Paragraph(
        "Siendo las 21:42 horas, en presencia de los actuantes y previa lectura de sus "
        "derechos como investigado, el conductor del turismo D. JME manifiesta lo siguiente:",
        s["BodyAt"]))
    story.append(Paragraph(
        "<i>«Que circulaba con el SEAT Ibiza por el Barrio Zubero auzoa, en sentido "
        "ascendente, a una velocidad que estima entre los diez y los veinte kilómetros por "
        "hora. Que es vecino del barrio y conoce sobradamente el trazado, la pendiente y "
        "la limitación de velocidad. Que al tomar la curva vio aparecer al ciclista en "
        "sentido contrario y, según su propio relato, accionó el freno al máximo de sus "
        "posibilidades. Que en el momento del impacto el vehículo turismo no se encontraba "
        "totalmente detenido. Que tras el impacto descendió del vehículo y procedió a llamar "
        "a los servicios de emergencia. Que no había ingerido bebidas alcohólicas ni se "
        "encontraba bajo los efectos de medicamentos o estupefacientes.»</i>", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "El conductor firma la declaración tras serle leída íntegramente y mostrar su "
        "conformidad con su contenido.", s["BodyAt"]))

    # ── DILIGENCIA QUINTA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA QUINTA.— Sobre la víctima y la imposibilidad de toma de declaración",
        s["Diligencia"]))
    story.append(Paragraph(
        "El ciclista D. IBU, conductor del vehículo nº 2, presenta a la llegada de los "
        "primeros servicios sanitarios lesiones de extrema gravedad, principalmente en "
        "región cefálica, siendo evacuado al Centro Hospitalario más próximo. A las 21:55 "
        "horas se confirma su fallecimiento por el equipo médico, sin que haya sido posible "
        "tomarle declaración. Las lesiones son aparentemente compatibles con un impacto en "
        "región frontal y craneal contra estructura del vehículo turismo (parabrisas y "
        "umbral del techo).", s["BodyAt"]))

    # ── DILIGENCIA SEXTA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA SEXTA.— Trayectoria estimada y croquis",
        s["Diligencia"]))
    story.append(Paragraph(
        "Atendidas las posiciones finales de los vehículos, los daños observados y las "
        "marcas en la calzada, se estima provisionalmente la siguiente dinámica:",
        s["BodyAt"]))
    story.append(Paragraph(
        "El vehículo turismo circulaba en sentido ascendente por su mitad derecha de la "
        "calzada cuando entró en contacto con el ciclista, que lo hacía en sentido "
        "descendente, también por su mitad derecha. El impacto se produce con la zona "
        "delantera derecha del turismo (paragolpes, capó y parabrisas), siendo proyectado "
        "el cuerpo del ciclista sobre el capó y posteriormente sobre el parabrisas y "
        "umbral del techo, antes de caer a la calzada. La bicicleta queda detenida a "
        "escasos metros del punto de impacto. Tras la colisión, según declaración del "
        "conductor, el turismo retrocede ligeramente. Se levanta el correspondiente "
        "croquis a mano alzada, sin escala numerada.", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Huellas y elementos sobre la calzada:</b> NO se observan huellas de frenado "
        "atribuibles al vehículo turismo. SÍ se aprecia una huella longitudinal de "
        "aproximadamente 8 metros, atribuible a la bicicleta, que finaliza a 1,2 metros "
        "del borde derecho de la calzada (sentido descendente del ciclista) e inicia a "
        "menos de 1 metro del mismo borde.", s["BodyAtNoIndent"]))
    story.append(Paragraph(
        "<b>Posiciones finales:</b> el turismo queda detenido prácticamente en el punto "
        "de impacto, ligeramente retrocedido. La bicicleta queda en el centro de la "
        "calzada. El ciclista resulta proyectado y queda en el margen derecho.",
        s["BodyAtNoIndent"]))

    # ── DILIGENCIA SÉPTIMA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA SÉPTIMA.— Pruebas de detección de alcohol y otras sustancias",
        s["Diligencia"]))
    story.append(Paragraph(
        "Practicada al conductor del vehículo turismo prueba de detección alcohólica "
        "mediante etilómetro evidencial, arroja resultado de 0,00 miligramos de alcohol "
        "por litro de aire espirado en ambas determinaciones realizadas con quince "
        "minutos de diferencia. NO se practican pruebas de detección de drogas u otras "
        "sustancias estupefacientes en el lugar.", s["BodyAt"]))

    # ── DILIGENCIA OCTAVA ────────────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA OCTAVA.— Conclusiones provisionales del instructor",
        s["Diligencia"]))
    story.append(Paragraph(
        "A juicio del instructor del atestado, y sin perjuicio de cuantas diligencias "
        "complementarias pueda acordar la Autoridad Judicial, se infiere razonadamente "
        "que el conductor del turismo SEAT Ibiza, conociendo la peligrosidad del trazado "
        "en curva y la limitación de velocidad genérica de 30 km/h propia del entorno "
        "urbano, pudo no haber adecuado su velocidad al campo de visión disponible, "
        "viéndose imposibilitado para detener el vehículo dentro de la zona visible al "
        "advertir la presencia del ciclista. La ausencia de huellas de frenado del "
        "turismo, pese a haber declarado el conductor frenada al máximo, podría apuntar "
        "asimismo a una falta de la atención debida a la circulación.", s["BodyAt"]))
    story.append(Paragraph(
        "El ciclista circulaba aparentemente por su mitad derecha de la calzada y "
        "realizó frenada que dejó huella visible, lo que sugiere percepción del riesgo "
        "y reacción defensiva.", s["BodyAt"]))
    story.append(Paragraph(
        "Se estima provisionalmente que el conductor del turismo pudo haber realizado "
        "una maniobra evasiva hacia su derecha, aprovechando la franja terriza diáfana "
        "existente en ese margen, sin que se observen circunstancias que se lo "
        "hubieran impedido.", s["BodyAt"]))

    # ── DILIGENCIA NOVENA — Cierre ────────────────────────────────────────
    story.append(Paragraph(
        "DILIGENCIA NOVENA.— Remisión de actuaciones",
        s["Diligencia"]))
    story.append(Paragraph(
        "Se acuerda la remisión inmediata del presente atestado al Juzgado de Instrucción "
        "de Markina-Xemein, junto con copia del acta de inspección ocular, croquis del "
        "lugar, reportaje fotográfico practicado por estos instructores y boletín de "
        "denuncia, quedando los vehículos depositados a disposición judicial.", s["BodyAt"]))
    story.append(Paragraph(
        "Y en prueba de conformidad se firma el presente atestado por el Instructor y "
        "Secretario, así como por el conductor declarante, todos en el lugar y fecha "
        "indicados.", s["BodyAt"]))

    story.append(Paragraph(
        "Markina-Xemein, a 22 de mayo de 2020", s["Firma"]))
    story.append(Paragraph(
        "EL INSTRUCTOR (Agente nº 12.345) — EL SECRETARIO (Agente nº 67.890)",
        s["Firma"]))
    story.append(Paragraph(
        "EL DECLARANTE (D. JME)", s["Firma"]))

    doc.build(story)
    print(f"Atestado PDF generado en: {OUT}")
    print(f"Tamaño: {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

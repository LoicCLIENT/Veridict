"""
Generador de informe pericial en formato UNE-EN 16775.
Secciones completas para minimizar el trabajo manual del perito.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

from models import Caso, Resultado

# ── Estilos ───────────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Heading1"],
            fontSize=16, spaceAfter=6, alignment=1,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Normal"],
            fontSize=10, spaceAfter=2, alignment=1,
            textColor=colors.HexColor("#4a4a6a"),
        ),
        "seccion": ParagraphStyle(
            "Seccion", parent=base["Heading2"],
            fontSize=12, spaceBefore=14, spaceAfter=4,
            textColor=colors.HexColor("#1a1a2e"),
            borderPad=4,
        ),
        "subseccion": ParagraphStyle(
            "Subseccion", parent=base["Heading3"],
            fontSize=10, spaceBefore=8, spaceAfter=3,
            textColor=colors.HexColor("#2d2d5e"),
        ),
        "normal": ParagraphStyle(
            "NormalV", parent=base["Normal"],
            fontSize=9, spaceAfter=3, leading=13,
        ),
        "negrita": ParagraphStyle(
            "Negrita", parent=base["Normal"],
            fontSize=9, spaceAfter=3, fontName="Helvetica-Bold",
        ),
        "aviso": ParagraphStyle(
            "Aviso", parent=base["Normal"],
            fontSize=8, spaceAfter=3, textColor=colors.HexColor("#7a7a7a"),
            fontName="Helvetica-Oblique",
        ),
        "pie": ParagraphStyle(
            "Pie", parent=base["Normal"],
            fontSize=7, textColor=colors.grey, alignment=1,
        ),
    }
    return styles


def _tabla(data, col_widths, header_row=True):
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7fb")]),
    ]
    if header_row:
        style_cmds += [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(style_cmds))
    return t

# ── Generador principal ───────────────────────────────────────────────────────

async def generate_pdf(
    caso: Caso,
    resultado: Resultado,
    conclusion: str = "",
    perito_nombre: str = "Perito Forense",
    perito_num_colegiado: str = "—",
    num_informe: str = "",
) -> bytes:

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2.2 * cm, leftMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    s = _build_styles()
    story = []

    if not num_informe:
        num_informe = f"VRD-{datetime.utcnow().strftime('%Y%m%d')}-{caso.id[:6].upper()}"

    fecha_informe = datetime.utcnow().strftime("%d/%m/%Y")

    # ── PORTADA ───────────────────────────────────────────────────────────────
    story += [
        Spacer(1, 1 * cm),
        Paragraph("INFORME PERICIAL DE ACCIDENTE DE TRÁFICO", s["titulo"]),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")),
        Spacer(1, 6),
        Paragraph(f"Referencia: {num_informe}", s["subtitulo"]),
        Paragraph(f"Fecha del informe: {fecha_informe}", s["subtitulo"]),
        Paragraph("Normativa de referencia: UNE-EN 16775:2017", s["subtitulo"]),
        Spacer(1, 0.5 * cm),
        _tabla([
            ["Perito", perito_nombre],
            ["Núm. colegiado", perito_num_colegiado],
            ["Sistema utilizado", "Veridict AI — reconstrucción forense asistida"],
        ], [4 * cm, 12 * cm], header_row=False),
        Spacer(1, 0.4 * cm),
        Paragraph(
            "⚠ El presente informe ha sido generado con asistencia de inteligencia artificial. "
            "El perito firmante es responsable de su contenido, revisión y firma.",
            s["aviso"],
        ),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")),
        Spacer(1, 0.6 * cm),
    ]

    # ── 1. DATOS DEL ACCIDENTE ────────────────────────────────────────────────
    story.append(Paragraph("1. DATOS DEL ACCIDENTE", s["seccion"]))

    ctx = resultado.contexto
    direccion = ctx.direccion if ctx and ctx.direccion else f"{caso.ubicacion.lat:.5f}, {caso.ubicacion.lon:.5f}"
    municipio = ctx.municipio if ctx and ctx.municipio else "—"
    provincia = ctx.provincia if ctx and ctx.provincia else "—"

    tipo_via = "—"
    limite_vel = "—"
    num_carriles = "—"
    superficie = "—"
    if ctx and ctx.via:
        tipo_via = ctx.via.tipo_via or "—"
        limite_vel = f"{ctx.via.velocidad_maxima} km/h" if ctx.via.velocidad_maxima else "—"
        num_carriles = str(ctx.via.num_carriles) if ctx.via.num_carriles else "—"
        superficie = ctx.via.superficie or "—"

    story.append(_tabla([
        ["Fecha y hora", caso.fecha_accidente.strftime("%d/%m/%Y  %H:%M h")],
        ["Lugar", direccion],
        ["Municipio", municipio],
        ["Provincia", provincia],
        ["Tipo de colisión", caso.tipo_colision.value.capitalize()],
        ["Tipo de vía", tipo_via],
        ["Límite de velocidad", limite_vel],
        ["Número de carriles", num_carriles],
        ["Pavimento", superficie],
    ], [5 * cm, 11 * cm], header_row=False))
    story.append(Spacer(1, 0.4 * cm))

    # ── 2. CONDICIONES AMBIENTALES ────────────────────────────────────────────
    story.append(Paragraph("2. CONDICIONES AMBIENTALES EN EL MOMENTO DEL ACCIDENTE", s["seccion"]))

    meteo_rows = [["Parámetro", "Valor", "Fuente"]]
    sol_txt = "—"
    deslumbramiento = "No evaluado"

    if ctx and ctx.meteo:
        m = ctx.meteo
        if m.estado_tiempo:
            meteo_rows.append(["Estado del tiempo", m.estado_tiempo.capitalize(), m.fuente or ""])
        if m.temperatura is not None:
            meteo_rows.append(["Temperatura", f"{m.temperatura} °C", m.fuente or ""])
        if m.humedad is not None:
            meteo_rows.append(["Humedad relativa", f"{m.humedad:.0f}%", m.fuente or ""])
        if m.precipitacion is not None:
            precip_txt = f"{m.precipitacion} mm/h" if m.precipitacion > 0 else "Sin precipitación"
            meteo_rows.append(["Precipitación", precip_txt, m.fuente or ""])
        if m.viento_velocidad is not None:
            meteo_rows.append(["Viento", f"{m.viento_velocidad} km/h — {m.viento_direccion or ''}", m.fuente or ""])
        if m.visibilidad:
            meteo_rows.append(["Visibilidad", m.visibilidad, m.fuente or ""])
    else:
        meteo_rows.append(["Meteorología", "No disponible", "—"])

    if ctx and ctx.sol:
        sol = ctx.sol
        es_dia = "Diurno" if sol.es_dia else "Nocturno"
        if sol.hora_amanecer and sol.hora_atardecer:
            sol_txt = f"{es_dia} (amanecer {sol.hora_amanecer}, atardecer {sol.hora_atardecer})"
        else:
            sol_txt = es_dia
        if sol.altitude is not None:
            meteo_rows.append(["Posición solar", f"Azimut {sol.azimuth:.1f}°, elevación {sol.altitude:.1f}°", "Cálculo astronómico"])
        meteo_rows.append(["Condición lumínica", sol_txt, "Cálculo astronómico"])
        if sol.deslumbramiento_posible is not None:
            deslumbramiento = "Posible — evaluar en campo" if sol.deslumbramiento_posible else "No significativo"
        meteo_rows.append(["Riesgo de deslumbramiento", deslumbramiento, "Cálculo astronómico"])

    if len(meteo_rows) > 1:
        story.append(_tabla(meteo_rows, [5 * cm, 7 * cm, 4 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    # ── 3. VEHÍCULOS IMPLICADOS ───────────────────────────────────────────────
    story.append(Paragraph("3. VEHÍCULOS IMPLICADOS", s["seccion"]))

    for v in caso.vehiculos:
        story.append(Paragraph(f"Vehículo {v.id}", s["subseccion"]))

        coef_src = "introducidos por el perito" if (v.coef_rigidez_a > 0) else "auto-lookup BD NHTSA"
        coef_a = v.coef_rigidez_a or 700.0
        coef_b = v.coef_rigidez_b or 2400.0

        v_data = [
            ["Matrícula", v.matricula or "—", "Modelo", v.modelo or "—"],
            ["Masa (kg)", f"{v.masa_kg:.0f}" if v.masa_kg else "—",
             "Coef. rigidez A/B", f"{coef_a:.0f} / {coef_b:.0f} kPa ({coef_src})"],
        ]
        story.append(_tabla(v_data, [3 * cm, 5 * cm, 4 * cm, 4 * cm], header_row=False))

        if any(c > 0 for c in v.mediciones_C):
            story.append(Paragraph("Mediciones de deformación C1-C6 (cm):", s["normal"]))
            med_data = [["C1", "C2", "C3", "C4", "C5", "C6", "Media", "Ancho zona (cm)"]]
            c_avg = sum(v.mediciones_C) / 6
            med_data.append([
                *[f"{c:.1f}" for c in v.mediciones_C],
                f"{c_avg:.1f}",
                f"{v.ancho_zona_danada_cm:.0f}",
            ])
            story.append(_tabla(med_data, [1.7 * cm] * 6 + [1.9 * cm, 2.9 * cm]))

        if v.longitud_frenada_m:
            story.append(Paragraph(f"Longitud de huella de frenada: {v.longitud_frenada_m} m", s["normal"]))

        if v.version_conductor:
            story.append(Paragraph(
                f'<b>Declaración del conductor:</b> "{v.version_conductor}"', s["normal"]
            ))
        story.append(Spacer(1, 0.3 * cm))

    # ── 4. CÁLCULOS FÍSICOS ───────────────────────────────────────────────────
    story.append(Paragraph("4. ANÁLISIS CINEMÁTICO Y CÁLCULOS FÍSICOS", s["seccion"]))
    story.append(Paragraph(
        "Los cálculos siguientes se basan en metodología CRASH3 (McHenry, 1975) "
        "y Stannard Baker, de conformidad con los estándares NHTSA.",
        s["aviso"],
    ))
    story.append(Spacer(1, 4))

    if resultado.calculos:
        calc_data = [["Cálculo", "Fórmula", "Resultado", "Justificación"]]
        for c in resultado.calculos:
            calc_data.append([
                c.nombre,
                c.formula,
                f"{c.valor} {c.unidad}",
                c.justificacion,
            ])
        story.append(_tabla(calc_data, [4 * cm, 4 * cm, 2.5 * cm, 5.5 * cm]))
    else:
        story.append(Paragraph("No se realizaron cálculos (datos de deformación insuficientes).", s["normal"]))
    story.append(Spacer(1, 0.4 * cm))

    # ── 5. CRONOLOGÍA DEL ACCIDENTE ───────────────────────────────────────────
    story.append(Paragraph("5. RECONSTRUCCIÓN CRONOLÓGICA", s["seccion"]))

    if resultado.cronologia:
        cron_data = [["Tiempo (s)", "Descripción del evento"]]
        for e in resultado.cronologia:
            cron_data.append([f"T={e.timestamp:+.1f}", e.descripcion])
        story.append(_tabla(cron_data, [2.5 * cm, 13.5 * cm]))
    else:
        story.append(Paragraph("Cronología no disponible.", s["normal"]))
    story.append(Spacer(1, 0.4 * cm))

    sec = 6  # contador dinámico de secciones

    # ── 6. CONTRASTE DECLARACIONES VS FÍSICA ─────────────────────────────────
    if resultado.contraste_versiones:
        story.append(Paragraph(f"{sec}. CONTRASTE TÉCNICO DE DECLARACIONES", s["seccion"]))
        story.append(Paragraph(
            "Análisis técnico de compatibilidad entre las declaraciones de los conductores "
            "y la evidencia física objetiva. No implica atribución de responsabilidad.",
            s["aviso"],
        ))
        story.append(Spacer(1, 4))

        cv_data = [["Vehículo", "V. declarada (km/h)", "V. calculada (km/h)", "Compatible", "Observación técnica"]]
        for cv in resultado.contraste_versiones:
            cv_data.append([
                f"Vehículo {cv.vehiculo_id}",
                f"{cv.velocidad_declarada_kmh:.0f}" if cv.velocidad_declarada_kmh else "No indicada",
                f"{cv.velocidad_calculada_kmh:.1f}" if cv.velocidad_calculada_kmh else "—",
                "Sí" if cv.compatible else "No",
                cv.observacion,
            ])
        story.append(_tabla(cv_data, [2 * cm, 2.5 * cm, 2.5 * cm, 1.8 * cm, 7.2 * cm]))
        story.append(Spacer(1, 0.4 * cm))
        sec += 1

    # ── ANÁLISIS DE RESPONSABILIDAD (opcional) ────────────────────────────────
    if resultado.veredicto:
        story.append(Paragraph(f"{sec}. ANÁLISIS DE RESPONSABILIDAD CIVIL", s["seccion"]))
        story.append(Paragraph(
            "Atribución de responsabilidad civil estimada conforme a LRCSCVM (RDLeg 8/2004) "
            "art. 1.1-1.3, LSV (RDLeg 6/2015) y jurisprudencia del Tribunal Supremo "
            "(STS 536/2012 y STS 294/2019). Carácter orientativo: la determinación definitiva "
            "corresponde al órgano jurisdiccional competente.",
            s["aviso"],
        ))
        story.append(Spacer(1, 6))

        v = resultado.veredicto
        culpa_a_pct = f"{v.culpa_a * 100:.0f}%"
        culpa_b_pct = f"{v.culpa_b * 100:.0f}%"
        confianza_pct = f"{v.confidence * 100:.0f}%"
        confianza_nivel = (
            "Alta (evidencia sólida)" if v.confidence >= 0.85
            else "Media (alguna ambigüedad)" if v.confidence >= 0.70
            else "Baja — aplicar regla supletoria TS"
        )

        ver_data = [
            ["Parámetro", "Vehículo A", "Vehículo B"],
            ["Responsabilidad civil estimada", culpa_a_pct, culpa_b_pct],
            ["Confianza del análisis", f"{confianza_pct} — {confianza_nivel}", "—"],
        ]
        story.append(_tabla(ver_data, [7 * cm, 6 * cm, 3 * cm]))
        story.append(Spacer(1, 6))

        # Nexo causal por infracción
        if v.nexo_causal:
            story.append(Paragraph("Análisis de nexo causal por infracción (LRCSCVM art. 1.3):", s["subseccion"]))
            nexo_data = [["Veh.", "Artículo", "Gravedad LSV", "Nexo causal", "Justificación"]]
            gravedad_label = {"muy_grave": "Muy grave", "grave": "Grave", "leve": "Leve"}
            nexo_label = {
                "causa_eficiente": "Causa eficiente ●",
                "concurrente": "Concurrente ◐",
                "sin_nexo": "Sin nexo ○",
            }
            for n in v.nexo_causal:
                nexo_data.append([
                    f"Veh. {n.vehiculo}",
                    n.articulo,
                    gravedad_label.get(n.gravedad, n.gravedad),
                    nexo_label.get(n.nexo, n.nexo),
                    n.justificacion,
                ])
            story.append(_tabla(nexo_data, [1.5 * cm, 3 * cm, 2 * cm, 2.5 * cm, 7 * cm]))
            story.append(Spacer(1, 6))

        # Razonamiento jurídico
        if v.razonamiento:
            story.append(Paragraph("Razonamiento jurídico:", s["subseccion"]))
            story.append(Paragraph(v.razonamiento, s["normal"]))
            story.append(Spacer(1, 6))

        # Advertencia daños personales
        if v.advertencia_personal:
            story.append(Paragraph(
                "⚠ ADVERTENCIA — Daños personales: La evidencia disponible no permite "
                "determinar con certeza suficiente el porcentaje de incidencia causal de cada "
                "vehículo. Conforme a STS 536/2012, cada conductor responde al 100 % ante los "
                "ocupantes del otro vehículo. El perito firmante debe evaluar esta circunstancia.",
                s["aviso"],
            ))
            story.append(Spacer(1, 6))

        # Compatibilidad de declaraciones
        if resultado.compatibilidad_versiones:
            comp = resultado.compatibilidad_versiones
            story.append(Paragraph("Compatibilidad de declaraciones con la evidencia física:", s["subseccion"]))
            comp_rows = [
                ["Conductor", "Declaración compatible"],
                ["Vehículo A", "Sí ✓" if comp.a else "No ✗"],
                ["Vehículo B", "Sí ✓" if comp.b else "No ✗"],
            ]
            story.append(_tabla(comp_rows, [4 * cm, 12 * cm]))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<i>{comp.justificacion}</i>", s["normal"]))

        story.append(Spacer(1, 0.4 * cm))
        sec += 1

    # ── VERIFICACIÓN ADVERSARIAL (opcional) ───────────────────────────────────
    if resultado.verificacion_adversarial:
        story.append(Paragraph(f"{sec}. VERIFICACIÓN ADVERSARIAL", s["seccion"]))
        va = resultado.verificacion_adversarial
        if va.passed:
            story.append(Paragraph(
                "✓ El análisis superó la verificación adversarial automatizada. "
                "No se detectaron inconsistencias físicas, cinemáticas ni de versiones.",
                s["normal"],
            ))
        else:
            story.append(Paragraph(
                f"⚠ La verificación adversarial detectó {len(va.failures)} incidencia(s) "
                "que requieren revisión por parte del perito firmante:",
                s["normal"],
            ))
            story.append(Spacer(1, 4))
            inc_data = [["#", "Incidencia detectada"]]
            for idx, f in enumerate(va.failures, 1):
                inc_data.append([str(idx), f])
            story.append(_tabla(inc_data, [1 * cm, 15 * cm]))
        story.append(Spacer(1, 0.4 * cm))
        sec += 1

    # ── ARTÍCULOS APLICABLES ──────────────────────────────────────────────────
    story.append(Paragraph(f"{sec}. ARTÍCULOS APLICABLES DEL RGC Y LSV", s["seccion"]))

    if resultado.infracciones:
        inf_data = [["Vehículo", "Artículo", "Descripción", "Referencia BOE"]]
        for i in resultado.infracciones:
            inf_data.append([f"Vehículo {i.vehiculo}", i.articulo, i.descripcion, i.fuente])
        story.append(_tabla(inf_data, [2 * cm, 3 * cm, 8 * cm, 3 * cm]))
    else:
        story.append(Paragraph("No se identificaron infracciones específicas.", s["normal"]))
    story.append(Spacer(1, 0.4 * cm))
    sec += 1

    # ── CONCLUSIÓN PERICIAL ───────────────────────────────────────────────────
    story.append(Paragraph(f"{sec}. CONCLUSIÓN PERICIAL", s["seccion"]))

    if conclusion:
        story.append(Paragraph(conclusion, s["normal"]))
    else:
        story.append(Paragraph(
            "El perito firmante debe redactar y completar las conclusiones del presente informe.",
            s["aviso"],
        ))
    story.append(Spacer(1, 1 * cm))

    # Espacio para firma
    story.append(HRFlowable(width="50%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{perito_nombre}", s["normal"]))
    story.append(Paragraph(f"Colegiado nº {perito_num_colegiado}", s["normal"]))
    story.append(Paragraph(f"Fecha: {fecha_informe}", s["normal"]))

    # ── PIE ───────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#aaaaaa")))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generado por Veridict AI · Referencia {num_informe} · "
        f"Formato UNE-EN 16775:2017 · {fecha_informe}",
        s["pie"],
    ))
    if resultado.sigstore_hash:
        story.append(Paragraph(
            f"Hash de integridad: {resultado.sigstore_hash}",
            s["pie"],
        ))

    doc.build(story)
    return buffer.getvalue()

"""BOE — texto consolidado de artículos legales.

v1: pasarela laxa que devuelve siempre el texto del seed local enriquecido con
un placeholder de URL del BOE. La integración real con la API de Datos Abiertos
del BOE queda como mejora v2 (requiere mapping referencia → identificador BOE).
"""

from __future__ import annotations

from datetime import date
from typing import Optional


def texto_consolidado(referencia: str, fecha_siniestro: Optional[date] = None) -> dict:
    """Devuelve {referencia, url_boe, vigente_a_fecha, nota}.

    La consolidación real exige mapear cada referencia a su id BOE; aquí
    proporcionamos la URL canónica del Reglamento o Ley del que procede.
    """
    ref = referencia.lower()
    if "rgc" in ref or "1428/2003" in ref:
        url = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514"
        norma = "Reglamento General de Circulación (RD 1428/2003)"
    elif "lsv" in ref or "6/2015" in ref:
        url = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11722"
        norma = "Ley sobre Tráfico, Circulación de Vehículos a Motor y Seguridad Vial (RDLeg 6/2015)"
    elif "ece-r12" in ref:
        url = "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX%3A42010X0327%2801%29"
        norma = "Reglamento ECE-R12 — Protección del conductor frente al sistema de dirección"
    elif "fmvss-208" in ref or "fmvss" in ref:
        url = "https://www.ecfr.gov/current/title-49/section-571.208"
        norma = "FMVSS 208 — Occupant crash protection (49 CFR §571.208)"
    elif "rgv" in ref or "2822/1998" in ref:
        url = "https://www.boe.es/buscar/act.php?id=BOE-A-1999-1826"
        norma = "Reglamento General de Vehículos (RD 2822/1998)"
    elif "rdl 8/2004" in ref or "8/2004" in ref:
        url = "https://www.boe.es/buscar/act.php?id=BOE-A-2004-18911"
        norma = "RDL 8/2004 — Responsabilidad civil y seguro en circulación"
    else:
        url = None
        norma = referencia

    return {
        "referencia": referencia,
        "norma_madre": norma,
        "url_boe": url,
        "vigente_a_fecha": fecha_siniestro.isoformat() if fecha_siniestro else None,
        "fuente": "BOE/EUR-Lex",
        "nota": (
            "URL al texto consolidado actual. La verificación de la versión "
            "vigente a la fecha del siniestro debe ser confirmada por el perito."
        ),
    }

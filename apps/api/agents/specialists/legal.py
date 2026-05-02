"""LegalAgent — normativa aplicable + texto consolidado BOE/EUR-Lex."""

from __future__ import annotations

import time
from datetime import date, datetime
from typing import Optional

from models import TipoEncargo, ToolCallLog
from services.external.boe import texto_consolidado
from services.research import bibliografia_para, normativa_para


async def consultar_legal(tipo_encargo: str, fecha_siniestro_iso: Optional[str] = None,
                          palabras_clave: Optional[list[str]] = None) -> dict:
    t0 = time.time()
    try:
        tipo = TipoEncargo(tipo_encargo)
    except ValueError:
        tipo = TipoEncargo.RESPONSABILIDAD_TRAFICO

    fecha = None
    if fecha_siniestro_iso:
        try:
            fecha = datetime.fromisoformat(fecha_siniestro_iso.replace("Z", "")).date()
        except ValueError:
            fecha = None

    base = normativa_para(tipo)
    biblio = bibliografia_para(tipo)

    # Filtro por palabras clave si se pasan
    if palabras_clave:
        kw = [p.lower() for p in palabras_clave]
        filtrada = [
            n for n in base
            if any(k in (n.titulo + " " + (n.extracto or "") + " " + n.referencia).lower() for k in kw)
        ]
        if filtrada:
            base = filtrada

    # Enriquecer cada artículo con la URL BOE/EUR-Lex consolidada
    enriquecida = []
    for n in base:
        consolidado = texto_consolidado(n.referencia, fecha)
        d = n.model_dump(mode="json")
        d["url_boe"] = consolidado["url_boe"]
        d["norma_madre"] = consolidado["norma_madre"]
        enriquecida.append(d)

    falta = None
    if fecha and fecha.year < 2003:
        falta = (
            "El siniestro es anterior a la entrada en vigor del RGC 2003. "
            "Se debe verificar la normativa de tráfico vigente en esa fecha (RGC 1992)."
        )

    log = ToolCallLog(
        agente="LegalAgent",
        pregunta=f"Normativa aplicable a encargo='{tipo.value}' (fecha {fecha_siniestro_iso or '?'})",
        inputs={"tipo_encargo": tipo.value, "fecha": fecha_siniestro_iso,
                "palabras_clave": palabras_clave or []},
        resultado_resumen=f"{len(enriquecida)} artículos relevantes, {len(biblio)} referencias bibliográficas",
        fuentes_consultadas=["BOE/EUR-Lex", "Veridict normativa seed"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": {"normativa": enriquecida, "bibliografia": biblio}, "_log": log}

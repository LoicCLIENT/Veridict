"""EscenaAgent — geometría de la vía, señales, imágenes ground-level.

Fuentes:
- OpenStreetMap Overpass (anchura, lanes, maxspeed, señales, cycleway)
- Open-Elevation (pendiente)
- Mapillary (imágenes ground-level)
"""

from __future__ import annotations

import time

from models import ImagenAnalizada, ToolCallLog
from services.external.elevacion import perfil_y_pendiente
from services.external.mapillary import imagenes_cerca
from services.external.osm import consultar_via


async def analizar_escena(lat: float, lon: float, radio_m: int = 50) -> dict:
    """Devuelve {datos, imagenes, _log}."""
    t0 = time.time()
    osm = await consultar_via(lat, lon, radio_m)
    elev = await perfil_y_pendiente(lat, lon, radio_m)
    fotos_raw = await imagenes_cerca(lat, lon, radio_m, max_n=4)

    # Resumir vía dominante
    vias = osm.get("vias", [])
    via_principal = max(vias, key=lambda v: 1 if v.get("name") else 0, default=None) if vias else None

    fuentes = ["OpenStreetMap Overpass", "Open-Elevation"]
    if fotos_raw:
        fuentes.append("Mapillary")

    imagenes = [
        ImagenAnalizada(
            url=f["url"], thumb_url=f["thumb_url"], fuente="Mapillary",
            captured_at=str(f.get("captured_at") or ""), compass_angle=f.get("compass_angle"),
            lat=f.get("lat"), lon=f.get("lon"),
            relevancia="Imagen ground-level del lugar del siniestro",
        )
        for f in fotos_raw if f.get("url")
    ]

    senales = osm.get("senales", [])
    datos = {
        "via_principal": via_principal,
        "n_vias": len(vias),
        "todas_las_vias": vias[:5],
        "senales": senales,
        "n_senales": len(senales),
        "tiene_carril_bici": osm.get("cycleway", False),
        "n_pasos_peatones": osm.get("crossings", 0),
        "elevacion_m": elev.get("elevacion_m"),
        "pendiente_pct": elev.get("pendiente_pct"),
        "pendiente_media_pct": elev.get("pendiente_media_pct"),
        "imagenes_disponibles": len(imagenes),
    }

    falta_info = None
    requiere_foto = False
    if not vias:
        falta_info = (
            "OpenStreetMap no devuelve datos de vía en estas coordenadas. "
            "Por favor confirma latitud/longitud exactas o sube foto del entorno."
        )
        requiere_foto = True
    if not imagenes:
        if not falta_info:
            falta_info = (
                "No hay imágenes de Mapillary disponibles en la zona. "
                "Si el perito puede subir fotografía panorámica del lugar, mejorará el análisis."
            )
            requiere_foto = True

    resumen = (
        f"Vía: {via_principal.get('name') or via_principal.get('highway') if via_principal else 'desconocida'}, "
        f"velocidad máx OSM: {via_principal.get('maxspeed') if via_principal else '—'}, "
        f"pendiente: {elev.get('pendiente_pct')}%, "
        f"señales próximas: {len(senales)}, imágenes: {len(imagenes)}"
    )

    log = ToolCallLog(
        agente="EscenaAgent",
        pregunta=f"Geometría y señales en lat={lat}, lon={lon}, radio={radio_m}m",
        inputs={"lat": lat, "lon": lon, "radio_m": radio_m},
        resultado_resumen=resumen,
        fuentes_consultadas=fuentes,
        imagenes=imagenes,
        falta_info=falta_info,
        requiere_foto=requiere_foto,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": datos, "imagenes": [i.model_dump() for i in imagenes], "_log": log}

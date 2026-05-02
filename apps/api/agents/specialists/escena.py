"""EscenaAgent — geometría de la vía, señales, imágenes ground-level.

Fuentes:
- Nominatim (geocoding directo si se aporta dirección)
- OpenStreetMap Overpass (anchura, lanes, maxspeed, señales, cycleway)
  · Reintenta con radio 100 m y 250 m si el inicial devuelve [].
- Open-Elevation (pendiente)
- Mapillary (imágenes ground-level)
"""

from __future__ import annotations

import time
from typing import Optional

from models import ImagenAnalizada, ToolCallLog
from services.external.elevacion import perfil_y_pendiente
from services.external.mapillary import imagenes_cerca
from services.external.nominatim import geocode, reverse
from services.external.osm import consultar_via


async def analizar_escena(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radio_m: int = 50,
    direccion: Optional[str] = None,
) -> dict:
    """Devuelve {datos, imagenes, _log}.

    Si se aporta `direccion`, primero se geocodifica con Nominatim para obtener
    lat/lon precisas. Si OSM no devuelve vías en el radio inicial, reintenta con
    100 m y 250 m antes de marcar fallo.
    """
    t0 = time.time()
    fuentes: list[str] = []

    direccion_resuelta: Optional[str] = None
    lat_eff, lon_eff = lat, lon

    # 1) Geocoding directo si se aporta dirección
    if direccion:
        g = await geocode(direccion)
        if g:
            lat_eff, lon_eff = g["lat"], g["lon"]
            direccion_resuelta = g.get("display_name")
            fuentes.append("Nominatim (geocoding)")

    if lat_eff is None or lon_eff is None:
        log = ToolCallLog(
            agente="EscenaAgent",
            pregunta=f"Geometría sin coords resueltas (direccion={direccion!r})",
            inputs={"lat": lat, "lon": lon, "direccion": direccion, "radio_m": radio_m},
            resultado_resumen="sin coordenadas",
            fuentes_consultadas=fuentes,
            falta_info=("No se han podido resolver coordenadas. Aporta lat/lon o una "
                        "dirección reconocible por OpenStreetMap."),
            requiere_foto=False,
            duracion_ms=int((time.time() - t0) * 1000),
        )
        return {"datos": {}, "imagenes": [], "_log": log}

    # 2) Geocoding inverso (siempre que tengamos lat/lon)
    rev = await reverse(lat_eff, lon_eff)
    if rev and not direccion_resuelta:
        direccion_resuelta = rev.get("display_name")
        fuentes.append("Nominatim (reverso)")

    # 3) OSM con reintentos progresivos
    intentos = [(radio_m, "OpenStreetMap Overpass"),
                (max(150, radio_m * 2), "OpenStreetMap Overpass (radio ampliado)"),
                (max(400, radio_m * 5), "OpenStreetMap Overpass (radio rural)")]
    osm = None
    radio_efectivo = radio_m
    for r, etiqueta in intentos:
        candidato = await consultar_via(lat_eff, lon_eff, r)
        if candidato.get("vias"):
            osm = candidato
            radio_efectivo = r
            fuentes.append(etiqueta)
            break
    if osm is None:
        osm = await consultar_via(lat_eff, lon_eff, intentos[-1][0])
        fuentes.append("OpenStreetMap Overpass (sin match)")

    # 4) Pendiente
    elev = await perfil_y_pendiente(lat_eff, lon_eff, max(60, radio_efectivo))
    fuentes.append("Open-Elevation (DEM SRTM)")

    # 5) Mapillary
    fotos_raw = await imagenes_cerca(lat_eff, lon_eff, max(60, radio_efectivo), max_n=4)
    if fotos_raw:
        fuentes.append("Mapillary")

    # ── Composición ────────────────────────────────────────────────────────
    vias = osm.get("vias", [])
    via_principal = max(vias, key=lambda v: 1 if v.get("name") else 0, default=None) if vias else None

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
        "direccion_resuelta": direccion_resuelta,
        "lat_resuelta": lat_eff,
        "lon_resuelta": lon_eff,
        "radio_efectivo_m": radio_efectivo,
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
        "fuentes": fuentes,
    }

    falta_info = None
    requiere_foto = False
    if not vias:
        falta_info = (
            f"OpenStreetMap no devuelve vías en {lat_eff:.5f},{lon_eff:.5f} "
            f"ni ampliando el radio a {intentos[-1][0]} m. La zona puede no estar "
            f"mapeada con detalle. Pídele al perito una foto del entorno o "
            f"confirmación de la dirección exacta."
        )
        requiere_foto = True
    elif not imagenes:
        falta_info = (
            "No hay imágenes Mapillary disponibles en la zona. Si el perito puede "
            "subir fotografía panorámica del lugar, mejorará el análisis."
        )
        requiere_foto = True

    nombre_via = via_principal.get("name") if via_principal else None
    resumen = (
        f"Vía: {nombre_via or via_principal.get('highway') if via_principal else 'desconocida'}, "
        f"vmáx OSM: {via_principal.get('maxspeed') if via_principal else '—'}, "
        f"pendiente: {elev.get('pendiente_pct')}%, señales: {len(senales)}, "
        f"imágenes Mapillary: {len(imagenes)}, "
        f"radio efectivo: {radio_efectivo} m"
    )
    if direccion_resuelta:
        resumen = f"{direccion_resuelta[:80]}. " + resumen

    log = ToolCallLog(
        agente="EscenaAgent",
        pregunta=(f"Geometría y señales en {direccion or f'{lat_eff:.5f},{lon_eff:.5f}'} "
                  f"(radio {radio_m}→{radio_efectivo}m)"),
        inputs={"lat": lat, "lon": lon, "direccion": direccion, "radio_m": radio_m,
                "radio_efectivo_m": radio_efectivo},
        resultado_resumen=resumen,
        fuentes_consultadas=fuentes,
        imagenes=imagenes,
        falta_info=falta_info,
        requiere_foto=requiere_foto,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": datos, "imagenes": [i.model_dump() for i in imagenes], "_log": log}

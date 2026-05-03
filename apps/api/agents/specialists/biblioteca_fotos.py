"""BibliotecaFotosAgent.

Dos funciones:
- `clasificar_foto(image_url, contexto)` — visión Claude analiza una foto recién
  subida y devuelve {tipo, tags, vehiculo_id, descripcion, calidad}.
- `buscar_foto(criterio, fotos_indexadas)` — el orquestador pide una foto que
  cumpla un criterio descriptivo. Si no la encuentra, devuelve falta_info con
  `requiere_foto=True` para que el chat la pida al perito.
"""

from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from anthropic import APIError

from config import get_claude, get_settings
from models import Foto, ImagenAnalizada, TipoFoto, ToolCallLog


_UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


async def _imagen_a_source(url: str) -> dict | None:
    """Convierte una URL en el bloque `source` que admite Claude visión.

    Estrategia:
      - Si la URL es localhost/127.0.0.1/IP privada → leemos el fichero local
        bajo apps/api/uploads/... y enviamos base64 (Claude no puede llegar a
        localhost).
      - Si es pública → URL directa.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    host = (parsed.hostname or "").lower()
    is_local = host in ("localhost", "127.0.0.1", "0.0.0.0") or host.startswith("192.168.") or host.startswith("10.")

    if not is_local:
        return {"type": "url", "url": url}

    # Mapear /uploads/<rest> al fichero en disco
    if parsed.path.startswith("/uploads/"):
        rel = parsed.path[len("/uploads/"):]
        abs_path = _UPLOADS_DIR / rel
        if not abs_path.exists():
            return None
        data = abs_path.read_bytes()
    else:
        # último intento: bajarla por HTTP
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(url)
                r.raise_for_status()
                data = r.content
        except Exception:
            return None

    # Detectar mime básico por bytes
    if data[:3] == b"\xff\xd8\xff":
        media = "image/jpeg"
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        media = "image/png"
    elif data[:6] in (b"GIF87a", b"GIF89a"):
        media = "image/gif"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        media = "image/webp"
    else:
        media = "image/jpeg"  # asunción

    return {
        "type": "base64",
        "media_type": media,
        "data": base64.b64encode(data).decode("ascii"),
    }


SYS_CLASIFICAR = """Eres un clasificador visual de fotos forenses de accidentes de tráfico.

Devuelves UN OBJETO JSON con esta forma EXACTA (sin markdown, sin texto extra):
{
  "tipo": "vehiculo_frontal|vehiculo_trasero|vehiculo_lateral_izq|vehiculo_lateral_dch|vehiculo_detalle_dano|vehiculo_interior|vehiculo_general|escena_general|escena_huellas|escena_senalizacion|atestado_pagina|croquis|lesion|otro",
  "tags": ["lista breve de palabras clave: parabrisas_danado, capo_hundido, huella_frenada_calzada, etc."],
  "vehiculo_id": "A" | "B" | "C" | null,
  "descripcion": "frase breve y técnica en español de lo que se ve (máx 30 palabras)",
  "elementos_visibles": ["pieza1", "pieza2", "..."],
  "calidad": "alta|media|baja"
}

Reglas:
- Si reconoces la matrícula y coincide con alguna del caso, asigna su id.
- Tags en snake_case y cortos.
- NO atribuyas culpa, NO infieres velocidades.
- Si no estás seguro del tipo, usa "otro".
"""


SYS_BUSCAR = """Eres un bibliotecario de fotos forenses. Tu tarea: dado un CRITERIO de búsqueda y una LISTA de fotos indexadas (cada una con id, tipo, descripción, tags), eliges:

1. La foto que MEJOR cumple el criterio (su id) o null si ninguna sirve.
2. Hasta 3 alternativas (otros ids que podrían interesar al perito).
3. Si NO hay foto que cumpla aproximadamente el criterio, devuelve match=null y propones `pedir_al_perito` con una pregunta concreta y específica para que la suba.

Devuelve UN ÚNICO objeto JSON con la forma:
{
  "match_id": "<id>" | null,
  "razon": "una frase corta explicando por qué encaja (o por qué no)",
  "alternativas_ids": ["<id1>", "<id2>"],
  "pedir_al_perito": "pregunta concreta para el perito si no hay match suficiente, o null"
}
Sin markdown, sin texto extra fuera del JSON.
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first, last = text.find("{"), text.rfind("}")
        if 0 <= first < last:
            return json.loads(text[first : last + 1])
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Clasificación al subir
# ─────────────────────────────────────────────────────────────────────────────

async def clasificar_foto(image_url: str, contexto: dict | None = None) -> dict:
    """Devuelve la clasificación o un dict con error si falla la visión.

    `contexto` opcional: {vehiculos: [{id, marca, modelo, matricula}], tipo_colision}.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        return {"error": "ANTHROPIC_API_KEY no configurada"}

    contexto_txt = ""
    if contexto:
        contexto_txt = (
            "Contexto del caso (puede ayudar a asignar vehiculo_id si reconoces matrícula): "
            + json.dumps(contexto, ensure_ascii=False)
        )

    source = await _imagen_a_source(image_url)
    if source is None:
        return {"error": "no se pudo cargar la imagen (URL no resoluble o fichero ausente)"}

    client = get_claude()
    try:
        # Clasificación masiva (40+ fotos) → Haiku 4.5: visión rápida y barata
        resp = await client.messages.create(
            model=settings.model_haiku,
            max_tokens=600,
            system=SYS_CLASIFICAR,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": source},
                    {"type": "text", "text": contexto_txt or "Clasifica esta foto."},
                ],
            }],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        data = _extract_json(text)
    except (APIError, ValueError, json.JSONDecodeError) as e:
        return {"error": str(e)}

    return data


async def aplicar_clasificacion_a_foto(foto: Foto, contexto: dict | None = None) -> Foto:
    """Helper: clasifica y rellena los campos de la Foto."""
    data = await clasificar_foto(foto.url, contexto)
    if "error" in data:
        foto.error_indexacion = data["error"]
        foto.indexada = True
        return foto
    try:
        foto.tipo = TipoFoto(data.get("tipo", "otro"))
    except ValueError:
        foto.tipo = TipoFoto.OTRO
    foto.tags = data.get("tags", []) or []
    foto.vehiculo_id = data.get("vehiculo_id")
    foto.descripcion = data.get("descripcion") or foto.descripcion
    foto.elementos_visibles = data.get("elementos_visibles", []) or []
    foto.calidad = data.get("calidad")
    foto.indexada = True
    return foto


# ─────────────────────────────────────────────────────────────────────────────
# Búsqueda por criterio (invocada por el Perito como tool)
# ─────────────────────────────────────────────────────────────────────────────

async def listar_biblioteca(fotos: list[Foto]) -> dict:
    """Devuelve el catálogo COMPLETO de fotos del caso.

    Útil para que el Perito coordinador "abra el armario" y vea qué tipos
    de imágenes hay disponibles antes de buscar por criterio.
    """
    t0 = time.time()
    fotos_validas = [f for f in fotos if f.url]

    # Agrupar por tipo. Recortamos descripcion a 140 chars y omitimos calidad
    # para que el payload entre dentro del rate limit aunque haya 40+ fotos.
    por_tipo: dict[str, list[dict]] = {}
    for f in fotos_validas:
        tipo = f.tipo.value if f.tipo else "otro"
        desc = (f.descripcion or "")
        if len(desc) > 140:
            desc = desc[:140] + "…"
        por_tipo.setdefault(tipo, []).append({
            "id": f.id,
            "descripcion": desc,
            "vehiculo_id": f.vehiculo_id,
        })

    resumen = (
        f"{len(fotos_validas)} fotos clasificadas en {len(por_tipo)} tipos: "
        + ", ".join(f"{t} ({len(v)})" for t, v in por_tipo.items())
    )
    log = ToolCallLog(
        agente="BibliotecaFotosAgent",
        pregunta="listar_biblioteca: inventario completo",
        inputs={"n_fotos": len(fotos_validas)},
        resultado_resumen=resumen,
        fuentes_consultadas=["Repositorio de fotos del caso"],
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {
        "datos": {
            "total": len(fotos_validas),
            "por_tipo": por_tipo,
            "tipos_disponibles": list(por_tipo.keys()),
        },
        "_log": log,
    }


async def buscar_foto(criterio: str, fotos: list[Foto]) -> dict:
    """Devuelve {datos, _log} con los campos:
    datos = {match: {id,url,descripcion,tipo,tags,vehiculo_id} | None,
             alternativas: [...], razon: str, falta_info: str | None,
             requiere_foto: bool}
    """
    t0 = time.time()
    fotos_validas = [f for f in fotos if f.url]

    if not fotos_validas:
        falta = (
            f"El perito no ha subido ninguna foto. Para responder al criterio "
            f"«{criterio}» se necesita que adjunte la imagen correspondiente."
        )
        log = ToolCallLog(
            agente="BibliotecaFotosAgent",
            pregunta=f"buscar_foto: {criterio}",
            inputs={"criterio": criterio, "fotos_disponibles": 0},
            resultado_resumen="Sin fotos en el caso",
            fuentes_consultadas=["Repositorio de fotos del caso"],
            falta_info=falta, requiere_foto=True,
            duracion_ms=int((time.time() - t0) * 1000),
        )
        return {"datos": {"match": None, "alternativas": [], "razon": "no hay fotos",
                          "falta_info": falta, "requiere_foto": True}, "_log": log}

    # Si solo hay 1 foto y está indexada, la devolvemos como match (ahorramos llamada)
    if len(fotos_validas) == 1 and fotos_validas[0].indexada:
        f = fotos_validas[0]
        match_data = _foto_to_dict(f)
        log = ToolCallLog(
            agente="BibliotecaFotosAgent",
            pregunta=f"buscar_foto: {criterio}",
            inputs={"criterio": criterio, "fotos_disponibles": 1},
            resultado_resumen=f"Única foto disponible: {f.descripcion or f.tipo}",
            fuentes_consultadas=["Repositorio de fotos del caso"],
            imagenes=[ImagenAnalizada(
                url=f.url, descripcion=f.descripcion, fuente="perito",
                relevancia=criterio,
            )],
            duracion_ms=int((time.time() - t0) * 1000),
        )
        return {"datos": {"match": match_data, "alternativas": [], "razon": "única foto en el caso",
                          "falta_info": None, "requiere_foto": False}, "_log": log}

    # Matching con Claude: le pasamos un catálogo compacto y elige
    settings = get_settings()
    if not settings.anthropic_api_key:
        return _matching_fallback(criterio, fotos_validas, t0)

    catalog = [_foto_to_catalog_entry(f) for f in fotos_validas]
    user_msg = (
        f"CRITERIO: {criterio}\n\n"
        f"FOTOS INDEXADAS DISPONIBLES:\n{json.dumps(catalog, ensure_ascii=False, indent=2)}"
    )

    client = get_claude()
    try:
        # Match semántico simple → Haiku 4.5
        resp = await client.messages.create(
            model=settings.model_haiku,
            max_tokens=400,
            system=SYS_BUSCAR,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        decision = _extract_json(text)
    except (APIError, ValueError, json.JSONDecodeError) as e:
        return _matching_fallback(criterio, fotos_validas, t0, error=str(e))

    by_id = {f.id: f for f in fotos_validas}
    match_id = decision.get("match_id")
    match = by_id.get(match_id) if match_id else None
    alt_ids = decision.get("alternativas_ids", []) or []
    alternativas = [_foto_to_dict(by_id[i]) for i in alt_ids if i in by_id and i != match_id]
    pedir = decision.get("pedir_al_perito")

    falta = None
    requiere = False
    imagenes_log: list[ImagenAnalizada] = []
    if match:
        imagenes_log.append(ImagenAnalizada(
            url=match.url, descripcion=match.descripcion, fuente="perito",
            relevancia=criterio,
        ))
        resumen = f"Match → {match.descripcion or match.tipo} ({len(alternativas)} alternativas)"
    else:
        falta = pedir or f"Ninguna de las {len(fotos_validas)} fotos cumple «{criterio}»."
        requiere = True
        resumen = f"Sin match. {falta[:120]}"

    log = ToolCallLog(
        agente="BibliotecaFotosAgent",
        pregunta=f"buscar_foto: {criterio}",
        inputs={"criterio": criterio, "fotos_disponibles": len(fotos_validas)},
        resultado_resumen=resumen,
        fuentes_consultadas=["Repositorio de fotos del caso", "Claude visión"],
        imagenes=imagenes_log,
        falta_info=falta, requiere_foto=requiere,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {
        "datos": {
            "match": _foto_to_dict(match) if match else None,
            "alternativas": alternativas,
            "razon": decision.get("razon", ""),
            "falta_info": falta,
            "requiere_foto": requiere,
        },
        "_log": log,
    }


def _matching_fallback(criterio: str, fotos: list[Foto], t0: float, error: str | None = None) -> dict:
    """Si no hay Claude o la llamada falla, scoring por keyword sobre tags+descripcion."""
    kw = [w.lower() for w in re.split(r"\W+", criterio) if len(w) > 3]
    scored = []
    for f in fotos:
        haystack = " ".join([f.descripcion or "", f.tipo.value if f.tipo else "", " ".join(f.tags)]).lower()
        score = sum(1 for k in kw if k in haystack)
        scored.append((score, f))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] == 0:
        falta = f"No hay foto que cumpla «{criterio}». Pídele al perito que la suba."
        log = ToolCallLog(
            agente="BibliotecaFotosAgent",
            pregunta=f"buscar_foto: {criterio}",
            inputs={"criterio": criterio, "fotos_disponibles": len(fotos), "fallback": True},
            resultado_resumen="Sin match keyword",
            fuentes_consultadas=["Repositorio de fotos del caso (matching keyword)"],
            falta_info=(error or "") + " " + falta, requiere_foto=True,
            duracion_ms=int((time.time() - t0) * 1000),
        )
        return {"datos": {"match": None, "alternativas": [], "razon": "matching keyword sin éxito",
                          "falta_info": falta, "requiere_foto": True}, "_log": log}
    match = scored[0][1]
    alts = [_foto_to_dict(f) for _, f in scored[1:4] if _ > 0]
    log = ToolCallLog(
        agente="BibliotecaFotosAgent",
        pregunta=f"buscar_foto: {criterio}",
        inputs={"criterio": criterio, "fotos_disponibles": len(fotos), "fallback": True},
        resultado_resumen=f"Match keyword: {match.descripcion or match.tipo}",
        fuentes_consultadas=["Repositorio de fotos del caso (matching keyword)"],
        imagenes=[ImagenAnalizada(url=match.url, descripcion=match.descripcion, fuente="perito",
                                  relevancia=criterio)],
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {"datos": {"match": _foto_to_dict(match), "alternativas": alts,
                      "razon": "matching por keyword", "falta_info": None,
                      "requiere_foto": False}, "_log": log}


def _foto_to_dict(foto: Foto) -> dict:
    return {
        "id": foto.id,
        "url": foto.url,
        "descripcion": foto.descripcion,
        "tipo": foto.tipo.value if foto.tipo else None,
        "tags": foto.tags,
        "vehiculo_id": foto.vehiculo_id,
        "elementos_visibles": foto.elementos_visibles,
    }


def _foto_to_catalog_entry(foto: Foto) -> dict:
    return {
        "id": foto.id,
        "tipo": foto.tipo.value if foto.tipo else "otro",
        "vehiculo_id": foto.vehiculo_id,
        "descripcion": foto.descripcion or "",
        "tags": foto.tags,
        "elementos_visibles": foto.elementos_visibles,
        "calidad": foto.calidad,
    }

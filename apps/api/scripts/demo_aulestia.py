"""Demo end-to-end del caso Aulestia (IURGI vs Ertzaintza, 21/05/2020).

1. Extrae las fotos embebidas del PDF original IURGI con PyMuPDF.
2. Crea un caso con TODA la información que los peritos reales tenían
   (atestado Ertzaintza, declaraciones, lesiones, geometría conocida).
3. Sube las fotos → BibliotecaFotosAgent las indexa con visión Claude.
4. Lanza la generación del informe (Perito Opus 4.7 con 8 tools).
5. Descarga el PDF resultante a apps/api/uploads/_pdfs/.

Uso:
    python -m scripts.demo_aulestia
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
import httpx


API = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent.parent
PDF_ORIGINAL = Path(
    r"C:\Users\javie\.claude\projects\c--Users-javie-OneDrive-Escritorio-Veridict"
    r"\377c5beb-a37d-4980-a2bf-585ce655bb35\tool-results\webfetch-1777726327426-fqvtc2.pdf"
)
EXTRACT_DIR = ROOT / "uploads" / "_demo_aulestia_imgs"


# ── Inputs reales del caso Aulestia 21/05/2020 ────────────────────────────────

CASO_INPUT = {
    "fecha_accidente": "2020-05-21T20:38:00",
    # Aulestia (Bizkaia) — Barrio Zubero. Coords del centro de Aulestia.
    # El Perito puede pasar `direccion` a consultar_escena para que Nominatim
    # afine las coordenadas reales del barrio.
    "ubicacion": {"lat": 43.3300, "lon": -2.6203},
    "tipo_colision": "atropello",
    "encargo": {
        "tipo": "atropello",
        "preguntas": [
            "Determinar la velocidad real del turismo en el momento de la colision contra el ciclista.",
            "Establecer si el accidente era evitable cumpliendo la normativa de circulacion.",
            "Indicar la conducta del conductor del turismo respecto al limite de velocidad y la atencion debida."
        ],
        "solicitante": "Juzgado de Instruccion de Markina-Xemein",
        "parte": "demandante",
        "procedimiento": "Diligencias previas accidente Aulestia 21/05/2020",
        "observaciones": (
            "Atropello mortal del ciclista IBU por el turismo SEAT Ibiza (3526-BKL) "
            "en Barrio Zubero, Aulestia, durante el ascenso por una via estrecha en "
            "pendiente y trazado curvo con visibilidad reducida."
        ),
    },
    "vehiculos_identificacion": [
        {
            "id": "A",
            "matricula": "3526-BKL",
            "marca": "SEAT",
            "modelo": "Ibiza",
            "anio": 2018,
            "color": "blanco",
            "conductor": "JME (vecino de la zona)",
        }
    ],
    "hechos_atestado": {
        "numero_atestado": "Ertzaintza Aulestia 21052020",
        "cuerpo_actuante": "ertzaintza",
        "hay_huellas_frenada": True,
        "velocidades_declaradas": [
            {"vehiculo_id": "A", "valor_kmh": 20, "fuente": "declaracion_conductor"}
        ],
        "condiciones_meteorologicas": "asfalto seco, tarde clara",
        "estado_calzada": "asfalto seco",
        "visibilidad": (
            "diurna pero trazado curvo, visibilidad efectiva del conductor "
            "estimada por el atestado en 20 m; el perito constata 26.5 m"
        ),
        "declaraciones": (
            "El conductor del turismo declara que circulaba entre 10 y 20 km/h "
            "ascendiendo una pendiente del 9 al 11.6 %. Manifiesta que vio al ciclista "
            "y acciono el freno al maximo, pero en el momento del impacto el turismo "
            "no estaba detenido. El atestado indica 'no se observan huellas del turismo' "
            "pero tambien recoge que el ciclista dejo una huella de frenado de 8 m que "
            "termina a 1.2 m del borde de la via, iniciando a menos de 1 m del borde."
        ),
        "observaciones": (
            "Caracteristicas del lugar (medidas in situ por el perito instructor): "
            "anchura de la calzada 3.10 a 3.20 m; pendiente entre 9 y 11.6 %; "
            "distancia de visibilidad efectiva 26.5 m lineales (>30 m segun trayectoria curva); "
            "zona terriza diafana de varios metros de anchura a la derecha del turismo "
            "(desnivel maximo 4 cm) que permitiria maniobra evasiva. Limite de velocidad: "
            "no existia en 2020 limite generico de 30 km/h en via urbana (incorporado posteriormente); "
            "el atestado afirma una senal especifica de 20 km/h pero no aporta fotografia de la senal. "
            "Coeficiente de adherencia neumatico-asfalto estimado mu = 0.75."
        ),
    },
    "lesiones": [
        {
            "ocupante": "IBU",
            "vehiculo_id": "A",  # ciclista atropellado por A
            "zona_corporal": "principalmente cabeza",
            "gravedad": "fallecimiento",
            "secuelas": (
                "Lesiones cefalicas incompatibles con la vida segun autopsia. "
                "Trayectoria del cuerpo del ciclista: impacto inicial en paragolpes "
                "delantero, deslizamiento sobre el capo (impronta visible), impacto "
                "contra parabrisas delantero lado derecho y hendidura en techo extremo derecho."
            ),
        }
    ],
}


# ── Extracción de imágenes del PDF original ──────────────────────────────────

def extraer_fotos_del_pdf(pdf: Path, out_dir: Path, max_n: int = 6) -> list[Path]:
    """Devuelve hasta max_n imágenes del PDF, las más relevantes (más grandes)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf))
    extraidas: list[tuple[int, Path]] = []
    seen = set()
    for page_num in range(len(doc)):
        for img_info in doc.get_page_images(page_num):
            xref = img_info[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.colorspace and pix.colorspace.n >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                w, h = pix.width, pix.height
                if w * h < 100_000:  # descartamos miniaturas pequeñas
                    pix = None
                    continue
                fname = out_dir / f"p{page_num+1:02d}_x{xref}.png"
                pix.save(str(fname))
                extraidas.append((w * h, fname))
                pix = None
            except Exception as e:
                print(f"  ! no se pudo extraer xref={xref} de p{page_num}: {e}")
    doc.close()
    extraidas.sort(reverse=True)
    return [p for _, p in extraidas[:max_n]]


# ── Cliente del backend ──────────────────────────────────────────────────────

async def crear_caso(client: httpx.AsyncClient, payload: dict) -> str:
    r = await client.post(f"{API}/api/casos", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


async def subir_foto(client: httpx.AsyncClient, caso_id: str, path: Path) -> dict:
    with path.open("rb") as f:
        files = {"file": (path.name, f, "image/png")}
        r = await client.post(f"{API}/api/casos/{caso_id}/upload/foto", files=files, timeout=120)
    r.raise_for_status()
    return r.json()


async def generar_informe(client: httpx.AsyncClient, caso_id: str) -> dict:
    r = await client.post(f"{API}/api/casos/{caso_id}/informe", timeout=600)
    r.raise_for_status()
    return r.json()


async def descargar_pdf(client: httpx.AsyncClient, caso_id: str, dest: Path) -> Path:
    r = await client.get(f"{API}/api/casos/{caso_id}/informe.pdf", timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    if not PDF_ORIGINAL.exists():
        print(f"!! PDF original no encontrado: {PDF_ORIGINAL}")
        sys.exit(1)
    print(f">> Extrayendo fotos del PDF original ({PDF_ORIGINAL.name})…")
    fotos = extraer_fotos_del_pdf(PDF_ORIGINAL, EXTRACT_DIR, max_n=6)
    print(f"   {len(fotos)} fotos extraídas en {EXTRACT_DIR}:")
    for f in fotos:
        size_kb = f.stat().st_size // 1024
        print(f"     - {f.name} ({size_kb} KB)")

    async with httpx.AsyncClient() as client:
        print("\n>> Creando caso Aulestia con el atestado Ertzaintza completo…")
        caso_id = await crear_caso(client, CASO_INPUT)
        print(f"   caso_id = {caso_id}")

        print("\n>> Subiendo fotos al BibliotecaFotosAgent (visión Claude indexa cada una)…")
        for f in fotos:
            t0 = time.time()
            r = await subir_foto(client, caso_id, f)
            print(f"   - {f.name}  →  tipo={r.get('tipo')}, vehiculo={r.get('vehiculo_id')}, "
                  f"{int((time.time()-t0)*1000)} ms")
            if r.get("descripcion"):
                print(f"       desc: {r['descripcion'][:140]}")
            if r.get("tags"):
                print(f"       tags: {r['tags']}")

        print("\n>> Generando informe (Perito Opus 4.7 con tool_use)…")
        t0 = time.time()
        informe = await generar_informe(client, caso_id)
        print(f"   informe generado en {int(time.time()-t0)} s")

        print("\n=== TOOL CALLS ===")
        for tc in informe.get("tool_calls", []):
            n_img = len(tc.get("imagenes", []))
            extra = f" [+{n_img}img]" if n_img else ""
            print(f"  - {tc['agente']:25s}{extra} ({tc.get('duracion_ms', 0)} ms)")
            print(f"      pregunta: {tc['pregunta'][:140]}")
            if tc.get("resultado_resumen"):
                print(f"      resumen: {tc['resultado_resumen'][:160]}")
            if tc.get("falta_info"):
                print(f"      [!] falta: {tc['falta_info'][:160]}")

        print("\n=== RESPUESTAS ===")
        for r in informe.get("respuestas", []):
            print(f"\n  {r['pregunta_id']} (confianza {r['confianza']})")
            print(f"  Q: {r['pregunta']}")
            print(f"  A: {r['respuesta'][:600]}")
            if r.get("citas"):
                print(f"     citas: {[(c['tipo'], c['referencia']) for c in r['citas']]}")

        print("\n=== INFO FALTANTE ===")
        for q in informe.get("info_faltante", []):
            tag = " [REQUIERE FOTO]" if q.get("requiere_foto") else ""
            print(f"  [{q['prioridad']}]{tag} {q['pregunta'][:200]}")

        print(f"\n>> Confianza global: {informe.get('confianza_global')}")

        print("\n>> Descargando PDF…")
        out_pdf = ROOT / "uploads" / "_pdfs" / f"informe_aulestia_{caso_id[:8]}.pdf"
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        await descargar_pdf(client, caso_id, out_pdf)
        print(f"   PDF guardado en: {out_pdf}")
        print(f"   Tamaño: {out_pdf.stat().st_size // 1024} KB")
        print("\n>> Listo. Abre el PDF para revisarlo:")
        print(f"   {out_pdf}")


if __name__ == "__main__":
    asyncio.run(main())

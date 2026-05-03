"""Demo end-to-end del caso Vilagarcía 2010 (José Carlos Álvarez Feal — peritaje airbag).

Procedimiento Ordinario 230/2010 - Juzgado de 1.ª Instancia nº 1 de Vilagarcía.
Colisión por alcance del 26/11/2008 en la AP-9: camión Nissan Cabstar (0019 FJD)
contra la parte trasera de un vehículo articulado formado por tractocamión
MAN 19422FLT (0649 BRY) y semirremolque Leciñena ML19330 (O-01982-R).

Encargo (3 cuestiones del juzgado):
  i.   Si el airbag del Nissan Cabstar debió activarse.
  ii.  Si los daños son imputables a la falta de activación del airbag.
  iii. Si las lesiones (incapacidad temporal) habrían cambiado con airbag.

Diferencias con Aulestia:
  - Tipo: ALCANCE (no atropello).
  - Encargo: SEGURIDAD_PASIVA + cuantía daños (no responsabilidad).
  - Velocidades: Nissan 100 km/h (declaración), MAN 62 km/h (tacógrafo) → Δv ≈ 38 km/h.
  - "No se observan huellas de frenado".
  - Lesiones moderadas (extremidades inferiores), sin fallecimiento.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import fitz  # PyMuPDF
import httpx


API = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent.parent
PDF_ORIGINAL = Path(
    r"C:\Users\javie\.claude\projects\c--Users-javie-OneDrive-Escritorio-Veridict"
    r"\377c5beb-a37d-4980-a2bf-585ce655bb35\tool-results\webfetch-1777726324042-o18z7k.pdf"
)
EXTRACT_DIR = ROOT / "uploads" / "_demo_vilagarcia_imgs"


# ── Inputs reales del caso Vilagarcía 26/11/2008 ─────────────────────────────

CASO_INPUT = {
    "fecha_accidente": "2008-11-26T08:30:00",
    # AP-9 a la altura de Vilagarcía de Arousa, Galicia. Coords aproximadas.
    "ubicacion": {"lat": 42.5969, "lon": -8.7700},
    "tipo_colision": "alcance",
    "encargo": {
        "tipo": "seguridad_pasiva",
        "preguntas": [
            "Determinar si el airbag del camion Nissan Cabstar debio activarse en el siniestro del 26/11/2008.",
            "Establecer el importe de los danos directamente imputables a la falta de activacion del airbag, y la posible reduccion de danos en caso de haberse activado.",
            "Indicar si las lesiones causantes de Incapacidad Temporal habrian cambiado de haber funcionado el airbag."
        ],
        "solicitante": "Juzgado de 1.a Instancia n.o 1 de Vilagarcia de Arousa",
        "parte": "demandante",
        "procedimiento": "Procedimiento Ordinario 230/2010",
        "observaciones": (
            "Encargo de la parte demandante (Boigo Iber Vac SL): determinar si el airbag "
            "del Nissan Cabstar deberia haberse activado y si los danos del vehiculo y las "
            "lesiones de los dos operarios son imputables a la falta de activacion. Cuantia "
            "reclamada total: 56.073,91 EUR (baja laboral 16.336,20 EUR + reparacion 34.640,09 EUR + "
            "lucro cesante 10%)."
        ),
    },
    "vehiculos_identificacion": [
        {
            "id": "A",
            "matricula": "0019 FJD",
            "marca": "Nissan",
            "modelo": "Cabstar",
            "anio": 2007,
            "color": "blanco",
            "conductor": (
                "Dos operarios de Boigo Iber Vac SL en cabina (conductor y pasajero). "
                "Cinturones de seguridad puestos."
            ),
        },
        {
            "id": "B",
            "matricula": "0649 BRY",
            "marca": "MAN",
            "modelo": "19422FLT (tractocamion articulado con semirremolque Lecinena ML19330 0-01982-R)",
            "anio": 2006,
            "color": "blanco",
            "conductor": "Conductor profesional del tractocamion.",
        },
    ],
    "hechos_atestado": {
        "numero_atestado": "Atestado Policial de Circulacion 26112008",
        "cuerpo_actuante": "guardia_civil",
        "hay_huellas_frenada": False,
        "velocidades_declaradas": [
            {"vehiculo_id": "A", "valor_kmh": 100, "fuente": "declaracion_conductor"},
            {"vehiculo_id": "B", "valor_kmh": 62, "fuente": "tacografo"},
        ],
        "condiciones_meteorologicas": "diurno (a confirmar por meteo)",
        "estado_calzada": "asfalto seco (autopista AP-9)",
        "visibilidad": "diurna autopista, sin restricciones meteorologicas declaradas",
        "declaraciones": (
            "El conductor del Nissan Cabstar manifiesta que circulaba a una velocidad "
            "aproximada de 100 km/h. El tacografo del tractocamion MAN registra 62 km/h "
            "en el momento del impacto. El atestado consigna expresamente que 'no se "
            "observan huellas de frenado' del Nissan Cabstar. Diferencia de velocidades "
            "en el momento del impacto: aproximadamente 38 km/h."
        ),
        "observaciones": (
            "Datos tecnicos relevantes:\n"
            "- Nissan Cabstar: parachoques delantero entre 0,35 m (parte inferior) y 0,66 m "
            "(parte superior). Largueros longitudinales de refuerzo a 0,50 m del suelo.\n"
            "- Semirremolque Lecinena ML19330: altura de plataforma de carga entre 1,112 m "
            "y 1,247 m segun estado de carga.\n"
            "- Dispositivo antiempotramiento del semirremolque integrado segun directiva CE / "
            "RD 2822/1998 RGV (>= 0,40 m del suelo).\n"
            "- El centro de los danos del Nissan Cabstar se situa POR ENCIMA del parachoques, "
            "correspondiendo con la altura de la plataforma del semirremolque (canto rigido a ~1,1 m).\n"
            "- El impacto del Nissan se produce ENCIMA de los largueros longitudinales que "
            "aportan rigidez, en zona de baja resistencia mecanica.\n"
            "- Equipamiento del Cabstar (segun ficha del fabricante): airbag de conductor y "
            "pasajero EN OPCION (instalado en el vehiculo siniestrado), cinturones con "
            "pretensores y limitador de esfuerzo, barra antiempotramiento trasero de serie, "
            "barras de proteccion lateral integradas en puertas.\n"
            "- Precios Nissan Cabstar 2007: modelo basico 19.915 EUR, Premium 26.865 EUR + extras.\n"
            "- Presupuesto reparacion solicitado: 34.640,09 EUR.\n"
            "- Coste baja laboral estimado por la empresa: 16.336,20 EUR (nominas + SS).\n"
            "- Total reclamado con lucro cesante 10%: 56.073,91 EUR."
        ),
    },
    "lesiones": [
        {
            "ocupante": "Operario 1 (conductor Cabstar)",
            "vehiculo_id": "A",
            "zona_corporal": "extremidades inferiores",
            "gravedad": "moderada",
            "dias_baja": None,
            "secuelas": (
                "Lesiones en extremidades inferiores que motivaron Incapacidad Temporal. "
                "Cinturon de seguridad puesto. Sin impacto cefalico contra volante o salpicadero."
            ),
        },
        {
            "ocupante": "Operario 2 (pasajero Cabstar)",
            "vehiculo_id": "A",
            "zona_corporal": "extremidades inferiores",
            "gravedad": "moderada",
            "dias_baja": None,
            "secuelas": (
                "Lesiones en extremidades inferiores que motivaron Incapacidad Temporal. "
                "Cinturon de seguridad puesto. Sin impacto cefalico contra parabrisas/salpicadero."
            ),
        },
    ],
}


# ── Extracción de imágenes (igual que Aulestia) ─────────────────────────────

def extraer_fotos_del_pdf(pdf: Path, out_dir: Path, max_n: int = 40) -> list[Path]:
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
                if w * h < 50_000:
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


# ── Cliente backend ─────────────────────────────────────────────────────────

async def crear_caso(client, payload):
    r = await client.post(f"{API}/api/casos", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]


async def subir_foto(client, caso_id, path):
    with path.open("rb") as f:
        files = {"file": (path.name, f, "image/png")}
        r = await client.post(f"{API}/api/casos/{caso_id}/upload/foto",
                              files=files, timeout=120)
    r.raise_for_status()
    return r.json()


async def generar_informe(client, caso_id):
    r = await client.post(f"{API}/api/casos/{caso_id}/informe", timeout=600)
    r.raise_for_status()
    return r.json()


async def descargar_pdf(client, caso_id, dest):
    r = await client.get(f"{API}/api/casos/{caso_id}/informe.pdf", timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


async def descargar_trace(client, caso_id, dest):
    r = await client.get(f"{API}/api/casos/{caso_id}/trace.md", timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    if not PDF_ORIGINAL.exists():
        print(f"!! PDF original no encontrado: {PDF_ORIGINAL}")
        import sys; sys.exit(1)

    print(f">> Extrayendo fotos del PDF original Vilagarcía ({PDF_ORIGINAL.name})…")
    fotos = extraer_fotos_del_pdf(PDF_ORIGINAL, EXTRACT_DIR, max_n=40)
    print(f"   {len(fotos)} fotos extraídas en {EXTRACT_DIR}:")
    for f in fotos:
        size_kb = f.stat().st_size // 1024
        print(f"     - {f.name} ({size_kb} KB)")

    async with httpx.AsyncClient() as client:
        print("\n>> Creando caso Vilagarcía con el atestado completo…")
        caso_id = await crear_caso(client, CASO_INPUT)
        print(f"   caso_id = {caso_id}")

        print("\n>> Subiendo fotos al BibliotecaFotosAgent (visión Claude indexa cada una)…")
        for f in fotos:
            t0 = time.time()
            try:
                r = await subir_foto(client, caso_id, f)
                print(f"   - {f.name}  →  tipo={r.get('tipo')}, vehiculo={r.get('vehiculo_id')}, "
                      f"{int((time.time()-t0)*1000)} ms")
                if r.get("descripcion"):
                    print(f"       desc: {r['descripcion'][:140]}")
                if r.get("tags"):
                    print(f"       tags: {r['tags']}")
            except Exception as e:
                print(f"   - {f.name}  →  ERROR: {e}")

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
                print(f"     citas: {[(c['tipo'], c['referencia'][:60]) for c in r['citas'][:6]]}")

        print("\n=== INFO FALTANTE ===")
        for q in informe.get("info_faltante", []):
            tag = " [REQUIERE FOTO]" if q.get("requiere_foto") else ""
            print(f"  [{q['prioridad']}]{tag} {q['pregunta'][:200]}")

        print(f"\n>> Confianza global: {informe.get('confianza_global')}")

        print("\n>> Descargando PDF…")
        out_pdf = ROOT / "uploads" / "_pdfs" / f"informe_vilagarcia_{caso_id[:8]}.pdf"
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        await descargar_pdf(client, caso_id, out_pdf)
        print(f"   PDF guardado en: {out_pdf}")
        print(f"   Tamaño: {out_pdf.stat().st_size // 1024} KB")

        print("\n>> Descargando trace deep-log (.md)…")
        out_trace = ROOT / "uploads" / "_pdfs" / f"trace_vilagarcia_{caso_id[:8]}.md"
        await descargar_trace(client, caso_id, out_trace)
        print(f"   Trace guardado en: {out_trace}")

        print("\n>> Listo. Abre los dos archivos:")
        print(f"   PDF:   {out_pdf}")
        print(f"   Trace: {out_trace}")


if __name__ == "__main__":
    asyncio.run(main())

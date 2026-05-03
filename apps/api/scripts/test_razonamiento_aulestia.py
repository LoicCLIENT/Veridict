"""Test directo (sin HTTP) del razonamiento del orquestador y de los specialists.

Construye el Caso Aulestia en memoria, llama a `coordinar(caso)` directamente,
y vuelca turno a turno:

  - El razonamiento textual del Perito (los text-blocks que Claude emite entre
    tool_use cuando "piensa en voz alta").
  - Las tools que pide en cada turno y con qué inputs.
  - El resumen del resultado de cada specialist.
  - El JSON final del informe.

Ejecuta con la cwd en apps/api y el .env cargado:

    python -m scripts.test_razonamiento_aulestia
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Forzar utf-8 en stdout para no chocar con cp1252 de Windows
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Hacer importable apps/api/ aunque ejecutemos el script "a pelo"
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cargar .env explícitamente porque ejecutamos como script
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass

from agents.perito import coordinar  # noqa: E402
from models import (  # noqa: E402
    Caso,
    Encargo,
    HechosAtestado,
    IdentificacionVehiculo,
    Lesion,
    GravedadLesion,
    ParteSolicitante,
    TipoColision,
    TipoEncargo,
    Ubicacion,
    VelocidadDeclarada,
    FuenteVelocidad,
)


def construir_caso_aulestia() -> Caso:
    return Caso(
        fecha_accidente=datetime.fromisoformat("2020-05-21T20:38:00"),
        ubicacion=Ubicacion(lat=43.3300, lon=-2.6203),
        tipo_colision=TipoColision.ATROPELLO,
        encargo=Encargo(
            tipo=TipoEncargo.ATROPELLO,
            preguntas=[
                "Determinar la velocidad real del turismo en el momento de la colision contra el ciclista.",
                "Establecer si el accidente era evitable cumpliendo la normativa de circulacion.",
                "Indicar la conducta del conductor del turismo respecto al limite de velocidad y la atencion debida.",
            ],
            solicitante="Juzgado de Instruccion de Markina-Xemein",
            parte=ParteSolicitante.DEMANDANTE,
            procedimiento="Diligencias previas accidente Aulestia 21/05/2020",
            observaciones=(
                "Atropello mortal del ciclista IBU por el turismo SEAT Ibiza (3526-BKL) "
                "en Barrio Zubero, Aulestia, durante el ascenso por una via estrecha en "
                "pendiente y trazado curvo con visibilidad reducida."
            ),
        ),
        vehiculos_identificacion=[
            IdentificacionVehiculo(
                id="A",
                matricula="3526-BKL",
                marca="SEAT",
                modelo="Ibiza",
                anio=2018,
                color="blanco",
                conductor="JME (vecino de la zona, conoce el trazado y la limitacion)",
            ),
            IdentificacionVehiculo(
                id="B",
                matricula="n/a",
                marca="Orbea",
                modelo="bicicleta deportiva (n.º bastidor 3773)",
                color="rojo",
                conductor=(
                    "IBU (ciclista) — sillin a 79 cm del suelo, manillar 55 cm. "
                    "Circulaba descendente por la mitad derecha. Marcas de derrape "
                    "en cubierta trasera de la bicicleta."
                ),
            ),
        ],
        hechos_atestado=HechosAtestado(
            numero_atestado="Ertzaintza Aulestia 21052020",
            cuerpo_actuante="ertzaintza",
            hay_huellas_frenada=True,
            velocidades_declaradas=[
                VelocidadDeclarada(vehiculo_id="A", valor_kmh=20, fuente=FuenteVelocidad.DECLARACION)
            ],
            condiciones_meteorologicas="asfalto seco, tarde clara",
            estado_calzada="asfalto seco",
            visibilidad=(
                "diurna pero trazado curvo, visibilidad efectiva del conductor "
                "estimada por el atestado en 20 m; el perito constata 26.5 m"
            ),
            declaraciones=(
                "El conductor del turismo declara que circulaba entre 10 y 20 km/h "
                "ascendiendo una pendiente del 9 al 11.6 %. Dice haber visto al ciclista "
                "y haber accionado el freno al maximo, pero en el momento del impacto "
                "el turismo no estaba detenido. El atestado indica 'no se observan huellas "
                "del turismo' pero recoge que el ciclista dejo una huella de 8 m que termina "
                "a 1.2 m del borde, iniciando a menos de 1 m del borde."
            ),
            observaciones=(
                "Anchura calzada 3.10-3.20 m; pendiente 9-11.6 %; visibilidad efectiva "
                "26.5 m lineales (>30 m por trayectoria curva); zona terriza de varios m "
                "a la derecha del turismo (desnivel max 4 cm) que permitiria evasiva. "
                "Limite de velocidad: en 2020 no existia limite generico de 30 km/h en via "
                "urbana; el atestado afirma una senal especifica de 20 km/h pero no aporta "
                "fotografia. Coef. adherencia neumatico-asfalto estimado mu=0.75."
            ),
        ),
        lesiones=[
            Lesion(
                ocupante="IBU",
                vehiculo_id="A",
                zona_corporal="principalmente cabeza",
                gravedad=GravedadLesion.FALLECIMIENTO,
                secuelas=(
                    "Lesiones cefalicas incompatibles con la vida segun autopsia. "
                    "Trayectoria del cuerpo: impacto inicial en paragolpes delantero, "
                    "deslizamiento sobre el capo (impronta visible), impacto contra "
                    "parabrisas delantero lado derecho y hendidura en techo extremo derecho."
                ),
            )
        ],
    )


def _fmt(obj, max_chars: int = 600) -> str:
    if obj is None:
        return "<null>"
    if isinstance(obj, (dict, list)):
        s = json.dumps(obj, ensure_ascii=False, default=str)
    else:
        s = str(obj)
    return s if len(s) <= max_chars else s[:max_chars] + "…"


def _resumen_specialist(tool_name: str, datos: dict) -> str:
    """Extrae el campo más relevante de cada specialist para un log legible."""
    if not isinstance(datos, dict):
        return _fmt(datos, 300)
    for key in (
        "resumen", "resumen_tecnico", "resumen_pericial",
        "valoracion", "conclusion", "veredicto",
        "valor_kmh", "velocidad_kmh", "velocidad_calculada_kmh",
        "tiempo_total_s", "distancia_total_m",
        "compatibilidad", "compatible",
    ):
        if key in datos:
            return f"{key}={_fmt(datos[key], 300)}"
    # Si trae una lista de incongruencias (conformidad)
    if "incongruencias" in datos:
        ic = datos["incongruencias"]
        return f"incongruencias={len(ic) if isinstance(ic, list) else '?'} | {_fmt(ic, 300)}"
    return _fmt(datos, 300)


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    print("=" * 78)
    print("TEST RAZONAMIENTO — Caso Aulestia (atropello mortal)")
    print("=" * 78)
    print(f"  ANTHROPIC_API_KEY presente: {bool(api_key)} (longitud {len(api_key)})")

    caso = construir_caso_aulestia()
    print(f"  caso_id (in-memory): {caso.id}")
    print(f"  encargo: {caso.encargo.tipo.value} — {len(caso.encargo.preguntas)} preguntas")

    print("\n>> Llamando a coordinar(caso) — esto puede tardar 60-180 s…")
    try:
        out = await coordinar(caso)
    except Exception as e:
        print(f"\n!! Excepción cruda en coordinar(): {type(e).__name__}: {e}")
        raise

    if out.get("error"):
        print(f"\n!! coordinar() devolvió error: {out['error']}")

    razonamiento = out.get("razonamiento_perito", []) or []
    tool_calls = out.get("tool_calls", []) or []
    datos_completos = out.get("datos_completos", []) or []
    informe_data = out.get("informe_data")

    # ── Razonamiento del orquestador, turno a turno ──────────────────────────
    print("\n" + "=" * 78)
    print("RAZONAMIENTO DEL ORQUESTADOR (Perito) — turno a turno")
    print("=" * 78)
    if not razonamiento:
        print("  (vacío — el modelo no emitió text-blocks)")
    for r in razonamiento:
        turno = r.get("turno")
        stop = r.get("stop_reason")
        texto = (r.get("razonamiento") or "").strip()
        tools_pedidas = r.get("tools_pedidas") or []
        print(f"\n── Turno {turno} (stop_reason={stop}) ──")
        if texto:
            print("  THINK:")
            for line in texto.splitlines():
                print(f"    {line}")
        else:
            print("  THINK: <sin texto previo a las tools>")
        if tools_pedidas:
            print("  TOOLS pedidas:")
            for t in tools_pedidas:
                print(f"    → {t['name']}({_fmt(t['input'], 300)})")

    # ── Specialists: input + resumen del output ──────────────────────────────
    print("\n" + "=" * 78)
    print("SPECIALISTS — qué les pidió el Perito y qué devolvieron")
    print("=" * 78)
    for i, d in enumerate(datos_completos, 1):
        print(f"\n[{i}] turno={d.get('turno')}  tool={d.get('tool')}")
        print(f"    inputs : {_fmt(d.get('inputs'), 400)}")
        print(f"    salida : {_resumen_specialist(d.get('tool'), d.get('datos'))}")

    # ── Tool-call logs (lo que verá el PDF/UI) ───────────────────────────────
    print("\n" + "=" * 78)
    print("TOOL-CALL LOGS (resumen pericial por agente)")
    print("=" * 78)
    for tc in tool_calls:
        # ToolCallLog es Pydantic — usar atributos
        agente = getattr(tc, "agente", "?")
        pregunta = getattr(tc, "pregunta", "")
        resumen = getattr(tc, "resultado_resumen", "") or ""
        falta = getattr(tc, "falta_info", "") or ""
        dur = getattr(tc, "duracion_ms", 0)
        n_img = len(getattr(tc, "imagenes", []) or [])
        extra = f" [+{n_img}img]" if n_img else ""
        print(f"\n  - {agente:28s}{extra} ({dur} ms)")
        print(f"      Q: {_fmt(pregunta, 200)}")
        if resumen:
            print(f"      R: {_fmt(resumen, 300)}")
        if falta:
            print(f"      [!] falta_info: {_fmt(falta, 300)}")

    # ── Informe final ────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("INFORME FINAL (JSON tal cual lo devuelve el Perito)")
    print("=" * 78)
    if informe_data is None:
        print("  (no hay informe_data — revisa el error arriba)")
    else:
        print(f"  resumen_caso: {_fmt(informe_data.get('resumen_caso'), 400)}")
        print(f"  confianza_global: {informe_data.get('confianza_global')}")
        print(f"  respuestas: {len(informe_data.get('respuestas', []) or [])}")
        for r in informe_data.get("respuestas", []) or []:
            print(f"\n   • {r.get('pregunta_id')} (conf {r.get('confianza')})")
            print(f"     Q: {_fmt(r.get('pregunta'), 200)}")
            print(f"     A: {_fmt(r.get('respuesta'), 700)}")
            citas = r.get("citas", []) or []
            if citas:
                print(f"     citas ({len(citas)}): "
                      f"{[(c.get('tipo'), c.get('referencia')) for c in citas[:6]]}")
        info_falt = informe_data.get("info_faltante", []) or []
        if info_falt:
            print(f"\n  info_faltante ({len(info_falt)}):")
            for q in info_falt:
                print(f"    [{q.get('prioridad')}] {_fmt(q.get('pregunta'), 200)}")

    # ── Volcado completo a JSON para inspección posterior ────────────────────
    out_path = ROOT / "uploads" / "_pdfs" / "trace_test_razonamiento_aulestia.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {
        "error": out.get("error"),
        "razonamiento_perito": razonamiento,
        "datos_completos": datos_completos,
        "tool_calls": [
            {
                "agente": getattr(tc, "agente", None),
                "pregunta": getattr(tc, "pregunta", None),
                "resultado_resumen": getattr(tc, "resultado_resumen", None),
                "falta_info": getattr(tc, "falta_info", None),
                "duracion_ms": getattr(tc, "duracion_ms", None),
                "n_imagenes": len(getattr(tc, "imagenes", []) or []),
            }
            for tc in tool_calls
        ],
        "informe_data": informe_data,
    }
    out_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n>> Volcado completo en: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())

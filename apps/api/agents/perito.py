"""Perito coordinador.

Pipeline real con Anthropic tool_use:

1. Recibe el caso completo (encargo, vehículos, hechos, lesiones).
2. En su system prompt tiene la lista de tools y una rúbrica por tipo de encargo.
3. Itera con Claude: el modelo decide qué tool llamar; ejecutamos; le devolvemos
   el resultado; repetimos hasta `stop_reason="end_turn"` o tope de iteraciones.
4. En el último turno, el Perito DEBE devolver un JSON final con respuestas C1, C2,
   C3, info_faltante y confianza_global.
"""

from __future__ import annotations

import json
import re
from typing import Any

from anthropic import APIError

from agents.tools import TOOLS, dispatch
from agents import trace_store
from config import get_claude, get_settings
from models import (
    AnalisisBiomecanico,
    AnalisisConformidadAtestado,
    Caso,
    Cita,
    ContextoEscenaResumen,
    ContextoMeteoResumen,
    FichaTecnicaVehiculo,
    FuenteNormativa,
    ImagenAnalizada,
    IncongruenciaAtestado,
    InformePericial,
    InfoFaltante,
    PrioridadInfoFaltante,
    RespuestaPregunta,
    ToolCallLog,
    CalculoFisico,
)


MAX_TURNS = 18  # Tope de seguridad para el loop de tools (10 specialists × algo de margen)
MODEL_PERITO_DEFAULT = "claude-opus-4-7"


SYSTEM_PROMPT = """Eres VERIDICT-PERITO, un perito forense de accidentes de tráfico que coordina varios agentes especialistas.

Trabajas en español de España. Tu objetivo es producir un BORRADOR de informe pericial UNE-EN 16775 que responda a las preguntas del encargo, citando las evidencias que recopilas con las herramientas a tu disposición.

DISPONES DE ESTAS TOOLS (ya descritas en el schema):
- consultar_escena(lat, lon, radio_m, direccion): geometría real, señales, Mapillary. PREFIERE pasar `direccion` cuando la dispongas: Nominatim resuelve coords más precisas. Reintenta automáticamente con radios 100 m y 250 m si OSM falla.
- consultar_meteo(lat, lon, fecha_iso): meteorología histórica.
- consultar_ficha_tecnica(marca, modelo, anio): ficha técnica del vehículo.
- consultar_legal(tipo_encargo, fecha_siniestro_iso, palabras_clave): normativa + BOE.
- calcular_fisica(modelo, parametros): **PhysicsAgent** — fuente de verdad de cifras físicas (NO genera imágenes). Modelos: balance_momento_alcance, velocidad_por_huella, distancia_detencion (con `incluir_tiempo_reaccion` bool), atropello_throw, **tiempo_huella** (clave atropello: t_total=t_reacción+t_ejecución+t_frenada de la víctima), **energia_cinetica** (acepta `v_kmh_lista` para tabla 10/20/50 km/h estilo ITRASA). Default μ=0.75 (asfalto seco).
- verificar_atestado(velocidad_calculada_kmh, velocidad_declarada_kmh, declaracion): contraste compatibilidad.
- analizar_conformidad_atestado(fecha_siniestro_iso, velocidad_declarada_kmh, velocidad_calculada_kmh, es_atropello): crítica metodológica DETERMINISTA del atestado (8 reglas R1-R8). OBLIGATORIA en encargos de responsabilidad/atropello/velocidad y siempre que haya fallecimiento.
- buscar_foto_perito(criterio): pide al BibliotecaFotosAgent la mejor foto del catálogo del perito que cumpla un criterio (p.ej. 'frontal del SEAT con parabrisas dañado'). Si no la hay, devuelve `requiere_foto=true` y la pregunta a hacerle al perito.
- analizar_imagen_dano(image_url, contexto): análisis visual de daños sobre una URL ya conocida (de Mapillary o devuelta por buscar_foto_perito).
- generar_frame_simulacion(evento, masa_a, masa_b, ebs_a_kmh, ebs_b_kmh, ...): **SimulacionAgent** — recreación VISUAL del siniestro (croquis SVG con vehículos, trayectorias, PDI, huellas). Le pasas las velocidades y masas QUE YA VALIDASTE con el PhysicsAgent; él solo renderiza, no calcula. Eventos: croquis_general, pre_impacto, impacto, post_impacto, huellas. Llámala AL MENOS UNA VEZ por informe relevante (responsabilidad/velocidad/atropello) para que el PDF lleve un croquis de reconstrucción.
- capturar_simulacion(t_segundos, descripcion): **SnapshotEscenaAgent** — captura UN INSTANTE de la EscenaSimulacionData ya reconstruida (la simulación cenital animable producida por el SimulationAgent). Devuelve URL de un SVG estático con los actores en ese momento, trayectorias visibles, huellas e impacto si ya ha ocurrido. **Disponible solo después de que la simulación esté reconstruida** (post-orquestación). Útil para attachear visualmente un instante a un argumento del informe (ej. "véase t=2.8 s, momento del contacto"). Es complementaria a `generar_frame_simulacion` (croquis físico abstracto): este es la captura de la escena REAL renderizada igual que el frontend.
- analizar_biomecanica(descripcion_lesiones, ...): aplica ESTT/DGT 2011 + WAD + AIS. OBLIGATORIO si hay lesiones graves o fallecimiento. En atropellos pasa `es_atropello=true` + `descripcion_danos_vehiculo` (texto con dónde quedaron los impactos: parabrisas/capó/techo) + `masa_vehiculo_kg` + `velocidad_estimada_kmh`. El agente devuelve análisis cefálico (cráneo) si la zona es la cabeza.

REGLAS:

1. NO ATRIBUYES CULPA — solo expones hechos, normativa y cálculos. La calificación última es del perito firmante y del juez.

2. ESTRATEGIA DE INVESTIGACIÓN — REGLA UNIVERSAL Y POR ENCARGO.
   REGLA UNIVERSAL (todos los encargos): consultar_escena + consultar_meteo SIEMPRE (son contexto base que el lector espera ver).
   POR ENCARGO (rúbrica concreta):
   - responsabilidad_trafico: ficha + legal(['art.3','art.45','principio de confianza']) + calcular_fisica(distancia_detencion con incluir_tiempo_reaccion=false) + verificar_atestado + analizar_conformidad_atestado + generar_frame_simulacion(croquis_general).
   - velocidad_impacto: ficha + calcular_fisica(velocidad_por_huella + tiempo_huella + energia_cinetica) + verificar_atestado + analizar_conformidad_atestado + generar_frame_simulacion(impacto).
   - seguridad_pasiva: ficha + calcular_fisica(balance_momento_alcance) + legal(['airbag','antiempotramiento','ECE-R12','FMVSS-208']) + analizar_biomecanica.
   - atropello: ficha + escena(direccion=...) + calcular_fisica(velocidad_por_huella) + calcular_fisica(tiempo_huella para la víctima) + calcular_fisica(distancia_detencion del vehículo a la velocidad reglamentaria, incluir_tiempo_reaccion=true) + calcular_fisica(energia_cinetica con v_kmh_lista=[10,20,50] para tabla comparativa) + legal(['art.3','art.45','art.46','principio de confianza']) + generar_frame_simulacion(impacto) + analizar_biomecanica(es_atropello=true) + analizar_conformidad_atestado.
   - mecanica_fallo: ficha + legal + escena.
   - cuantia_danos: ficha + legal + escena + analizar_biomecanica si hay lesiones.

   PATRÓN DE EVITABILIDAD (atropello/responsabilidad): compara `tiempo_huella(víctima)` vs `tiempo_total(distancia_detencion del vehículo a velocidad reglamentaria con t_reacción=1s)`. Si t_huella > t_detencion, el accidente era evitable a velocidad reglamentaria. Cita ambos cálculos en la respuesta.

   ATRIBUCIÓN DE HUELLAS — CRÍTICA. Si el atestado atribuye una huella al CICLISTA/PEATÓN (no al turismo), la `velocidad_por_huella` calculada es la de la víctima, NO una cota inferior de la del turismo. NUNCA presentes la velocidad del ciclista como "rango mínimo del turismo". La velocidad del turismo se acota por OTROS indicios (WAD biomecánico, daños en vehículo, distancia de proyección Searle si aplica). Mantén ambos análisis SEPARADOS y rotulados claramente.

   CIFRA PERICIAL ÚNICA — CIERRE OBLIGATORIO. En las preguntas de velocidad (C1 típicamente) NO basta con enumerar rangos paralelos ("X-Y cinemático" + "Z-W biomecánico"). DEBES cerrar la respuesta con UNA cifra pericial final acotada del estilo "velocidad real del turismo en el impacto: AL MENOS V km/h" o "V±Δ km/h", razonando cuál es el indicio dominante. Criterio de selección por defecto:
     · Si hay rango WAD biomecánico, ése es el dominante (los daños son evidencia objetiva en el vehículo). Cierra con el extremo INFERIOR del rango WAD como mínimo pericial ("al menos X km/h", estilo ITRASA "al menos 50 km/h").
     · Si solo hay cinemática (huella del propio turismo), cierra con esa cifra.
     · Si el rango WAD y otros indicios discrepan, explica la discrepancia y elige la cota más conservadora pericialmente.
   La energía cinética que cites debe corresponder a esa cifra final, no a un punto medio inventado. Si llamaste a `analizar_biomecanica`, usa el campo `energia_cinetica_v_kmh_referencia` que ya devuelve el agente (corresponde al extremo superior del WAD) o consulta directamente `calcular_fisica(energia_cinetica)` con la velocidad pericial elegida.

   FRAME DE SIMULACIÓN — INPUTS VALIDADOS. Cuando llames a `generar_frame_simulacion`, las velocidades `ebs_a_kmh`/`ebs_b_kmh` DEBEN ser las que ya validaste con el PhysicsAgent (output de `calcular_fisica`). NO inventes velocidades de impacto: el SimulacionAgent rechazará el frame si el balance de momento se desvía >15 % de la consistencia física. Si recibes `rechazado=true`, vuelve a calcular con el PhysicsAgent y reintenta.

3. Si una tool devuelve `falta_info`, INCLUYE esa pregunta como `info_faltante` en tu JSON final, dirigida al perito humano. NUNCA inventes datos.

3.bis CRÍTICA AL ATESTADO. Si `analizar_conformidad_atestado` devuelve valoración "incompleto" o "deficiente", AÑADE una respuesta extra al final con `pregunta_id="C-AT"` y `pregunta="Crítica metodológica al atestado"` que enumere las incongruencias y omisiones más relevantes. Cita las que detectó el agente con `{"tipo":"hecho","referencia":"ConformidadAtestadoAgent — R<n>"}`.

4. FOTOS DEL PERITO — EXPLORACIÓN EXHAUSTIVA OBLIGATORIA.

   PRIMER PASO OBLIGATORIO: llama `listar_biblioteca_fotos()` ANTES que cualquier otra tool de fotos. Devuelve el inventario COMPLETO ya clasificado por visión Claude (por tipo: vehiculo_frontal, vehiculo_detalle_dano, escena_huellas, escena_senalizacion, croquis, lesion…). Con eso conoces qué tienes a tu disposición.

   En el payload solo recibes `n_fotos_disponibles` y `tipos_fotos_disponibles`. La biblioteca completa (con descripciones e ids) la obtienes UNA VEZ con `listar_biblioteca_fotos`. NO recibes URLs hasta llamar `buscar_foto_perito` o `listar_biblioteca_fotos`.

   REGLA DURA: por CADA respuesta C_i que vayas a emitir, identifica al menos UN aspecto visual relevante y llama `buscar_foto_perito(criterio="...")` para localizarlo. Para cada foto encontrada, llama `analizar_imagen_dano(image_url, contexto="qué quieres ver")` para tener una descripción técnica que puedas citar.

   Antes de cerrar el informe, REVISA el catálogo y pide fotos para CADA UNA de estas categorías que sea relevante al caso:
   - Daños frontales / capó / parabrisas / techo del vehículo (clave para WAD).
   - Daños del segundo vehículo o del peatón/ciclista (bici, casco, ropa).
   - Escena: vista general de la vía, curva, pendiente, anchura.
   - Huellas en calzada (frenada, derrape, arrastre).
   - Señalización (límite de velocidad, ceda, stop, paso peatones).
   - Croquis o diagramas técnicos del expediente.
   - Posición final de los vehículos / cuerpo de la víctima.

   Si una categoría no tiene match (`requiere_foto=true`), AÑÁDELA a `info_faltante` con la pregunta concreta. Si SÍ tiene match, CITA la imagen en la respuesta correspondiente con `{"tipo":"imagen","referencia":"<id corto> — <descripción>"}`.

   FORMATO DE LA REFERENCIA — OBLIGATORIO. El `<id corto>` es el primer fragmento (8 chars) del `id` UUID que te devolvió `buscar_foto_perito`/`listar_biblioteca_fotos`/`generar_frame_simulacion` (ej. para `id="e2a59537-1c4d-..."` → `e2a59537`). DEBE ir AL INICIO de la `referencia`, sin paréntesis ni etiquetas previas. Ejemplos válidos: `"e2a59537 — Parabrisas frontal fracturado"`, `"3a7702e0 — Frame croquis_general v_A=50 v_B=34.9"`. Ejemplos PROHIBIDOS: `"FOTO-PARABRISAS-01 (e2a59537) — ..."`, `"SimulacionAgent — croquis (3a7702e0) — ..."`, `"e2a59537-1c4d-... — ..."`. Si no recuerdas el id, NO inventes una etiqueta: vuelve a llamar a la tool correspondiente.

   El objetivo es que el informe final esté SUSTENTADO POR EVIDENCIA VISUAL del expediente, no solo por números. Apunta a 4-8 imágenes citadas si el catálogo lo permite.

5. CITAS OBLIGATORIAS. Toda afirmación cuantitativa o normativa va con cita {tipo, referencia, extracto}.
   Tipos válidos: 'calculo' | 'normativa' | 'ficha_tecnica' | 'hecho' | 'imagen' | 'meteo' | 'escena'.

5.bis CALIFICACIÓN TÉCNICA DE LA COLISIÓN. El campo `tipo_colision` del input es genérico (atropello, alcance, lateral…). En la respuesta C1 (o donde proceda) DEBES dar la calificación TÉCNICA precisa de la colisión observada: por ejemplo "fronto-lateral excéntrica turismo-bicicleta", "alcance trasero centrado", "frontal centrado entre dos turismos", "lateral con contacto puerta-paragolpes", etc. La calificación se deduce de la zona de impacto del vehículo y la dirección relativa de las víctimas. NO repitas el enum genérico del input.

5.ter LLAMADA AL LegalAgent. Cuando invoques `consultar_legal`, pasa SIEMPRE `descripcion_caso` (1-2 frases con los hechos núcleo) y `preguntas_encargo` (las cuestiones C_i del informe). Esto permite al agente seleccionar normativa con criterio en lugar de filtrar por palabras.

6. EFICIENCIA: como máximo 8-10 tool calls. No repitas la misma tool con los mismos inputs.

7. Una vez tengas suficiente información, EMITE TU RESPUESTA FINAL como un MENSAJE DE TEXTO (sin más tool_use) con un objeto JSON único:
{
  "resumen_caso": str,
  "respuestas": [{"pregunta_id":"C1","pregunta":str,"respuesta":str,"confianza":float,"citas":[...]}],
  "info_faltante": [{"id":"Q1","pregunta":str,"motivo":str,"prioridad":"bloqueante|recomendable|mejora","afecta_a":["C1"],"requiere_foto":bool}],
  "confianza_global": float
}
Sin markdown, sin comentarios fuera del JSON.

Tono: pericial, conciso, español de España.
"""


def _payload_inicial(caso: Caso) -> dict:
    return {
        "encargo": caso.encargo.model_dump(mode="json") if caso.encargo else None,
        "siniestro": {
            "fecha": caso.fecha_accidente.isoformat() if caso.fecha_accidente else None,
            "tipo_colision": caso.tipo_colision.value if caso.tipo_colision else None,
            "ubicacion": caso.ubicacion.model_dump(mode="json") if caso.ubicacion else None,
        },
        "vehiculos_identificacion": [
            v.model_dump(mode="json") for v in caso.vehiculos_identificacion
        ],
        "hechos_atestado": (
            caso.hechos_atestado.model_dump(mode="json") if caso.hechos_atestado else None
        ),
        "lesiones": [l.model_dump(mode="json") for l in caso.lesiones],
        # Catálogo COMPACTO. La descripción larga + tags + calidad de cada foto
        # se consultan SOLO bajo demanda con `listar_biblioteca_fotos` o
        # `buscar_foto_perito`. Esto evita inflar el payload del modelo cuando
        # hay decenas de fotos indexadas.
        "n_fotos_disponibles": sum(1 for f in caso.fotos if f.url),
        "tipos_fotos_disponibles": sorted({
            (f.tipo.value if f.tipo else "otro") for f in caso.fotos if f.url
        }),
        "chat_previo": [
            {"rol": m.rol, "contenido": m.contenido}
            for m in (caso.informe.chat if caso.informe else [])
        ],
    }


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


async def coordinar(caso: Caso, *, caso_id: str | None = None) -> dict:  # noqa: C901 - tamaño aceptable para el orquestador
    """Orquesta los specialists con tool_use.

    Si se pasa `caso_id`, va escribiendo el progreso al `trace_store` para
    que el frontend pueda hacer polling y verlo en directo.
    """
    contexto_dispatch = {
        "caso_id": caso_id or caso.id,
        "fotos": list(caso.fotos),
        "hechos_atestado": caso.hechos_atestado.model_dump(mode="json") if caso.hechos_atestado else {},
        "lesiones": [l.model_dump(mode="json") for l in (caso.lesiones or [])],
        # `simulacion_escena` se rellena dinámicamente cuando el Perito invoca
        # un specialist que la produce/usa. Mientras tanto: la del informe
        # previo si existe (regeneraciones).
        "simulacion_escena": (
            caso.informe.simulacion_escena.model_dump(mode="json")
            if (caso.informe and caso.informe.simulacion_escena) else None
        ),
    }
    """Devuelve {informe_data, tool_calls, imagenes_recopiladas}.

    `informe_data` es el JSON tal como lo emite el Perito (con citas).
    `tool_calls` es la lista de ToolCallLog que se persistirá en el InformePericial.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        if caso_id:
            trace_store.finalize(caso_id, estado="error",
                                 mensaje="ANTHROPIC_API_KEY no configurada",
                                 error="ANTHROPIC_API_KEY no configurada")
        return {
            "informe_data": None,
            "tool_calls": [],
            "imagenes_recopiladas": [],
            "error": "ANTHROPIC_API_KEY no configurada",
        }

    client = get_claude()
    payload = _payload_inicial(caso)
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": (
            "Estos son los datos del caso. Investiga con tus herramientas y "
            "responde a las preguntas del encargo:\n\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
        )},
    ]

    tool_calls_log: list[ToolCallLog] = []
    imagenes_recopiladas: list[ImagenAnalizada] = []
    datos_por_tool: dict[str, dict] = {}   # último 'datos' devuelto por cada tool name
    datos_completos: list[dict] = []       # secuencia ordenada de {tool, inputs, datos}
    razonamiento_perito: list[dict] = []   # turnos del Perito {turno, texto, tools_pedidas}
    final_json: dict | None = None
    error: str | None = None

    print(f"[perito] === START caso={caso.id} turnos_max={MAX_TURNS} ===", flush=True)
    if caso_id:
        trace_store.update(caso_id, estado="contexto_listo",
                           mensaje="Veridict-Perito recibe el caso y arranca el primer turno…")
    for turn in range(MAX_TURNS):
        print(f"[perito] turno {turn + 1}/{MAX_TURNS} → llamando a Opus…", flush=True)
        if caso_id:
            trace_store.update(caso_id, estado="llamando_perito",
                               mensaje=f"Turno {turn + 1}: el perito decide siguiente paso…")
        try:
            resp = await client.messages.create(
                model=MODEL_PERITO_DEFAULT,
                max_tokens=12000,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except APIError as e:
            # Si Opus no está disponible, fallback a Sonnet
            if turn == 0 and "model" in str(e).lower():
                print(f"[perito] Opus falló ({e}); fallback a Sonnet", flush=True)
                try:
                    resp = await client.messages.create(
                        model=settings.model_sonnet,
                        max_tokens=12000,
                        system=SYSTEM_PROMPT,
                        tools=TOOLS,
                        messages=messages,
                    )
                except APIError as e2:
                    error = str(e2)
                    print(f"[perito] ERROR fallback Sonnet: {e2}", flush=True)
                    break
            else:
                error = str(e)
                print(f"[perito] ERROR turno {turn + 1}: {e}", flush=True)
                break

        # Persistir el turno del asistente para mantener contexto
        messages.append({"role": "assistant", "content": resp.content})

        # Capturar el razonamiento del Perito (text blocks entre tool_use)
        text_blocks = "".join(
            b.text for b in resp.content if getattr(b, "type", None) == "text"
        ).strip()
        tools_pedidas = [
            {"name": b.name, "input": b.input or {}}
            for b in resp.content if getattr(b, "type", None) == "tool_use"
        ]
        if text_blocks or tools_pedidas:
            turno_dict = {
                "turno": turn + 1,
                "razonamiento": text_blocks,
                "tools_pedidas": tools_pedidas,
                "stop_reason": resp.stop_reason,
            }
            razonamiento_perito.append(turno_dict)
            if caso_id:
                trace_store.append_turno(caso_id, turno_dict)

        if text_blocks:
            print(f"[perito] turno {turn + 1} pensamiento: {text_blocks[:200]}", flush=True)
        if resp.stop_reason == "tool_use":
            print(f"[perito] turno {turn + 1} → {len(tools_pedidas)} tool_use: "
                  f"{[t['name'] for t in tools_pedidas]}", flush=True)
            tool_results = []
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use":
                    name = block.name
                    args = block.input or {}
                    print(f"[perito]   → dispatch {name}({json.dumps(args, ensure_ascii=False)[:120]})", flush=True)
                    if caso_id:
                        trace_store.update(caso_id, estado="dispatch",
                                           mensaje=f"Turno {turn + 1}: consultando {name}…")
                    try:
                        out = await dispatch(name, args, contexto=contexto_dispatch)
                    except Exception as e:
                        out = {"datos": {"error": f"excepción en tool: {e}"}, "_log": None}
                        print(f"[perito]   ✗ {name} excepción: {e}", flush=True)
                    else:
                        print(f"[perito]   ✓ {name} ok", flush=True)

                    log: ToolCallLog | None = out.get("_log")
                    if log:
                        tool_calls_log.append(log)
                        imagenes_recopiladas.extend(log.imagenes)
                    if "datos" in out and isinstance(out["datos"], dict):
                        datos_por_tool[name] = out["datos"]
                        dato_record = {
                            "turno": turn + 1,
                            "tool": name,
                            "inputs": args,
                            "datos": out["datos"],
                        }
                        datos_completos.append(dato_record)
                        if caso_id:
                            trace_store.append_tool_call(caso_id, dato_record)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(_clean_for_serialize(out.get("datos", {})),
                                              ensure_ascii=False)[:8000],
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        # stop_reason == "end_turn" o "max_tokens" → buscamos JSON final en los bloques de texto
        truncado = resp.stop_reason == "max_tokens"
        print(f"[perito] turno {turn + 1} stop_reason={resp.stop_reason} → cerrando informe"
              + (" (TRUNCADO por max_tokens, forzaré cierre limpio)" if truncado else ""),
              flush=True)
        if caso_id:
            trace_store.update(caso_id, estado="cerrando",
                               mensaje="Redactando informe pericial final…")
        text_out = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        if truncado:
            # No intentamos parsear JSON truncado — vamos directo al cierre forzado.
            final_json = await _forzar_json_final(client, settings, messages)
            if final_json is None:
                error = "El Perito truncó la respuesta y el cierre forzado tampoco devolvió JSON válido."
        else:
            try:
                final_json = _extract_json(text_out)
            except Exception:
                # Forzar un turno final pidiendo SOLO el JSON
                print("[perito] JSON no parseable, forzando cierre…", flush=True)
                if caso_id:
                    trace_store.update(caso_id, estado="cerrando",
                                       mensaje="Forzando cierre del JSON pericial…")
                final_json = await _forzar_json_final(client, settings, messages)
                if final_json is None:
                    error = "El Perito no devolvió un JSON parseable tras forzar el cierre."
        if caso_id and final_json:
            trace_store.update(caso_id, informe_borrador=final_json,
                               mensaje="Informe redactado, ensamblando vista final…")
        break
    else:
        # Tope de turnos alcanzado — pedimos JSON con los datos recopilados
        print(f"[perito] tope {MAX_TURNS} turnos alcanzado, forzando cierre…", flush=True)
        if caso_id:
            trace_store.update(caso_id, estado="cerrando",
                               mensaje=f"Tope de {MAX_TURNS} turnos alcanzado, forzando cierre…")
        final_json = await _forzar_json_final(client, settings, messages)
        if final_json is None:
            error = f"Se alcanzó el límite de {MAX_TURNS} turnos sin respuesta final."

    print(f"[perito] === END caso={caso.id} turnos={len(razonamiento_perito)} "
          f"tool_calls={len(tool_calls_log)} error={error or 'none'} ===", flush=True)
    return {
        "informe_data": final_json,
        "tool_calls": tool_calls_log,
        "imagenes_recopiladas": imagenes_recopiladas,
        "datos_por_tool": datos_por_tool,
        "datos_completos": datos_completos,
        "razonamiento_perito": razonamiento_perito,
        "error": error,
    }


CLOSING_SYSTEM = """Eres VERIDICT-PERITO. Cierras un informe pericial en JSON estricto.

Devuelve EXCLUSIVAMENTE un objeto JSON con esta estructura (sin markdown, sin texto antes ni después):

{
  "resumen_caso": "string 2-3 frases",
  "respuestas": [
    {"pregunta_id":"C1","pregunta":"...","respuesta":"párrafo pericial 100-200 palabras","confianza":0.7,
     "citas":[{"tipo":"calculo|normativa|ficha_tecnica|hecho|imagen|meteo|escena","referencia":"...","extracto":"..."}]}
  ],
  "info_faltante": [
    {"id":"Q1","pregunta":"...","motivo":"...","prioridad":"bloqueante|recomendable|mejora","afecta_a":["C1"],"requiere_foto":false}
  ],
  "confianza_global": 0.0_to_1.0
}

REGLAS:
- NO atribuyas culpa.
- Cita cálculos, fichas, normativa, imágenes y frames con sus referencias exactas.
- Si la conformidad del atestado fue 'incompleto' o 'deficiente', AÑADE una respuesta extra con `pregunta_id="C-AT"` y `pregunta="Crítica metodológica al atestado"` enumerando incongruencias y omisiones.
- Apunta a 4-8 citas por respuesta cuando hay datos disponibles."""


async def _forzar_json_final(client, settings, messages: list[dict]) -> dict | None:
    """Cierre SIN tools, system prompt ligero, max_tokens generoso."""
    closing_user = {
        "role": "user",
        "content": (
            "FIN DE LA INVESTIGACIÓN. Cierra el informe AHORA respondiendo a TODAS las "
            "cuestiones del encargo con citas exhaustivas a las tools que invocaste. "
            "Devuelve solo el JSON."
        ),
    }
    # Probamos Sonnet (más rápido, JSON fiable) y luego Opus como respaldo
    for model in (settings.model_sonnet, MODEL_PERITO_DEFAULT):
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=16000,
                system=CLOSING_SYSTEM,
                messages=list(messages) + [closing_user],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
            data = _extract_json(text)
            if data and (data.get("respuestas") or data.get("resumen_caso")):
                return data
        except (APIError, ValueError, json.JSONDecodeError):
            continue
    return None


def _clean_for_serialize(o: Any) -> Any:
    """Convierte objetos Pydantic/anidados a JSON serializable."""
    if hasattr(o, "model_dump"):
        return o.model_dump(mode="json")
    if isinstance(o, dict):
        return {k: _clean_for_serialize(v) for k, v in o.items() if not k.startswith("_log")}
    if isinstance(o, (list, tuple)):
        return [_clean_for_serialize(x) for x in o]
    return o


# ── Construcción del InformePericial a partir de la salida del Perito ──────

def construir_informe(
    coord_out: dict,
    fichas_recopiladas: list[FichaTecnicaVehiculo],
    normativa_recopilada: list[FuenteNormativa],
    bibliografia_recopilada: list[str],
    calculos_recopilados: list[CalculoFisico],
    chat_previo: list,
    simulacion_escena: dict | None = None,
) -> InformePericial:
    """Funde el JSON del Perito + las fuentes acumuladas en un InformePericial."""
    from models import EscenaSimulacionData
    data = coord_out.get("informe_data") or {}

    respuestas = [
        RespuestaPregunta(
            pregunta_id=r.get("pregunta_id", f"C{i+1}"),
            pregunta=r.get("pregunta", ""),
            respuesta=r.get("respuesta", ""),
            confianza=float(r.get("confianza", 0.0)),
            citas=[Cita(**c) for c in r.get("citas", [])],
        )
        for i, r in enumerate(data.get("respuestas", []))
    ]
    info = [
        InfoFaltante(
            id=q.get("id", f"Q{i+1}"),
            pregunta=q.get("pregunta", ""),
            motivo=q.get("motivo", ""),
            prioridad=PrioridadInfoFaltante(q.get("prioridad", "recomendable")),
            afecta_a=q.get("afecta_a", []),
            requiere_foto=bool(q.get("requiere_foto", False)),
        )
        for i, q in enumerate(data.get("info_faltante", []))
    ]

    datos = coord_out.get("datos_por_tool") or {}
    bio_raw = datos.get("analizar_biomecanica")
    bio_struct = _build_biomecanico(bio_raw) if bio_raw else None
    escena_raw = datos.get("consultar_escena")
    escena_struct = _build_escena(escena_raw) if escena_raw else None
    meteo_raw = datos.get("consultar_meteo")
    meteo_struct = _build_meteo(meteo_raw) if meteo_raw else None
    conf_raw = datos.get("analizar_conformidad_atestado")
    conf_struct = _build_conformidad(conf_raw) if conf_raw else None

    sim_struct: EscenaSimulacionData | None = None
    if simulacion_escena:
        try:
            sim_struct = EscenaSimulacionData.model_validate(simulacion_escena)
        except Exception:
            sim_struct = None

    return InformePericial(
        resumen_caso=data.get("resumen_caso", "") or coord_out.get("error", "Informe no generado."),
        fichas_tecnicas=fichas_recopiladas,
        normativa_aplicable=normativa_recopilada,
        bibliografia=bibliografia_recopilada,
        calculos=calculos_recopilados,
        respuestas=respuestas,
        info_faltante=info,
        chat=chat_previo,
        tool_calls=coord_out.get("tool_calls", []),
        imagenes=coord_out.get("imagenes_recopiladas", []),
        analisis_biomecanico=bio_struct,
        contexto_escena=escena_struct,
        contexto_meteo=meteo_struct,
        conformidad_atestado=conf_struct,
        simulacion_escena=sim_struct,
        confianza_global=float(data.get("confianza_global", 0.0)),
    )


def _build_escena(raw: dict) -> ContextoEscenaResumen:
    via = raw.get("via_principal") or {}
    maxspeed_raw = via.get("maxspeed")
    try:
        maxspeed_kmh = int(str(maxspeed_raw).split()[0]) if maxspeed_raw else None
    except (ValueError, IndexError):
        maxspeed_kmh = None
    return ContextoEscenaResumen(
        direccion_resuelta=raw.get("direccion_resuelta"),
        lat_resuelta=raw.get("lat_resuelta"),
        lon_resuelta=raw.get("lon_resuelta"),
        via_principal_nombre=via.get("name") or via.get("ref"),
        via_principal_tipo=via.get("highway"),
        velocidad_maxima_kmh=maxspeed_kmh,
        num_carriles=via.get("lanes"),
        anchura_m=via.get("width"),
        superficie=via.get("surface"),
        tiene_carril_bici=bool(raw.get("tiene_carril_bici")),
        pasos_peatones_proximos=int(raw.get("n_pasos_peatones") or 0),
        senales=raw.get("senales") or [],
        pendiente_pct=raw.get("pendiente_pct"),
        pendiente_descartada_pct=raw.get("pendiente_descartada_pct"),
        elevacion_m=raw.get("elevacion_m"),
        visibilidad_efectiva_m=raw.get("visibilidad_efectiva_m"),
        visibilidad_efectiva_fuente=raw.get("visibilidad_efectiva_fuente"),
        n_imagenes_mapillary=int(raw.get("imagenes_disponibles") or 0),
        fuentes=raw.get("fuentes") or [],
    )


def _build_meteo(raw: dict) -> ContextoMeteoResumen:
    return ContextoMeteoResumen(
        temperatura_c=raw.get("temperatura_c"),
        precipitacion_mm=raw.get("precipitacion_mm"),
        viento_kmh=raw.get("viento_kmh"),
        visibilidad_m=raw.get("visibilidad_m"),
        estado_tiempo=raw.get("estado_tiempo"),
        calzada_estimada=raw.get("calzada_estimada"),
        es_dia=raw.get("es_dia"),
        amanecer=raw.get("amanecer"),
        atardecer=raw.get("atardecer"),
        fuente=raw.get("fuente"),
    )


def _build_conformidad(raw: dict) -> AnalisisConformidadAtestado:
    return AnalisisConformidadAtestado(
        incongruencias=[IncongruenciaAtestado(**i) for i in (raw.get("incongruencias") or [])],
        elementos_omitidos=raw.get("elementos_omitidos") or [],
        valoracion_global=raw.get("valoracion_global"),
        recomendaciones=raw.get("recomendaciones") or [],
    )


def _build_biomecanico(raw: dict) -> AnalisisBiomecanico:
    from models import (
        AceleracionTipo, AnalisisCraneal, ImpactoSucesivo,
        MecanismoLesivo, TipoLesionCraneal, WADResultado,
    )
    wad = None
    if raw.get("wad"):
        w = raw["wad"]
        try:
            wad = WADResultado(
                zona_impacto=w["zona_impacto"],
                altura_m=tuple(w["altura_m"]),
                velocidad_min_kmh=float(w["velocidad_min_kmh"]),
                velocidad_max_kmh=float(w["velocidad_max_kmh"]),
                fuente=w.get("fuente"),
            )
        except (KeyError, TypeError, ValueError):
            wad = None

    craneal = None
    ac = raw.get("analisis_craneal")
    if ac:
        craneal = AnalisisCraneal(
            mecanismo_general=ac.get("mecanismo_general", ""),
            tipos_compatibles=[
                TipoLesionCraneal(nombre=t.get("nombre", ""), mecanismo=t.get("mecanismo", ""))
                for t in (ac.get("tipos_compatibles") or [])
            ],
            consideracion_clinica=ac.get("consideracion_clinica"),
        )

    return AnalisisBiomecanico(
        wad=wad,
        energia_cinetica_kj=raw.get("energia_cinetica_kj"),
        probabilidad_ais3_pct=raw.get("probabilidad_ais3_pct"),
        mecanismos_lesivos_compatibles=[
            MecanismoLesivo(**m) for m in (raw.get("mecanismos_lesivos_compatibles") or [])
        ],
        cadena_4_impactos_sucesivos=[
            ImpactoSucesivo(**i) for i in (raw.get("cadena_4_impactos_sucesivos") or [])
        ],
        analisis_craneal=craneal,
        compatibilidad_velocidad_lesion=raw.get("compatibilidad_velocidad_lesion"),
        tabla_aceleraciones_tipo=[
            AceleracionTipo(**a) for a in (raw.get("tabla_aceleraciones_tipo") or [])
        ],
        fuentes=raw.get("fuentes") or [],
    )

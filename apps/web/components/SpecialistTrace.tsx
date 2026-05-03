"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { RazonamientoOrquestador, ToolCallTrace } from "@veridict/types";
import {
  Wrench,
  ChevronDown,
  ChevronRight,
  Loader2,
  Brain,
  ExternalLink,
} from "lucide-react";

interface SpecialistMeta {
  icon: string;
  color: string;
  label: string;
  /** Campos del `respuesta_completa.datos` que merece la pena destacar arriba. */
  highlights?: string[];
}

const SPECIALIST_META: Record<string, SpecialistMeta> = {
  consultar_escena: {
    icon: "📍",
    color: "text-emerald-300",
    label: "EscenaAgent",
    highlights: [
      "direccion_resuelta",
      "via_principal",
      "n_vias",
      "n_senales",
      "tiene_carril_bici",
      "n_pasos_peatones",
      "elevacion_m",
      "pendiente_pct",
      "pendiente_media_pct",
      "pendiente_fiable",
      "pendiente_descartada_pct",
      "visibilidad_efectiva_m",
      "visibilidad_efectiva_fuente",
      "imagenes_disponibles",
      "radio_efectivo_m",
    ],
  },
  consultar_meteo: {
    icon: "🌤️",
    color: "text-sky-300",
    label: "MeteoAgent",
    highlights: [
      "temperatura_c",
      "precipitacion_mm",
      "humedad_pct",
      "viento_kmh",
      "viento_direccion",
      "visibilidad_km",
      "nubosidad_pct",
      "estado_tiempo",
      "es_dia",
      "hora_amanecer",
      "hora_atardecer",
      "azimuth_sol",
      "altitude_sol",
      "deslumbramiento_posible",
    ],
  },
  consultar_ficha_tecnica: {
    icon: "🚗",
    color: "text-blue-300",
    label: "FichaAgent",
    highlights: [
      "marca",
      "modelo",
      "anio",
      "masa_kg",
      "longitud_m",
      "ancho_m",
      "altura_m",
      "altura_parachoques_m",
      "altura_largueros_m",
      "rigidez_a",
      "rigidez_b",
      "sistemas_seguridad",
    ],
  },
  consultar_legal: {
    icon: "⚖️",
    color: "text-purple-300",
    label: "LegalAgent",
    highlights: ["referencia", "titulo", "boe", "extracto", "n_articulos"],
  },
  calcular_fisica: {
    icon: "📐",
    color: "text-amber-300",
    label: "PhysicsAgent",
    highlights: [
      "velocidad_minima_kmh",
      "delta_v_kmh",
      "distancia_total_m",
      "distancia_frenada_m",
      "tiempo_total_s",
      "t_frenada_s",
      "energia_cinetica_kj",
      "modelo_aplicado",
      "formula",
      "asunciones",
    ],
  },
  // Alias deprecado
  simular_fisica: {
    icon: "📐",
    color: "text-amber-300",
    label: "PhysicsAgent",
    highlights: [
      "velocidad_minima_kmh",
      "delta_v_kmh",
      "distancia_total_m",
      "distancia_frenada_m",
      "tiempo_total_s",
      "modelo_aplicado",
      "formula",
      "asunciones",
    ],
  },
  verificar_atestado: {
    icon: "🔍",
    color: "text-pink-300",
    label: "AtestadoAgent",
    highlights: [
      "campos_verificados",
      "incongruencias",
      "huellas_consignadas",
      "compatible_con_evidencia",
    ],
  },
  analizar_conformidad_atestado: {
    icon: "📋",
    color: "text-rose-300",
    label: "ConformidadAgent",
    highlights: [
      "puntuacion_conformidad",
      "fortalezas",
      "deficiencias",
      "articulos_aplicables",
    ],
  },
  generar_frame_simulacion: {
    icon: "🎬",
    color: "text-indigo-300",
    label: "SimulacionAgent",
    highlights: ["frame_url", "evento", "v_pre_a_kmh", "v_pre_b_kmh", "delta_v_a_kmh", "delta_v_b_kmh", "error_momento_pct"],
  },
  // Alias deprecado
  obtener_frame_simulacion: {
    icon: "🎬",
    color: "text-indigo-300",
    label: "SimulacionAgent",
    highlights: ["frame_url", "evento", "v_pre_a_kmh", "v_pre_b_kmh", "delta_v_a_kmh", "delta_v_b_kmh"],
  },
  analizar_biomecanica: {
    icon: "🩺",
    color: "text-red-300",
    label: "BiomecanicaAgent",
    highlights: [
      "wad_m",
      "velocidad_estimada_kmh",
      "patron_lesional",
      "compatibilidad_con_velocidad",
      "zonas_impacto",
    ],
  },
  listar_biblioteca_fotos: {
    icon: "📚",
    color: "text-cyan-300",
    label: "BibliotecaFotos · listado",
    highlights: ["n_fotos", "categorias"],
  },
  buscar_foto_perito: {
    icon: "📷",
    color: "text-cyan-300",
    label: "BibliotecaFotos · búsqueda",
    highlights: ["query", "n_resultados", "fotos"],
  },
  analizar_imagen_dano: {
    icon: "👁️",
    color: "text-violet-300",
    label: "Vision · daños",
    highlights: ["zona_danada", "intensidad", "compatible_con_relato"],
  },
};

function metaFor(tool: string): SpecialistMeta {
  return (
    SPECIALIST_META[tool] || { icon: "🔧", color: "text-zinc-300", label: tool }
  );
}

interface Props {
  casoId: string;
  /** Nombre(s) de la tool a mostrar (e.g. ["consultar_escena"]). */
  tools: string[];
  /** Título de la sección. */
  title?: string;
  /** Texto introductorio breve. */
  description?: string;
}

interface CallWithTurn extends ToolCallTrace {
  turno: number;
  razonamientoTurno: string;
}

export function SpecialistTrace({ casoId, tools, title, description }: Props) {
  const [data, setData] = useState<RazonamientoOrquestador | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fetchData = async () => {
      try {
        const r = await api.getRazonamiento(casoId);
        if (!cancelled) {
          setData(r);
          setError(null);
        }
      } catch {
        if (!cancelled) setError("aún no disponible");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchData();
    const id = setInterval(fetchData, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [casoId]);

  const calls: CallWithTurn[] = useMemo(() => {
    if (!data) return [];
    const out: CallWithTurn[] = [];
    for (const turno of data.turnos) {
      for (const tc of turno.tools_pedidas) {
        if (tools.includes(tc.tool)) {
          out.push({ ...tc, turno: turno.turno, razonamientoTurno: turno.razonamiento });
        }
      }
    }
    return out;
  }, [data, tools]);

  const headerTitle = title ?? "Trabajo de los agentes especialistas";
  const headerDesc =
    description ??
    "Output completo y estructurado que el specialist devolvió al orquestador. Esta es la fuente de la que el Perito ha extraído la información para esta pestaña.";

  if (loading) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 flex items-center gap-3 text-sm text-zinc-400">
        <Loader2 className="w-4 h-4 animate-spin" />
        Cargando trabajo de los specialists…
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 text-sm text-zinc-500">
        El trabajo de los specialists aparecerá aquí una vez se genere el informe.
      </div>
    );
  }

  if (calls.length === 0) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 text-sm text-zinc-500">
        El orquestador no invocó ningún specialist relacionado con esta sección
        ({tools.join(", ")}) durante la generación del informe.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-purple-500/5 p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-blue-500/20 rounded-lg">
          <Wrench className="w-4 h-4 text-blue-300" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-white">{headerTitle}</h3>
            <span className="text-[11px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-200 border border-blue-500/30">
              {calls.length} {calls.length === 1 ? "llamada" : "llamadas"}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">{headerDesc}</p>
        </div>
      </div>

      <div className="space-y-2">
        {calls.map((c, i) => (
          <SpecialistCallCard key={i} call={c} />
        ))}
      </div>
    </div>
  );
}

function SpecialistCallCard({ call }: { call: CallWithTurn }) {
  const meta = metaFor(call.tool);
  const [expanded, setExpanded] = useState(true);
  const [showJson, setShowJson] = useState(false);

  // Extrae los datos del specialist (estructura {datos, imagenes, _log})
  const respuesta = (call.respuesta_completa ?? {}) as Record<string, unknown>;
  const datos = (respuesta.datos ?? respuesta) as Record<string, unknown>;
  const imagenes = Array.isArray(respuesta.imagenes)
    ? (respuesta.imagenes as Record<string, unknown>[])
    : [];
  const log = (respuesta._log ?? {}) as Record<string, unknown>;
  const fuentes = Array.isArray(log.fuentes_consultadas)
    ? (log.fuentes_consultadas as string[])
    : [];
  const faltaInfo = typeof log.falta_info === "string" ? log.falta_info : null;
  const duracion = typeof log.duracion_ms === "number" ? log.duracion_ms : null;

  const highlightFields = (meta.highlights ?? []).filter((k) => datos[k] !== undefined);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left p-3 flex items-start justify-between gap-3 hover:bg-zinc-900/80 rounded-t-lg"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-base">{meta.icon}</span>
            <span className={`text-sm font-bold ${meta.color}`}>{meta.label}</span>
            <span className="text-xs text-zinc-500 font-mono">.{call.tool}</span>
            <span className="text-[10px] uppercase tracking-wide text-zinc-500">
              · turno {call.turno}
            </span>
            {duracion != null && (
              <span className="text-[10px] text-zinc-500 font-mono">{duracion} ms</span>
            )}
          </div>
          {call.respuesta_resumen && (
            <p className="text-sm text-zinc-200 mt-1">
              <span className="text-zinc-500">→ </span>
              {call.respuesta_resumen}
            </p>
          )}
        </div>
        {expanded ? (
          <ChevronDown className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-1" />
        ) : (
          <ChevronRight className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-1" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-zinc-800 p-3 space-y-3">
          {/* Razonamiento del Perito que motivó esta llamada */}
          {call.razonamientoTurno && (
            <div className="p-2.5 rounded bg-blue-500/5 border border-blue-500/15">
              <div className="flex items-center gap-1.5 mb-1">
                <Brain className="w-3 h-3 text-blue-400" />
                <span className="text-[10px] uppercase tracking-wide text-blue-300">
                  ¿Por qué el Perito invocó este specialist?
                </span>
              </div>
              <p className="text-xs text-zinc-300 italic leading-relaxed">
                {call.razonamientoTurno}
              </p>
            </div>
          )}

          {/* Inputs */}
          {Object.keys(call.inputs).length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wide text-zinc-500 mb-1">
                Inputs del Perito
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                {Object.entries(call.inputs).map(([k, v]) => (
                  <KeyValueRow key={k} label={k} value={v} />
                ))}
              </div>
            </div>
          )}

          {/* Highlights del specialist */}
          {highlightFields.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wide text-zinc-500 mb-1">
                Datos devueltos por el specialist
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                {highlightFields.map((k) => (
                  <KeyValueRow key={k} label={k} value={datos[k]} />
                ))}
              </div>
            </div>
          )}

          {/* Imágenes */}
          {imagenes.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wide text-zinc-500 mb-1">
                Imágenes recopiladas ({imagenes.length})
              </p>
              <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                {imagenes.map((img, i) => {
                  const url = (img.url as string) ?? null;
                  const thumb = (img.thumb_url as string) ?? url;
                  const desc = (img.descripcion as string) ?? (img.relevancia as string) ?? "";
                  return (
                    <a
                      key={i}
                      href={url ?? undefined}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded border border-zinc-800 hover:border-zinc-600 overflow-hidden"
                    >
                      {thumb ? (
                        <img
                          src={thumb}
                          alt={desc}
                          className="w-full h-20 object-cover"
                        />
                      ) : (
                        <div className="w-full h-20 bg-zinc-900 flex items-center justify-center text-[10px] text-zinc-600">
                          sin miniatura
                        </div>
                      )}
                      {desc && (
                        <p className="text-[10px] text-zinc-400 truncate p-1">{desc}</p>
                      )}
                    </a>
                  );
                })}
              </div>
            </div>
          )}

          {/* Fuentes consultadas */}
          {fuentes.length > 0 && (
            <div className="text-xs">
              <span className="text-zinc-500">Fuentes consultadas: </span>
              <span className="text-zinc-300">{fuentes.join(" · ")}</span>
            </div>
          )}

          {/* Falta info */}
          {faltaInfo && (
            <div className="text-xs p-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-200">
              ⚠ {faltaInfo}
            </div>
          )}

          {/* JSON crudo colapsable */}
          <div>
            <button
              type="button"
              onClick={() => setShowJson(!showJson)}
              className="text-[11px] text-zinc-500 hover:text-zinc-300 inline-flex items-center gap-1"
            >
              <ExternalLink className="w-3 h-3" />
              {showJson ? "ocultar" : "ver"} JSON completo del specialist
            </button>
            {showJson && (
              <pre className="mt-1.5 text-[11px] text-zinc-400 bg-zinc-950 border border-zinc-800 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all max-h-72 overflow-y-auto">
                {JSON.stringify(call.respuesta_completa, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function KeyValueRow({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="text-xs flex gap-2 items-baseline border-b border-zinc-800/60 py-0.5">
      <span className="text-zinc-500 font-mono flex-shrink-0">{label}:</span>
      <span className="text-zinc-200 font-mono break-all">{formatValue(value)}</span>
    </div>
  );
}

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "boolean") return v ? "sí" : "no";
  if (typeof v === "number") return String(v);
  if (typeof v === "string") return v;
  if (Array.isArray(v)) {
    if (v.length === 0) return "[]";
    if (v.every((x) => typeof x === "string" || typeof x === "number")) {
      return v.join(", ");
    }
    return `[${v.length} elementos]`;
  }
  if (typeof v === "object") {
    try {
      return JSON.stringify(v);
    } catch {
      return "{…}";
    }
  }
  return String(v);
}

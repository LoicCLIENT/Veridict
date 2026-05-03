"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { RazonamientoOrquestador, TurnoOrquestador, ToolCallTrace } from "@veridict/types";
import { BorradorEnVivo } from "./BorradorEnVivo";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Brain,
  Wrench,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Loader2,
  RefreshCw,
  Sparkles,
  ArrowRight,
} from "lucide-react";

type PanelDestino =
  | "escena"
  | "contexto"
  | "vehiculos"
  | "legal"
  | "calculos"
  | "confrontacion"
  | "mapa"
  | "docs";

interface Props {
  casoId: string;
  onNavigateToPanel?: (panel: PanelDestino) => void;
}

const TOOL_META: Record<
  string,
  { icon: string; color: string; label: string; panel: PanelDestino; panelLabel: string }
> = {
  consultar_escena: {
    icon: "📍",
    color: "text-emerald-300",
    label: "EscenaAgent",
    panel: "escena",
    panelLabel: "Scene",
  },
  consultar_meteo: {
    icon: "🌤️",
    color: "text-sky-300",
    label: "MeteoAgent",
    panel: "contexto",
    panelLabel: "Context",
  },
  consultar_ficha_tecnica: {
    icon: "🚗",
    color: "text-blue-300",
    label: "FichaAgent",
    panel: "vehiculos",
    panelLabel: "Vehicles",
  },
  consultar_legal: {
    icon: "⚖️",
    color: "text-purple-300",
    label: "LegalAgent",
    panel: "legal",
    panelLabel: "Legal framework",
  },
  calcular_fisica: {
    icon: "📐",
    color: "text-amber-300",
    label: "PhysicsAgent",
    panel: "calculos",
    panelLabel: "Calculations",
  },
  // Deprecated alias — old runs
  simular_fisica: {
    icon: "📐",
    color: "text-amber-300",
    label: "PhysicsAgent",
    panel: "calculos",
    panelLabel: "Calculations",
  },
  verificar_atestado: {
    icon: "🔍",
    color: "text-pink-300",
    label: "AtestadoAgent",
    panel: "confrontacion",
    panelLabel: "Confrontation",
  },
  analizar_conformidad_atestado: {
    icon: "📋",
    color: "text-rose-300",
    label: "ConformidadAgent",
    panel: "confrontacion",
    panelLabel: "Confrontation",
  },
  generar_frame_simulacion: {
    icon: "🎬",
    color: "text-indigo-300",
    label: "SimulacionAgent",
    panel: "mapa",
    panelLabel: "Simulation",
  },
  // Deprecated alias — old runs
  obtener_frame_simulacion: {
    icon: "🎬",
    color: "text-indigo-300",
    label: "SimulacionAgent",
    panel: "mapa",
    panelLabel: "Simulation",
  },
  analizar_biomecanica: {
    icon: "🩺",
    color: "text-red-300",
    label: "BiomecanicaAgent",
    panel: "calculos",
    panelLabel: "Calculations",
  },
  listar_biblioteca_fotos: {
    icon: "📚",
    color: "text-cyan-300",
    label: "BibliotecaFotos",
    panel: "docs",
    panelLabel: "Docs/Fotos",
  },
  buscar_foto_perito: {
    icon: "📷",
    color: "text-cyan-300",
    label: "BibliotecaFotos",
    panel: "docs",
    panelLabel: "Docs/Fotos",
  },
  analizar_imagen_dano: {
    icon: "👁️",
    color: "text-violet-300",
    label: "Vision",
    panel: "docs",
    panelLabel: "Docs/Fotos",
  },
};

function metaFor(tool: string) {
  return (
    TOOL_META[tool] || {
      icon: "🔧",
      color: "text-zinc-300",
      label: tool,
      panel: null as PanelDestino | null,
      panelLabel: "",
    }
  );
}

const ESTADO_LABEL: Record<string, string> = {
  iniciando: "Preparing context…",
  contexto_listo: "Context ready, starting first turn",
  llamando_perito: "Veridict-Expert thinking…",
  dispatch: "Consulting specialist…",
  cerrando: "Drafting final report…",
  completado: "Expert report ready",
  error: "An error occurred",
};

export function RazonamientoOrquestadorView({ casoId, onNavigateToPanel }: Props) {
  const [data, setData] = useState<RazonamientoOrquestador | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTurns, setExpandedTurns] = useState<Set<number>>(new Set());
  const autoExpandRef = useRef<Set<number>>(new Set());

  const fetchData = async () => {
    try {
      const r = await api.getRazonamiento(casoId);
      setData(r);
      setError(null);
      // Auto-expand any new turn that appears live
      if (r) {
        setExpandedTurns((prev) => {
          const next = new Set(prev);
          for (const t of r.turnos) {
            if (!autoExpandRef.current.has(t.turno)) {
              autoExpandRef.current.add(t.turno);
              next.add(t.turno);
            }
          }
          return next;
        });
      }
    } catch {
      setError("not yet available");
    } finally {
      setLoading(false);
    }
  };

  // Polling every 1.5s while generation is in progress
  useEffect(() => {
    fetchData();
    const id = setInterval(() => {
      // If the last state is terminal, stop requesting
      const estado = data?.estado;
      if (estado === "completado" || estado === "error") return;
      fetchData();
    }, 1500);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [casoId, data?.estado]);

  const toggleTurn = (n: number) => {
    setExpandedTurns((prev) => {
      const next = new Set(prev);
      if (next.has(n)) next.delete(n);
      else next.add(n);
      return next;
    });
  };

  if (loading) {
    return (
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardContent className="flex items-center gap-3 p-6 text-zinc-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading orchestrator reasoning…
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card className="bg-zinc-900/50 border-zinc-800">
        <CardContent className="p-6 text-center text-zinc-400 space-y-3">
          <p>The orchestrator reasoning will appear here when the report is generated.</p>
          <div className="flex items-center justify-center gap-2 text-xs text-zinc-500">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            Waiting for you to start a generation…
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Brain className="w-5 h-5 text-blue-300" />
              </div>
              <div>
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  Orchestrator reasoning
                  <Sparkles className="w-4 h-4 text-blue-300" />
                </CardTitle>
                <CardDescription>
                  Veridict-Expert (Opus 4.7) coordinating specialist agents live.
                </CardDescription>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchData}
              className="border-zinc-700 text-zinc-300"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-0 space-y-3">
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-zinc-500">Turns: </span>
              <span className="font-bold text-white">{data.n_turnos}</span>
            </div>
            <div>
              <span className="text-zinc-500">Tool calls: </span>
              <span className="font-bold text-white">{data.n_tool_calls}</span>
            </div>
            <div>
              <span className="text-zinc-500">Model: </span>
              <span className="font-mono text-blue-300">claude-opus-4-7</span>
            </div>
          </div>

          {/* Live status banner */}
          {data.estado && data.estado !== "completado" && (
            <div
              className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm border ${
                data.estado === "error"
                  ? "border-red-500/40 bg-red-500/10 text-red-200"
                  : "border-blue-500/40 bg-blue-500/10 text-blue-100"
              }`}
            >
              {data.estado === "error" ? (
                <span className="text-base">⚠️</span>
              ) : (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              <div className="flex-1 min-w-0">
                <div className="font-semibold">
                  {ESTADO_LABEL[data.estado] || data.estado}
                </div>
                {data.mensaje && (
                  <div className="text-xs text-zinc-300 truncate">
                    {data.mensaje}
                  </div>
                )}
                {data.error && (
                  <div className="text-xs text-red-300 mt-1">
                    {data.error}
                  </div>
                )}
              </div>
            </div>
          )}
          {data.estado === "completado" && data.en_vivo === false && (
            <div className="flex items-center gap-2 text-xs text-emerald-300">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Generation completed
            </div>
          )}
        </CardContent>
      </Card>

      {/* Live draft: the report is being built */}
      <BorradorEnVivo data={data} />

      {/* Turn timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[19px] top-2 bottom-2 w-px bg-zinc-800" aria-hidden />

        <div className="space-y-3">
          {data.turnos.map((t, idx) => (
            <TurnoCard
              key={`${t.turno}-${idx}`}
              turno={t}
              expanded={expandedTurns.has(t.turno)}
              onToggle={() => toggleTurn(t.turno)}
              onNavigateToPanel={onNavigateToPanel}
            />
          ))}
        </div>
      </div>
    </div>
  );
}


function TurnoCard({
  turno,
  expanded,
  onToggle,
  onNavigateToPanel,
}: {
  turno: TurnoOrquestador;
  expanded: boolean;
  onToggle: () => void;
  onNavigateToPanel?: (panel: PanelDestino) => void;
}) {
  const isFinal = turno.stop_reason === "end_turn";
  return (
    <div className="relative pl-12">
      {/* Timeline point */}
      <div
        className={`absolute left-0 top-0 w-10 h-10 rounded-full flex items-center justify-center border-2 z-10 ${
          isFinal
            ? "bg-green-500/20 border-green-500/40 text-green-300"
            : "bg-blue-500/20 border-blue-500/40 text-blue-300"
        }`}
      >
        {isFinal ? <CheckCircle2 className="w-4 h-4" /> : <span className="text-sm font-bold">{turno.turno}</span>}
      </div>

      <Card className="bg-zinc-900/50 border-zinc-800">
        <button
          type="button"
          onClick={onToggle}
          className="w-full text-left p-4 flex items-start justify-between gap-3 hover:bg-zinc-900/70 transition-colors rounded-t-xl"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase tracking-wide text-zinc-500">Turn {turno.turno}</span>
              {isFinal ? (
                <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-300 border border-green-500/30">
                  report closure
                </span>
              ) : turno.tools_pedidas.length > 0 ? (
                <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  {turno.tools_pedidas.length} {turno.tools_pedidas.length === 1 ? "tool" : "tools"}
                </span>
              ) : null}
            </div>
            {turno.razonamiento ? (
              <p className="text-sm text-zinc-200 line-clamp-2 italic">
                <Brain className="w-3.5 h-3.5 inline mr-1 text-blue-400" />
                {turno.razonamiento}
              </p>
            ) : (
              <p className="text-xs text-zinc-500 italic">No intermediate reasoning in this turn.</p>
            )}
          </div>
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-1" />
          ) : (
            <ChevronRight className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-1" />
          )}
        </button>

        {expanded && (
          <CardContent className="pt-0 space-y-3 border-t border-zinc-800">
            {turno.razonamiento && (
              <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/15">
                <div className="flex items-center gap-2 mb-1.5">
                  <Brain className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-xs font-medium text-blue-300">Expert reasoning</span>
                </div>
                <p className="text-sm text-zinc-200 whitespace-pre-line leading-relaxed">
                  {turno.razonamiento}
                </p>
              </div>
            )}

            {turno.tools_pedidas.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Wrench className="w-3.5 h-3.5 text-zinc-400" />
                  <span className="text-xs uppercase tracking-wide text-zinc-500">
                    Calls to specialists
                  </span>
                </div>
                <div className="space-y-2">
                  {turno.tools_pedidas.map((tc, i) => (
                    <ToolCallCard key={i} call={tc} onNavigateToPanel={onNavigateToPanel} />
                  ))}
                </div>
              </div>
            )}

            {isFinal && (
              <div className="p-3 rounded-lg bg-green-500/5 border border-green-500/20 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <p className="text-sm text-green-200">
                  The Expert closes the investigation and issues the structured JSON of the report.
                </p>
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
}


function ToolCallCard({
  call,
  onNavigateToPanel,
}: {
  call: ToolCallTrace;
  onNavigateToPanel?: (panel: PanelDestino) => void;
}) {
  const meta = metaFor(call.tool);
  const [showDetails, setShowDetails] = useState(false);
  const canNavigate = !!(onNavigateToPanel && meta.panel);

  return (
    <div
      className={`p-3 rounded-lg border bg-zinc-900/40 transition-colors ${
        canNavigate
          ? "border-zinc-800 hover:border-blue-500/50 hover:bg-zinc-900/70 cursor-pointer"
          : "border-zinc-800"
      }`}
      onClick={
        canNavigate
          ? () => onNavigateToPanel!(meta.panel as PanelDestino)
          : undefined
      }
      role={canNavigate ? "button" : undefined}
      tabIndex={canNavigate ? 0 : undefined}
      onKeyDown={
        canNavigate
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onNavigateToPanel!(meta.panel as PanelDestino);
              }
            }
          : undefined
      }
      title={
        canNavigate ? `View the full work of ${meta.label} in the ${meta.panelLabel} tab` : undefined
      }
    >
      <div className="flex items-baseline justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-base">{meta.icon}</span>
          <span className={`text-sm font-bold ${meta.color}`}>{meta.label}</span>
          <span className="text-xs text-zinc-500 font-mono">.{call.tool}</span>
          {canNavigate && (
            <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30">
              go to {meta.panelLabel}
              <ArrowRight className="w-3 h-3" />
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setShowDetails(!showDetails);
          }}
          className="text-xs text-zinc-500 hover:text-zinc-300"
        >
          {showDetails ? "hide" : "view inputs/outputs"}
        </button>
      </div>

      {/* Human summary of the response */}
      {call.respuesta_resumen && (
        <p className="mt-1.5 text-sm text-zinc-200">
          <span className="text-zinc-500">→ </span>
          {call.respuesta_resumen}
        </p>
      )}

      {/* Expandable details */}
      {showDetails && (
        <div className="mt-3 space-y-2">
          <div>
            <p className="text-[10px] uppercase tracking-wide text-zinc-500 mb-1">
              Expert inputs
            </p>
            <pre className="text-xs text-zinc-400 bg-zinc-950 border border-zinc-800 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
              {JSON.stringify(call.inputs, null, 2)}
            </pre>
          </div>
          {call.respuesta_completa && (
            <div>
              <p className="text-[10px] uppercase tracking-wide text-zinc-500 mb-1">
                Specialist response (truncated)
              </p>
              <pre className="text-xs text-zinc-400 bg-zinc-950 border border-zinc-800 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all max-h-72 overflow-y-auto">
                {JSON.stringify(call.respuesta_completa, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

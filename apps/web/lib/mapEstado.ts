import type { EstadoAnalisis } from "@veridict/types";
import type { AgentState } from "@/components/processing";

const AGENTS = ["extractor", "reconstructor", "legal", "adversarial"] as const;

const STAGES: Array<{ end: number; label: string }> = [
  { end: 30, label: "extractor" },
  { end: 65, label: "reconstructor" },
  { end: 90, label: "legal" },
  { end: 100, label: "adversarial" },
];

export function mapEstadoToAgents(estado: EstadoAnalisis): AgentState[] {
  const progreso = estado.progreso ?? 0;
  const etapa = estado.etapa_actual ?? "";

  const activeIdx = (() => {
    if (estado.estado === "completado") return AGENTS.length;
    for (let i = 0; i < STAGES.length; i++) {
      if (progreso < STAGES[i].end) return i;
    }
    return AGENTS.length - 1;
  })();

  return AGENTS.map((agent, i) => {
    if (i < activeIdx) {
      return { agent, status: "done", completedMessage: "Completado" };
    }
    if (i === activeIdx) {
      const start = i === 0 ? 0 : STAGES[i - 1].end;
      const span = STAGES[i].end - start;
      const local = Math.max(0, Math.min(100, ((progreso - start) / span) * 100));
      return {
        agent,
        status: "thinking",
        progress: Math.round(local),
        message: etapa || "Procesando...",
      };
    }
    return { agent, status: "idle" };
  });
}

export function isTerminal(estado: EstadoAnalisis): "completado" | "error" | null {
  if (estado.estado === "completado") return "completado";
  if (estado.estado === "error" || estado.estado === "escalado_humano") return "error";
  return null;
}

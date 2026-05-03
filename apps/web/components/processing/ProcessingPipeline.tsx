"use client";

import { motion } from "framer-motion";
import AgentCard, { AgentCardCompact } from "./AgentCard";
import { AgentType, AgentStatus } from "./AgentIcon";
import { CircularProgress } from "./ThinkingAnimation";
import { ArrowRight, CheckCircle2 } from "lucide-react";

export interface AgentState {
  agent: AgentType;
  status: AgentStatus;
  progress?: number;
  message?: string;
  completedMessage?: string;
}

interface ProcessingPipelineProps {
  agents: AgentState[];
  overallProgress?: number;
  variant?: "vertical" | "horizontal";
  showConnectors?: boolean;
}

const agentOrder: AgentType[] = [
  "extractor",
  "reconstructor",
  "legal",
  "adversarial",
];

export default function ProcessingPipeline({
  agents,
  overallProgress = 0,
  variant = "vertical",
  showConnectors = true,
}: ProcessingPipelineProps) {
  // Ordenar agentes según el orden del pipeline
  const orderedAgents = agentOrder.map((agentType) => {
    const found = agents.find((a) => a.agent === agentType);
    return (
      found || {
        agent: agentType,
        status: "idle" as AgentStatus,
      }
    );
  });

  const allDone = orderedAgents.every((a) => a.status === "done");

  if (variant === "horizontal") {
    return (
      <div className="w-full">
        {/* Barra de progreso global */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-veridict-gray">
              Processing analysis...
            </span>
            <span className="text-sm font-mono text-veridict-lime">
              {Math.round(overallProgress)}%
            </span>
          </div>
          <div className="h-2 bg-veridict-green-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-veridict-lime/80 to-veridict-lime rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${overallProgress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Pipeline horizontal */}
        <div className="flex items-center justify-between gap-2">
          {orderedAgents.map((agentState, index) => (
            <div key={agentState.agent} className="flex items-center flex-1">
              <AgentCardCompact
                agent={agentState.agent}
                status={agentState.status}
                progress={agentState.progress}
              />
              {/* Conector */}
              {showConnectors && index < orderedAgents.length - 1 && (
                <div className="flex-1 flex items-center justify-center px-2">
                  <motion.div
                    className={`
                      h-0.5 flex-1 rounded-full transition-colors duration-300
                      ${
                        agentState.status === "done"
                          ? "bg-veridict-lime/60"
                          : "bg-veridict-green-700"
                      }
                    `}
                  />
                  <ArrowRight
                    size={14}
                    className={`
                      mx-1 transition-colors duration-300
                      ${
                        agentState.status === "done"
                          ? "text-veridict-lime/60"
                          : "text-veridict-green-600"
                      }
                    `}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Variante vertical (por defecto)
  return (
    <div className="w-full max-w-md mx-auto">
      {/* Header con progreso circular */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-medium text-veridict-white">
            {allDone ? "Analysis Completed" : "Analyzing Case"}
          </h2>
          <p className="text-sm text-veridict-gray">
            {allDone
              ? "All agents have finished"
              : "AI agents are processing..."}
          </p>
        </div>
        {!allDone && (
          <CircularProgress progress={overallProgress} size={56} strokeWidth={4} />
        )}
        {allDone && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            <CheckCircle2 size={48} className="text-veridict-lime" />
          </motion.div>
        )}
      </div>

      {/* Cards de agentes */}
      <div className="space-y-3">
        {orderedAgents.map((agentState, index) => (
          <div key={agentState.agent} className="relative">
            {/* Línea conectora vertical */}
            {showConnectors && index < orderedAgents.length - 1 && (
              <div
                className={`
                  absolute left-[28px] top-[60px] w-0.5 h-[20px]
                  transition-colors duration-300
                  ${
                    agentState.status === "done"
                      ? "bg-veridict-lime/40"
                      : "bg-veridict-green-700"
                  }
                `}
              />
            )}

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
            >
              <AgentCard
                agent={agentState.agent}
                status={agentState.status}
                progress={agentState.progress}
                message={agentState.message}
                completedMessage={agentState.completedMessage}
              />
            </motion.div>
          </div>
        ))}
      </div>

      {/* Mensaje de completado */}
      {allDone && (
        <motion.div
          className="mt-6 p-4 bg-veridict-lime/10 border border-veridict-lime/30 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-sm text-veridict-lime text-center">
            The expert report is ready for review
          </p>
        </motion.div>
      )}
    </div>
  );
}

// Hook para simular el progreso del pipeline (para demos)
export function useProcessingSimulation() {
  // Este hook puede usarse para simular el progreso
  // en desarrollo o demos
  return {
    startSimulation: () => {},
    resetSimulation: () => {},
  };
}

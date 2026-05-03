"use client";

import { motion, AnimatePresence } from "framer-motion";
import AgentIcon, { AgentType, AgentStatus, agentConfig } from "./AgentIcon";
import ThinkingAnimation, { CircularProgress } from "./ThinkingAnimation";

interface AgentCardProps {
  agent: AgentType;
  status: AgentStatus;
  progress?: number; // 0-100, solo para status "thinking"
  message?: string;
  completedMessage?: string;
}

const statusMessages: Record<AgentType, Record<AgentStatus, string>> = {
  extractor: {
    idle: "Waiting for documents...",
    thinking: "Extracting data from report...",
    done: "Extraction completed",
  },
  reconstructor: {
    idle: "Waiting for extracted data...",
    thinking: "Calculating impact physics...",
    done: "Reconstruction completed",
  },
  legal: {
    idle: "Waiting for physical analysis...",
    thinking: "Analyzing applicable regulations...",
    done: "Legal analysis completed",
  },
  adversarial: {
    idle: "Waiting for preliminary report...",
    thinking: "Verifying consistency...",
    done: "Verification completed",
  },
};

const agentTitles: Record<AgentType, string> = {
  extractor: "Extractor Agent",
  reconstructor: "Reconstructor Agent",
  legal: "Legal Agent",
  adversarial: "Devil's Advocate",
};

export default function AgentCard({
  agent,
  status,
  progress = 0,
  message,
  completedMessage,
}: AgentCardProps) {
  const displayMessage =
    message || statusMessages[agent][status] || "";
  const finalMessage =
    status === "done" && completedMessage
      ? completedMessage
      : displayMessage;

  return (
    <motion.div
      className={`
        relative overflow-hidden rounded-lg border-2 p-4
        transition-colors duration-300
        ${
          status === "idle"
            ? "bg-veridict-green-800/50 border-veridict-green-700"
            : status === "thinking"
            ? "bg-veridict-green-800 border-veridict-lime/40"
            : "bg-veridict-green-800 border-veridict-lime/60"
        }
      `}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Efecto de brillo de fondo cuando está pensando */}
      <AnimatePresence>
        {status === "thinking" && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-veridict-lime/5 to-transparent"
            initial={{ x: "-100%" }}
            animate={{ x: "200%" }}
            exit={{ opacity: 0 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        )}
      </AnimatePresence>

      <div className="relative flex items-start gap-4">
        {/* Icono del agente */}
        <div className="flex-shrink-0">
          <AgentIcon agent={agent} status={status} size={20} />
        </div>

        {/* Contenido */}
        <div className="flex-1 min-w-0">
          {/* Título del agente */}
          <h3
            className={`
            text-sm font-medium mb-1 transition-colors duration-300
            ${
              status === "idle"
                ? "text-veridict-gray"
                : "text-veridict-white"
            }
          `}
          >
            {agentTitles[agent]}
          </h3>

          {/* Mensaje de estado */}
          <AnimatePresence mode="wait">
            <motion.p
              key={`${agent}-${status}-${finalMessage}`}
              className={`
                text-xs transition-colors duration-300
                ${
                  status === "idle"
                    ? "text-veridict-gray/60"
                    : status === "thinking"
                    ? "text-veridict-lime/80"
                    : "text-veridict-lime"
                }
              `}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
            >
              {finalMessage}
            </motion.p>
          </AnimatePresence>

          {/* Barra de progreso (solo cuando está pensando) */}
          <AnimatePresence>
            {status === "thinking" && progress > 0 && (
              <motion.div
                className="mt-3"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="h-1 bg-veridict-green-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-veridict-lime rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  />
                </div>
                <p className="text-xs text-veridict-gray/60 mt-1 text-right font-mono">
                  {Math.round(progress)}%
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Indicador de estado (esquina superior derecha) */}
        <div className="flex-shrink-0">
          {status === "thinking" && (
            <ThinkingAnimation size="sm" color="lime" />
          )}
          {status === "done" && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                className="text-veridict-lime"
              >
                <motion.path
                  d="M3 8L6.5 11.5L13 5"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                />
              </svg>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// Versión compacta para el pipeline horizontal
export function AgentCardCompact({
  agent,
  status,
  progress,
}: {
  agent: AgentType;
  status: AgentStatus;
  progress?: number;
}) {
  return (
    <motion.div
      className={`
        relative flex flex-col items-center gap-2 p-3 rounded-lg
        transition-all duration-300
        ${
          status === "idle"
            ? "opacity-50"
            : status === "thinking"
            ? "opacity-100"
            : "opacity-100"
        }
      `}
      whileHover={{ scale: status !== "idle" ? 1.02 : 1 }}
    >
      {/* Icono */}
      <AgentIcon agent={agent} status={status} size={16} />

      {/* Nombre */}
      <span
        className={`
        text-xs font-medium text-center
        ${
          status === "idle"
            ? "text-veridict-gray/60"
            : "text-veridict-white"
        }
      `}
      >
        {agentTitles[agent].split(" ")[1] || agentTitles[agent]}
      </span>

      {/* Mini progreso */}
      {status === "thinking" && progress !== undefined && (
        <div className="w-full h-0.5 bg-veridict-green-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-veridict-lime"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      )}
    </motion.div>
  );
}

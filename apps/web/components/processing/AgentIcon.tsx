"use client";

import { motion } from "framer-motion";
import {
  FileSearch,
  Calculator,
  Scale,
  ShieldAlert,
  CheckCircle2,
  Circle,
} from "lucide-react";

export type AgentType =
  | "extractor"
  | "reconstructor"
  | "legal"
  | "adversarial";

export type AgentStatus = "idle" | "thinking" | "done";

interface AgentIconProps {
  agent: AgentType;
  status: AgentStatus;
  size?: number;
}

const agentConfig: Record<
  AgentType,
  {
    icon: typeof FileSearch;
    label: string;
    thinkingColor: string;
    doneColor: string;
  }
> = {
  extractor: {
    icon: FileSearch,
    label: "Extractor",
    thinkingColor: "text-veridict-lime",
    doneColor: "text-veridict-lime",
  },
  reconstructor: {
    icon: Calculator,
    label: "Reconstructor",
    thinkingColor: "text-veridict-lime",
    doneColor: "text-veridict-lime",
  },
  legal: {
    icon: Scale,
    label: "Legal",
    thinkingColor: "text-veridict-lime",
    doneColor: "text-veridict-lime",
  },
  adversarial: {
    icon: ShieldAlert,
    label: "Devil's Advocate",
    thinkingColor: "text-veridict-lime",
    doneColor: "text-veridict-lime",
  },
};

export default function AgentIcon({
  agent,
  status,
  size = 24,
}: AgentIconProps) {
  const config = agentConfig[agent];
  const Icon = config.icon;

  // Estado idle - círculo vacío con icono gris
  if (status === "idle") {
    return (
      <div
        className="relative flex items-center justify-center"
        style={{ width: size * 2, height: size * 2 }}
      >
        <div className="absolute inset-0 rounded-full border-2 border-veridict-green-600" />
        <Icon
          size={size}
          className="text-veridict-gray/50"
          strokeWidth={1.5}
        />
      </div>
    );
  }

  // Estado thinking - animación de pulso
  if (status === "thinking") {
    return (
      <div
        className="relative flex items-center justify-center"
        style={{ width: size * 2, height: size * 2 }}
      >
        {/* Anillos de pulso */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-veridict-lime/60"
          animate={{
            scale: [1, 1.3],
            opacity: [0.6, 0],
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeOut",
          }}
        />
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-veridict-lime/60"
          animate={{
            scale: [1, 1.3],
            opacity: [0.6, 0],
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeOut",
            delay: 0.4,
          }}
        />

        {/* Círculo base pulsante */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-veridict-lime bg-veridict-lime/10"
          animate={{
            borderColor: [
              "rgba(194, 233, 75, 0.6)",
              "rgba(194, 233, 75, 1)",
              "rgba(194, 233, 75, 0.6)",
            ],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* Icono con brillo */}
        <motion.div
          animate={{
            filter: [
              "brightness(1)",
              "brightness(1.4)",
              "brightness(1)",
            ],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <Icon
            size={size}
            className={config.thinkingColor}
            strokeWidth={2}
          />
        </motion.div>
      </div>
    );
  }

  // Estado done - check verde con animación de entrada
  if (status === "done") {
    return (
      <div
        className="relative flex items-center justify-center"
        style={{ width: size * 2, height: size * 2 }}
      >
        {/* Círculo base */}
        <motion.div
          className="absolute inset-0 rounded-full bg-veridict-lime/20 border-2 border-veridict-lime"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />

        {/* Check animado */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            duration: 0.3,
            delay: 0.1,
            type: "spring",
            stiffness: 200,
          }}
        >
          <CheckCircle2
            size={size}
            className="text-veridict-lime"
            strokeWidth={2}
          />
        </motion.div>
      </div>
    );
  }

  return null;
}

// Exportar configuración para uso externo
export { agentConfig };

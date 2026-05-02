"use client";

import { motion } from "framer-motion";

interface ThinkingAnimationProps {
  size?: "sm" | "md" | "lg";
  color?: "lime" | "white" | "gray";
}

const sizeMap = {
  sm: { dot: 6, gap: 4 },
  md: { dot: 8, gap: 6 },
  lg: { dot: 10, gap: 8 },
};

const colorMap = {
  lime: "bg-veridict-lime",
  white: "bg-veridict-white",
  gray: "bg-veridict-gray",
};

export default function ThinkingAnimation({
  size = "md",
  color = "lime",
}: ThinkingAnimationProps) {
  const { dot, gap } = sizeMap[size];
  const dotColor = colorMap[color];

  const containerVariants = {
    animate: {
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const dotVariants = {
    initial: { scale: 0.6, opacity: 0.4 },
    animate: {
      scale: [0.6, 1, 0.6],
      opacity: [0.4, 1, 0.4],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  return (
    <motion.div
      className="flex items-center justify-center"
      style={{ gap: `${gap}px` }}
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      {[0, 1, 2].map((index) => (
        <motion.span
          key={index}
          className={`rounded-full ${dotColor}`}
          style={{ width: dot, height: dot }}
          variants={dotVariants}
          custom={index}
        />
      ))}
    </motion.div>
  );
}

// Variante de onda/pulso para usar en AgentCard
export function PulseRing({
  size = 40,
  color = "lime",
}: {
  size?: number;
  color?: "lime" | "white";
}) {
  const ringColor =
    color === "lime"
      ? "border-veridict-lime"
      : "border-veridict-white/50";

  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* Anillos de pulso */}
      <motion.div
        className={`absolute inset-0 rounded-full border-2 ${ringColor}`}
        initial={{ scale: 0.8, opacity: 1 }}
        animate={{
          scale: [0.8, 1.4],
          opacity: [0.8, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeOut",
        }}
      />
      <motion.div
        className={`absolute inset-0 rounded-full border-2 ${ringColor}`}
        initial={{ scale: 0.8, opacity: 1 }}
        animate={{
          scale: [0.8, 1.4],
          opacity: [0.8, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeOut",
          delay: 0.5,
        }}
      />
      {/* Centro pulsante */}
      <motion.div
        className={`absolute inset-2 rounded-full ${
          color === "lime" ? "bg-veridict-lime/30" : "bg-veridict-white/20"
        }`}
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.5, 0.8, 0.5],
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
}

// Animación de progreso circular
export function CircularProgress({
  progress,
  size = 48,
  strokeWidth = 3,
}: {
  progress: number;
  size?: number;
  strokeWidth?: number;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* Track */}
      <svg
        className="absolute inset-0 -rotate-90"
        width={size}
        height={size}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-veridict-green-700"
        />
        {/* Progreso */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          className="text-veridict-lime"
          style={{
            strokeDasharray: circumference,
          }}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </svg>
      {/* Porcentaje */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-mono text-veridict-lime">
          {Math.round(progress)}%
        </span>
      </div>
    </div>
  );
}

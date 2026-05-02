"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion, useAnimationControls } from "framer-motion";

type Phase = "approach" | "impact" | "chaos" | "reconstruct" | "forensic";

const LIME = "#C2E94B";
const CYAN = "#60efff";
const RED = "#dc2626";
const BLUE = "#2563eb";

const VBW = 1000;
const VBH = 500;
const CX = 500;
const CY = 250;
const CAR_A_X = 460;
const CAR_B_X = 540;

const DEBRIS = (() => {
  const arr: {
    id: number;
    x: number;
    y: number;
    size: number;
    type: number;
    rot: number;
    delay: number;
  }[] = [];
  for (let i = 0; i < 34; i++) {
    const angle = (i / 34) * Math.PI * 2 + Math.sin(i * 13.7) * 0.6;
    const distance = 90 + ((i * 41) % 110) + Math.abs(Math.cos(i * 7.3)) * 50;
    arr.push({
      id: i,
      x: Math.cos(angle) * distance,
      y: Math.sin(angle) * distance * 0.55,
      size: 2 + (i % 4),
      type: i % 3,
      rot: (i * 47) % 360,
      delay: (i % 6) * 0.012,
    });
  }
  return arr;
})();

const PHASE_LABEL: Record<Phase, string> = {
  approach: "// MONITORIZANDO TRAYECTORIA",
  impact: "// IMPACTO DETECTADO",
  chaos: "// ANÁLISIS DE COLISIÓN",
  reconstruct: "// RECONSTRUYENDO SECUENCIA",
  forensic: "// DICTAMEN FORENSE",
};

export default function CrashReconstruction({
  className = "",
}: {
  className?: string;
}) {
  const [phase, setPhase] = useState<Phase>("approach");
  const carA = useAnimationControls();
  const carB = useAnimationControls();
  const sceneCtl = useAnimationControls();

  useEffect(() => {
    let cancelled = false;
    const wait = (ms: number) =>
      new Promise<void>((resolve) => setTimeout(resolve, ms));

    async function loop() {
      while (!cancelled) {
        // Reset cars off-screen
        carA.set({ x: -650, y: 0, rotate: 0, scaleX: 1 });
        carB.set({ x: 650, y: 0, rotate: 0, scaleX: 1 });
        sceneCtl.set({ x: 0, y: 0 });
        setPhase("approach");

        // Approach
        await Promise.all([
          carA.start({
            x: 0,
            transition: { duration: 2.4, ease: [0.4, 0, 0.7, 1] },
          }),
          carB.start({
            x: 0,
            transition: { duration: 2.4, ease: [0.4, 0, 0.7, 1] },
          }),
        ]);
        if (cancelled) return;

        // Impact
        setPhase("impact");
        sceneCtl.start({
          x: [0, -10, 8, -6, 4, 0],
          y: [0, 4, -3, 5, -2, 0],
          transition: { duration: 0.45 },
        });
        await Promise.all([
          carA.start({ scaleX: 0.92, transition: { duration: 0.1 } }),
          carB.start({ scaleX: 0.92, transition: { duration: 0.1 } }),
        ]);
        await wait(180);
        if (cancelled) return;

        // Chaos
        setPhase("chaos");
        await Promise.all([
          carA.start({
            x: -28,
            y: -10,
            rotate: -9,
            scaleX: 1,
            transition: { duration: 0.4, ease: "easeOut" },
          }),
          carB.start({
            x: 28,
            y: 8,
            rotate: 8,
            scaleX: 1,
            transition: { duration: 0.4, ease: "easeOut" },
          }),
        ]);
        await wait(950);
        if (cancelled) return;

        // Reconstruct
        setPhase("reconstruct");
        await Promise.all([
          carA.start({
            x: 0,
            y: 0,
            rotate: 0,
            transition: { duration: 1.9, ease: [0.2, 0, 0.2, 1] },
          }),
          carB.start({
            x: 0,
            y: 0,
            rotate: 0,
            transition: { duration: 1.9, ease: [0.2, 0, 0.2, 1] },
          }),
        ]);
        if (cancelled) return;

        // Forensic
        setPhase("forensic");
        await wait(2400);
      }
    }
    loop();
    return () => {
      cancelled = true;
    };
  }, [carA, carB, sceneCtl]);

  return (
    <div className={`relative w-full ${className}`}>
      <svg
        viewBox={`0 0 ${VBW} ${VBH}`}
        className="w-full h-full block"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <filter id="limeGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" />
          </filter>
          <radialGradient id="headlightGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#fffae0" stopOpacity="0.95" />
            <stop offset="60%" stopColor="#fff7c2" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#fffae0" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="flashGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
            <stop offset="35%" stopColor="#fff7c2" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#ffae00" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="impactBgGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={LIME} stopOpacity="0.18" />
            <stop offset="100%" stopColor={LIME} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Forensic grid background */}
        <g opacity="0.07">
          {Array.from({ length: 21 }).map((_, i) => (
            <line
              key={`v${i}`}
              x1={i * 50}
              y1={0}
              x2={i * 50}
              y2={VBH}
              stroke={LIME}
              strokeWidth="0.5"
            />
          ))}
          {Array.from({ length: 11 }).map((_, i) => (
            <line
              key={`h${i}`}
              x1={0}
              y1={i * 50}
              x2={VBW}
              y2={i * 50}
              stroke={LIME}
              strokeWidth="0.5"
            />
          ))}
        </g>

        {/* Camera viewfinder corners */}
        <g stroke={LIME} strokeWidth="1.5" fill="none" opacity="0.45">
          <path d="M 24 24 L 24 56 M 24 24 L 56 24" />
          <path d={`M ${VBW - 24} 24 L ${VBW - 24} 56 M ${VBW - 24} 24 L ${VBW - 56} 24`} />
          <path d={`M 24 ${VBH - 24} L 24 ${VBH - 56} M 24 ${VBH - 24} L 56 ${VBH - 24}`} />
          <path
            d={`M ${VBW - 24} ${VBH - 24} L ${VBW - 24} ${VBH - 56} M ${VBW - 24} ${VBH - 24} L ${VBW - 56} ${VBH - 24}`}
          />
        </g>

        {/* HUD: top-left phase label */}
        <g transform="translate(40, 56)">
          <AnimatePresence mode="wait">
            <motion.text
              key={phase}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 0.8, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              transition={{ duration: 0.25 }}
              fill={LIME}
              fontFamily="ui-monospace, JetBrains Mono, monospace"
              fontSize="11"
              letterSpacing="0.15em"
            >
              {PHASE_LABEL[phase]}
            </motion.text>
          </AnimatePresence>
        </g>

        {/* HUD: top-right timestamp */}
        <g transform={`translate(${VBW - 40}, 56)`} textAnchor="end">
          <text
            fill={LIME}
            fontFamily="ui-monospace, monospace"
            fontSize="10"
            opacity="0.6"
            letterSpacing="0.1em"
          >
            VERIDICT.AI · CASE #2024-0317
          </text>
        </g>

        {/* Scene group (shaken on impact) */}
        <motion.g animate={sceneCtl}>
          {/* Soft impact halo (during chaos / reconstruct) */}
          <AnimatePresence>
            {(phase === "chaos" || phase === "reconstruct") && (
              <motion.circle
                cx={CX}
                cy={CY}
                r={180}
                fill="url(#impactBgGrad)"
                initial={{ opacity: 0, scale: 0.4 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                style={{ originX: "50%", originY: "50%" }}
              />
            )}
          </AnimatePresence>

          {/* Reconstruction scan rings */}
          <AnimatePresence>
            {phase === "reconstruct" && (
              <g>
                {[0, 0.45, 0.9].map((delay, i) => (
                  <motion.circle
                    key={`ring-${i}`}
                    cx={CX}
                    cy={CY}
                    fill="none"
                    stroke={LIME}
                    strokeWidth="2"
                    initial={{ r: 240, opacity: 0 }}
                    animate={{ r: [240, 30, 240], opacity: [0, 0.9, 0] }}
                    exit={{ opacity: 0 }}
                    transition={{
                      duration: 1.6,
                      delay,
                      repeat: Infinity,
                      ease: "easeOut",
                    }}
                    filter="url(#limeGlow)"
                  />
                ))}
                {/* Vertical scan line */}
                <motion.rect
                  y={0}
                  width="2.5"
                  height={VBH}
                  fill={LIME}
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: VBW + 10, opacity: [0, 0.7, 0] }}
                  exit={{ opacity: 0 }}
                  transition={{
                    duration: 1.4,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                  filter="url(#limeGlow)"
                />
              </g>
            )}
          </AnimatePresence>

          {/* Forensic overlay */}
          <AnimatePresence>
            {phase === "forensic" && (
              <g>
                {/* Trajectory dashed lines */}
                <motion.line
                  x1={-40}
                  y1={CY}
                  x2={CAR_A_X}
                  y2={CY}
                  stroke={LIME}
                  strokeWidth="2"
                  strokeDasharray="6 5"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 0.85 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.9, ease: "easeInOut" }}
                />
                <motion.line
                  x1={VBW + 40}
                  y1={CY}
                  x2={CAR_B_X}
                  y2={CY}
                  stroke={CYAN}
                  strokeWidth="2"
                  strokeDasharray="6 5"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 0.85 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.9, delay: 0.1, ease: "easeInOut" }}
                />

                {/* Impact crosshair */}
                <motion.g
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.4, delay: 0.7 }}
                  style={{ originX: "50%", originY: "50%" }}
                >
                  <circle
                    cx={CX}
                    cy={CY}
                    r="10"
                    fill="none"
                    stroke={LIME}
                    strokeWidth="2"
                  />
                  <circle cx={CX} cy={CY} r="3" fill={LIME} />
                  <line
                    x1={CX - 18}
                    y1={CY}
                    x2={CX - 12}
                    y2={CY}
                    stroke={LIME}
                    strokeWidth="2"
                  />
                  <line
                    x1={CX + 12}
                    y1={CY}
                    x2={CX + 18}
                    y2={CY}
                    stroke={LIME}
                    strokeWidth="2"
                  />
                  <line
                    x1={CX}
                    y1={CY - 18}
                    x2={CX}
                    y2={CY - 12}
                    stroke={LIME}
                    strokeWidth="2"
                  />
                  <line
                    x1={CX}
                    y1={CY + 12}
                    x2={CX}
                    y2={CY + 18}
                    stroke={LIME}
                    strokeWidth="2"
                  />
                </motion.g>

                {/* Velocity card vehicle A */}
                <motion.g
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 1.0, duration: 0.4 }}
                >
                  <rect
                    x="100"
                    y={CY - 110}
                    width="160"
                    height="48"
                    rx="4"
                    fill="rgba(31,51,41,0.9)"
                    stroke={LIME}
                    strokeOpacity="0.5"
                  />
                  <line
                    x1="100"
                    y1={CY - 110}
                    x2="100"
                    y2={CY - 62}
                    stroke={LIME}
                    strokeWidth="3"
                  />
                  <text
                    x="115"
                    y={CY - 90}
                    fill={LIME}
                    fontFamily="ui-monospace, monospace"
                    fontSize="10"
                    letterSpacing="0.12em"
                  >
                    VEHÍCULO A · CRASH3
                  </text>
                  <text
                    x="115"
                    y={CY - 72}
                    fill="#F5F5F0"
                    fontFamily="ui-monospace, monospace"
                    fontSize="15"
                    fontWeight="600"
                  >
                    v₁ = 84 km/h
                  </text>
                  {/* connector line to car */}
                  <line
                    x1="180"
                    y1={CY - 62}
                    x2={CAR_A_X - 30}
                    y2={CY - 22}
                    stroke={LIME}
                    strokeOpacity="0.4"
                    strokeWidth="1"
                    strokeDasharray="2 3"
                  />
                </motion.g>

                {/* Velocity card vehicle B */}
                <motion.g
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 1.15, duration: 0.4 }}
                >
                  <rect
                    x={VBW - 260}
                    y={CY + 62}
                    width="160"
                    height="48"
                    rx="4"
                    fill="rgba(31,51,41,0.9)"
                    stroke={CYAN}
                    strokeOpacity="0.5"
                  />
                  <line
                    x1={VBW - 100}
                    y1={CY + 62}
                    x2={VBW - 100}
                    y2={CY + 110}
                    stroke={CYAN}
                    strokeWidth="3"
                  />
                  <text
                    x={VBW - 245}
                    y={CY + 82}
                    fill={CYAN}
                    fontFamily="ui-monospace, monospace"
                    fontSize="10"
                    letterSpacing="0.12em"
                  >
                    VEHÍCULO B · CRASH3
                  </text>
                  <text
                    x={VBW - 245}
                    y={CY + 100}
                    fill="#F5F5F0"
                    fontFamily="ui-monospace, monospace"
                    fontSize="15"
                    fontWeight="600"
                  >
                    v₂ = 71 km/h
                  </text>
                  <line
                    x1={VBW - 180}
                    y1={CY + 62}
                    x2={CAR_B_X + 30}
                    y2={CY + 22}
                    stroke={CYAN}
                    strokeOpacity="0.4"
                    strokeWidth="1"
                    strokeDasharray="2 3"
                  />
                </motion.g>

                {/* Center "Análisis completado" badge */}
                <motion.g
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: 1.4, duration: 0.45 }}
                >
                  <rect
                    x={CX - 105}
                    y={VBH - 80}
                    width="210"
                    height="34"
                    rx="17"
                    fill="rgba(31,51,41,0.92)"
                    stroke={LIME}
                    strokeOpacity="0.7"
                  />
                  <circle cx={CX - 80} cy={VBH - 63} r="4" fill={LIME}>
                    <animate
                      attributeName="opacity"
                      values="1;0.3;1"
                      dur="1.4s"
                      repeatCount="indefinite"
                    />
                  </circle>
                  <text
                    x={CX - 65}
                    y={VBH - 58}
                    fill={LIME}
                    fontFamily="ui-monospace, monospace"
                    fontSize="11"
                    letterSpacing="0.18em"
                    fontWeight="600"
                  >
                    DICTAMEN · UNE-EN 16775
                  </text>
                </motion.g>
              </g>
            )}
          </AnimatePresence>

          {/* Car A — red, drives right */}
          <g transform={`translate(${CAR_A_X}, ${CY})`}>
            <motion.g
              animate={carA}
              initial={{ x: -650 }}
              style={{ originX: "50%", originY: "50%" }}
            >
              {/* Headlight cone */}
              <AnimatePresence>
                {(phase === "approach" || phase === "impact") && (
                  <motion.ellipse
                    cx="78"
                    cy="0"
                    rx="58"
                    ry="22"
                    fill="url(#headlightGrad)"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.55 }}
                    exit={{ opacity: 0, transition: { duration: 0.25 } }}
                  />
                )}
              </AnimatePresence>
              {/* Speed lines */}
              <AnimatePresence>
                {phase === "approach" && (
                  <motion.g
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.65 }}
                    exit={{ opacity: 0 }}
                  >
                    <rect x="-78" y="-15" width="22" height="2.5" fill={RED} opacity="0.55" />
                    <rect x="-108" y="-15" width="14" height="2.5" fill={RED} opacity="0.3" />
                    <rect x="-78" y="12.5" width="22" height="2.5" fill={RED} opacity="0.55" />
                    <rect x="-108" y="12.5" width="14" height="2.5" fill={RED} opacity="0.3" />
                  </motion.g>
                )}
              </AnimatePresence>
              <CarBody color={RED} damage={phase === "chaos" ? "front" : "none"} />
            </motion.g>
          </g>

          {/* Car B — blue, drives left (mirrored) */}
          <g transform={`translate(${CAR_B_X}, ${CY})`}>
            <motion.g
              animate={carB}
              initial={{ x: 650 }}
              style={{ originX: "50%", originY: "50%" }}
            >
              <AnimatePresence>
                {(phase === "approach" || phase === "impact") && (
                  <motion.ellipse
                    cx="-78"
                    cy="0"
                    rx="58"
                    ry="22"
                    fill="url(#headlightGrad)"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.55 }}
                    exit={{ opacity: 0, transition: { duration: 0.25 } }}
                  />
                )}
              </AnimatePresence>
              <AnimatePresence>
                {phase === "approach" && (
                  <motion.g
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.65 }}
                    exit={{ opacity: 0 }}
                  >
                    <rect x="56" y="-15" width="22" height="2.5" fill={BLUE} opacity="0.55" />
                    <rect x="94" y="-15" width="14" height="2.5" fill={BLUE} opacity="0.3" />
                    <rect x="56" y="12.5" width="22" height="2.5" fill={BLUE} opacity="0.55" />
                    <rect x="94" y="12.5" width="14" height="2.5" fill={BLUE} opacity="0.3" />
                  </motion.g>
                )}
              </AnimatePresence>
              <CarBody color={BLUE} mirrored damage={phase === "chaos" ? "front" : "none"} />
            </motion.g>
          </g>

          {/* Impact flash */}
          <AnimatePresence>
            {phase === "impact" && (
              <motion.circle
                cx={CX}
                cy={CY}
                r={140}
                fill="url(#flashGrad)"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: [0, 1, 0], scale: [0, 1.3, 1.8] }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                style={{ originX: "50%", originY: "50%" }}
              />
            )}
          </AnimatePresence>

          {/* Debris field — scales out from center on impact, sucked back during reconstruct */}
          <g transform={`translate(${CX}, ${CY})`}>
            {DEBRIS.map((d) => (
              <DebrisPiece key={d.id} d={d} phase={phase} />
            ))}
          </g>
        </motion.g>
      </svg>
    </div>
  );
}

function CarBody({
  color,
  mirrored = false,
  damage = "none",
}: {
  color: string;
  mirrored?: boolean;
  damage?: "none" | "front";
}) {
  return (
    <g transform={mirrored ? "scale(-1, 1)" : ""}>
      {/* shadow */}
      <ellipse cx="0" cy="24" rx="44" ry="6" fill="#000" opacity="0.32" />
      {/* body */}
      <rect x="-40" y="-18" width="80" height="36" rx="6" fill={color} />
      {/* subtle gloss */}
      <rect x="-40" y="-18" width="80" height="6" rx="6" fill="#fff" opacity="0.12" />
      {/* damage on front (right side after mirror correction) */}
      {damage === "front" && (
        <g>
          <path
            d="M 36 -16 L 32 -10 L 38 -4 L 30 2 L 36 8 L 30 14"
            stroke="#1a0a0a"
            strokeWidth="2"
            fill="none"
            opacity="0.5"
          />
          <path
            d="M 38 -14 Q 30 -8 34 -2 Q 28 4 32 10 Q 26 14 30 16"
            stroke={color}
            strokeWidth="3"
            fill="none"
            opacity="0.8"
          />
        </g>
      )}
      {/* roof */}
      <rect x="-15" y="-14" width="30" height="28" rx="3" fill="#161616" opacity="0.88" />
      {/* windshield (front edge) */}
      <rect x="13" y="-12" width="3.5" height="24" rx="1" fill={CYAN} opacity="0.55" />
      {/* rear window */}
      <rect x="-16.5" y="-12" width="2.5" height="24" rx="1" fill={CYAN} opacity="0.32" />
      {/* center seam */}
      <line
        x1="-40"
        y1="0"
        x2="40"
        y2="0"
        stroke="#000"
        strokeOpacity="0.18"
        strokeWidth="0.5"
      />
      {/* wheels */}
      <rect x="-30" y="-22" width="14" height="6" rx="1.5" fill="#0a0a0a" />
      <rect x="-30" y="16" width="14" height="6" rx="1.5" fill="#0a0a0a" />
      <rect x="16" y="-22" width="14" height="6" rx="1.5" fill="#0a0a0a" />
      <rect x="16" y="16" width="14" height="6" rx="1.5" fill="#0a0a0a" />
      {/* headlights front */}
      <rect x="36" y="-12" width="3" height="5" rx="0.5" fill="#fff7c2" />
      <rect x="36" y="7" width="3" height="5" rx="0.5" fill="#fff7c2" />
      {/* taillights rear */}
      <rect x="-39" y="-12" width="2" height="5" rx="0.5" fill="#ff3030" />
      <rect x="-39" y="7" width="2" height="5" rx="0.5" fill="#ff3030" />
    </g>
  );
}

function DebrisPiece({
  d,
  phase,
}: {
  d: { x: number; y: number; size: number; type: number; rot: number; delay: number };
  phase: Phase;
}) {
  const isOut = phase === "impact" || phase === "chaos";
  const colors = ["#9aeaff", "#a3a99e", "#ffd166"]; // glass, metal, spark

  return (
    <motion.g
      initial={{ x: 0, y: 0, scale: 0, opacity: 0, rotate: 0 }}
      animate={{
        x: isOut ? d.x : 0,
        y: isOut ? d.y : 0,
        scale: isOut ? 1 : 0.05,
        opacity: isOut ? 1 : 0,
        rotate: isOut ? d.rot : 0,
      }}
      transition={{
        duration: isOut ? 0.45 : 1.5,
        delay: isOut ? d.delay : 0,
        ease: isOut ? [0.16, 0.84, 0.32, 1] : [0.6, 0, 0.4, 1],
      }}
    >
      {d.type === 0 && (
        <polygon
          points={`0,-${d.size} ${d.size},${d.size * 0.8} -${d.size * 0.7},${d.size}`}
          fill={colors[0]}
          opacity="0.9"
        />
      )}
      {d.type === 1 && (
        <rect
          x={-d.size}
          y={-d.size / 2}
          width={d.size * 2}
          height={d.size}
          fill={colors[1]}
          opacity="0.85"
        />
      )}
      {d.type === 2 && (
        <circle
          cx="0"
          cy="0"
          r={d.size * 0.7}
          fill={colors[2]}
          filter="url(#limeGlow)"
        />
      )}
    </motion.g>
  );
}

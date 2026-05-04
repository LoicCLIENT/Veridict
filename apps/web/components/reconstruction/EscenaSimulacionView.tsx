"use client";

/**
 * Multi-actor accident scene player driven by `EscenaSimulacionData` produced
 * by the backend SimulationAgent (LLM). Animates an arbitrary set of actors
 * (cars, bicycles, pedestrians, mobiliario) interpolating their trajectories
 * over a `currentTime` 0-100 scrubber. Replaces the hard-coded
 * `AccidentScene2D` for cases where the backend returns a real reconstruction.
 */

import { useCallback, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  ActorSimulacion,
  EscenaSimulacionData,
  ObstaculoEscena,
  TrayectoriaPunto,
} from "@veridict/types";

interface EscenaSimulacionViewProps {
  data: EscenaSimulacionData;
  currentTime: number; // 0-100
  showMeasurements?: boolean;
  showTrajectories?: boolean;
  showGrid?: boolean;
  showImpactZone?: boolean;
  compact?: boolean;
}

interface ActorState {
  id: string;
  actor: ActorSimulacion;
  x: number;
  y: number;
  rotation: number;
  speed: number;
  braking: boolean;
}

// ─── Color palette per actor type ─────────────────────────────────────────
const colorForActor = (actor: ActorSimulacion): string => {
  if (actor.color) return actor.color;
  switch (actor.tipo) {
    case "turismo": return "#3B82F6";
    case "camion":
    case "autobus": return "#8B5CF6";
    case "motocicleta":
    case "ciclomotor": return "#F97316";
    case "bicicleta": return "#10B981";
    case "peaton": return "#EF4444";
    case "mobiliario_urbano": return "#6B7280";
    default: return "#9CA3AF";
  }
};

// ─── Trajectory interpolation ─────────────────────────────────────────────
function getActorStateAtTime(actor: ActorSimulacion, t: number): ActorState {
  const traj = actor.trayectoria;
  if (!traj || traj.length === 0) {
    return {
      id: actor.id,
      actor,
      x: 0, y: 0, rotation: 0, speed: 0,
      braking: false,
    };
  }
  const tEnd = traj[traj.length - 1].t;
  const tNorm = (t / 100) * tEnd;

  let prev: TrayectoriaPunto = traj[0];
  let next: TrayectoriaPunto = traj[traj.length - 1];
  for (let i = 0; i < traj.length - 1; i++) {
    if (traj[i].t <= tNorm && traj[i + 1].t >= tNorm) {
      prev = traj[i];
      next = traj[i + 1];
      break;
    }
  }
  const span = next.t - prev.t || 1e-6;
  const f = Math.min(1, Math.max(0, (tNorm - prev.t) / span));
  const x = prev.x + (next.x - prev.x) * f;
  const y = prev.y + (next.y - prev.y) * f;
  const speed = prev.v_kmh + (next.v_kmh - prev.v_kmh) * f;

  let rotation: number;
  if (prev.rotation_deg != null && next.rotation_deg != null) {
    rotation = prev.rotation_deg + (next.rotation_deg - prev.rotation_deg) * f;
  } else {
    const dx = next.x - prev.x;
    const dy = next.y - prev.y;
    rotation = Math.atan2(dy, dx) * (180 / Math.PI);
  }
  const braking = prev.frenando === true || next.frenando === true ||
    (actor.frena_desde_t != null && tNorm >= actor.frena_desde_t);
  return { id: actor.id, actor, x, y, rotation, speed, braking };
}

// ─── Pan & zoom ────────────────────────────────────────────────────────────
interface Transform { x: number; y: number; scale: number }

// ─── Component ─────────────────────────────────────────────────────────────
export function EscenaSimulacionView({
  data,
  currentTime,
  showMeasurements = true,
  showTrajectories = true,
  showGrid = true,
  showImpactZone = true,
  compact = false,
}: EscenaSimulacionViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState<Transform>({ x: 0, y: 0, scale: 1 });
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const lastTransform = useRef({ x: 0, y: 0 });

  // Compute fitted viewBox from trajectory points + impact (NOT obstacles, que pueden ser
  // polígonos enormes que descuadran el encuadre). Los obstáculos los clippeamos visualmente
  // pero no expandimos el viewBox por ellos.
  const sceneBounds = useMemo(() => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const expand = (x: number, y: number) => {
      if (!Number.isFinite(x) || !Number.isFinite(y)) return;
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    };
    for (const a of data.actores || []) {
      for (const p of a.trayectoria || []) expand(p.x, p.y);
    }
    if (data.impacto) expand(data.impacto.x, data.impacto.y);
    // Nothing → default bounds
    if (!Number.isFinite(minX) || !Number.isFinite(maxX)) {
      minX = -20; maxX = 20; minY = -15; maxY = 15;
    }
    // Ensure minimum size (scenes with everything in ±2m gave a tiny viewBox
    // that inflated the visual size of SVG text).
    const wRaw = maxX - minX;
    const hRaw = maxY - minY;
    if (wRaw < 30) { const c = (minX + maxX) / 2; minX = c - 15; maxX = c + 15; }
    if (hRaw < 22) { const c = (minY + maxY) / 2; minY = c - 11; maxY = c + 11; }
    const padX = Math.max(6, (maxX - minX) * 0.12);
    const padY = Math.max(6, (maxY - minY) * 0.12);
    return {
      minX: minX - padX, minY: minY - padY,
      width: (maxX - minX) + 2 * padX,
      height: (maxY - minY) + 2 * padY,
    };
  }, [data]);

  const states = useMemo(
    () => (data.actores || []).map(a => getActorStateAtTime(a, currentTime)),
    [data.actores, currentTime]
  );

  const tEnd = useMemo(() => {
    let t = 0;
    for (const a of data.actores || []) {
      const last = a.trayectoria?.[a.trayectoria.length - 1]?.t;
      if (last && last > t) t = last;
    }
    return t || data.duracion_s || 4;
  }, [data]);

  const tNow = (currentTime / 100) * tEnd;
  const isAtImpact = data.impacto != null && tNow >= data.impacto.t - 0.05;

  // ── Pan & zoom handlers (simple)
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY;
    const zoom = delta > 0 ? 1.1 : 0.9;
    setTransform(prev => ({
      ...prev,
      scale: Math.min(Math.max(prev.scale * zoom, 0.5), 5),
    }));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    isDragging.current = true;
    dragStart.current = { x: e.clientX, y: e.clientY };
    lastTransform.current = { x: transform.x, y: transform.y };
  }, [transform.x, transform.y]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current) return;
    const dx = e.clientX - dragStart.current.x;
    const dy = e.clientY - dragStart.current.y;
    setTransform(prev => ({
      ...prev,
      x: lastTransform.current.x + dx,
      y: lastTransform.current.y + dy,
    }));
  }, []);

  const handleMouseUp = useCallback(() => { isDragging.current = false; }, []);

  // ── viewBox transformation
  const vbW = sceneBounds.width / transform.scale;
  const vbH = sceneBounds.height / transform.scale;
  const vbX = sceneBounds.minX + (sceneBounds.width - vbW) / 2 - transform.x / 20;
  const vbY = sceneBounds.minY + (sceneBounds.height - vbH) / 2 - transform.y / 20;
  const viewBox = `${vbX.toFixed(2)} ${vbY.toFixed(2)} ${vbW.toFixed(2)} ${vbH.toFixed(2)}`;

  return (
    <div
      ref={containerRef}
      className={`relative w-full ${compact ? "h-72" : "h-full min-h-[550px]"} bg-[#0d110d] rounded-lg overflow-hidden select-none`}
      style={{ cursor: isDragging.current ? "grabbing" : "grab" }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-[#0d110d] to-transparent p-3 pointer-events-none">
        <div className="flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-4">
            <span className="text-[#C2E94B]">VERIDICT FORENSICS</span>
            <span className="text-zinc-400">SIM v3</span>
          </div>
          <div className="flex items-center gap-4 text-zinc-400">
            <span>T: {tNow.toFixed(2)}s</span>
            <span>ZOOM: {Math.round(transform.scale * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Description chip — collapsible, doesn't cover the scene */}
      {data.descripcion && (
        <div className="absolute top-12 left-3 right-3 z-10 pointer-events-auto">
          <DescripcionChip texto={data.descripcion} />
        </div>
      )}

      {/* SVG scene */}
      <svg
        viewBox={viewBox}
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
        style={{ background: "linear-gradient(180deg, #1a1f1a 0%, #0d110d 100%)" }}
        onWheel={handleWheel}
      >
        <defs>
          <clipPath id="esim-scene-clip">
            <rect
              x={sceneBounds.minX}
              y={sceneBounds.minY}
              width={sceneBounds.width}
              height={sceneBounds.height}
            />
          </clipPath>
          <pattern id="esim-grid" patternUnits="userSpaceOnUse" width="5" height="5">
            <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#2a3a2a" strokeWidth="0.1" />
          </pattern>
          <pattern id="esim-asphalt" patternUnits="userSpaceOnUse" width="2" height="2">
            <rect width="2" height="2" fill="#2a2f2a" />
            <circle cx="0.5" cy="0.5" r="0.15" fill="#222622" />
          </pattern>
          <pattern id="esim-terriza" patternUnits="userSpaceOnUse" width="3" height="3">
            <rect width="3" height="3" fill="#3a2f1f" />
            <circle cx="1" cy="1" r="0.3" fill="#5c4a32" />
            <circle cx="2.2" cy="2.4" r="0.2" fill="#7a6342" />
          </pattern>
          <filter id="esim-glow">
            <feGaussianBlur stdDeviation="0.3" />
          </filter>
          <marker id="esim-arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#C2E94B" opacity="0.6" />
          </marker>
        </defs>

        {showGrid && (
          <rect
            x={sceneBounds.minX - 100}
            y={sceneBounds.minY - 100}
            width={sceneBounds.width + 200}
            height={sceneBounds.height + 200}
            fill="url(#esim-grid)"
            opacity="0.5"
          />
        )}

        <RoadSurface bounds={sceneBounds} via={data.via} />

        {/* Obstacles (clippeados al viewBox para que no descuadren) */}
        <g clipPath="url(#esim-scene-clip)">
          {(data.obstaculos || []).map((ob, i) => (
            <ObstaculoNode key={`ob-${i}`} obstaculo={ob} bounds={sceneBounds} />
          ))}
        </g>

        {/* Trayectorias */}
        {showTrajectories && data.actores.map((a) => (
          <TrayectoriaPath key={`traj-${a.id}`} actor={a} currentTime={currentTime} />
        ))}

        {/* Huellas */}
        {(data.huellas || []).map((h, i) => (
          <line
            key={`h-${i}`}
            x1={h.inicio[0]} y1={h.inicio[1]}
            x2={h.fin[0]} y2={h.fin[1]}
            stroke="#1a1a1a"
            strokeWidth="0.4"
            strokeDasharray={h.tipo === "derrape" ? "0.6,0.4" : undefined}
            opacity="0.85"
          />
        ))}

        {/* Impact point */}
        {isAtImpact && data.impacto && showImpactZone && (
          <ImpactNode impacto={data.impacto} />
        )}

        {/* Actores */}
        {states.map((s) => (
          <ActorNode key={s.id} state={s} isAtImpact={isAtImpact} />
        ))}

        {/* Measurements: show speed labels */}
        {showMeasurements && states.map((s) => (
          <SpeedLabel key={`lbl-${s.id}`} state={s} />
        ))}

        {/* Scale bar */}
        <g transform={`translate(${sceneBounds.minX + 2}, ${sceneBounds.minY + sceneBounds.height - 3})`}>
          <line x1="0" y1="0" x2="10" y2="0" stroke="#C2E94B" strokeWidth="0.25" />
          <line x1="0" y1="-0.5" x2="0" y2="0.5" stroke="#C2E94B" strokeWidth="0.25" />
          <line x1="10" y1="-0.5" x2="10" y2="0.5" stroke="#C2E94B" strokeWidth="0.25" />
          <text x="5" y="1.8" fontSize="1.6" fill="#C2E94B" textAnchor="middle" fontFamily="monospace">10 m</text>
        </g>

        {/* North */}
        <g transform={`translate(${sceneBounds.minX + sceneBounds.width - 5}, ${sceneBounds.minY + 5})`}>
          <circle r="2.5" fill="none" stroke="#4B7759" strokeWidth="0.18" />
          <path d="M0,-2 L0.7,1 L0,0 L-0.7,1 Z" fill="#C2E94B" />
          <text y="-3.2" fontSize="1.4" fill="#C2E94B" textAnchor="middle" fontFamily="monospace">N</text>
        </g>
      </svg>

      {/* Actor legend */}
      <div className="absolute bottom-3 left-3 z-20 pointer-events-none flex flex-wrap gap-2 max-w-[60%]">
        {states.map((s) => {
          const vImpacto = s.actor.velocidad_impacto_kmh;
          const vInicial = s.actor.velocidad_inicial_kmh;
          return (
            <div
              key={`legend-${s.id}`}
              className="bg-[#0d110d]/95 rounded-md px-2.5 py-1.5 backdrop-blur-sm"
              style={{ borderColor: `${colorForActor(s.actor)}66`, borderWidth: 1 }}
            >
              <div className="flex items-center gap-1.5 mb-0.5">
                <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: colorForActor(s.actor) }} />
                <span className="text-[10px] font-mono font-bold" style={{ color: colorForActor(s.actor) }}>
                  {s.actor.etiqueta || s.actor.id}
                </span>
              </div>
              <div className="text-xs font-mono text-zinc-400 leading-tight">
                <div>
                  <span className="text-[9px] uppercase opacity-60 mr-1">now</span>
                  <span className="font-bold text-sm" style={{ color: colorForActor(s.actor) }}>
                    {Math.round(s.speed)}
                  </span>
                  <span className="text-[10px] ml-0.5">km/h</span>
                  {s.braking && (
                    <span className="ml-2 text-red-400 animate-pulse text-[10px]">● BRAKING</span>
                  )}
                </div>
                {vImpacto != null && (
                  <div className="text-[10px] opacity-75">
                    <span className="opacity-60">v_imp:</span>{" "}
                    <span className="text-amber-300 font-bold">{Math.round(vImpacto)}</span> km/h
                    {vInicial != null && vInicial !== vImpacto && (
                      <>
                        {" "}<span className="opacity-60">· v_ini:</span>{" "}
                        <span className="opacity-90">{Math.round(vInicial)}</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Impact banner */}
      {isAtImpact && data.impacto && (
        <motion.div
          className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 bg-red-500/20 border border-red-500/50 rounded-lg px-4 py-2 backdrop-blur-sm pointer-events-none"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <div className="text-xs font-mono text-red-400 text-center">
            <div className="font-bold text-sm">⚠ IMPACT · t = {data.impacto.t.toFixed(2)}s</div>
            <div className="flex gap-3 mt-1 flex-wrap justify-center">
              {Object.entries(data.impacto.delta_v_por_actor).map(([id, dv]) => (
                <span key={id}>
                  ΔV-{id}: <span className="text-white">{dv.toFixed(1)}</span> km/h
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Missing info banner */}
      {data.falta_info && data.falta_info.length > 0 && (
        <div className="absolute top-3 right-3 z-20 max-w-[40%]">
          <div className="bg-amber-500/15 border border-amber-500/40 rounded-md px-3 py-2 text-[11px] text-amber-300 font-mono">
            <strong>Missing:</strong> {data.falta_info[0]}
            {data.falta_info.length > 1 && ` (+${data.falta_info.length - 1})`}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Sub-components ────────────────────────────────────────────────────────

function RoadSurface({
  bounds,
  via,
}: {
  bounds: { minX: number; minY: number; width: number; height: number };
  via: EscenaSimulacionData["via"];
}) {
  const totalWidth = via.ancho_total_m ?? via.carriles * via.ancho_carril_m;
  const half = totalWidth / 2;
  const xStart = bounds.minX - 5;
  const xEnd = bounds.minX + bounds.width + 5;

  // ── Vía curva: si el LLM proporcionó eje_via con ≥2 puntos, la dibujamos
  //    como un path con stroke-width = ancho_total_m. Funciona para curvas,
  //    rotondas, calles sinuosas, etc.
  const ejeVia = via.eje_via;
  if (Array.isArray(ejeVia) && ejeVia.length >= 2) {
    const ejePath = ejeVia.map(([x, y], i) => `${i === 0 ? "M" : "L"} ${x} ${y}`).join(" ");
    const isUrbanaEstrecha = via.tipo === "urbana_estrecha";
    const surfaceFill = isUrbanaEstrecha ? "url(#esim-asphalt)" : "url(#esim-asphalt)";
    const edgeColor = isUrbanaEstrecha ? "#5a4f3a" : "#4B5563";
    const edgeOuter = totalWidth + (isUrbanaEstrecha ? 1.6 : 3);
    const edgeShoulder = isUrbanaEstrecha ? 0 : totalWidth + 1.5;
    const showCenterLine = !isUrbanaEstrecha && via.carriles >= 2;
    return (
      <g className="road-curve">
        {/* Borde exterior (acera/cuneta) */}
        <path
          d={ejePath}
          fill="none"
          stroke={edgeColor}
          strokeWidth={edgeOuter}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Asfalto principal con el ancho total */}
        <path
          d={ejePath}
          fill="none"
          stroke={surfaceFill}
          strokeWidth={totalWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Líneas de borde blancas (no en urbana estrecha) */}
        {!isUrbanaEstrecha && (
          <>
            <path
              d={ejePath}
              fill="none"
              stroke="#FFFFFF"
              strokeWidth="0.18"
              strokeLinejoin="round"
              transform={`translate(0, ${-half + 0.3})`}
              style={{ transformBox: "fill-box" }}
            />
          </>
        )}
        {/* Línea central amarilla discontinua siguiendo el eje */}
        {showCenterLine && (
          <path
            d={ejePath}
            fill="none"
            stroke="#FFD700"
            strokeWidth="0.18"
            strokeDasharray="2,1.5"
            strokeLinejoin="round"
          />
        )}
      </g>
    );
  }

  if (via.tipo === "urbana_estrecha") {
    // Narrow urban road (~3m), no painted lanes, stone-like edges, optional pendiente gradient
    return (
      <g className="road">
        <rect
          x={xStart} y={-half - 1.2}
          width={xEnd - xStart} height={totalWidth + 2.4}
          fill="#3a3327"
        />
        <rect
          x={xStart} y={-half}
          width={xEnd - xStart} height={totalWidth}
          fill="url(#esim-asphalt)"
        />
        {via.pendiente_pct != null && Math.abs(via.pendiente_pct) > 1 && (
          <rect
            x={xStart} y={-half}
            width={xEnd - xStart} height={totalWidth}
            fill={via.pendiente_pct > 0
              ? "url(#esim-asphalt)"
              : "url(#esim-asphalt)"}
            opacity="0"
          />
        )}
        {/* Stone edges */}
        <rect x={xStart} y={-half - 0.3} width={xEnd - xStart} height="0.3" fill="#5a4f3a" />
        <rect x={xStart} y={half} width={xEnd - xStart} height="0.3" fill="#5a4f3a" />
      </g>
    );
  }

  if (via.tipo === "interseccion") {
    return (
      <g className="road">
        <rect x={xStart} y={-half - 1.5} width={xEnd - xStart} height={totalWidth + 3} fill="#2A2E2A" />
        <rect x={xStart} y={-half} width={xEnd - xStart} height={totalWidth} fill="url(#esim-asphalt)" />
        <rect x={-half} y={bounds.minY} width={totalWidth} height={bounds.height} fill="url(#esim-asphalt)" />
        {/* Crosswalk */}
        {[...Array(8)].map((_, i) => (
          <rect key={i} x={-half + 0.4} y={half + 0.5 + i * 1.2}
            width={totalWidth - 0.8} height="0.7" fill="#FFFFFF" opacity="0.8" />
        ))}
      </g>
    );
  }

  // recta / autovía / curva (genérico)
  return (
    <g className="road">
      <rect x={xStart} y={-half - 1.5} width={xEnd - xStart} height={totalWidth + 3} fill="#3A3E3A" />
      <rect x={xStart} y={-half} width={xEnd - xStart} height={totalWidth} fill="url(#esim-asphalt)" />
      <line x1={xStart} y1={-half + 0.3} x2={xEnd} y2={-half + 0.3} stroke="#FFFFFF" strokeWidth="0.18" />
      <line x1={xStart} y1={half - 0.3} x2={xEnd} y2={half - 0.3} stroke="#FFFFFF" strokeWidth="0.18" />
      <line x1={xStart} y1="0" x2={xEnd} y2="0" stroke="#FFD700" strokeWidth="0.18" />
      {via.carriles >= 3 && Array.from({ length: via.carriles - 1 }).map((_, i) => {
        const y = -half + (i + 1) * via.ancho_carril_m;
        if (Math.abs(y) < 0.3) return null;
        return (
          <line key={i} x1={xStart} y1={y} x2={xEnd} y2={y}
            stroke="#FFFFFF" strokeWidth="0.13" strokeDasharray="3,4" />
        );
      })}
    </g>
  );
}

function ObstaculoNode({
  obstaculo,
  bounds,
}: {
  obstaculo: ObstaculoEscena;
  bounds: { minX: number; minY: number; width: number; height: number };
}) {
  const pts = (obstaculo.poligono || []).map(([x, y]) => `${x},${y}`).join(" ");
  if (!pts) return null;
  let fill = "#4B5563";
  let stroke = "#1F2937";
  let opacity = 0.85;
  if (obstaculo.tipo === "edificio") { fill = "#3f3f46"; stroke = "#1f1f22"; opacity = 0.55; }
  if (obstaculo.tipo === "zona_terriza") { fill = "url(#esim-terriza)"; stroke = "#5c4a32"; opacity = 0.7; }
  if (obstaculo.tipo === "talud") { fill = "url(#esim-terriza)"; stroke = "#7a5a32"; opacity = 0.65; }
  if (obstaculo.tipo === "vegetacion") { fill = "#365314"; stroke = "#1A2A0E"; opacity = 0.7; }
  if (obstaculo.tipo === "muro" || obstaculo.tipo === "barrera" || obstaculo.tipo === "quitamiedos") {
    fill = "#737373"; stroke = "#262626"; opacity = 0.75;
  }
  if (obstaculo.tipo === "acera" || obstaculo.tipo === "bordillo") {
    fill = "#52525B"; stroke = "#3F3F46"; opacity = 0.7;
  }

  // Label: only if the first polygon point falls within the viewBox.
  const [lx, ly] = obstaculo.poligono?.[0] ?? [0, 0];
  const within =
    lx >= bounds.minX && lx <= bounds.minX + bounds.width &&
    ly >= bounds.minY && ly <= bounds.minY + bounds.height;
  // Small text, fixed scale independent of zoom: 0.8 SVG units.
  const FONT = 0.8;
  const label = (obstaculo.descripcion || "").slice(0, 38);
  const labelW = Math.max(2.5, label.length * FONT * 0.55);

  return (
    <g>
      <polygon points={pts} fill={fill} stroke={stroke} strokeWidth="0.12" opacity={opacity} />
      {label && within && (
        <g transform={`translate(${lx}, ${ly - 1.1})`}>
          <rect
            x={-labelW / 2} y={-FONT * 0.95}
            width={labelW} height={FONT * 1.4} rx={0.18}
            fill="#0d110d" opacity="0.85" stroke={stroke} strokeWidth="0.06"
          />
          <text
            x={0} y={FONT * 0.25}
            fontSize={FONT} fill="#cbd5e1" textAnchor="middle"
            fontFamily="monospace" pointerEvents="none"
          >
            {label}
          </text>
        </g>
      )}
    </g>
  );
}

function TrayectoriaPath({ actor, currentTime }: { actor: ActorSimulacion; currentTime: number }) {
  if (!actor.trayectoria || actor.trayectoria.length < 2) return null;
  const tEnd = actor.trayectoria[actor.trayectoria.length - 1].t;
  const tNorm = (currentTime / 100) * tEnd;
  const visible = actor.trayectoria.filter(p => p.t <= tNorm);
  if (visible.length < 2) return null;
  const d = visible.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const color = colorForActor(actor);
  return (
    <path
      d={d}
      fill="none"
      stroke={color}
      strokeWidth="0.22"
      strokeDasharray="0.8,0.4"
      opacity="0.55"
      markerEnd="url(#esim-arrow)"
    />
  );
}

function ImpactNode({ impacto }: { impacto: NonNullable<EscenaSimulacionData["impacto"]> }) {
  return (
    <g transform={`translate(${impacto.x}, ${impacto.y})`}>
      <motion.circle r="1.5" fill="none" stroke="#EF4444" strokeWidth="0.18"
        initial={{ r: 0, opacity: 1 }}
        animate={{ r: 4, opacity: 0 }}
        transition={{ duration: 1.5, repeat: Infinity }} />
      <circle r="0.7" fill="#EF4444" />
      <circle r="0.35" fill="#FFFFFF" />
    </g>
  );
}

function SpeedLabel({ state }: { state: ActorState }) {
  const c = colorForActor(state.actor);
  // Tamaño compacto: en lugar de un cartel enorme, una pastilla discreta encima del actor.
  const FONT = 0.95;
  const txt = `${Math.round(state.speed)} km/h`;
  const w = Math.max(3.2, txt.length * FONT * 0.6);
  return (
    <g transform={`translate(${state.x}, ${state.y - 1.7})`} pointerEvents="none">
      <rect
        x={-w / 2} y={-FONT * 0.95} width={w} height={FONT * 1.45} rx="0.22"
        fill="#0d110d" opacity="0.9" stroke={c} strokeWidth="0.07"
      />
      <text
        x="0" y={FONT * 0.32} fontSize={FONT} fill={c}
        textAnchor="middle" fontFamily="monospace" fontWeight="bold"
      >
        {txt}
      </text>
      {state.braking && (
        <circle cx={w / 2 - 0.25} cy={-FONT * 0.25} r="0.2" fill="#ef4444">
          <animate attributeName="opacity" values="1;0.3;1" dur="0.6s" repeatCount="indefinite" />
        </circle>
      )}
    </g>
  );
}

function DescripcionChip({ texto }: { texto: string }) {
  const [open, setOpen] = useState(false);
  const corto = texto.length > 110 ? texto.slice(0, 110) + "…" : texto;
  return (
    <button
      onClick={() => setOpen(o => !o)}
      className="block max-w-full text-left bg-[#0d110d]/90 border border-white/10 hover:border-[#C2E94B]/40 text-xs text-zinc-300 px-3 py-1.5 rounded-md font-mono cursor-pointer transition-colors"
      title={open ? "Click to collapse" : "Click to expand"}
    >
      <span className="text-[#C2E94B] mr-2">🔬</span>
      {open ? texto : corto}
    </button>
  );
}

// ─── Actor rendering switchboard ───────────────────────────────────────────
function ActorNode({ state, isAtImpact }: { state: ActorState; isAtImpact: boolean }) {
  switch (state.actor.tipo) {
    case "turismo":
    case "camion":
    case "autobus":
      return <CarShape state={state} isAtImpact={isAtImpact} />;
    case "motocicleta":
    case "ciclomotor":
      return <BikeShape state={state} isAtImpact={isAtImpact} thinned />;
    case "bicicleta":
      return <BikeShape state={state} isAtImpact={isAtImpact} />;
    case "peaton":
      return <PedestrianShape state={state} isAtImpact={isAtImpact} />;
    case "mobiliario_urbano":
      return <FurnitureShape state={state} />;
    default:
      return <CarShape state={state} isAtImpact={isAtImpact} />;
  }
}

function CarShape({ state, isAtImpact }: { state: ActorState; isAtImpact: boolean }) {
  const L = state.actor.largo_m || (state.actor.tipo === "camion" || state.actor.tipo === "autobus" ? 9 : 4.6);
  const W = state.actor.ancho_m || (state.actor.tipo === "camion" || state.actor.tipo === "autobus" ? 2.5 : 1.8);
  const c = colorForActor(state.actor);
  return (
    <motion.g
      initial={false}
      animate={{ x: state.x, y: state.y, rotate: state.rotation }}
      transition={{ type: "tween", duration: 0.08, ease: "linear" }}
    >
      <ellipse cx={0.2} cy={0.2} rx={L / 2 + 0.2} ry={W / 2 + 0.15} fill="#000" opacity="0.4" />
      <rect x={-L / 2} y={-W / 2} width={L} height={W} rx="0.4"
        fill={c} stroke={isAtImpact ? "#EF4444" : "#0F172A"} strokeWidth={isAtImpact ? "0.3" : "0.12"}
        filter={state.braking ? "url(#esim-glow)" : undefined} />
      {/* windshield */}
      <rect x={L / 2 - L * 0.4} y={-W / 2 + 0.18} width={L * 0.18} height={W - 0.36} fill="#0F172A" opacity="0.7" />
      {/* rear lights */}
      <rect x={-L / 2} y={-W / 2 + 0.15} width="0.12" height="0.4" fill={state.braking ? "#FF0000" : "#7F1D1D"} />
      <rect x={-L / 2} y={W / 2 - 0.55} width="0.12" height="0.4" fill={state.braking ? "#FF0000" : "#7F1D1D"} />
      {/* id badge */}
      <circle cx="0" cy="0" r="0.6" fill="#0F172A" stroke="#fff" strokeWidth="0.06" />
      <text x="0" y="0.3" fontSize="0.85" fill="#fff" textAnchor="middle" fontFamily="monospace">
        {state.actor.id.slice(0, 1).toUpperCase()}
      </text>
    </motion.g>
  );
}

function BikeShape({ state, isAtImpact, thinned = false }: { state: ActorState; isAtImpact: boolean; thinned?: boolean }) {
  const L = state.actor.largo_m || (thinned ? 2.0 : 1.7);
  const W = state.actor.ancho_m || 0.55;
  const c = colorForActor(state.actor);
  return (
    <motion.g
      initial={false}
      animate={{ x: state.x, y: state.y, rotate: state.rotation }}
      transition={{ type: "tween", duration: 0.08, ease: "linear" }}
    >
      {/* shadow */}
      <ellipse cx={0.1} cy={0.1} rx={L / 2 + 0.1} ry={W / 2 + 0.05} fill="#000" opacity="0.35" />
      {/* frame line */}
      <line x1={-L / 2} y1="0" x2={L / 2} y2="0" stroke={c} strokeWidth="0.2"
        filter={isAtImpact ? "url(#esim-glow)" : undefined} />
      {/* wheels */}
      <circle cx={-L / 2 + 0.15} cy="0" r="0.3" fill="none" stroke="#222" strokeWidth="0.08" />
      <circle cx={L / 2 - 0.15} cy="0" r="0.3" fill="none" stroke="#222" strokeWidth="0.08" />
      {/* handlebar */}
      <line x1={L / 2 - 0.25} y1={-W / 2} x2={L / 2 - 0.25} y2={W / 2}
        stroke={c} strokeWidth="0.12" />
      {/* rider blob */}
      <circle cx="0" cy="0" r="0.32" fill={isAtImpact ? "#EF4444" : c} stroke="#0F172A" strokeWidth="0.08" />
      {/* id badge */}
      <text x="0" y="-0.6" fontSize="0.7" fill={c} textAnchor="middle" fontFamily="monospace" fontWeight="bold">
        {state.actor.id.slice(0, 4)}
      </text>
    </motion.g>
  );
}

function PedestrianShape({ state, isAtImpact }: { state: ActorState; isAtImpact: boolean }) {
  const c = colorForActor(state.actor);
  return (
    <motion.g
      initial={false}
      animate={{ x: state.x, y: state.y, rotate: state.rotation }}
      transition={{ type: "tween", duration: 0.08, ease: "linear" }}
    >
      <ellipse cx="0.05" cy="0.05" rx="0.35" ry="0.2" fill="#000" opacity="0.4" />
      <circle r="0.32" fill={isAtImpact ? "#EF4444" : c} stroke="#0F172A" strokeWidth="0.08"
        filter={isAtImpact ? "url(#esim-glow)" : undefined} />
      {/* facing line */}
      <line x1="0" y1="0" x2="0.5" y2="0" stroke="#fff" strokeWidth="0.1" />
    </motion.g>
  );
}

function FurnitureShape({ state }: { state: ActorState }) {
  const L = state.actor.largo_m || 0.6;
  const W = state.actor.ancho_m || 0.6;
  return (
    <motion.g
      initial={false}
      animate={{ x: state.x, y: state.y, rotate: state.rotation }}
      transition={{ type: "tween", duration: 0.08, ease: "linear" }}
    >
      <rect x={-L / 2} y={-W / 2} width={L} height={W} fill="#6B7280" stroke="#1F2937" strokeWidth="0.1" />
    </motion.g>
  );
}

export default EscenaSimulacionView;

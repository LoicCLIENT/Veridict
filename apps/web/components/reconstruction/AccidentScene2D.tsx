"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { ZoomIn, ZoomOut, Maximize, Navigation, Play, Pause } from "lucide-react";

// Types for accident reconstruction
export interface VehicleState {
  id: "A" | "B";
  x: number;
  y: number;
  rotation: number;
  speed: number;
  braking: boolean;
  color: string;
}

export interface TrajectoryPoint {
  x: number;
  y: number;
  time: number;
  speed: number;
}

export interface AccidentSceneData {
  road: {
    type: "straight" | "intersection" | "curve" | "highway";
    lanes: number;
    laneWidth: number;
    speedLimit: number;
  };
  vehicleA: {
    trajectory: TrajectoryPoint[];
    brakeStartTime: number;
    brakeDistance: number;
    initialSpeed: number;
    impactSpeed: number;
  };
  vehicleB: {
    trajectory: TrajectoryPoint[];
    brakeStartTime: number;
    brakeDistance: number;
    initialSpeed: number;
    impactSpeed: number;
  };
  impact: {
    x: number;
    y: number;
    time: number;
    angle: number;
    deltaV_A: number;
    deltaV_B: number;
  };
  metadata: {
    scaleMetersPerUnit: number;
    weatherCondition: string;
    roadCondition: string;
    visibility: string;
  };
}

interface AccidentScene2DProps {
  data: AccidentSceneData;
  currentTime: number;
  showMeasurements?: boolean;
  showTrajectories?: boolean;
  showGrid?: boolean;
  interactive?: boolean;
  compact?: boolean;
  // New customization props
  vehicleAColor?: string;
  vehicleBColor?: string;
  centerTarget?: "A" | "B" | "impact" | "overview" | null;
  showSpeedLabels?: boolean;
  showImpactZone?: boolean;
  viewMode?: "2d-top" | "2d-isometric";
}

// Pure function to calculate vehicle state at time
function getVehicleStateAtTime(
  trajectory: TrajectoryPoint[],
  time: number,
  vehicleId: "A" | "B",
  color: string,
  brakeStartTime: number
): VehicleState {
  const normalizedTime = (time / 100) * (trajectory[trajectory.length - 1]?.time || 1);

  let prevPoint = trajectory[0];
  let nextPoint = trajectory[trajectory.length - 1];

  for (let i = 0; i < trajectory.length - 1; i++) {
    if (trajectory[i].time <= normalizedTime && trajectory[i + 1].time >= normalizedTime) {
      prevPoint = trajectory[i];
      nextPoint = trajectory[i + 1];
      break;
    }
  }

  const t = nextPoint.time === prevPoint.time
    ? 0
    : (normalizedTime - prevPoint.time) / (nextPoint.time - prevPoint.time);

  const clampedT = Math.min(1, Math.max(0, t));
  const x = prevPoint.x + (nextPoint.x - prevPoint.x) * clampedT;
  const y = prevPoint.y + (nextPoint.y - prevPoint.y) * clampedT;
  const speed = prevPoint.speed + (nextPoint.speed - prevPoint.speed) * clampedT;

  const dx = nextPoint.x - prevPoint.x;
  const dy = nextPoint.y - prevPoint.y;
  const rotation = Math.atan2(dy, dx) * (180 / Math.PI);

  return {
    id: vehicleId,
    x,
    y,
    rotation,
    speed,
    braking: normalizedTime >= brakeStartTime,
    color,
  };
}

// Transform state for pan/zoom
interface Transform {
  x: number;
  y: number;
  scale: number;
}

export function AccidentScene2D({
  data,
  currentTime,
  showMeasurements = true,
  showTrajectories = true,
  showGrid = true,
  interactive = true,
  compact = false,
  vehicleAColor = "#3B82F6",
  vehicleBColor = "#F97316",
  centerTarget = null,
  showSpeedLabels = true,
  showImpactZone = true,
  viewMode = "2d-top",
}: AccidentScene2DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Transform state (scale and translation)
  const [transform, setTransform] = useState<Transform>({ x: 0, y: 0, scale: 1 });
  const [autoFollow, setAutoFollow] = useState(true);

  // Interaction state
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const lastTransform = useRef({ x: 0, y: 0 });
  const velocity = useRef({ x: 0, y: 0 });
  const lastMoveTime = useRef(0);
  const lastMousePos = useRef({ x: 0, y: 0 });
  const momentumFrame = useRef<number | null>(null);

  // Base scene dimensions (in scene units/meters)
  const sceneWidth = 160;
  const sceneHeight = 90;
  const sceneCenterX = 65;
  const sceneCenterY = 10;

  // Get current vehicle positions
  const vehicleAState = getVehicleStateAtTime(
    data.vehicleA.trajectory,
    currentTime,
    "A",
    vehicleAColor,
    data.vehicleA.brakeStartTime
  );

  const vehicleBState = getVehicleStateAtTime(
    data.vehicleB.trajectory,
    currentTime,
    "B",
    vehicleBColor,
    data.vehicleB.brakeStartTime
  );

  // Handle center target changes
  useEffect(() => {
    if (!centerTarget) return;

    setAutoFollow(false);

    if (centerTarget === "overview") {
      setTransform({ x: 0, y: 0, scale: 1 });
      setAutoFollow(true);
    } else if (centerTarget === "A") {
      const targetX = -(vehicleAState.x - sceneCenterX) * transform.scale;
      const targetY = -(vehicleAState.y - sceneCenterY) * transform.scale;
      setTransform(prev => ({ ...prev, x: targetX, y: targetY, scale: 1.5 }));
    } else if (centerTarget === "B") {
      const targetX = -(vehicleBState.x - sceneCenterX) * transform.scale;
      const targetY = -(vehicleBState.y - sceneCenterY) * transform.scale;
      setTransform(prev => ({ ...prev, x: targetX, y: targetY, scale: 1.5 }));
    } else if (centerTarget === "impact") {
      const targetX = -(data.impact.x - sceneCenterX) * transform.scale;
      const targetY = -(data.impact.y - sceneCenterY) * transform.scale;
      setTransform(prev => ({ ...prev, x: targetX, y: targetY, scale: 2 }));
    }
  }, [centerTarget]);

  const impactProgress = (currentTime / 100) * (data.vehicleA.trajectory[data.vehicleA.trajectory.length - 1]?.time || 1);
  const isAtImpact = impactProgress >= data.impact.time;

  // Auto-follow effect
  useEffect(() => {
    if (!autoFollow) return;

    const centerX = (vehicleAState.x + vehicleBState.x) / 2;
    const centerY = (vehicleAState.y + vehicleBState.y) / 2;

    // Calculate target offset to center vehicles
    const targetX = -(centerX - sceneCenterX) * transform.scale;
    const targetY = -(centerY - sceneCenterY) * transform.scale;

    // Smooth interpolation
    setTransform(prev => ({
      ...prev,
      x: prev.x + (targetX - prev.x) * 0.08,
      y: prev.y + (targetY - prev.y) * 0.08,
    }));
  }, [currentTime, autoFollow, vehicleAState.x, vehicleAState.y, vehicleBState.x, vehicleBState.y, transform.scale]);

  // Convert screen coordinates to scene coordinates
  const screenToScene = useCallback((screenX: number, screenY: number) => {
    const container = containerRef.current;
    if (!container) return { x: 0, y: 0 };

    const rect = container.getBoundingClientRect();
    const containerWidth = rect.width;
    const containerHeight = rect.height;

    // Calculate the scale factor from scene to screen
    const scaleX = containerWidth / sceneWidth;
    const scaleY = containerHeight / sceneHeight;
    const baseScale = Math.min(scaleX, scaleY);

    // Position relative to container center
    const centerOffsetX = screenX - rect.left - containerWidth / 2;
    const centerOffsetY = screenY - rect.top - containerHeight / 2;

    // Convert to scene coordinates
    const sceneX = (centerOffsetX - transform.x) / (baseScale * transform.scale) + sceneCenterX;
    const sceneY = (centerOffsetY - transform.y) / (baseScale * transform.scale) + sceneCenterY;

    return { x: sceneX, y: sceneY };
  }, [transform]);

  // Zoom toward a point
  const zoomAtPoint = useCallback((screenX: number, screenY: number, zoomFactor: number) => {
    const container = containerRef.current;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const containerWidth = rect.width;
    const containerHeight = rect.height;

    // Point relative to container center
    const px = screenX - rect.left - containerWidth / 2;
    const py = screenY - rect.top - containerHeight / 2;

    setTransform(prev => {
      const newScale = Math.min(Math.max(prev.scale * zoomFactor, 0.5), 5);
      const scaleChange = newScale / prev.scale;

      // Adjust translation to zoom toward the mouse point
      const newX = px - (px - prev.x) * scaleChange;
      const newY = py - (py - prev.y) * scaleChange;

      return { x: newX, y: newY, scale: newScale };
    });

    // Disable auto-follow when user interacts
    setAutoFollow(false);
  }, []);

  // Handle wheel zoom (deltaY > 0 = scroll down = zoom out)
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (!interactive) return;
    e.preventDefault();

    // Normalizar deltaY para diferentes navegadores
    const delta = -e.deltaY || -e.detail;
    const zoomFactor = delta > 0 ? 1.1 : 0.9;
    zoomAtPoint(e.clientX, e.clientY, zoomFactor);
  }, [interactive, zoomAtPoint]);

  // Stop momentum
  const stopMomentum = useCallback(() => {
    if (momentumFrame.current) {
      cancelAnimationFrame(momentumFrame.current);
      momentumFrame.current = null;
    }
  }, []);

  // Apply momentum after drag
  const applyMomentum = useCallback(() => {
    const friction = 0.95;
    const minVelocity = 0.5;

    const animate = () => {
      velocity.current.x *= friction;
      velocity.current.y *= friction;

      if (Math.abs(velocity.current.x) < minVelocity && Math.abs(velocity.current.y) < minVelocity) {
        stopMomentum();
        return;
      }

      setTransform(prev => ({
        ...prev,
        x: prev.x + velocity.current.x,
        y: prev.y + velocity.current.y,
      }));

      momentumFrame.current = requestAnimationFrame(animate);
    };

    momentumFrame.current = requestAnimationFrame(animate);
  }, [stopMomentum]);

  // Mouse down - start drag
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!interactive || e.button !== 0) return;

    stopMomentum();
    isDragging.current = true;
    dragStart.current = { x: e.clientX, y: e.clientY };
    lastTransform.current = { x: transform.x, y: transform.y };
    lastMousePos.current = { x: e.clientX, y: e.clientY };
    lastMoveTime.current = performance.now();
    velocity.current = { x: 0, y: 0 };

    // Disable auto-follow when user starts dragging
    setAutoFollow(false);

    // Change cursor
    if (containerRef.current) {
      containerRef.current.style.cursor = 'grabbing';
    }
  }, [interactive, transform.x, transform.y, stopMomentum]);

  // Mouse move - handle drag
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current) return;

    const now = performance.now();
    const dt = now - lastMoveTime.current;

    const dx = e.clientX - dragStart.current.x;
    const dy = e.clientY - dragStart.current.y;

    // Calculate velocity for momentum
    if (dt > 0) {
      velocity.current = {
        x: (e.clientX - lastMousePos.current.x) / (dt / 16), // Normalize to ~60fps
        y: (e.clientY - lastMousePos.current.y) / (dt / 16),
      };
    }

    lastMousePos.current = { x: e.clientX, y: e.clientY };
    lastMoveTime.current = now;

    setTransform(prev => ({
      ...prev,
      x: lastTransform.current.x + dx,
      y: lastTransform.current.y + dy,
    }));
  }, []);

  // Mouse up - end drag
  const handleMouseUp = useCallback(() => {
    if (!isDragging.current) return;

    isDragging.current = false;

    // Restore cursor
    if (containerRef.current) {
      containerRef.current.style.cursor = 'grab';
    }

    // Apply momentum if velocity is significant
    if (Math.abs(velocity.current.x) > 1 || Math.abs(velocity.current.y) > 1) {
      applyMomentum();
    }
  }, [applyMomentum]);

  // Mouse leave - cancel drag
  const handleMouseLeave = useCallback(() => {
    if (isDragging.current) {
      handleMouseUp();
    }
  }, [handleMouseUp]);

  // Touch handlers for mobile
  const touchStartRef = useRef<{ x: number; y: number; dist: number } | null>(null);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (!interactive) return;
    stopMomentum();
    setAutoFollow(false);

    if (e.touches.length === 1) {
      // Single touch - pan
      isDragging.current = true;
      dragStart.current = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      lastTransform.current = { x: transform.x, y: transform.y };
      velocity.current = { x: 0, y: 0 };
    } else if (e.touches.length === 2) {
      // Two fingers - pinch zoom
      const dx = e.touches[1].clientX - e.touches[0].clientX;
      const dy = e.touches[1].clientY - e.touches[0].clientY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      touchStartRef.current = { x: centerX, y: centerY, dist };
    }
  }, [interactive, transform.x, transform.y, stopMomentum]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!interactive) return;

    if (e.touches.length === 1 && isDragging.current) {
      const dx = e.touches[0].clientX - dragStart.current.x;
      const dy = e.touches[0].clientY - dragStart.current.y;

      setTransform(prev => ({
        ...prev,
        x: lastTransform.current.x + dx,
        y: lastTransform.current.y + dy,
      }));
    } else if (e.touches.length === 2 && touchStartRef.current) {
      const dx = e.touches[1].clientX - e.touches[0].clientX;
      const dy = e.touches[1].clientY - e.touches[0].clientY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

      const zoomFactor = dist / touchStartRef.current.dist;
      zoomAtPoint(centerX, centerY, zoomFactor);

      touchStartRef.current = { x: centerX, y: centerY, dist };
    }
  }, [interactive, zoomAtPoint]);

  const handleTouchEnd = useCallback(() => {
    isDragging.current = false;
    touchStartRef.current = null;
  }, []);

  // Zoom button handlers
  const handleZoomIn = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const rect = container.getBoundingClientRect();
    zoomAtPoint(rect.left + rect.width / 2, rect.top + rect.height / 2, 1.3);
  }, [zoomAtPoint]);

  const handleZoomOut = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const rect = container.getBoundingClientRect();
    zoomAtPoint(rect.left + rect.width / 2, rect.top + rect.height / 2, 0.7);
  }, [zoomAtPoint]);

  const handleResetView = useCallback(() => {
    stopMomentum();
    setTransform({ x: 0, y: 0, scale: 1 });
    setAutoFollow(true);
  }, [stopMomentum]);

  // Calculate viewBox based on transform
  const viewBoxWidth = sceneWidth / transform.scale;
  const viewBoxHeight = sceneHeight / transform.scale;

  // Calculate center offset based on transform
  const container = containerRef.current;
  const containerWidth = container?.clientWidth || 800;
  const containerHeight = container?.clientHeight || 500;
  const scaleX = containerWidth / sceneWidth;
  const scaleY = containerHeight / sceneHeight;
  const baseScale = Math.min(scaleX, scaleY);

  const viewBoxX = sceneCenterX - viewBoxWidth / 2 - transform.x / (baseScale * transform.scale);
  const viewBoxY = sceneCenterY - viewBoxHeight / 2 - transform.y / (baseScale * transform.scale);

  const viewBox = `${viewBoxX.toFixed(2)} ${viewBoxY.toFixed(2)} ${viewBoxWidth.toFixed(2)} ${viewBoxHeight.toFixed(2)}`;

  return (
    <div
      ref={containerRef}
      className={`relative w-full ${compact ? "h-72" : "h-full min-h-[550px]"} bg-[#0d110d] rounded-lg overflow-hidden select-none`}
      style={{ cursor: interactive ? (isDragging.current ? 'grabbing' : 'grab') : 'default' }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-[#0d110d] to-transparent p-3 pointer-events-none">
        <div className="flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-4">
            <span className="text-veridict-lime">VERIDICT FORENSICS</span>
            <span className="text-veridict-gray">v2.1.4</span>
          </div>
          <div className="flex items-center gap-4 text-veridict-gray">
            <span>T: {(currentTime / 100 * data.impact.time).toFixed(2)}s</span>
            <span>ZOOM: {Math.round(transform.scale * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      {interactive && (
        <div className="absolute top-14 right-4 z-30 flex flex-col gap-1.5">
          <button
            onClick={handleZoomIn}
            className="p-2.5 rounded-lg bg-veridict-green-800/95 hover:bg-veridict-green-700 text-veridict-lime border border-veridict-green-600 transition-all hover:scale-105 active:scale-95 shadow-lg"
            title="Zoom in"
          >
            <ZoomIn size={20} />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2.5 rounded-lg bg-veridict-green-800/95 hover:bg-veridict-green-700 text-veridict-lime border border-veridict-green-600 transition-all hover:scale-105 active:scale-95 shadow-lg"
            title="Zoom out"
          >
            <ZoomOut size={20} />
          </button>
          <button
            onClick={handleResetView}
            className="p-2.5 rounded-lg bg-veridict-green-800/95 hover:bg-veridict-green-700 text-veridict-lime border border-veridict-green-600 transition-all hover:scale-105 active:scale-95 shadow-lg"
            title="Reset view"
          >
            <Maximize size={20} />
          </button>
          <button
            onClick={() => setAutoFollow(prev => !prev)}
            className={`p-2.5 rounded-lg border transition-all hover:scale-105 active:scale-95 shadow-lg ${
              autoFollow
                ? "bg-veridict-lime/25 text-veridict-lime border-veridict-lime/50"
                : "bg-veridict-green-800/95 text-veridict-gray border-veridict-green-600 hover:bg-veridict-green-700"
            }`}
            title={autoFollow ? "Following vehicles" : "Follow vehicles"}
          >
            <Navigation size={20} />
          </button>
        </div>
      )}

      {/* Auto-follow indicator */}
      {autoFollow && (
        <div className="absolute top-14 left-4 z-30 px-3 py-2 rounded-lg bg-veridict-lime/15 border border-veridict-lime/30 text-xs font-mono text-veridict-lime flex items-center gap-2 shadow-lg pointer-events-none">
          <Navigation size={14} className="animate-pulse" />
          Following vehicles
        </div>
      )}

      {/* Main SVG Scene */}
      <svg
        ref={svgRef}
        viewBox={viewBox}
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
        style={{
          background: "linear-gradient(180deg, #1a1f1a 0%, #0d110d 100%)",
          transform: viewMode === "2d-isometric" ? "rotateX(30deg) rotateZ(-15deg)" : undefined,
          transformStyle: "preserve-3d",
        }}
        onWheel={handleWheel}
      >
        <defs>
          {/* Road surface pattern */}
          <pattern id="asphalt" patternUnits="userSpaceOnUse" width="4" height="4">
            <rect width="4" height="4" fill="#2a2f2a" />
            <circle cx="1" cy="1" r="0.3" fill="#222622" />
            <circle cx="3" cy="3" r="0.2" fill="#252825" />
          </pattern>

          {/* Grid pattern */}
          <pattern id="grid" patternUnits="userSpaceOnUse" width="10" height="10">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#2a3a2a" strokeWidth="0.2" />
          </pattern>

          {/* Glow effects */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="1" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="impactGlow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Arrow markers */}
          <marker id="arrowBlue" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#3B82F6" opacity="0.7" />
          </marker>
          <marker id="arrowOrange" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#F97316" opacity="0.7" />
          </marker>
        </defs>

        {/* Background grid */}
        {showGrid && (
          <rect x="-100" y="-100" width="400" height="300" fill="url(#grid)" opacity="0.5" />
        )}

        {/* Road System */}
        <RoadSystem data={data} />

        {/* Brake marks */}
        {showTrajectories && currentTime > 30 && (
          <BrakeMarks
            vehicleA={data.vehicleA}
            vehicleB={data.vehicleB}
            currentTime={currentTime}
            impact={data.impact}
          />
        )}

        {/* Trajectories */}
        {showTrajectories && (
          <Trajectories
            vehicleA={data.vehicleA}
            vehicleB={data.vehicleB}
            currentTime={currentTime}
          />
        )}

        {/* Impact point */}
        {isAtImpact && showImpactZone && (
          <ImpactPoint
            x={data.impact.x}
            y={data.impact.y}
            angle={data.impact.angle}
          />
        )}

        {/* Vehicles */}
        <Vehicle state={vehicleAState} isAtImpact={isAtImpact} />
        <Vehicle state={vehicleBState} isAtImpact={isAtImpact} />

        {/* Measurements */}
        {showMeasurements && (
          <MeasurementsOverlay
            data={data}
            currentTime={currentTime}
            vehicleA={vehicleAState}
            vehicleB={vehicleBState}
            showSpeedLabels={showSpeedLabels}
          />
        )}

        {/* Scale bar */}
        <g transform="translate(-30, 60)">
          <line x1="0" y1="0" x2="20" y2="0" stroke="#C2E94B" strokeWidth="0.5" />
          <line x1="0" y1="-1" x2="0" y2="1" stroke="#C2E94B" strokeWidth="0.5" />
          <line x1="20" y1="-1" x2="20" y2="1" stroke="#C2E94B" strokeWidth="0.5" />
          <text x="10" y="4" fontSize="3" fill="#C2E94B" textAnchor="middle" fontFamily="monospace">
            20m
          </text>
        </g>

        {/* North indicator */}
        <g transform="translate(140, -40)">
          <circle cx="0" cy="0" r="6" fill="none" stroke="#4B7759" strokeWidth="0.3" />
          <path d="M0,-5 L1.5,2 L0,0 L-1.5,2 Z" fill="#C2E94B" />
          <text x="0" y="-8" fontSize="3" fill="#C2E94B" textAnchor="middle" fontFamily="monospace">
            N
          </text>
        </g>
      </svg>

      {/* Vehicle data overlay */}
      <div className="absolute bottom-3 left-3 z-20 pointer-events-none">
        <div className="flex gap-2">
          <div
            className="bg-[#0d110d]/95 rounded-lg px-3 py-2 backdrop-blur-sm"
            style={{ borderColor: `${vehicleAColor}66`, borderWidth: 1 }}
          >
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: vehicleAColor }} />
              <span className="text-[10px] font-mono font-bold" style={{ color: vehicleAColor }}>VEHICLE A</span>
            </div>
            <div className="text-xs font-mono text-zinc-400">
              <span className="font-bold text-sm" style={{ color: vehicleAColor }}>{vehicleAState.speed.toFixed(0)}</span>
              <span className="text-[10px] ml-0.5">km/h</span>
              {vehicleAState.braking && (
                <span className="ml-2 text-red-400 animate-pulse text-[10px]">● BRAKING</span>
              )}
            </div>
          </div>

          <div
            className="bg-[#0d110d]/95 rounded-lg px-3 py-2 backdrop-blur-sm"
            style={{ borderColor: `${vehicleBColor}66`, borderWidth: 1 }}
          >
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: vehicleBColor }} />
              <span className="text-[10px] font-mono font-bold" style={{ color: vehicleBColor }}>VEHICLE B</span>
            </div>
            <div className="text-xs font-mono text-zinc-400">
              <span className="font-bold text-sm" style={{ color: vehicleBColor }}>{vehicleBState.speed.toFixed(0)}</span>
              <span className="text-[10px] ml-0.5">km/h</span>
              {vehicleBState.braking && (
                <span className="ml-2 text-red-400 animate-pulse text-[10px]">● BRAKING</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Impact indicator */}
      {isAtImpact && (
        <motion.div
          className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 bg-red-500/20 border border-red-500/50 rounded-lg px-4 py-2 backdrop-blur-sm pointer-events-none"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <div className="text-xs font-mono text-red-400 text-center">
            <div className="font-bold text-sm">⚠ IMPACT</div>
            <div className="flex gap-3 mt-1">
              <span>ΔV-A: <span className="text-white">{data.impact.deltaV_A.toFixed(1)}</span> km/h</span>
              <span>ΔV-B: <span className="text-white">{data.impact.deltaV_B.toFixed(1)}</span> km/h</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Label */}
      <div className="absolute bottom-3 right-3 z-20 pointer-events-none">
        <span className="text-[10px] text-veridict-gray/60 font-mono bg-[#0d110d]/80 px-2 py-1 rounded">
          2D RECONSTRUCTION • Drag to move • Scroll to zoom
        </span>
      </div>
    </div>
  );
}

// Road System Component
function RoadSystem({ data }: { data: AccidentSceneData }) {
  const { road } = data;
  const roadWidth = road.lanes * road.laneWidth;
  const halfWidth = roadWidth / 2;
  const shoulderWidth = 1.5;

  if (road.type === "intersection") {
    return (
      <g className="road-system">
        <rect x="-30" y="-60" width="200" height="150" fill="#1a2a1a" />
        <rect x="-20" y={-halfWidth - shoulderWidth} width="160" height={roadWidth + shoulderWidth * 2} fill="#2A2E2A" />
        <rect x={60 - halfWidth - shoulderWidth} y="-50" width={roadWidth + shoulderWidth * 2} height="130" fill="#2A2E2A" />
        <rect x="-20" y={-halfWidth} width="160" height={roadWidth} fill="url(#asphalt)" />
        <rect x={60 - halfWidth} y="-50" width={roadWidth} height="130" fill="url(#asphalt)" />
        <rect x="-20" y={-halfWidth - shoulderWidth} width="160" height="0.4" fill="#4B5563" />
        <rect x="-20" y={halfWidth + shoulderWidth - 0.4} width="160" height="0.4" fill="#4B5563" />
        <rect x={60 - halfWidth - shoulderWidth} y="-50" width="0.4" height="130" fill="#4B5563" />
        <rect x={60 + halfWidth + shoulderWidth - 0.4} y="-50" width="0.4" height="130" fill="#4B5563" />
        <line x1="-20" y1={-halfWidth + 0.3} x2="140" y2={-halfWidth + 0.3} stroke="#FFFFFF" strokeWidth="0.2" />
        <line x1="-20" y1={halfWidth - 0.3} x2="140" y2={halfWidth - 0.3} stroke="#FFFFFF" strokeWidth="0.2" />
        <line x1="-20" y1="-0.15" x2={60 - halfWidth} y2="-0.15" stroke="#FFD700" strokeWidth="0.2" />
        <line x1="-20" y1="0.15" x2={60 - halfWidth} y2="0.15" stroke="#FFD700" strokeWidth="0.2" />
        <line x1={60 + halfWidth} y1="-0.15" x2="140" y2="-0.15" stroke="#FFD700" strokeWidth="0.2" />
        <line x1={60 + halfWidth} y1="0.15" x2="140" y2="0.15" stroke="#FFD700" strokeWidth="0.2" />
        <g>
          {[...Array(10)].map((_, i) => (
            <rect key={`crosswalk-h-${i}`} x={60 - halfWidth + 0.5} y={halfWidth + 1.5 + i * 1.8} width={roadWidth - 1} height="0.9" fill="#FFFFFF" opacity="0.9" />
          ))}
        </g>
        <line x1={60 - halfWidth} y1={halfWidth + 0.8} x2={60 + halfWidth} y2={halfWidth + 0.8} stroke="#FFFFFF" strokeWidth="0.5" />
      </g>
    );
  }

  return (
    <g className="road-system">
      <rect x="-30" y={-halfWidth - 15} width="180" height={roadWidth + 30} fill="#1a2a1a" />
      <rect x="-20" y={-halfWidth - shoulderWidth} width="160" height={roadWidth + shoulderWidth * 2} fill="#3A3E3A" />
      <rect x="-20" y={-halfWidth} width="160" height={roadWidth} fill="url(#asphalt)" />
      <rect x="-20" y={-halfWidth - shoulderWidth - 0.3} width="160" height="0.5" fill="#4B5563" />
      <rect x="-20" y={halfWidth + shoulderWidth - 0.2} width="160" height="0.5" fill="#4B5563" />
      <line x1="-20" y1={-halfWidth - shoulderWidth - 0.5} x2="140" y2={-halfWidth - shoulderWidth - 0.5} stroke="#6B7280" strokeWidth="0.3" />
      <line x1="-20" y1={halfWidth + shoulderWidth + 0.5} x2="140" y2={halfWidth + shoulderWidth + 0.5} stroke="#6B7280" strokeWidth="0.3" />
      <line x1="-20" y1={-halfWidth + 0.4} x2="140" y2={-halfWidth + 0.4} stroke="#FFFFFF" strokeWidth="0.25" />
      <line x1="-20" y1={halfWidth - 0.4} x2="140" y2={halfWidth - 0.4} stroke="#FFFFFF" strokeWidth="0.25" />
      <line x1="-20" y1="-0.25" x2="140" y2="-0.25" stroke="#FFD700" strokeWidth="0.2" />
      <line x1="-20" y1="0.25" x2="140" y2="0.25" stroke="#FFD700" strokeWidth="0.2" />
      {road.lanes === 4 && (
        <>
          <line x1="-20" y1={-road.laneWidth} x2="140" y2={-road.laneWidth} stroke="#FFFFFF" strokeWidth="0.18" strokeDasharray="4,6" />
          <line x1="-20" y1={road.laneWidth} x2="140" y2={road.laneWidth} stroke="#FFFFFF" strokeWidth="0.18" strokeDasharray="4,6" />
        </>
      )}
      {road.lanes === 3 && (
        <>
          <line x1="-20" y1={-road.laneWidth/2 - 0.5} x2="140" y2={-road.laneWidth/2 - 0.5} stroke="#FFFFFF" strokeWidth="0.18" strokeDasharray="4,6" />
          <line x1="-20" y1={road.laneWidth/2 + 0.5} x2="140" y2={road.laneWidth/2 + 0.5} stroke="#FFFFFF" strokeWidth="0.18" strokeDasharray="4,6" />
        </>
      )}
      <g transform="translate(-15, -12)">
        <circle r="2.5" fill="#FFFFFF" stroke="#EF4444" strokeWidth="0.4" />
        <text y="0.8" fontSize="2.2" fill="#1F2937" textAnchor="middle" fontFamily="Arial" fontWeight="bold">
          {road.speedLimit}
        </text>
      </g>
    </g>
  );
}

// Vehicle Component
function Vehicle({ state, isAtImpact }: { state: VehicleState; isAtImpact: boolean }) {
  const carLength = 5.5;
  const carWidth = 2.2;
  const bodyColor = state.color;
  const highlightColor = state.id === "A" ? "#60A5FA" : "#FB923C";
  const darkColor = state.id === "A" ? "#1E40AF" : "#C2410C";

  return (
    <motion.g
      initial={false}
      animate={{ x: state.x, y: state.y, rotate: state.rotation }}
      transition={{ type: "tween", duration: 0.08, ease: "linear" }}
    >
      <ellipse cx={0.4} cy={0.4} rx={carLength/2 + 0.3} ry={carWidth/2 + 0.2} fill="#000000" opacity="0.4" />
      <rect x={-carLength/2} y={-carWidth/2} width={carLength} height={carWidth} rx="0.8" ry="0.6"
        fill={bodyColor} stroke={isAtImpact ? "#EF4444" : darkColor} strokeWidth={isAtImpact ? "0.4" : "0.15"}
        filter={state.braking || isAtImpact ? "url(#glow)" : undefined} />
      <path d={`M ${carLength/2 - 0.3} ${-carWidth/2 + 0.15} L ${carLength/2 - 0.3} ${carWidth/2 - 0.15} L ${carLength/2 - 1.8} ${carWidth/2 - 0.3} L ${carLength/2 - 1.8} ${-carWidth/2 + 0.3} Z`}
        fill={highlightColor} opacity="0.3" />
      <rect x={carLength/2 - 2.2} y={-carWidth/2 + 0.25} width="1.4" height={carWidth - 0.5} rx="0.15" fill="#0F172A" stroke="#1E3A5F" strokeWidth="0.08" />
      <rect x={-carLength/2 + 1.5} y={-carWidth/2 + 0.3} width={carLength - 3.7} height={carWidth - 0.6} rx="0.1" fill="#0F172A" opacity="0.7" />
      <rect x={-carLength/2 + 0.4} y={-carWidth/2 + 0.35} width="1.1" height={carWidth - 0.7} rx="0.12" fill="#0F172A" stroke="#1E3A5F" strokeWidth="0.06" />
      <ellipse cx={carLength/2 - 2} cy={-carWidth/2 - 0.3} rx="0.25" ry="0.15" fill={bodyColor} stroke={darkColor} strokeWidth="0.05" />
      <ellipse cx={carLength/2 - 2} cy={carWidth/2 + 0.3} rx="0.25" ry="0.15" fill={bodyColor} stroke={darkColor} strokeWidth="0.05" />
      <rect x={carLength/2 - 0.15} y={-carWidth/2 + 0.25} width="0.15" height="0.5" rx="0.05" fill="#FEF9C3" opacity="0.95" />
      <rect x={carLength/2 - 0.15} y={carWidth/2 - 0.75} width="0.15" height="0.5" rx="0.05" fill="#FEF9C3" opacity="0.95" />
      <rect x={-carLength/2} y={-carWidth/2 + 0.2} width="0.15" height="0.6" rx="0.05" fill={state.braking ? "#FF0000" : "#991B1B"} filter={state.braking ? "url(#glow)" : undefined} />
      <rect x={-carLength/2} y={carWidth/2 - 0.8} width="0.15" height="0.6" rx="0.05" fill={state.braking ? "#FF0000" : "#991B1B"} filter={state.braking ? "url(#glow)" : undefined} />
      <rect x={carLength/2 - 1.3} y={-carWidth/2 - 0.1} width="0.9" height="0.35" rx="0.1" fill="#1F2937" stroke="#374151" strokeWidth="0.05" />
      <rect x={carLength/2 - 1.3} y={carWidth/2 - 0.25} width="0.9" height="0.35" rx="0.1" fill="#1F2937" stroke="#374151" strokeWidth="0.05" />
      <rect x={-carLength/2 + 0.4} y={-carWidth/2 - 0.1} width="0.9" height="0.35" rx="0.1" fill="#1F2937" stroke="#374151" strokeWidth="0.05" />
      <rect x={-carLength/2 + 0.4} y={carWidth/2 - 0.25} width="0.9" height="0.35" rx="0.1" fill="#1F2937" stroke="#374151" strokeWidth="0.05" />
      <circle cx="0" cy="0" r="1" fill={darkColor} stroke="#FFFFFF" strokeWidth="0.1" />
      <text x="0" y="0.4" fontSize="1.2" fill="#FFFFFF" textAnchor="middle" fontFamily="monospace" fontWeight="bold">
        {state.id}
      </text>
      {isAtImpact && (
        <>
          <motion.circle cx={state.id === "A" ? carLength/2 : -carLength/2} cy="0" r="0.8" fill="none" stroke="#EF4444" strokeWidth="0.2"
            initial={{ scale: 0.5, opacity: 1 }} animate={{ scale: 1.5, opacity: 0 }} transition={{ duration: 0.5, repeat: Infinity }} />
          <circle cx={state.id === "A" ? carLength/2 : -carLength/2} cy="0" r="0.4" fill="#EF4444" opacity="0.8" />
        </>
      )}
    </motion.g>
  );
}

// Trajectories Component
function Trajectories({ vehicleA, vehicleB, currentTime }: { vehicleA: AccidentSceneData["vehicleA"]; vehicleB: AccidentSceneData["vehicleB"]; currentTime: number }) {
  const createPathFromTrajectory = (trajectory: TrajectoryPoint[]): string => {
    if (trajectory.length === 0) return "";
    const maxTime = trajectory[trajectory.length - 1].time;
    const currentMaxTime = (currentTime / 100) * maxTime;
    const visiblePoints = trajectory.filter(p => p.time <= currentMaxTime);
    if (visiblePoints.length === 0) return "";
    return visiblePoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  };

  return (
    <g className="trajectories">
      <path d={createPathFromTrajectory(vehicleA.trajectory)} fill="none" stroke="#3B82F6" strokeWidth="0.4" strokeDasharray="1,0.5" opacity="0.6" markerEnd="url(#arrowBlue)" />
      <path d={createPathFromTrajectory(vehicleB.trajectory)} fill="none" stroke="#F97316" strokeWidth="0.4" strokeDasharray="1,0.5" opacity="0.6" markerEnd="url(#arrowOrange)" />
    </g>
  );
}

// Brake Marks Component
function BrakeMarks({ vehicleA, vehicleB, currentTime, impact }: { vehicleA: AccidentSceneData["vehicleA"]; vehicleB: AccidentSceneData["vehicleB"]; currentTime: number; impact: AccidentSceneData["impact"] }) {
  const maxTime = vehicleA.trajectory[vehicleA.trajectory.length - 1]?.time || 1;
  const currentTimeNorm = (currentTime / 100) * maxTime;

  const getBrakeMarkPath = (trajectory: TrajectoryPoint[], brakeStartTime: number): string => {
    if (currentTimeNorm < brakeStartTime) return "";
    const brakePoints = trajectory.filter(p => p.time >= brakeStartTime && p.time <= currentTimeNorm);
    if (brakePoints.length < 2) return "";
    return brakePoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  };

  return (
    <g className="brake-marks">
      <path d={getBrakeMarkPath(vehicleA.trajectory, vehicleA.brakeStartTime)} fill="none" stroke="#1a1a1a" strokeWidth="1.2" opacity="0.7" transform="translate(0, -0.6)" />
      <path d={getBrakeMarkPath(vehicleA.trajectory, vehicleA.brakeStartTime)} fill="none" stroke="#1a1a1a" strokeWidth="1.2" opacity="0.7" transform="translate(0, 0.6)" />
      <path d={getBrakeMarkPath(vehicleB.trajectory, vehicleB.brakeStartTime)} fill="none" stroke="#1a1a1a" strokeWidth="1.2" opacity="0.7" transform="translate(0, -0.6)" />
      <path d={getBrakeMarkPath(vehicleB.trajectory, vehicleB.brakeStartTime)} fill="none" stroke="#1a1a1a" strokeWidth="1.2" opacity="0.7" transform="translate(0, 0.6)" />
    </g>
  );
}

// Impact Point Component
function ImpactPoint({ x, y, angle }: { x: number; y: number; angle: number }) {
  return (
    <g transform={`translate(${x}, ${y})`}>
      <motion.circle r="3" fill="none" stroke="#EF4444" strokeWidth="0.3"
        initial={{ r: 0, opacity: 1 }} animate={{ r: 8, opacity: 0 }} transition={{ duration: 1.5, repeat: Infinity }} />
      <motion.circle r="3" fill="none" stroke="#EF4444" strokeWidth="0.2"
        initial={{ r: 0, opacity: 0.7 }} animate={{ r: 6, opacity: 0 }} transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }} />
      <circle r="1.5" fill="#EF4444" filter="url(#impactGlow)" />
      <circle r="0.8" fill="#FFFFFF" />
      <line x1="0" y1="0" x2={Math.cos((angle * Math.PI) / 180) * 5} y2={Math.sin((angle * Math.PI) / 180) * 5} stroke="#EF4444" strokeWidth="0.3" strokeDasharray="0.5,0.5" />
      <text x="0" y="-4" fontSize="2.5" fill="#EF4444" textAnchor="middle" fontFamily="monospace">⚠</text>
    </g>
  );
}

// Measurements Overlay Component
function MeasurementsOverlay({ data, currentTime, vehicleA, vehicleB, showSpeedLabels = true }: { data: AccidentSceneData; currentTime: number; vehicleA: VehicleState; vehicleB: VehicleState; showSpeedLabels?: boolean }) {
  const distance = Math.sqrt(Math.pow(vehicleA.x - vehicleB.x, 2) + Math.pow(vehicleA.y - vehicleB.y, 2));
  const midX = (vehicleA.x + vehicleB.x) / 2;
  const midY = (vehicleA.y + vehicleB.y) / 2;
  const labelOffsetA = vehicleA.y < 0 ? -8 : 8;
  const labelOffsetB = vehicleB.y >= 0 ? 10 : -10;

  return (
    <g className="measurements" opacity="0.9">
      {distance > 10 && (
        <>
          <line x1={vehicleA.x} y1={vehicleA.y} x2={vehicleB.x} y2={vehicleB.y} stroke="#C2E94B" strokeWidth="0.2" strokeDasharray="1,0.5" />
          <rect x={midX - 6} y={midY - 2.5} width="12" height="4" fill="#0d110d" opacity="0.9" rx="0.5" />
          <text x={midX} y={midY + 0.8} fontSize="2.5" fill="#C2E94B" textAnchor="middle" fontFamily="monospace" fontWeight="bold">
            {distance.toFixed(1)}m
          </text>
        </>
      )}
      {showSpeedLabels && (
        <>
          <g transform={`translate(${vehicleA.x}, ${vehicleA.y + labelOffsetA})`}>
            <rect x="-7" y="-2.5" width="14" height="4.5" fill="#0d110d" opacity="0.9" rx="0.5" stroke={vehicleA.color} strokeWidth="0.15" />
            <text x="0" y="1" fontSize="2.8" fill={vehicleA.color} textAnchor="middle" fontFamily="monospace" fontWeight="bold">
              {vehicleA.speed.toFixed(0)} km/h
            </text>
          </g>
          <g transform={`translate(${vehicleB.x}, ${vehicleB.y + labelOffsetB})`}>
            <rect x="-7" y="-2.5" width="14" height="4.5" fill="#0d110d" opacity="0.9" rx="0.5" stroke={vehicleB.color} strokeWidth="0.15" />
            <text x="0" y="1" fontSize="2.8" fill={vehicleB.color} textAnchor="middle" fontFamily="monospace" fontWeight="bold">
              {vehicleB.speed.toFixed(0)} km/h
            </text>
          </g>
        </>
      )}
      {vehicleA.braking && (
        <g transform={`translate(${vehicleA.x - 12}, ${vehicleA.y + (vehicleA.y < 0 ? 3 : -3)})`}>
          <rect x="-8" y="-2" width="16" height="3.5" fill="#0d110d" opacity="0.85" rx="0.4" />
          <text x="0" y="0.8" fontSize="2.2" fill="#EF4444" textAnchor="middle" fontFamily="monospace">
            BRAKING: {data.vehicleA.brakeDistance.toFixed(1)}m
          </text>
        </g>
      )}
      {vehicleB.braking && (
        <g transform={`translate(${vehicleB.x + 12}, ${vehicleB.y + (vehicleB.y >= 0 ? 3 : -3)})`}>
          <rect x="-8" y="-2" width="16" height="3.5" fill="#0d110d" opacity="0.85" rx="0.4" />
          <text x="0" y="0.8" fontSize="2.2" fill="#EF4444" textAnchor="middle" fontFamily="monospace">
            BRAKING: {data.vehicleB.brakeDistance.toFixed(1)}m
          </text>
        </g>
      )}
    </g>
  );
}

export default AccidentScene2D;

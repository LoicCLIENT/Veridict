"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import TimelineEvent, { TimelineEventData } from "./TimelineEvent";
import { AccidentScene2D, AccidentSceneData, mockSceneDataCaso1 } from "../reconstruction";
import { Play, Pause, SkipBack, SkipForward, Clock, Maximize2, Minimize2 } from "lucide-react";

interface TimelineProps {
  events: TimelineEventData[];
  sceneData?: AccidentSceneData;
  currentTime?: number;
  onTimeChange?: (time: number) => void;
  autoPlay?: boolean;
  playbackSpeed?: number;
  showVisualization?: boolean;
}

export default function Timeline({
  events,
  sceneData = mockSceneDataCaso1,
  currentTime = 0,
  onTimeChange,
  autoPlay = false,
  playbackSpeed: initialSpeed = 1,
  showVisualization = true,
}: TimelineProps) {
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [internalTime, setInternalTime] = useState(currentTime);
  const [isExpanded, setIsExpanded] = useState(false);
  const [speed, setSpeed] = useState(initialSpeed);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isExternalUpdate = useRef(false);

  // Ordenar eventos por timestamp
  const sortedEvents = [...events].sort((a, b) => a.timestamp - b.timestamp);

  // Calcular rango de tiempo
  const minTime = Math.min(...events.map((e) => e.timestamp), 0);
  const maxTime = Math.max(...events.map((e) => e.timestamp), 0);
  const duration = maxTime - minTime;

  // Convertir tiempo interno a porcentaje para el AccidentScene2D
  const timePercentage = duration > 0 ? ((internalTime - minTime) / duration) * 100 : 0;

  // Encontrar evento activo actual
  const activeEventIndex = sortedEvents.findIndex(
    (event, index) => {
      const nextEvent = sortedEvents[index + 1];
      return (
        internalTime >= event.timestamp &&
        (!nextEvent || internalTime < nextEvent.timestamp)
      );
    }
  );

  // Manejar playback
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setInternalTime((prev) => {
          const next = prev + 0.1 * speed;
          if (next >= maxTime) {
            setIsPlaying(false);
            return maxTime;
          }
          return next;
        });
      }, 100);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, speed, maxTime]);

  // Sincronizar con tiempo externo
  useEffect(() => {
    if (currentTime !== undefined && currentTime !== internalTime) {
      isExternalUpdate.current = true;
      setInternalTime(currentTime);
    }
  }, [currentTime]);

  // Notificar cambios de tiempo (solo si el cambio fue interno)
  useEffect(() => {
    if (isExternalUpdate.current) {
      isExternalUpdate.current = false;
      return;
    }
    onTimeChange?.(internalTime);
  }, [internalTime]);

  const handleEventClick = (event: TimelineEventData) => {
    setInternalTime(event.timestamp);
    setIsPlaying(false);
  };

  const skipToEvent = (direction: "prev" | "next") => {
    const currentIndex = activeEventIndex;
    if (direction === "prev" && currentIndex > 0) {
      setInternalTime(sortedEvents[currentIndex - 1].timestamp);
    } else if (direction === "next" && currentIndex < sortedEvents.length - 1) {
      setInternalTime(sortedEvents[currentIndex + 1].timestamp);
    }
    setIsPlaying(false);
  };

  const resetPlayback = () => {
    setInternalTime(minTime);
    setIsPlaying(false);
  };

  const formatTime = (seconds: number) => {
    const sign = seconds < 0 ? "-" : "+";
    const abs = Math.abs(seconds);
    return `T${sign}${abs.toFixed(1)}s`;
  };

  return (
    <div className="flex flex-col h-full">
      {/* Visualización 2D del accidente - Larger visualization */}
      {showVisualization && (
        <div className={`flex-shrink-0 mb-4 transition-all duration-300 ${isExpanded ? "h-[450px]" : "h-72"}`}>
          <div className="relative h-full rounded-lg overflow-hidden border border-veridict-green-700">
            <AccidentScene2D
              data={sceneData}
              currentTime={timePercentage}
              showMeasurements={true}
              showTrajectories={true}
              showGrid={true}
              compact={!isExpanded}
            />

            {/* Botón expandir/contraer */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="absolute top-2 right-2 p-1.5 rounded bg-veridict-green-800/80 hover:bg-veridict-green-700 text-veridict-gray hover:text-veridict-white transition-colors z-20"
            >
              {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            </button>
          </div>
        </div>
      )}

      {/* Header con controles de reproducción */}
      <div className="flex-shrink-0 border-b border-veridict-green-700 pb-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-veridict-white flex items-center gap-2">
            <Clock size={16} className="text-veridict-lime" />
            Accident Timeline
          </h3>
          <div className="flex items-center gap-3">
            <span className="text-lg font-mono text-veridict-lime">
              {formatTime(internalTime)}
            </span>
            {activeEventIndex >= 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-veridict-green-700 text-veridict-gray">
                Event {activeEventIndex + 1}/{sortedEvents.length}
              </span>
            )}
          </div>
        </div>

        {/* Controles de reproducción */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            {/* Reset button */}
            <button
              onClick={resetPlayback}
              className="p-2 rounded-md hover:bg-veridict-green-700 text-veridict-gray hover:text-veridict-white transition-colors"
              title="Reset"
            >
              <SkipBack size={16} />
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className={`p-2.5 rounded-md transition-colors ${
                isPlaying
                  ? "bg-veridict-error/20 hover:bg-veridict-error/30 text-veridict-error"
                  : "bg-veridict-lime/10 hover:bg-veridict-lime/20 text-veridict-lime"
              }`}
            >
              {isPlaying ? <Pause size={18} /> : <Play size={18} />}
            </button>

            <button
              onClick={() => skipToEvent("next")}
              className="p-2 rounded-md hover:bg-veridict-green-700 text-veridict-gray hover:text-veridict-white transition-colors"
              disabled={activeEventIndex >= sortedEvents.length - 1}
              title="Next event"
            >
              <SkipForward size={16} />
            </button>
          </div>

          {/* Slider de tiempo */}
          <div className="flex-1 relative">
            {/* Track background con gradiente de progreso */}
            <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-2 rounded-full bg-veridict-green-700 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-veridict-lime/40 to-veridict-lime"
                style={{ width: `${((internalTime - minTime) / duration) * 100}%` }}
              />
            </div>

            <input
              type="range"
              min={minTime}
              max={maxTime}
              step={0.05}
              value={internalTime}
              onChange={(e) => {
                setInternalTime(parseFloat(e.target.value));
                setIsPlaying(false);
              }}
              className="relative w-full h-2 bg-transparent rounded-full appearance-none cursor-pointer z-10
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-veridict-lime
                [&::-webkit-slider-thumb]:shadow-[0_0_8px_rgba(194,233,75,0.5)]
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:transition-transform
                [&::-webkit-slider-thumb]:hover:scale-125
                [&::-moz-range-thumb]:w-4
                [&::-moz-range-thumb]:h-4
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:bg-veridict-lime
                [&::-moz-range-thumb]:border-0
                [&::-moz-range-thumb]:cursor-pointer"
            />

            {/* Marcadores de eventos en el slider */}
            <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-2 pointer-events-none">
              {sortedEvents.map((event, idx) => {
                const position = ((event.timestamp - minTime) / duration) * 100;
                const isActive = idx === activeEventIndex;
                return (
                  <motion.div
                    key={event.id}
                    className={`
                      absolute top-1/2 -translate-y-1/2 rounded-full transition-all
                      ${event.isHighlight
                        ? "w-2.5 h-2.5 bg-veridict-error shadow-[0_0_6px_rgba(233,75,75,0.6)]"
                        : isActive
                        ? "w-2 h-2 bg-veridict-lime shadow-[0_0_4px_rgba(194,233,75,0.5)]"
                        : "w-1.5 h-3 bg-veridict-lime/50"
                      }
                    `}
                    style={{ left: `${position}%`, marginLeft: "-3px" }}
                    animate={isActive ? { scale: [1, 1.2, 1] } : {}}
                    transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
                  />
                );
              })}
            </div>
          </div>

          <span className="text-xs text-veridict-gray font-mono min-w-[50px] text-right">
            {formatTime(maxTime)}
          </span>
        </div>

        {/* Speed controls */}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-xs text-veridict-gray">Speed:</span>
          {[0.5, 1, 2, 4].map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={`text-xs px-2 py-0.5 rounded transition-colors ${
                speed === s
                  ? "bg-veridict-lime/20 text-veridict-lime"
                  : "bg-veridict-green-700 text-veridict-gray hover:text-veridict-white"
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* Lista de eventos */}
      <div className="flex-1 overflow-y-auto pr-2 -mr-2 space-y-1">
        <AnimatePresence>
          {sortedEvents.map((event, index) => (
            <TimelineEvent
              key={event.id}
              event={event}
              isActive={index === activeEventIndex}
              isLast={index === sortedEvents.length - 1}
              onClick={() => handleEventClick(event)}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

// Datos de ejemplo para testing - Sincronizados con mockSceneDataCaso1
export const mockTimelineEvents: TimelineEventData[] = [
  {
    id: "1",
    timestamp: 0,
    type: "inicio",
    title: "Initial situation",
    description: "Vehicle A traveling in right lane at 67 km/h. Vehicle B traveling in left lane at 55 km/h.",
    details: [
      { label: "Speed A", value: "67", unit: "km/h" },
      { label: "Speed B", value: "55", unit: "km/h" },
      { label: "Conditions", value: "Light rain" },
    ],
    vehiculo: "ambos",
  },
  {
    id: "2",
    timestamp: 1.5,
    type: "frenada",
    title: "Vehicle B starts lane change",
    description: "Vehicle B begins lane change maneuver to the right WITHOUT signaling.",
    details: [
      { label: "Violation", value: "Art. 72.1 RGC" },
      { label: "Signaling", value: "No" },
    ],
    vehiculo: "B",
  },
  {
    id: "3",
    timestamp: 2.5,
    type: "frenada",
    title: "Vehicle A detects danger",
    description: "Driver A detects lane invasion and initiates emergency braking.",
    details: [
      { label: "Reaction time", value: "0.8", unit: "s" },
      { label: "Deceleration", value: "-7.8", unit: "m/s²" },
      { label: "Friction coef.", value: "0.65", unit: "(wet)" },
    ],
    vehiculo: "A",
  },
  {
    id: "4",
    timestamp: 3.5,
    type: "impacto",
    title: "COLLISION POINT",
    description: "Side impact between both vehicles. Contact zone: front right A with left side B.",
    details: [
      { label: "Speed A", value: "45.2", unit: "km/h" },
      { label: "Speed B", value: "50.3", unit: "km/h" },
      { label: "Impact angle", value: "15", unit: "°" },
      { label: "ΔV Vehicle A", value: "22.1", unit: "km/h" },
      { label: "ΔV Vehicle B", value: "18.7", unit: "km/h" },
    ],
    vehiculo: "ambos",
    isHighlight: true,
  },
  {
    id: "5",
    timestamp: 4.2,
    type: "posicion_final",
    title: "Final positions",
    description: "Vehicles immobilized after post-impact displacement.",
    details: [
      { label: "Displacement A", value: "6.2", unit: "m" },
      { label: "Displacement B", value: "4.8", unit: "m" },
      { label: "Rotation A", value: "12", unit: "°" },
    ],
    vehiculo: "ambos",
  },
];

"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Car, Gauge, MapPin, Clock } from "lucide-react";

export type EventType =
  | "inicio"
  | "frenada"
  | "impacto"
  | "posicion_final"
  | "generico";

export interface TimelineEventData {
  id: string;
  timestamp: number; // segundos desde T=0
  type: EventType;
  title: string;
  description: string;
  details?: {
    label: string;
    value: string;
    unit?: string;
  }[];
  vehiculo?: "A" | "B" | "ambos";
  isHighlight?: boolean;
}

interface TimelineEventProps {
  event: TimelineEventData;
  isActive?: boolean;
  isLast?: boolean;
  onClick?: () => void;
}

const eventIcons: Record<EventType, typeof Car> = {
  inicio: Car,
  frenada: Gauge,
  impacto: AlertTriangle,
  posicion_final: MapPin,
  generico: Clock,
};

const eventColors: Record<EventType, string> = {
  inicio: "text-veridict-gray",
  frenada: "text-yellow-400",
  impacto: "text-veridict-error",
  posicion_final: "text-veridict-lime",
  generico: "text-veridict-gray",
};

const vehiculoColors: Record<string, string> = {
  A: "bg-blue-500/20 text-blue-400 border-blue-500/40",
  B: "bg-orange-500/20 text-orange-400 border-orange-500/40",
  ambos: "bg-purple-500/20 text-purple-400 border-purple-500/40",
};

export default function TimelineEvent({
  event,
  isActive = false,
  isLast = false,
  onClick,
}: TimelineEventProps) {
  const Icon = eventIcons[event.type];
  const iconColor = eventColors[event.type];

  const formatTimestamp = (seconds: number) => {
    if (seconds < 0) return `T${seconds.toFixed(1)}s`;
    return `T+${seconds.toFixed(1)}s`;
  };

  return (
    <motion.div
      className={`
        relative flex gap-4 cursor-pointer group
        ${onClick ? "hover:bg-veridict-green-800/30" : ""}
        p-3 -mx-3 rounded-lg transition-colors duration-200
      `}
      onClick={onClick}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={onClick ? { x: 4 } : undefined}
      transition={{ duration: 0.2 }}
    >
      {/* Línea vertical */}
      {!isLast && (
        <div
          className={`
            absolute left-[22px] top-[44px] w-0.5 h-[calc(100%-20px)]
            transition-colors duration-300
            ${isActive ? "bg-veridict-lime/60" : "bg-veridict-green-600"}
          `}
        />
      )}

      {/* Indicador/Icono */}
      <div className="relative flex-shrink-0">
        <motion.div
          className={`
            w-10 h-10 rounded-full flex items-center justify-center
            border-2 transition-all duration-300
            ${
              isActive
                ? "bg-veridict-lime/20 border-veridict-lime"
                : event.isHighlight
                ? `bg-veridict-green-700 border-veridict-lime/50`
                : "bg-veridict-green-800 border-veridict-green-600"
            }
          `}
          animate={
            isActive
              ? {
                  boxShadow: [
                    "0 0 0 0 rgba(194, 233, 75, 0.4)",
                    "0 0 0 8px rgba(194, 233, 75, 0)",
                  ],
                }
              : {}
          }
          transition={
            isActive
              ? { duration: 1.5, repeat: Infinity }
              : {}
          }
        >
          <Icon
            size={18}
            className={isActive ? "text-veridict-lime" : iconColor}
          />
        </motion.div>
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0 pt-1">
        {/* Header con timestamp */}
        <div className="flex items-center gap-3 mb-1">
          <span
            className={`
              text-xs font-mono px-2 py-0.5 rounded
              ${
                isActive
                  ? "bg-veridict-lime/20 text-veridict-lime"
                  : "bg-veridict-green-700 text-veridict-gray"
              }
            `}
          >
            {formatTimestamp(event.timestamp)}
          </span>

          {event.vehiculo && (
            <span
              className={`
                text-xs px-2 py-0.5 rounded border
                ${vehiculoColors[event.vehiculo]}
              `}
            >
              {event.vehiculo === "ambos"
                ? "Vehículos A + B"
                : `Vehículo ${event.vehiculo}`}
            </span>
          )}
        </div>

        {/* Título */}
        <h4
          className={`
            text-sm font-medium mb-1 transition-colors duration-200
            ${isActive ? "text-veridict-white" : "text-veridict-white/80"}
          `}
        >
          {event.title}
        </h4>

        {/* Descripción */}
        <p className="text-xs text-veridict-gray leading-relaxed mb-2">
          {event.description}
        </p>

        {/* Detalles técnicos */}
        {event.details && event.details.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {event.details.map((detail, index) => (
              <div
                key={index}
                className="flex items-center gap-1.5 text-xs bg-veridict-green-700/50 px-2 py-1 rounded"
              >
                <span className="text-veridict-gray">{detail.label}:</span>
                <span className="text-veridict-white font-mono">
                  {detail.value}
                  {detail.unit && (
                    <span className="text-veridict-gray ml-0.5">
                      {detail.unit}
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

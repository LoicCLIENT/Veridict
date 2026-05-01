"use client";

import { useAppStore } from "@/lib/store";
import type { Evento } from "@/lib/api";

interface CronologiaTimelineProps {
  eventos: Evento[];
}

export function CronologiaTimeline({ eventos }: CronologiaTimelineProps) {
  const { tiempoActual, setTiempoActual } = useAppStore();

  if (eventos.length === 0) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        No hay eventos en la cronologia
      </div>
    );
  }

  return (
    <div className="p-4">
      <h3 className="font-semibold mb-4">Cronologia del Accidente</h3>
      <div className="space-y-4">
        {eventos.map((evento, index) => (
          <div
            key={index}
            className={`relative pl-6 pb-4 border-l-2 cursor-pointer transition ${
              tiempoActual === evento.timestamp
                ? "border-primary"
                : "border-border hover:border-primary/50"
            }`}
            onClick={() => setTiempoActual(evento.timestamp)}
          >
            <div
              className={`absolute -left-2 w-4 h-4 rounded-full ${
                tiempoActual === evento.timestamp
                  ? "bg-primary"
                  : "bg-secondary"
              }`}
            />
            <div className="text-xs text-muted-foreground mb-1">
              T+{evento.timestamp}s
            </div>
            <p className="text-sm">{evento.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

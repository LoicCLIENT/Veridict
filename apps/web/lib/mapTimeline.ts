import type { Evento } from "@veridict/types";
import type { TimelineEventData } from "@/components/caso/TimelineEvent";

const KEYWORDS: Array<{ re: RegExp; type: TimelineEventData["type"]; vehiculo?: "A" | "B" | "ambos" }> = [
  { re: /impacto|colisi[oó]n|choque/i, type: "impacto", vehiculo: "ambos" },
  { re: /frena/i, type: "frenada" },
  { re: /posici[oó]n final|detiene|reposo/i, type: "posicion_final" },
  { re: /inicia|comienza|circula/i, type: "inicio" },
];

function classify(descripcion: string): { type: TimelineEventData["type"]; vehiculo?: "A" | "B" | "ambos" } {
  for (const k of KEYWORDS) {
    if (k.re.test(descripcion)) return { type: k.type, vehiculo: k.vehiculo };
  }
  if (/veh[ií]culo\s*a\b/i.test(descripcion)) return { type: "generico", vehiculo: "A" };
  if (/veh[ií]culo\s*b\b/i.test(descripcion)) return { type: "generico", vehiculo: "B" };
  return { type: "generico" };
}

export function mapEventosToTimeline(eventos: Evento[]): TimelineEventData[] {
  return eventos.map((e, i) => {
    const c = classify(e.descripcion);
    const isHighlight = c.type === "impacto";
    return {
      id: `evt-${i}`,
      timestamp: e.timestamp,
      type: c.type,
      title: titleFor(c.type),
      description: e.descripcion,
      vehiculo: c.vehiculo,
      isHighlight,
      details: e.posicion
        ? [
            { label: "Lat", value: e.posicion.lat.toFixed(5) },
            { label: "Lon", value: e.posicion.lon.toFixed(5) },
          ]
        : undefined,
    };
  });
}

function titleFor(type: TimelineEventData["type"]): string {
  switch (type) {
    case "inicio":
      return "Inicio";
    case "frenada":
      return "Frenada";
    case "impacto":
      return "Impacto";
    case "posicion_final":
      return "Posición final";
    default:
      return "Evento";
  }
}

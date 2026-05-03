"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CheckCircle2, Loader2, Hourglass, FileText, Sparkles, ChevronDown, ChevronRight } from "lucide-react";
import type { RazonamientoOrquestador } from "@veridict/types";

interface Props {
  data: RazonamientoOrquestador;
}

interface SeccionDef {
  key: string;
  emoji: string;
  titulo: string;
  descripcion: string;
  /** Tools that fill this section. */
  tools: string[];
}

const SECCIONES: SeccionDef[] = [
  {
    key: "lugar",
    emoji: "🛣️",
    titulo: "Location and road",
    descripcion: "Geometry, signs and layout of the accident point",
    tools: ["consultar_escena"],
  },
  {
    key: "meteo",
    emoji: "🌤️",
    titulo: "Weather conditions",
    descripcion: "Weather, visibility and road condition on the day of the accident",
    tools: ["consultar_meteo"],
  },
  {
    key: "vehiculos",
    emoji: "🚗",
    titulo: "Vehicles involved",
    descripcion: "Technical data sheets, mass, safety systems",
    tools: ["consultar_ficha_tecnica"],
  },
  {
    key: "fotos",
    emoji: "📷",
    titulo: "Graphic material",
    descripcion: "Photos from the file analyzed by vision",
    tools: ["buscar_foto_perito", "listar_biblioteca_fotos", "analizar_imagen_dano"],
  },
  {
    key: "fisica",
    emoji: "📐",
    titulo: "Physical calculations",
    descripcion: "Speeds, stopping distances, kinetic energy (PhysicsAgent)",
    tools: ["calcular_fisica", "simular_fisica"],
  },
  {
    key: "simulacion",
    emoji: "🎬",
    titulo: "Visual reconstruction",
    descripcion: "SVG sketch of the impact based on PhysicsAgent calculations",
    tools: ["generar_frame_simulacion", "obtener_frame_simulacion"],
  },
  {
    key: "bio",
    emoji: "🩺",
    titulo: "Biomechanical analysis",
    descripcion: "Compatibility of injuries with calculated dynamics",
    tools: ["analizar_biomecanica"],
  },
  {
    key: "legal",
    emoji: "📜",
    titulo: "Legal framework",
    descripcion: "BOE articles, jurisprudence and applicable bibliography",
    tools: ["consultar_legal"],
  },
  {
    key: "atestado",
    emoji: "🔍",
    titulo: "Police report audit",
    descripcion: "Compares police report statements with physical evidence",
    tools: ["analizar_conformidad_atestado", "verificar_atestado"],
  },
];

const TOOL_FRIENDLY: Record<string, string> = {
  consultar_escena: "Scene Team",
  consultar_meteo: "Meteorology Team",
  consultar_ficha_tecnica: "Vehicles Team",
  buscar_foto_perito: "Photo Archive",
  listar_biblioteca_fotos: "Photo Archive",
  analizar_imagen_dano: "Computer Vision Team",
  calcular_fisica: "Physics Calculations Team (PhysicsAgent)",
  simular_fisica: "Physics Calculations Team (PhysicsAgent)",
  generar_frame_simulacion: "Visual Reconstruction Team (SimulationAgent)",
  obtener_frame_simulacion: "Visual Reconstruction Team (SimulationAgent)",
  analizar_biomecanica: "Medical-Biomechanical Team",
  consultar_legal: "Legal Team",
  analizar_conformidad_atestado: "Police Report Audit",
  verificar_atestado: "Police Report Audit",
};

type Estado = "pendiente" | "trabajando" | "listo";

interface SeccionEstado {
  estado: Estado;
  resumen?: string | null;
  toolEnUso?: string | null;
}

function detectarEstadoSeccion(
  seccion: SeccionDef,
  data: RazonamientoOrquestador
): SeccionEstado {
  // Has any tool in this section already responded?
  let resumen: string | null = null;
  let listo = false;
  for (const turno of data.turnos) {
    for (const tc of turno.tools_pedidas) {
      if (seccion.tools.includes(tc.tool)) {
        if (tc.respuesta_resumen || tc.respuesta_completa) {
          listo = true;
          if (!resumen && tc.respuesta_resumen) resumen = tc.respuesta_resumen;
        }
      }
    }
  }
  if (listo) return { estado: "listo", resumen };

  // Is the orchestrator currently consulting a tool in this section?
  if (data.estado === "dispatch" && data.mensaje) {
    for (const tool of seccion.tools) {
      if (data.mensaje.includes(tool)) {
        return { estado: "trabajando", toolEnUso: tool };
      }
    }
  }
  // Has the tool been requested but not responded yet?
  for (const turno of data.turnos) {
    for (const tc of turno.tools_pedidas) {
      if (seccion.tools.includes(tc.tool) && !tc.respuesta_completa && !tc.respuesta_resumen) {
        return { estado: "trabajando", toolEnUso: tc.tool };
      }
    }
  }
  return { estado: "pendiente" };
}

interface RespuestaPreguntaBorrador {
  pregunta_id?: string;
  pregunta?: string;
  respuesta?: string;
  confianza?: number;
}

function extraerRespuestas(borrador: Record<string, unknown> | null | undefined): RespuestaPreguntaBorrador[] {
  if (!borrador) return [];
  const raw = borrador.respuestas;
  if (!Array.isArray(raw)) return [];
  return raw.filter((r): r is RespuestaPreguntaBorrador => typeof r === "object" && r !== null);
}

export function BorradorEnVivo({ data }: Props) {
  const seccionesConEstado = useMemo(
    () => SECCIONES.map((s) => ({ def: s, estado: detectarEstadoSeccion(s, data) })),
    [data]
  );
  const totalListas = seccionesConEstado.filter((s) => s.estado.estado === "listo").length;
  const respuestas = extraerRespuestas(data.informe_borrador);
  const conclusionesListas = respuestas.length > 0;

  return (
    <Card className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/20">
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 rounded-lg">
              <FileText className="w-5 h-5 text-emerald-300" />
            </div>
            <div>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                The report is being assembled
                <Sparkles className="w-4 h-4 text-emerald-300" />
              </CardTitle>
              <CardDescription>
                Watch live how sections are filled as each team delivers their part.
              </CardDescription>
            </div>
          </div>
          <div className="text-right text-xs text-zinc-300">
            <div className="font-bold text-emerald-300 text-lg">
              {totalListas}/{SECCIONES.length}
            </div>
            <div>sections ready</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {seccionesConEstado.map(({ def, estado }) => (
          <SeccionRow key={def.key} def={def} estado={estado} />
        ))}

        {/* Conclusions — only appear when informe_borrador arrives */}
        <ConclusionesBorrador respuestas={respuestas} listas={conclusionesListas} />
      </CardContent>
    </Card>
  );
}

function SeccionRow({ def, estado }: { def: SeccionDef; estado: SeccionEstado }) {
  const colorBorder =
    estado.estado === "listo"
      ? "border-emerald-500/30 bg-emerald-500/5"
      : estado.estado === "trabajando"
      ? "border-blue-500/40 bg-blue-500/5"
      : "border-zinc-800 bg-zinc-900/30";

  const equipo = estado.toolEnUso ? TOOL_FRIENDLY[estado.toolEnUso] : null;

  return (
    <div className={`flex items-start gap-3 rounded-lg border px-3 py-2 ${colorBorder}`}>
      <div className="text-2xl leading-none mt-0.5">{def.emoji}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-white text-sm">{def.titulo}</span>
          {estado.estado === "listo" && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-emerald-300">
              <CheckCircle2 className="w-3 h-3" />
              ready
            </span>
          )}
          {estado.estado === "trabajando" && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-blue-300">
              <Loader2 className="w-3 h-3 animate-spin" />
              live
            </span>
          )}
          {estado.estado === "pendiente" && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-zinc-500">
              <Hourglass className="w-3 h-3" />
              pending
            </span>
          )}
        </div>
        <div className="text-xs text-zinc-400 mt-0.5">
          {estado.estado === "listo" && estado.resumen
            ? estado.resumen
            : estado.estado === "trabajando"
            ? equipo
              ? `Veridict-Expert is currently requesting the report from ${equipo}…`
              : "Request in progress to a specialist team…"
            : def.descripcion}
        </div>
      </div>
    </div>
  );
}

function ConclusionesBorrador({
  respuestas,
  listas,
}: {
  respuestas: RespuestaPreguntaBorrador[];
  listas: boolean;
}) {
  const [abierto, setAbierto] = useState(false);
  return (
    <div
      className={`rounded-lg border px-3 py-3 mt-3 ${
        listas
          ? "border-purple-500/30 bg-purple-500/5"
          : "border-zinc-800 bg-zinc-900/30"
      }`}
    >
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        disabled={!listas}
        className="flex items-center gap-2 w-full text-left disabled:cursor-default"
      >
        {listas ? (
          abierto ? (
            <ChevronDown className="w-4 h-4 text-purple-300" />
          ) : (
            <ChevronRight className="w-4 h-4 text-purple-300" />
          )
        ) : (
          <ChevronRight className="w-4 h-4 text-zinc-600" />
        )}
        <span className="text-xl leading-none">✍️</span>
        <span className="font-semibold text-white text-sm">
          Expert conclusions (C1, C2, C3…)
        </span>
        {listas ? (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-purple-300">
            <Sparkles className="w-3 h-3" />
            {respuestas.length} {respuestas.length === 1 ? "conclusion" : "conclusions"}
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-zinc-500">
            <Hourglass className="w-3 h-3" />
            waiting for team data
          </span>
        )}
      </button>
      {!listas ? (
        <div className="text-xs text-zinc-400 mt-2">
          When all teams have delivered, Veridict-Expert will start writing the
          answers to the assignment questions right here.
        </div>
      ) : abierto ? (
        <div className="space-y-3 mt-3">
          {respuestas.map((r, i) => (
            <ConclusionEstatica key={r.pregunta_id || i} respuesta={r} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

function ConclusionEstatica({ respuesta }: { respuesta: RespuestaPreguntaBorrador }) {
  const texto = respuesta.respuesta || "";
  return (
    <div className="rounded-md border border-purple-500/15 bg-zinc-950/40 px-3 py-2">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] font-semibold uppercase tracking-wide text-purple-300">
          {respuesta.pregunta_id || "C?"}
        </span>
        <span className="text-xs text-zinc-300">{respuesta.pregunta}</span>
      </div>
      <p className="text-sm text-zinc-100 leading-relaxed whitespace-pre-line">
        {texto}
      </p>
      {typeof respuesta.confianza === "number" && (
        <div className="text-[11px] text-zinc-500 mt-1">
          Confidence: {Math.round(respuesta.confianza * 100)}%
        </div>
      )}
    </div>
  );
}

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
  /** Tools que rellenan esta sección. */
  tools: string[];
}

const SECCIONES: SeccionDef[] = [
  {
    key: "lugar",
    emoji: "🛣️",
    titulo: "Lugar y carretera",
    descripcion: "Geometría, señales y trazado del punto del siniestro",
    tools: ["consultar_escena"],
  },
  {
    key: "meteo",
    emoji: "🌤️",
    titulo: "Condiciones meteorológicas",
    descripcion: "Tiempo, visibilidad y estado de la calzada el día del siniestro",
    tools: ["consultar_meteo"],
  },
  {
    key: "vehiculos",
    emoji: "🚗",
    titulo: "Vehículos implicados",
    descripcion: "Fichas técnicas, masa, sistemas de seguridad",
    tools: ["consultar_ficha_tecnica"],
  },
  {
    key: "fotos",
    emoji: "📷",
    titulo: "Material gráfico",
    descripcion: "Fotos del expediente analizadas por visión",
    tools: ["buscar_foto_perito", "listar_biblioteca_fotos", "analizar_imagen_dano"],
  },
  {
    key: "fisica",
    emoji: "📐",
    titulo: "Cálculos físicos",
    descripcion: "Velocidades, distancias de detención, energía cinética (PhysicsAgent)",
    tools: ["calcular_fisica", "simular_fisica"],
  },
  {
    key: "simulacion",
    emoji: "🎬",
    titulo: "Recreación visual",
    descripcion: "Croquis SVG del impacto a partir de los cálculos del PhysicsAgent",
    tools: ["generar_frame_simulacion", "obtener_frame_simulacion"],
  },
  {
    key: "bio",
    emoji: "🩺",
    titulo: "Análisis biomecánico",
    descripcion: "Compatibilidad de las lesiones con la dinámica calculada",
    tools: ["analizar_biomecanica"],
  },
  {
    key: "legal",
    emoji: "📜",
    titulo: "Marco normativo",
    descripcion: "Artículos del BOE, jurisprudencia y bibliografía aplicables",
    tools: ["consultar_legal"],
  },
  {
    key: "atestado",
    emoji: "🔍",
    titulo: "Auditoría del atestado",
    descripcion: "Confronta declaraciones del atestado con la evidencia física",
    tools: ["analizar_conformidad_atestado", "verificar_atestado"],
  },
];

const TOOL_FRIENDLY: Record<string, string> = {
  consultar_escena: "Equipo de Escena",
  consultar_meteo: "Equipo Meteorología",
  consultar_ficha_tecnica: "Equipo Vehículos",
  buscar_foto_perito: "Archivo Fotográfico",
  listar_biblioteca_fotos: "Archivo Fotográfico",
  analizar_imagen_dano: "Equipo de Visión Computacional",
  calcular_fisica: "Equipo de Cálculos Físicos (PhysicsAgent)",
  simular_fisica: "Equipo de Cálculos Físicos (PhysicsAgent)",
  generar_frame_simulacion: "Equipo de Recreación Visual (SimulacionAgent)",
  obtener_frame_simulacion: "Equipo de Recreación Visual (SimulacionAgent)",
  analizar_biomecanica: "Equipo Médico-Biomecánico",
  consultar_legal: "Equipo Jurídico",
  analizar_conformidad_atestado: "Auditoría del Atestado",
  verificar_atestado: "Auditoría del Atestado",
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
  // ¿Algún tool de esta sección ha respondido ya?
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

  // ¿El orquestador está consultando ahora mismo un tool de esta sección?
  if (data.estado === "dispatch" && data.mensaje) {
    for (const tool of seccion.tools) {
      if (data.mensaje.includes(tool)) {
        return { estado: "trabajando", toolEnUso: tool };
      }
    }
  }
  // ¿El tool ha sido pedido pero aún no ha respondido?
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
                El informe se está montando
                <Sparkles className="w-4 h-4 text-emerald-300" />
              </CardTitle>
              <CardDescription>
                Mira en directo cómo se rellenan los apartados a medida que cada equipo entrega su parte.
              </CardDescription>
            </div>
          </div>
          <div className="text-right text-xs text-zinc-300">
            <div className="font-bold text-emerald-300 text-lg">
              {totalListas}/{SECCIONES.length}
            </div>
            <div>apartados listos</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {seccionesConEstado.map(({ def, estado }) => (
          <SeccionRow key={def.key} def={def} estado={estado} />
        ))}

        {/* Conclusiones — solo aparecen cuando llega el informe_borrador */}
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
              listo
            </span>
          )}
          {estado.estado === "trabajando" && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-blue-300">
              <Loader2 className="w-3 h-3 animate-spin" />
              en directo
            </span>
          )}
          {estado.estado === "pendiente" && (
            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-zinc-500">
              <Hourglass className="w-3 h-3" />
              pendiente
            </span>
          )}
        </div>
        <div className="text-xs text-zinc-400 mt-0.5">
          {estado.estado === "listo" && estado.resumen
            ? estado.resumen
            : estado.estado === "trabajando"
            ? equipo
              ? `Veridict-Perito está pidiendo ahora mismo el informe a ${equipo}…`
              : "Solicitud en curso a un equipo especialista…"
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
          Conclusiones del perito (C1, C2, C3…)
        </span>
        {listas ? (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-purple-300">
            <Sparkles className="w-3 h-3" />
            {respuestas.length} {respuestas.length === 1 ? "conclusión" : "conclusiones"}
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-wide text-zinc-500">
            <Hourglass className="w-3 h-3" />
            esperando datos de los equipos
          </span>
        )}
      </button>
      {!listas ? (
        <div className="text-xs text-zinc-400 mt-2">
          Cuando todos los equipos hayan entregado, Veridict-Perito empezará a escribir las
          respuestas a las preguntas del encargo aquí mismo.
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
          Confianza: {Math.round(respuesta.confianza * 100)}%
        </div>
      )}
    </div>
  );
}

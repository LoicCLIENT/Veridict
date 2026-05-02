"use client";

import type {
  InformePericial,
  Caso,
  RespuestaPregunta,
  FichaTecnicaVehiculo,
  FuenteNormativa,
} from "@veridict/types";
import { CalculoFisico } from "@veridict/types";

interface Props {
  informe: InformePericial;
  caso: Caso;
}

/**
 * Renderiza el informe pericial como un documento legible (estilo UNE-EN 16775),
 * con secciones numeradas y tipografía pericial. NO usa cards/tabs internas:
 * se lee de arriba abajo como si fuera el PDF firmable.
 */
export function InformeDocumento({ informe, caso }: Props) {
  const encargo = caso.encargo;
  const fechaStr = caso.fecha_accidente
    ? new Date(caso.fecha_accidente).toLocaleDateString("es-ES", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : "—";

  return (
    <article className="bg-zinc-950/40 border border-zinc-800 rounded-xl p-8 md:p-12 leading-relaxed text-zinc-200 font-serif">
      {/* Encabezado pericial */}
      <header className="border-b border-zinc-700 pb-6 mb-8">
        <p className="text-xs uppercase tracking-widest text-zinc-500 mb-2">
          Informe pericial UNE-EN 16775 — borrador asistido
        </p>
        <h1 className="text-2xl md:text-3xl font-bold text-white">
          Informe pericial sobre {tipoLabel(encargo?.tipo)}
        </h1>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 text-sm text-zinc-400">
          {encargo?.solicitante && (
            <div>
              <span className="text-zinc-500">Solicitante: </span>
              <span className="text-zinc-200">{encargo.solicitante}</span>
            </div>
          )}
          {encargo?.procedimiento && (
            <div>
              <span className="text-zinc-500">Procedimiento: </span>
              <span className="text-zinc-200">{encargo.procedimiento}</span>
            </div>
          )}
          {encargo?.parte && (
            <div>
              <span className="text-zinc-500">Parte: </span>
              <span className="text-zinc-200 capitalize">{encargo.parte}</span>
            </div>
          )}
          <div>
            <span className="text-zinc-500">Fecha del siniestro: </span>
            <span className="text-zinc-200">{fechaStr}</span>
          </div>
        </div>
      </header>

      {/* Sección 1 — Objeto del informe */}
      <Section number="1" title="Objeto del informe">
        <p>{informe.resumen_caso}</p>
        {encargo && encargo.preguntas.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-zinc-400 mb-2">
              Las cuestiones planteadas por el solicitante son:
            </p>
            <ol className="list-decimal pl-6 space-y-1 text-zinc-200 marker:text-zinc-500">
              {encargo.preguntas.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ol>
          </div>
        )}
      </Section>

      {/* Sección 2 — Antecedentes y hechos del atestado */}
      <Section number="2" title="Antecedentes y hechos del atestado">
        <DataGrid>
          <DataItem
            label="Tipo de colisión"
            value={caso.tipo_colision ? capitalize(caso.tipo_colision) : "—"}
          />
          <DataItem
            label="Atestado"
            value={
              caso.hechos_atestado?.numero_atestado
                ? `Nº ${caso.hechos_atestado.numero_atestado}` +
                  (caso.hechos_atestado.cuerpo_actuante
                    ? ` — ${capitalize(caso.hechos_atestado.cuerpo_actuante.replace("_", " "))}`
                    : "")
                : "—"
            }
          />
          <DataItem
            label="Huellas de frenada"
            value={
              caso.hechos_atestado?.hay_huellas_frenada == null
                ? "No consta"
                : caso.hechos_atestado.hay_huellas_frenada
                ? "Sí, observadas en calzada"
                : "No se observan"
            }
          />
          <DataItem
            label="Condiciones"
            value={
              [
                caso.hechos_atestado?.condiciones_meteorologicas,
                caso.hechos_atestado?.estado_calzada,
                caso.hechos_atestado?.visibilidad,
              ]
                .filter(Boolean)
                .join(" · ") || "—"
            }
          />
        </DataGrid>

        {(caso.hechos_atestado?.velocidades_declaradas?.length ?? 0) > 0 && (
          <div className="mt-4">
            <p className="text-sm text-zinc-400 mb-2">Velocidades registradas:</p>
            <ul className="space-y-1 text-sm">
              {caso.hechos_atestado!.velocidades_declaradas!.map((v, i) => (
                <li key={i} className="text-zinc-200">
                  Vehículo <span className="font-bold">{v.vehiculo_id}</span>:{" "}
                  <span className="font-mono">{v.valor_kmh} km/h</span>{" "}
                  <span className="text-zinc-500">
                    ({fuenteVelocidadLabel(v.fuente)})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {caso.hechos_atestado?.declaraciones && (
          <div className="mt-4">
            <p className="text-sm text-zinc-400 mb-2">Declaraciones recogidas:</p>
            <blockquote className="border-l-2 border-zinc-700 pl-4 italic text-zinc-300">
              {caso.hechos_atestado.declaraciones}
            </blockquote>
          </div>
        )}

        {(caso.lesiones?.length ?? 0) > 0 && (
          <div className="mt-4">
            <p className="text-sm text-zinc-400 mb-2">Lesiones:</p>
            <ul className="text-sm space-y-1 list-disc pl-5 text-zinc-200">
              {caso.lesiones!.map((l, i) => (
                <li key={i}>
                  <strong>{l.ocupante}</strong> (vehículo {l.vehiculo_id ?? "—"}):{" "}
                  {l.zona_corporal} — {capitalize(l.gravedad.replace("_", " "))}
                  {l.dias_baja ? `, ${l.dias_baja} días de baja` : ""}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Section>

      {/* Sección 3 — Vehículos implicados */}
      <Section number="3" title="Vehículos implicados">
        {informe.fichas_tecnicas.length === 0 ? (
          <p className="text-zinc-500">No se han identificado vehículos.</p>
        ) : (
          <div className="space-y-5">
            {informe.fichas_tecnicas.map((f) => (
              <FichaBloque key={f.vehiculo_id} ficha={f} />
            ))}
          </div>
        )}
      </Section>

      {/* Sección 4 — Análisis técnico */}
      {informe.calculos.length > 0 && (
        <Section number="4" title="Análisis técnico y cálculos">
          <p className="mb-4">
            A partir de los datos del atestado y de las fichas técnicas se han
            realizado los siguientes cálculos físicos deterministas:
          </p>
          <div className="space-y-3">
            {informe.calculos.map((c, i) => (
              <CalculoBloque key={i} calculo={c} />
            ))}
          </div>
        </Section>
      )}

      {/* Sección 5 — Marco normativo */}
      {informe.normativa_aplicable.length > 0 && (
        <Section number="5" title="Marco normativo aplicable">
          <div className="space-y-3">
            {informe.normativa_aplicable.map((n, i) => (
              <NormativaBloque key={i} fuente={n} />
            ))}
          </div>
        </Section>
      )}

      {/* Sección 6 — Conclusiones (respuestas a las preguntas) */}
      {informe.respuestas.length > 0 && (
        <Section number="6" title="Conclusiones periciales">
          <p className="mb-4 text-zinc-400 text-sm">
            Respuesta razonada a cada cuestión planteada en el encargo. Las
            citas remiten a los cálculos, normativa y datos del expediente.
          </p>
          <div className="space-y-6">
            {informe.respuestas.map((r) => (
              <RespuestaBloque key={r.pregunta_id} respuesta={r} />
            ))}
          </div>
        </Section>
      )}

      {/* Investigación de los agentes (tool calls) */}
      {informe.tool_calls && informe.tool_calls.length > 0 && (
        <Section number="6.1" title="Investigación realizada por los agentes especialistas">
          <p className="mb-3 text-sm text-zinc-400">
            El perito coordinador ha consultado a los siguientes agentes para llegar a las
            conclusiones anteriores. Cada agente tiene acceso a fuentes externas reales
            (OpenStreetMap, BOE, Mapillary, Open-Meteo, etc.).
          </p>
          <div className="space-y-2">
            {informe.tool_calls.map((tc) => (
              <div key={tc.id} className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/30">
                <div className="flex items-baseline justify-between gap-3">
                  <span className="text-sm font-bold text-blue-300">{tc.agente}</span>
                  {tc.duracion_ms != null && (
                    <span className="text-xs text-zinc-500">{tc.duracion_ms} ms</span>
                  )}
                </div>
                <p className="text-sm text-zinc-300 mt-0.5 italic">{tc.pregunta}</p>
                {tc.resultado_resumen && (
                  <p className="text-sm text-zinc-200 mt-1">→ {tc.resultado_resumen}</p>
                )}
                {tc.fuentes_consultadas.length > 0 && (
                  <p className="text-xs text-zinc-500 mt-1 font-sans">
                    Fuentes: {tc.fuentes_consultadas.join(" · ")}
                  </p>
                )}
                {tc.falta_info && (
                  <p className="text-xs text-amber-300 mt-1">
                    ⚠ {tc.falta_info}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Galería de imágenes recopiladas */}
      {informe.imagenes && informe.imagenes.length > 0 && (
        <Section number="6.2" title="Material gráfico recopilado">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {informe.imagenes.map((img, i) => (
              <a
                key={i}
                href={img.url ?? undefined}
                target="_blank"
                rel="noreferrer"
                className="block rounded-lg overflow-hidden border border-zinc-800 hover:border-zinc-600 transition-colors"
              >
                {img.thumb_url || img.url ? (
                  <img
                    src={img.thumb_url ?? img.url ?? undefined}
                    alt={img.descripcion ?? img.relevancia ?? "imagen"}
                    className="w-full h-32 object-cover"
                  />
                ) : (
                  <div className="w-full h-32 bg-zinc-900 flex items-center justify-center text-zinc-600 text-xs">
                    sin miniatura
                  </div>
                )}
                <div className="p-2 text-xs">
                  <p className="text-zinc-400 truncate">
                    {img.fuente}
                    {img.compass_angle != null ? ` · ${Math.round(img.compass_angle)}°` : ""}
                  </p>
                  {img.descripcion && (
                    <p className="text-zinc-300 line-clamp-2 mt-0.5">{img.descripcion}</p>
                  )}
                </div>
              </a>
            ))}
          </div>
        </Section>
      )}

      {/* Sección 7 — Bibliografía */}
      {informe.bibliografia.length > 0 && (
        <Section number="7" title="Bibliografía técnica consultada">
          <ol className="list-decimal pl-6 space-y-1 text-sm text-zinc-300 marker:text-zinc-500">
            {informe.bibliografia.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ol>
        </Section>
      )}

      {/* Pie */}
      <footer className="mt-12 pt-6 border-t border-zinc-700 text-xs text-zinc-500">
        <div className="flex justify-between flex-wrap gap-2">
          <span>
            Confianza global del borrador:{" "}
            <span className="text-zinc-200 font-mono">
              {Math.round(informe.confianza_global * 100)}%
            </span>
          </span>
          <span className="italic">
            Borrador asistido por Veridict AI. La calificación última corresponde
            al perito firmante.
          </span>
        </div>
      </footer>
    </article>
  );
}

// ─── Sub-componentes ────────────────────────────────────────────────────────

function Section({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-10">
      <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-baseline gap-3 border-b border-zinc-800 pb-2">
        <span className="text-zinc-500 font-mono text-base">{number}.</span>
        {title}
      </h2>
      <div className="text-zinc-200 text-[15px] leading-7">{children}</div>
    </section>
  );
}

function DataGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 text-sm">
      {children}
    </div>
  );
}

function DataItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-zinc-500">{label}: </span>
      <span className="text-zinc-200">{value}</span>
    </div>
  );
}

function FichaBloque({ ficha }: { ficha: FichaTecnicaVehiculo }) {
  return (
    <div>
      <h3 className="font-semibold text-white">
        Vehículo {ficha.vehiculo_id} — {ficha.marca} {ficha.modelo}
        {ficha.anio ? ` (${ficha.anio})` : ""}
      </h3>
      <div className="mt-1 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 text-sm text-zinc-300">
        {ficha.masa_kg != null && (
          <span>
            <span className="text-zinc-500">Masa: </span>
            {ficha.masa_kg} kg
          </span>
        )}
        {ficha.longitud_m != null && (
          <span>
            <span className="text-zinc-500">Longitud: </span>
            {ficha.longitud_m} m
          </span>
        )}
        {ficha.altura_parachoques_m && (
          <span>
            <span className="text-zinc-500">Altura parachoques: </span>
            {ficha.altura_parachoques_m[0]}–{ficha.altura_parachoques_m[1]} m
          </span>
        )}
        {ficha.altura_largueros_m != null && (
          <span>
            <span className="text-zinc-500">Largueros: </span>
            {ficha.altura_largueros_m} m
          </span>
        )}
      </div>
      {ficha.sistemas_seguridad.length > 0 && (
        <div className="mt-2 text-sm">
          <span className="text-zinc-500">Sistemas de seguridad: </span>
          <span className="text-zinc-300">
            {ficha.sistemas_seguridad.join("; ")}.
          </span>
        </div>
      )}
      {ficha.fuente && (
        <p className="mt-1 text-xs text-zinc-500 italic">Fuente: {ficha.fuente}</p>
      )}
    </div>
  );
}

function CalculoBloque({ calculo }: { calculo: CalculoFisico }) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-semibold text-white">{calculo.nombre}</h3>
        <span className="font-mono text-amber-300">
          {calculo.valor} <span className="text-xs text-zinc-400">{calculo.unidad}</span>
        </span>
      </div>
      <p className="text-xs text-zinc-500 font-mono mt-0.5">{calculo.formula}</p>
      <p className="text-sm text-zinc-300 mt-1">{calculo.justificacion}</p>
    </div>
  );
}

function NormativaBloque({ fuente }: { fuente: FuenteNormativa }) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="font-semibold text-purple-300">{fuente.referencia}</h3>
        {fuente.boe && (
          <span className="text-xs text-zinc-500 font-mono">{fuente.boe}</span>
        )}
      </div>
      <p className="text-sm text-zinc-300 mt-0.5">{fuente.titulo}</p>
      {fuente.extracto && (
        <blockquote className="mt-1 border-l-2 border-zinc-700 pl-3 text-sm italic text-zinc-400">
          «{fuente.extracto}»
        </blockquote>
      )}
    </div>
  );
}

function RespuestaBloque({ respuesta }: { respuesta: RespuestaPregunta }) {
  return (
    <div>
      <h3 className="font-semibold text-white">
        <span className="font-mono text-blue-400 mr-2">{respuesta.pregunta_id}.</span>
        {respuesta.pregunta}
      </h3>
      <p className="mt-2 text-zinc-200 whitespace-pre-line">{respuesta.respuesta}</p>
      {respuesta.citas.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {respuesta.citas.map((c, i) => (
            <span
              key={i}
              title={c.extracto ?? undefined}
              className="text-[11px] px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-300 border border-zinc-700 font-sans"
            >
              <span className="text-zinc-500 mr-1">{c.tipo}</span>
              {c.referencia}
            </span>
          ))}
        </div>
      )}
      <p className="mt-2 text-xs text-zinc-500 font-sans">
        Confianza: {Math.round(respuesta.confianza * 100)}%
      </p>
    </div>
  );
}

// ─── helpers ────────────────────────────────────────────────────────────────

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function tipoLabel(tipo?: string): string {
  switch (tipo) {
    case "responsabilidad_trafico":
      return "responsabilidad en accidente de tráfico";
    case "velocidad_impacto":
      return "determinación de velocidad de impacto";
    case "seguridad_pasiva":
      return "sistemas de seguridad pasiva";
    case "mecanica_fallo":
      return "fallo mecánico";
    case "atropello":
      return "atropello";
    case "cuantia_danos":
      return "cuantía y proporcionalidad de daños";
    default:
      return "siniestro de tráfico";
  }
}

function fuenteVelocidadLabel(f: string): string {
  switch (f) {
    case "declaracion_conductor":
      return "declaración del conductor";
    case "tacografo":
      return "tacógrafo";
    case "edr":
      return "EDR/centralita";
    case "testigo":
      return "testigo";
    default:
      return f;
  }
}

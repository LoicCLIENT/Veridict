"use client";

import { useState } from "react";
import type { CalculoFisico } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Calculator,
  ChevronDown,
  ChevronRight,
  Database,
  FileText,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Info,
  Gauge,
  Zap,
  Clock,
  Ruler,
  Weight,
  Target,
  ExternalLink,
  Microscope,
  Shield,
  TrendingUp,
} from "lucide-react";

interface CalculosFisicosProps {
  calculos: CalculoFisico[];
}

// Map category to icon and color
const categoryConfig: Record<string, { icon: typeof Calculator; color: string; bgColor: string }> = {
  velocidad: { icon: Gauge, color: "text-blue-400", bgColor: "bg-blue-500/10" },
  energia: { icon: Zap, color: "text-amber-400", bgColor: "bg-amber-500/10" },
  fuerza: { icon: TrendingUp, color: "text-red-400", bgColor: "bg-red-500/10" },
  tiempo: { icon: Clock, color: "text-purple-400", bgColor: "bg-purple-500/10" },
  distancia: { icon: Ruler, color: "text-green-400", bgColor: "bg-green-500/10" },
  masa: { icon: Weight, color: "text-orange-400", bgColor: "bg-orange-500/10" },
  otro: { icon: Calculator, color: "text-zinc-400", bgColor: "bg-zinc-500/10" },
};

// Map source type to readable English label
const sourceLabels: Record<string, string> = {
  atestado: "Police report",
  edr: "EDR (Event Data Recorder)",
  tacografo: "Digital tachograph",
  declaracion_conductor: "Driver statement",
  declaracion_testigo: "Witness statement",
  medicion_escena: "Scene measurement",
  foto_analisis: "Photo analysis",
  ficha_tecnica_dgt: "DGT vehicle datasheet",
  ficha_tecnica_fabricante: "Manufacturer datasheet",
  base_datos_crash3: "CRASH3 database",
  catalogo_europeo: "European Vehicle Catalog",
  calculo_derivado: "Derived calculation",
  estimacion_pericial: "Expert estimation",
  otro: "Other source",
};

const referenceTypeLabels: Record<string, { label: string; icon: typeof BookOpen }> = {
  normativa: { label: "Regulation", icon: Shield },
  paper: { label: "Scientific paper", icon: FileText },
  libro: { label: "Book/Manual", icon: BookOpen },
  manual: { label: "Technical manual", icon: BookOpen },
  base_datos: { label: "Database", icon: Database },
};

function ConfidenceBadge({ confidence }: { confidence?: number }) {
  if (confidence === undefined) return null;

  const pct = Math.round(confidence * 100);
  let color = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  let icon = <CheckCircle2 className="w-3 h-3" />;

  if (pct < 70) {
    color = "bg-amber-500/20 text-amber-300 border-amber-500/30";
    icon = <AlertTriangle className="w-3 h-3" />;
  } else if (pct < 85) {
    color = "bg-blue-500/20 text-blue-300 border-blue-500/30";
    icon = <Info className="w-3 h-3" />;
  }

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${color}`}>
      {icon}
      {pct}% confidence
    </span>
  );
}

function CalculoCard({ calculo, index }: { calculo: CalculoFisico; index: number }) {
  const [expanded, setExpanded] = useState(false);

  const category = calculo.categoria || "otro";
  const config = categoryConfig[category] || categoryConfig.otro;
  const CategoryIcon = config.icon;

  const hasDetails =
    (calculo.datos_entrada && calculo.datos_entrada.length > 0) ||
    (calculo.pasos && calculo.pasos.length > 0) ||
    (calculo.referencias && calculo.referencias.length > 0) ||
    calculo.metodo ||
    calculo.validaciones ||
    calculo.limitaciones;

  return (
    <Card className="bg-zinc-900/50 border-zinc-800 overflow-hidden">
      {/* Header - Always visible */}
      <CardHeader
        className={`pb-3 cursor-pointer transition-colors hover:bg-zinc-800/30 ${hasDetails ? "" : "cursor-default"}`}
        onClick={() => hasDetails && setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`p-2 rounded-lg ${config.bgColor} flex-shrink-0`}>
              <CategoryIcon className={`w-5 h-5 ${config.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <CardTitle className="text-base text-white">
                  {calculo.nombre}
                </CardTitle>
                <ConfidenceBadge confidence={calculo.confianza} />
              </div>
              {calculo.metodo && (
                <CardDescription className="text-xs text-zinc-400 mt-1">
                  Method: {calculo.metodo}
                </CardDescription>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="text-right">
              <div className="text-2xl font-bold text-white tabular-nums">
                {typeof calculo.valor === 'number' ? calculo.valor.toFixed(2) : calculo.valor}
                <span className="text-sm font-medium text-zinc-400 ml-1">{calculo.unidad}</span>
              </div>
              {calculo.sensibilidad && (
                <div className="text-[10px] text-zinc-500">{calculo.sensibilidad}</div>
              )}
            </div>
            {hasDetails && (
              <div className="text-zinc-500">
                {expanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
              </div>
            )}
          </div>
        </div>

        {/* Formula */}
        <div className="mt-3 p-2 bg-zinc-800/50 rounded-lg border border-zinc-700/50">
          <code className="text-xs text-zinc-300 font-mono">{calculo.formula}</code>
        </div>
      </CardHeader>

      {/* Expandable content */}
      {expanded && hasDetails && (
        <CardContent className="pt-0 space-y-4">
          {/* Justification */}
          <div className="p-3 bg-zinc-800/30 rounded-lg border border-zinc-700/30">
            <p className="text-sm text-zinc-300 leading-relaxed">
              {calculo.justificacion}
            </p>
          </div>

          {/* Input Data */}
          {calculo.datos_entrada && calculo.datos_entrada.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <Database className="w-3.5 h-3.5" />
                Input data used
              </h4>
              <div className="grid gap-2">
                {calculo.datos_entrada.map((dato, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 bg-zinc-800/40 rounded-lg border border-zinc-700/30"
                  >
                    <div className="flex-1">
                      <div className="text-sm text-white font-medium">{dato.nombre}</div>
                      <div className="text-[10px] text-zinc-500 flex items-center gap-1 mt-0.5">
                        <FileText className="w-3 h-3" />
                        {sourceLabels[dato.fuente] || dato.fuente}
                        {dato.fuente_detalle && (
                          <span className="text-zinc-600"> • {dato.fuente_detalle}</span>
                        )}
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-sm font-semibold text-white tabular-nums">
                        {dato.valor}
                        {dato.unidad && <span className="text-zinc-400 ml-1 text-xs">{dato.unidad}</span>}
                      </div>
                      {dato.confianza !== undefined && (
                        <div className="text-[10px] text-zinc-500">
                          {Math.round(dato.confianza * 100)}% reliable
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Methodology Steps */}
          {calculo.pasos && calculo.pasos.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <Microscope className="w-3.5 h-3.5" />
                Step-by-step methodology
              </h4>
              <div className="space-y-2">
                {calculo.pasos.sort((a, b) => a.orden - b.orden).map((paso, i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-2 bg-zinc-800/40 rounded-lg border border-zinc-700/30"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold">
                      {paso.orden}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-zinc-300">{paso.descripcion}</p>
                      {paso.formula_parcial && (
                        <code className="text-xs text-zinc-500 font-mono mt-1 block">
                          {paso.formula_parcial}
                        </code>
                      )}
                      {paso.resultado_parcial && (
                        <div className="text-xs text-emerald-400 mt-1">
                          → {paso.resultado_parcial}
                        </div>
                      )}
                      {paso.notas && (
                        <div className="text-[10px] text-zinc-500 mt-1 italic">
                          {paso.notas}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* References */}
          {calculo.referencias && calculo.referencias.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <BookOpen className="w-3.5 h-3.5" />
                Sources and references
              </h4>
              <div className="space-y-2">
                {calculo.referencias.map((ref, i) => {
                  const refConfig = referenceTypeLabels[ref.tipo] || { label: ref.tipo, icon: BookOpen };
                  const RefIcon = refConfig.icon;
                  return (
                    <div
                      key={i}
                      className="p-2 bg-zinc-800/40 rounded-lg border border-zinc-700/30"
                    >
                      <div className="flex items-start gap-2">
                        <RefIcon className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-700/50 text-zinc-400">
                              {refConfig.label}
                            </span>
                            {ref.anio && (
                              <span className="text-[10px] text-zinc-500">{ref.anio}</span>
                            )}
                            {ref.boe && (
                              <span className="text-[10px] text-zinc-500">{ref.boe}</span>
                            )}
                          </div>
                          <div className="text-sm text-white mt-1 font-medium">{ref.titulo}</div>
                          {ref.autores && (
                            <div className="text-xs text-zinc-500">{ref.autores}</div>
                          )}
                          {ref.extracto && (
                            <blockquote className="text-xs text-zinc-400 mt-2 pl-2 border-l-2 border-zinc-600 italic">
                              "{ref.extracto}"
                            </blockquote>
                          )}
                          {ref.url && (
                            <a
                              href={ref.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1 mt-1"
                            >
                              <ExternalLink className="w-3 h-3" />
                              View source
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Validations */}
          {calculo.validaciones && calculo.validaciones.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Validations performed
              </h4>
              <div className="flex flex-wrap gap-2">
                {calculo.validaciones.map((val, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-300"
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    {val}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Limitations */}
          {calculo.limitaciones && calculo.limitaciones.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                Limitations and considerations
              </h4>
              <div className="space-y-1">
                {calculo.limitaciones.map((lim, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 text-xs text-amber-300/80 bg-amber-500/5 border border-amber-500/10 rounded-lg p-2"
                  >
                    <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                    {lim}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alternatives considered */}
          {calculo.alternativas_consideradas && (
            <div className="p-3 bg-zinc-800/20 rounded-lg border border-zinc-700/20">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                <Target className="w-3.5 h-3.5" />
                Alternative methodologies considered
              </h4>
              <p className="text-xs text-zinc-400">{calculo.alternativas_consideradas}</p>
            </div>
          )}
        </CardContent>
      )}

      {/* Simple justification for non-expanded cards */}
      {!expanded && !hasDetails && (
        <CardContent className="pt-0">
          <p className="text-sm text-zinc-400">{calculo.justificacion}</p>
        </CardContent>
      )}
    </Card>
  );
}

export function CalculosFisicos({ calculos }: CalculosFisicosProps) {
  if (calculos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <div className="p-4 bg-zinc-800/50 rounded-full mb-4">
          <Calculator className="w-8 h-8 text-zinc-500" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">No calculations available</h3>
        <p className="text-sm text-zinc-500 max-w-md">
          Physical calculations will appear here once the analysis is complete.
          These include impact velocities, deformation energies, and other forensic metrics.
        </p>
      </div>
    );
  }

  // Group calculations by category
  const grouped = calculos.reduce((acc, calc) => {
    const cat = calc.categoria || "otro";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(calc);
    return acc;
  }, {} as Record<string, CalculoFisico[]>);

  const categoryOrder = ["velocidad", "energia", "fuerza", "distancia", "tiempo", "masa", "otro"];
  const sortedCategories = Object.keys(grouped).sort(
    (a, b) => categoryOrder.indexOf(a) - categoryOrder.indexOf(b)
  );

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Calculator className="w-5 h-5 text-blue-400" />
            Physical Calculations
          </h3>
          <p className="text-sm text-zinc-500 mt-1">
            {calculos.length} calculation{calculos.length !== 1 ? "s" : ""} performed with verified sources
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <Info className="w-4 h-4" />
          Click on any calculation to see details
        </div>
      </div>

      {/* Summary badges */}
      <div className="flex flex-wrap gap-2">
        {sortedCategories.map(cat => {
          const config = categoryConfig[cat] || categoryConfig.otro;
          const Icon = config.icon;
          const count = grouped[cat].length;
          return (
            <span
              key={cat}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${config.bgColor} ${config.color} border border-current/20`}
            >
              <Icon className="w-3.5 h-3.5" />
              {count} {cat === "velocidad" ? "velocity" : cat === "energia" ? "energy" : cat === "fuerza" ? "force" : cat === "distancia" ? "distance" : cat === "tiempo" ? "time" : cat === "masa" ? "mass" : "other"}
            </span>
          );
        })}
      </div>

      {/* Calculations grid */}
      <div className="grid gap-4">
        {calculos.map((calculo, index) => (
          <CalculoCard key={index} calculo={calculo} index={index} />
        ))}
      </div>

      {/* Footer note */}
      <div className="p-3 bg-zinc-800/30 rounded-lg border border-zinc-700/30 flex items-start gap-3">
        <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-zinc-400">
          <span className="font-semibold text-zinc-300">Methodology Note:</span> All calculations follow
          established forensic reconstruction standards including CRASH3, momentum conservation, and
          energy-based methods. Input data sources are documented and confidence levels reflect
          measurement uncertainties.
        </div>
      </div>
    </div>
  );
}

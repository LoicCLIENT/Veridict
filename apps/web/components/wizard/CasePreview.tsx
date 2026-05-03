"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  Scale,
  Calendar,
  MapPin,
  Car,
  FileQuestion,
  Camera,
  AlertCircle,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { WizardData, ENCARGO_PRESETS, TipoEncargoUI } from "./types";

interface CasePreviewProps {
  data: WizardData;
  currentStep: number;
}

export function CasePreview({ data, currentStep }: CasePreviewProps) {
  const preset = ENCARGO_PRESETS[data.encargo.tipo];
  const preguntasLlenas = data.encargo.preguntas.filter((p) => p.trim()).length;
  const vehiculosLlenos = data.vehiculos.filter((v) => v.marca && v.modelo).length;
  const fotosSubidas = data.files.fotos.length;

  // Calculate completeness
  const hasDate = !!data.siniestro.fecha_accidente;
  const hasQuestions = preguntasLlenas > 0;
  const hasVehicles = vehiculosLlenos > 0;

  const completenessScore = [
    data.encargo.tipo !== "otro",
    hasQuestions,
    hasDate,
    hasVehicles,
  ].filter(Boolean).length;

  return (
    <div className="h-full flex flex-col">
      {/* Header with logo and status */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-veridict-lime/20 to-veridict-lime/5 border border-veridict-lime/30 flex items-center justify-center">
            <Scale className="w-5 h-5 text-veridict-lime" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-veridict-white">Case Preview</h2>
            <p className="text-xs text-veridict-gray">Real-time summary</p>
          </div>
        </div>

        {/* Completeness indicator */}
        <div className="bg-veridict-green-800/50 rounded-xl p-4 border border-veridict-green-700/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-veridict-gray uppercase tracking-wide">
              Ready to analyze
            </span>
            <span className="text-sm font-semibold text-veridict-lime">
              {Math.round((completenessScore / 4) * 100)}%
            </span>
          </div>
          <div className="h-1.5 bg-veridict-green-900 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-veridict-lime/70 to-veridict-lime rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(completenessScore / 4) * 100}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>

      {/* Dynamic preview cards */}
      <div className="flex-1 space-y-4 overflow-y-auto pr-2">
        {/* Assignment type card - always visible */}
        <AnimatePresence mode="wait">
          <motion.div
            key={data.encargo.tipo}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`
              rounded-xl p-4 border transition-all duration-300
              ${currentStep === 1
                ? "bg-veridict-lime/10 border-veridict-lime/30 shadow-lg shadow-veridict-lime/5"
                : "bg-veridict-green-800/30 border-veridict-green-700/50"
              }
            `}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{preset.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-veridict-gray uppercase tracking-wide mb-1">
                  Analysis Type
                </p>
                <p className="text-base font-semibold text-veridict-white truncate">
                  {preset.label}
                </p>
                <p className="text-xs text-veridict-gray mt-1 line-clamp-2">
                  {preset.description}
                </p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Questions preview */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`
            rounded-xl p-4 border transition-all duration-300
            ${currentStep === 2
              ? "bg-veridict-lime/10 border-veridict-lime/30 shadow-lg shadow-veridict-lime/5"
              : "bg-veridict-green-800/30 border-veridict-green-700/50"
            }
          `}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
              <FileQuestion className="w-4 h-4 text-purple-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-veridict-gray uppercase tracking-wide mb-1">
                Questions to Answer
              </p>
              {preguntasLlenas > 0 ? (
                <div className="space-y-1.5">
                  {data.encargo.preguntas
                    .filter((p) => p.trim())
                    .slice(0, 3)
                    .map((pregunta, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-start gap-2"
                      >
                        <span className="text-[10px] font-mono text-veridict-lime mt-0.5">
                          C{i + 1}
                        </span>
                        <p className="text-sm text-veridict-white line-clamp-1">
                          {pregunta}
                        </p>
                      </motion.div>
                    ))}
                  {preguntasLlenas > 3 && (
                    <p className="text-xs text-veridict-gray">
                      +{preguntasLlenas - 3} more questions
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-veridict-gray italic">
                  No questions defined yet
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Incident details */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`
            rounded-xl p-4 border transition-all duration-300
            ${currentStep === 3
              ? "bg-veridict-lime/10 border-veridict-lime/30 shadow-lg shadow-veridict-lime/5"
              : "bg-veridict-green-800/30 border-veridict-green-700/50"
            }
          `}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <Calendar className="w-4 h-4 text-blue-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-veridict-gray uppercase tracking-wide mb-1">
                Incident Details
              </p>
              {hasDate ? (
                <div className="space-y-1">
                  <p className="text-sm font-medium text-veridict-white">
                    {new Date(data.siniestro.fecha_accidente).toLocaleDateString("en-US", {
                      weekday: "short",
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                    {data.siniestro.hora_accidente && (
                      <span className="text-veridict-gray ml-2">
                        at {data.siniestro.hora_accidente}
                      </span>
                    )}
                  </p>
                  {data.siniestro.direccion && (
                    <div className="flex items-center gap-1.5 text-xs text-veridict-gray">
                      <MapPin className="w-3 h-3" />
                      <span className="truncate">{data.siniestro.direccion}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 text-[10px] font-medium rounded bg-blue-500/20 text-blue-300 uppercase">
                      {data.siniestro.tipo_colision.replace("_", " ")}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-veridict-gray italic">
                  Set incident date and location
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Vehicles */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`
            rounded-xl p-4 border transition-all duration-300
            ${currentStep === 4
              ? "bg-veridict-lime/10 border-veridict-lime/30 shadow-lg shadow-veridict-lime/5"
              : "bg-veridict-green-800/30 border-veridict-green-700/50"
            }
          `}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
              <Car className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-veridict-gray uppercase tracking-wide mb-1">
                Vehicles Involved
              </p>
              {vehiculosLlenos > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {data.vehiculos
                    .filter((v) => v.marca && v.modelo)
                    .map((v, i) => (
                      <motion.div
                        key={v.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-veridict-green-800/50 border border-veridict-green-700/50"
                      >
                        <span className="w-5 h-5 rounded bg-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center justify-center">
                          {v.id}
                        </span>
                        <span className="text-sm text-veridict-white">
                          {v.marca} {v.modelo}
                        </span>
                      </motion.div>
                    ))}
                </div>
              ) : (
                <p className="text-sm text-veridict-gray italic">
                  Add at least one vehicle
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Photos */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`
            rounded-xl p-4 border transition-all duration-300
            ${currentStep === 5
              ? "bg-veridict-lime/10 border-veridict-lime/30 shadow-lg shadow-veridict-lime/5"
              : "bg-veridict-green-800/30 border-veridict-green-700/50"
            }
          `}
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
              <Camera className="w-4 h-4 text-amber-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-veridict-gray uppercase tracking-wide mb-1">
                Evidence Library
              </p>
              {fotosSubidas > 0 ? (
                <div className="flex items-center gap-3">
                  <div className="flex -space-x-2">
                    {data.files.fotos.slice(0, 4).map((foto, i) => (
                      <div
                        key={i}
                        className="w-8 h-8 rounded-lg border-2 border-veridict-green-900 overflow-hidden"
                      >
                        <img
                          src={URL.createObjectURL(foto)}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ))}
                    {fotosSubidas > 4 && (
                      <div className="w-8 h-8 rounded-lg border-2 border-veridict-green-900 bg-veridict-green-800 flex items-center justify-center">
                        <span className="text-[10px] font-medium text-veridict-gray">
                          +{fotosSubidas - 4}
                        </span>
                      </div>
                    )}
                  </div>
                  <span className="text-sm text-veridict-white">
                    {fotosSubidas} photo{fotosSubidas !== 1 ? "s" : ""} ready
                  </span>
                </div>
              ) : (
                <p className="text-sm text-veridict-gray italic">
                  Upload photos for AI analysis
                </p>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* AI capabilities hint */}
      <div className="mt-6 pt-4 border-t border-veridict-green-700/50">
        <div className="flex items-start gap-3 p-3 rounded-xl bg-gradient-to-r from-veridict-lime/5 to-transparent border border-veridict-lime/10">
          <Sparkles className="w-4 h-4 text-veridict-lime flex-shrink-0 mt-0.5" />
          <div className="text-xs text-veridict-gray leading-relaxed">
            <span className="text-veridict-lime font-medium">Veridict AI</span> will auto-complete
            vehicle specs, weather data, physics simulation, regulations, and case law based on your input.
          </div>
        </div>
      </div>
    </div>
  );
}

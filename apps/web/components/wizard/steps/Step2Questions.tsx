"use client";

import { useState } from "react";
import { motion, AnimatePresence, Reorder } from "framer-motion";
import {
  Plus,
  Trash2,
  Wand2,
  ArrowRight,
  ArrowLeft,
  GripVertical,
  Sparkles,
  Lightbulb,
} from "lucide-react";
import { TipoEncargoUI, ENCARGO_PRESETS, EncargoForm } from "../types";

interface Step2Props {
  encargo: EncargoForm;
  onChange: (encargo: EncargoForm) => void;
  onNext: () => void;
  onBack: () => void;
}

export function Step2Questions({ encargo, onChange, onNext, onBack }: Step2Props) {
  const preset = ENCARGO_PRESETS[encargo.tipo];
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);

  const updatePregunta = (idx: number, val: string) => {
    onChange({
      ...encargo,
      preguntas: encargo.preguntas.map((p, i) => (i === idx ? val : p)),
    });
  };

  const addPregunta = () => {
    onChange({ ...encargo, preguntas: [...encargo.preguntas, ""] });
  };

  const removePregunta = (idx: number) => {
    if (encargo.preguntas.length <= 1) return;
    onChange({
      ...encargo,
      preguntas: encargo.preguntas.filter((_, i) => i !== idx),
    });
  };

  const loadSuggested = () => {
    if (preset.preguntasSugeridas.length > 0) {
      onChange({ ...encargo, preguntas: [...preset.preguntasSugeridas] });
    }
  };

  const reorderPreguntas = (newOrder: string[]) => {
    onChange({ ...encargo, preguntas: newOrder });
  };

  const preguntasValidas = encargo.preguntas.filter((p) => p.trim()).length;
  const canContinue = preguntasValidas > 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl lg:text-4xl font-bold text-veridict-white mb-4"
        >
          What should Veridict answer?
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-veridict-gray"
        >
          Define the questions your expert report must answer. These will be labeled
          C1, C2, C3... in the final document.
        </motion.p>
      </div>

      {/* Suggested questions hint */}
      {preset.preguntasSugeridas.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-3xl mx-auto"
        >
          <button
            type="button"
            onClick={loadSuggested}
            className="w-full p-4 rounded-2xl border border-dashed border-veridict-lime/30 bg-veridict-lime/5 hover:bg-veridict-lime/10 hover:border-veridict-lime/50 transition-all duration-200 group"
          >
            <div className="flex items-center justify-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-veridict-lime/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Wand2 className="w-5 h-5 text-veridict-lime" />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-veridict-lime">
                  Load suggested questions for {preset.label}
                </p>
                <p className="text-xs text-veridict-gray">
                  {preset.preguntasSugeridas.length} questions tailored to this analysis type
                </p>
              </div>
            </div>
          </button>
        </motion.div>
      )}

      {/* Questions list */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="max-w-3xl mx-auto"
      >
        <Reorder.Group
          axis="y"
          values={encargo.preguntas}
          onReorder={reorderPreguntas}
          className="space-y-3"
        >
          <AnimatePresence initial={false}>
            {encargo.preguntas.map((pregunta, idx) => (
              <Reorder.Item
                key={idx}
                value={pregunta}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.2 }}
              >
                <div
                  className={`
                    relative group rounded-2xl border transition-all duration-200
                    ${focusedIndex === idx
                      ? "bg-veridict-green-800 border-veridict-lime/50 shadow-lg shadow-veridict-lime/10"
                      : "bg-veridict-green-800/50 border-veridict-green-700/50 hover:border-veridict-green-600"
                    }
                  `}
                >
                  {/* Question number badge */}
                  <div className="absolute -left-3 top-4 w-8 h-8 rounded-lg bg-veridict-green-900 border border-veridict-green-700 flex items-center justify-center shadow-md">
                    <span className="text-xs font-bold text-veridict-lime font-mono">
                      C{idx + 1}
                    </span>
                  </div>

                  <div className="flex items-start gap-2 p-4 pl-8">
                    {/* Drag handle */}
                    <button
                      type="button"
                      className="mt-3 opacity-0 group-hover:opacity-50 hover:!opacity-100 cursor-grab active:cursor-grabbing transition-opacity"
                    >
                      <GripVertical className="w-4 h-4 text-veridict-gray" />
                    </button>

                    {/* Question input */}
                    <div className="flex-1">
                      <textarea
                        rows={2}
                        placeholder="e.g., What was the estimated speed at the moment of impact?"
                        value={pregunta}
                        onChange={(e) => updatePregunta(idx, e.target.value)}
                        onFocus={() => setFocusedIndex(idx)}
                        onBlur={() => setFocusedIndex(null)}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-transparent text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/30 focus:bg-veridict-green-900 focus:outline-none transition-all resize-none text-base leading-relaxed"
                      />

                      {/* Character hint */}
                      {focusedIndex === idx && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="flex items-center gap-2 mt-2 px-2"
                        >
                          <Lightbulb className="w-3 h-3 text-veridict-gray" />
                          <span className="text-xs text-veridict-gray">
                            Be specific. Include vehicle IDs (A, B) if relevant.
                          </span>
                        </motion.div>
                      )}
                    </div>

                    {/* Delete button */}
                    {encargo.preguntas.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removePregunta(idx)}
                        className="mt-3 p-2 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/20 text-veridict-gray hover:text-red-400 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </Reorder.Item>
            ))}
          </AnimatePresence>
        </Reorder.Group>

        {/* Add question button */}
        <motion.button
          type="button"
          onClick={addPregunta}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="w-full mt-4 p-4 rounded-2xl border-2 border-dashed border-veridict-green-700/50 hover:border-veridict-lime/30 hover:bg-veridict-green-800/30 transition-all duration-200 group"
        >
          <div className="flex items-center justify-center gap-2 text-veridict-gray group-hover:text-veridict-lime transition-colors">
            <Plus className="w-5 h-5" />
            <span className="font-medium">Add another question</span>
          </div>
        </motion.button>
      </motion.div>

      {/* Info box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="max-w-3xl mx-auto"
      >
        <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-veridict-gray leading-relaxed">
              <span className="text-blue-300 font-medium">Pro tip:</span> Each question
              will get a dedicated section in the final report with physics calculations,
              legal references, and a confidence assessment. Complex questions work better
              when split into focused sub-questions.
            </div>
          </div>
        </div>
      </motion.div>

      {/* Navigation buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex items-center justify-center gap-4 pt-4"
      >
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-2 px-6 py-3 rounded-xl text-veridict-gray hover:text-veridict-white hover:bg-veridict-green-800/50 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <button
          type="button"
          onClick={onNext}
          disabled={!canContinue}
          className={`
            group flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-200
            ${canContinue
              ? "bg-veridict-lime text-veridict-green-900 hover:bg-veridict-lime-hover shadow-lg shadow-veridict-lime/20 hover:shadow-veridict-lime/30 hover:scale-[1.02]"
              : "bg-veridict-green-800 text-veridict-gray cursor-not-allowed"
            }
          `}
        >
          Continue to Incident
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>
      </motion.div>

      {/* Validation hint */}
      {!canContinue && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-sm text-amber-400"
        >
          Please enter at least one question to continue
        </motion.p>
      )}
    </div>
  );
}

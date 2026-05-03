"use client";

import { motion } from "framer-motion";
import { Check, ArrowRight } from "lucide-react";
import { TipoEncargoUI, ParteUI, ENCARGO_PRESETS, EncargoForm } from "../types";

interface Step1Props {
  encargo: EncargoForm;
  onChange: (encargo: EncargoForm) => void;
  onNext: () => void;
}

const PARTE_OPTIONS: { value: ParteUI; label: string; description: string }[] = [
  { value: "imparcial", label: "Court Expert", description: "Neutral, appointed by the court" },
  { value: "demandante", label: "Plaintiff", description: "Representing the claimant" },
  { value: "demandado", label: "Defendant", description: "Representing the defense" },
  { value: "aseguradora", label: "Insurance", description: "Insurance company assessment" },
];

export function Step1Assignment({ encargo, onChange, onNext }: Step1Props) {
  const tipos = Object.entries(ENCARGO_PRESETS) as [TipoEncargoUI, typeof ENCARGO_PRESETS[TipoEncargoUI]][];

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl lg:text-4xl font-bold text-veridict-white mb-4"
        >
          What type of analysis?
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-veridict-gray"
        >
          Select the primary focus of your expert report. Veridict will tailor the analysis
          and suggested questions accordingly.
        </motion.p>
      </div>

      {/* Type selection grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4"
      >
        {tipos.map(([key, preset], index) => {
          const isSelected = encargo.tipo === key;
          return (
            <motion.button
              key={key}
              type="button"
              onClick={() => onChange({ ...encargo, tipo: key })}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className={`
                relative p-5 rounded-2xl text-left transition-all duration-300
                border-2 group
                ${isSelected
                  ? "bg-veridict-lime/10 border-veridict-lime shadow-lg shadow-veridict-lime/10"
                  : "bg-veridict-green-800/30 border-veridict-green-700/50 hover:border-veridict-lime/30 hover:bg-veridict-green-800/50"
                }
              `}
            >
              {/* Selected indicator */}
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-3 right-3 w-6 h-6 rounded-full bg-veridict-lime flex items-center justify-center"
                >
                  <Check className="w-4 h-4 text-veridict-green-900" strokeWidth={3} />
                </motion.div>
              )}

              {/* Icon */}
              <span className="text-3xl mb-3 block">{preset.icon}</span>

              {/* Labels */}
              <h3 className={`
                font-semibold text-base mb-1 transition-colors
                ${isSelected ? "text-veridict-lime" : "text-veridict-white group-hover:text-veridict-lime"}
              `}>
                {preset.label}
              </h3>
              <p className="text-xs text-veridict-gray leading-relaxed line-clamp-2">
                {preset.description}
              </p>
            </motion.button>
          );
        })}
      </motion.div>

      {/* Requesting party */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        <p className="text-sm font-medium text-veridict-gray mb-4 text-center">
          Who is requesting this report?
        </p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {PARTE_OPTIONS.map((option) => {
            const isSelected = encargo.parte === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => onChange({ ...encargo, parte: option.value })}
                className={`
                  p-3 rounded-xl text-center transition-all duration-200
                  border
                  ${isSelected
                    ? "bg-veridict-green-800 border-veridict-lime/50 text-veridict-white"
                    : "bg-veridict-green-800/30 border-veridict-green-700/50 text-veridict-gray hover:border-veridict-green-600 hover:text-veridict-white"
                  }
                `}
              >
                <p className="text-sm font-medium">{option.label}</p>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Optional fields collapsed */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="max-w-2xl mx-auto space-y-4"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-veridict-gray mb-2">
              Requesting party name
              <span className="text-veridict-gray/50 ml-1">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g., Court of First Instance No. 1"
              value={encargo.solicitante}
              onChange={(e) => onChange({ ...encargo, solicitante: e.target.value })}
              className="w-full px-4 py-3 rounded-xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-veridict-gray mb-2">
              Case reference
              <span className="text-veridict-gray/50 ml-1">(optional)</span>
            </label>
            <input
              type="text"
              placeholder="e.g., Proceedings 230/2024"
              value={encargo.procedimiento}
              onChange={(e) => onChange({ ...encargo, procedimiento: e.target.value })}
              className="w-full px-4 py-3 rounded-xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
            />
          </div>
        </div>
      </motion.div>

      {/* Continue button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="flex justify-center pt-4"
      >
        <button
          type="button"
          onClick={onNext}
          className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-veridict-lime text-veridict-green-900 font-semibold text-lg hover:bg-veridict-lime-hover transition-all duration-200 shadow-lg shadow-veridict-lime/20 hover:shadow-veridict-lime/30 hover:scale-[1.02]"
        >
          Continue to Questions
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>
      </motion.div>
    </div>
  );
}

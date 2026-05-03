"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Zap,
} from "lucide-react";
import { SiniestroForm } from "../types";

interface Step3Props {
  siniestro: SiniestroForm;
  onChange: (siniestro: SiniestroForm) => void;
  onNext: () => void;
  onBack: () => void;
}

const COLLISION_TYPES = [
  { value: "frontal", label: "Frontal", icon: "💥", description: "Head-on collision" },
  { value: "lateral", label: "Lateral", icon: "↔️", description: "Side impact / T-bone" },
  { value: "alcance", label: "Rear-end", icon: "⬆️", description: "Vehicle struck from behind" },
  { value: "atropello", label: "Pedestrian", icon: "🚶", description: "Pedestrian involved" },
  { value: "multiple", label: "Multiple", icon: "🔄", description: "Chain reaction / pile-up" },
  { value: "salida_via", label: "Runoff", icon: "↗️", description: "Left the roadway" },
  { value: "vuelco", label: "Rollover", icon: "🔃", description: "Vehicle overturned" },
];

export function Step3Incident({ siniestro, onChange, onNext, onBack }: Step3Props) {
  const hasDate = !!siniestro.fecha_accidente;

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl lg:text-4xl font-bold text-veridict-white mb-4"
        >
          When and where?
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-veridict-gray"
        >
          Veridict will auto-fetch historical weather, road conditions, and sunrise/sunset data
          based on this information.
        </motion.p>
      </div>

      {/* Date and time - prominent */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="max-w-3xl mx-auto"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Date input - styled prominently */}
          <div className="relative">
            <label className="block text-sm font-medium text-veridict-gray mb-2">
              Accident Date <span className="text-veridict-lime">*</span>
            </label>
            <div className="relative">
              <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-veridict-gray" />
              <input
                type="date"
                value={siniestro.fecha_accidente}
                onChange={(e) => onChange({ ...siniestro, fecha_accidente: e.target.value })}
                className="w-full pl-12 pr-4 py-4 rounded-2xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-white text-lg focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all [color-scheme:dark]"
              />
            </div>
          </div>

          {/* Time input */}
          <div className="relative">
            <label className="block text-sm font-medium text-veridict-gray mb-2">
              Approximate Time
              <span className="text-veridict-gray/50 ml-1">(optional)</span>
            </label>
            <div className="relative">
              <Clock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-veridict-gray" />
              <input
                type="time"
                value={siniestro.hora_accidente}
                onChange={(e) => onChange({ ...siniestro, hora_accidente: e.target.value })}
                className="w-full pl-12 pr-4 py-4 rounded-2xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-white text-lg focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all [color-scheme:dark]"
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Collision type selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="max-w-4xl mx-auto"
      >
        <label className="block text-sm font-medium text-veridict-gray mb-4 text-center">
          Type of collision
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
          {COLLISION_TYPES.map((type) => {
            const isSelected = siniestro.tipo_colision === type.value;
            return (
              <button
                key={type.value}
                type="button"
                onClick={() => onChange({ ...siniestro, tipo_colision: type.value })}
                className={`
                  p-3 rounded-xl text-center transition-all duration-200 border
                  ${isSelected
                    ? "bg-veridict-lime/10 border-veridict-lime/50 text-veridict-white"
                    : "bg-veridict-green-800/30 border-veridict-green-700/50 text-veridict-gray hover:border-veridict-green-600 hover:text-veridict-white"
                  }
                `}
              >
                <span className="text-xl block mb-1">{type.icon}</span>
                <span className="text-xs font-medium">{type.label}</span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Location */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="max-w-3xl mx-auto"
      >
        <label className="block text-sm font-medium text-veridict-gray mb-2">
          Location / Kilometer point
          <span className="text-veridict-gray/50 ml-1">(optional - auto-geocoded)</span>
        </label>
        <div className="relative">
          <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-veridict-gray" />
          <input
            type="text"
            placeholder="e.g., AP-9, km 67.400 direction Vigo"
            value={siniestro.direccion}
            onChange={(e) => onChange({ ...siniestro, direccion: e.target.value })}
            className="w-full pl-12 pr-4 py-4 rounded-2xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 text-lg focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
          />
        </div>

        {/* Coordinate inputs collapsed */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-xs text-veridict-gray/70 mb-1">
              Latitude (auto-detected)
            </label>
            <input
              type="number"
              step="any"
              placeholder="42.1234"
              value={siniestro.lat}
              onChange={(e) => onChange({ ...siniestro, lat: e.target.value })}
              className="w-full px-4 py-2 rounded-xl bg-veridict-green-900/50 border border-veridict-green-800/50 text-veridict-white placeholder:text-veridict-gray/30 text-sm focus:border-veridict-green-700 focus:outline-none transition-all"
            />
          </div>
          <div>
            <label className="block text-xs text-veridict-gray/70 mb-1">
              Longitude (auto-detected)
            </label>
            <input
              type="number"
              step="any"
              placeholder="-8.5678"
              value={siniestro.lon}
              onChange={(e) => onChange({ ...siniestro, lon: e.target.value })}
              className="w-full px-4 py-2 rounded-xl bg-veridict-green-900/50 border border-veridict-green-800/50 text-veridict-white placeholder:text-veridict-gray/30 text-sm focus:border-veridict-green-700 focus:outline-none transition-all"
            />
          </div>
        </div>
      </motion.div>

      {/* Auto-fetch hint */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="max-w-3xl mx-auto"
      >
        <div className="p-4 rounded-2xl bg-gradient-to-r from-veridict-lime/5 to-transparent border border-veridict-lime/10">
          <div className="flex items-start gap-3">
            <Zap className="w-5 h-5 text-veridict-lime flex-shrink-0" />
            <div className="text-sm text-veridict-gray leading-relaxed">
              <span className="text-veridict-lime font-medium">Auto-enrichment:</span> Road
              surface type, speed limits, lane configuration, historical weather, visibility
              conditions, and solar position will be retrieved automatically.
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
          disabled={!hasDate}
          className={`
            group flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-200
            ${hasDate
              ? "bg-veridict-lime text-veridict-green-900 hover:bg-veridict-lime-hover shadow-lg shadow-veridict-lime/20 hover:shadow-veridict-lime/30 hover:scale-[1.02]"
              : "bg-veridict-green-800 text-veridict-gray cursor-not-allowed"
            }
          `}
        >
          Continue to Vehicles
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>
      </motion.div>

      {!hasDate && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-sm text-amber-400"
        >
          Accident date is required to continue
        </motion.p>
      )}
    </div>
  );
}

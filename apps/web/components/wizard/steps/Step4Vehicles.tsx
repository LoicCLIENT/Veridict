"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  Trash2,
  ArrowRight,
  ArrowLeft,
  Car,
  User,
  Palette,
  CalendarDays,
  Database,
} from "lucide-react";
import { VehiculoForm } from "../types";

interface Step4Props {
  vehiculos: VehiculoForm[];
  onChange: (vehiculos: VehiculoForm[]) => void;
  onNext: () => void;
  onBack: () => void;
}

export function Step4Vehicles({ vehiculos, onChange, onNext, onBack }: Step4Props) {
  const addVehiculo = () => {
    const nextId = String.fromCharCode(65 + vehiculos.length);
    onChange([
      ...vehiculos,
      { id: nextId, matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" },
    ]);
  };

  const removeVehiculo = (idx: number) => {
    if (vehiculos.length <= 1) return;
    const updated = vehiculos
      .filter((_, i) => i !== idx)
      .map((v, i) => ({ ...v, id: String.fromCharCode(65 + i) }));
    onChange(updated);
  };

  const updateVehiculo = (idx: number, patch: Partial<VehiculoForm>) => {
    onChange(vehiculos.map((v, i) => (i === idx ? { ...v, ...patch } : v)));
  };

  const vehiculosValidos = vehiculos.filter((v) => v.marca.trim() && v.modelo.trim()).length;
  const canContinue = vehiculosValidos > 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl lg:text-4xl font-bold text-veridict-white mb-4"
        >
          Vehicles involved
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-veridict-gray"
        >
          Just enter make and model. Veridict will auto-fetch mass, dimensions,
          safety systems, and structural data.
        </motion.p>
      </div>

      {/* Vehicles list */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="max-w-4xl mx-auto space-y-4"
      >
        <AnimatePresence initial={false}>
          {vehiculos.map((vehiculo, idx) => (
            <motion.div
              key={vehiculo.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.2 }}
              className="relative"
            >
              {/* Vehicle card */}
              <div className="rounded-2xl border border-veridict-green-700/50 bg-veridict-green-800/30 overflow-hidden">
                {/* Header with vehicle ID */}
                <div className="flex items-center justify-between px-5 py-3 bg-veridict-green-800/50 border-b border-veridict-green-700/30">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                      <span className="text-lg font-bold text-emerald-400">{vehiculo.id}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-veridict-white">
                        Vehicle {vehiculo.id}
                      </span>
                      {vehiculo.marca && vehiculo.modelo && (
                        <p className="text-xs text-veridict-gray">
                          {vehiculo.marca} {vehiculo.modelo}
                        </p>
                      )}
                    </div>
                  </div>
                  {vehiculos.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeVehiculo(idx)}
                      className="p-2 rounded-lg hover:bg-red-500/20 text-veridict-gray hover:text-red-400 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Form fields */}
                <div className="p-5">
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Make - required */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <Car className="w-3.5 h-3.5" />
                        Make <span className="text-veridict-lime">*</span>
                      </label>
                      <input
                        type="text"
                        placeholder="e.g., Toyota"
                        value={vehiculo.marca}
                        onChange={(e) => updateVehiculo(idx, { marca: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
                      />
                    </div>

                    {/* Model - required */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <Car className="w-3.5 h-3.5" />
                        Model <span className="text-veridict-lime">*</span>
                      </label>
                      <input
                        type="text"
                        placeholder="e.g., Corolla"
                        value={vehiculo.modelo}
                        onChange={(e) => updateVehiculo(idx, { modelo: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
                      />
                    </div>

                    {/* Year */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <CalendarDays className="w-3.5 h-3.5" />
                        Year
                      </label>
                      <input
                        type="number"
                        placeholder="e.g., 2019"
                        value={vehiculo.anio}
                        onChange={(e) => updateVehiculo(idx, { anio: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
                      />
                    </div>

                    {/* License plate */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <Database className="w-3.5 h-3.5" />
                        License plate
                      </label>
                      <input
                        type="text"
                        placeholder="e.g., 1234 ABC"
                        value={vehiculo.matricula}
                        onChange={(e) => updateVehiculo(idx, { matricula: e.target.value.toUpperCase() })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all uppercase"
                      />
                    </div>

                    {/* Color */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <Palette className="w-3.5 h-3.5" />
                        Color
                      </label>
                      <input
                        type="text"
                        placeholder="e.g., White"
                        value={vehiculo.color}
                        onChange={(e) => updateVehiculo(idx, { color: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
                      />
                    </div>

                    {/* Driver */}
                    <div>
                      <label className="flex items-center gap-1.5 text-sm font-medium text-veridict-gray mb-2">
                        <User className="w-3.5 h-3.5" />
                        Driver
                      </label>
                      <input
                        type="text"
                        placeholder="Initials / name"
                        value={vehiculo.conductor}
                        onChange={(e) => updateVehiculo(idx, { conductor: e.target.value })}
                        className="w-full px-4 py-3 rounded-xl bg-veridict-green-900/50 border border-veridict-green-700/50 text-veridict-white placeholder:text-veridict-gray/50 focus:border-veridict-lime/50 focus:outline-none focus:ring-1 focus:ring-veridict-lime/30 transition-all"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Add vehicle button */}
        <motion.button
          type="button"
          onClick={addVehiculo}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="w-full p-4 rounded-2xl border-2 border-dashed border-veridict-green-700/50 hover:border-emerald-500/30 hover:bg-emerald-500/5 transition-all duration-200 group"
        >
          <div className="flex items-center justify-center gap-2 text-veridict-gray group-hover:text-emerald-400 transition-colors">
            <Plus className="w-5 h-5" />
            <span className="font-medium">Add another vehicle</span>
          </div>
        </motion.button>
      </motion.div>

      {/* Auto-fetch hint */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="max-w-3xl mx-auto"
      >
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-500/5 to-transparent border border-emerald-500/10">
          <div className="flex items-start gap-3">
            <Database className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div className="text-sm text-veridict-gray leading-relaxed">
              <span className="text-emerald-400 font-medium">Auto-fetched data:</span> Vehicle
              mass, wheelbase, track width, frontal stiffness coefficients, airbag configuration,
              ABS/ESC systems, and Euro NCAP ratings will be retrieved automatically.
            </div>
          </div>
        </div>
      </motion.div>

      {/* Navigation buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
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
          Continue to Evidence
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>
      </motion.div>

      {!canContinue && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-sm text-amber-400"
        >
          At least one vehicle with make and model is required
        </motion.p>
      )}
    </div>
  );
}

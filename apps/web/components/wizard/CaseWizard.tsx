"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Scale, Upload, X } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { useAppStore } from "@/lib/store";

import { StepIndicator } from "./StepIndicator";
import { CasePreview } from "./CasePreview";
import { Step1Assignment } from "./steps/Step1Assignment";
import { Step2Questions } from "./steps/Step2Questions";
import { Step3Incident } from "./steps/Step3Incident";
import { Step4Vehicles } from "./steps/Step4Vehicles";
import { Step5Evidence } from "./steps/Step5Evidence";
import {
  WizardData,
  EncargoForm,
  SiniestroForm,
  VehiculoForm,
  AtestadoForm,
  VelocidadForm,
  LesionForm,
  FilesForm,
} from "./types";

const STORAGE_KEY = "veridict_nuevo_caso_draft_v2";

const initialData: WizardData = {
  encargo: {
    tipo: "responsabilidad_trafico",
    preguntas: [""],
    solicitante: "",
    parte: "imparcial",
    procedimiento: "",
    observaciones: "",
  },
  siniestro: {
    fecha_accidente: "",
    hora_accidente: "",
    tipo_colision: "alcance",
    direccion: "",
    lat: "",
    lon: "",
  },
  vehiculos: [
    { id: "A", matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" },
    { id: "B", matricula: "", marca: "", modelo: "", anio: "", color: "", conductor: "" },
  ],
  atestado: {
    numero_atestado: "",
    cuerpo_actuante: "guardia_civil",
    hay_huellas_frenada: "no_consta",
    condiciones_meteorologicas: "",
    estado_calzada: "",
    visibilidad: "",
    declaraciones: "",
  },
  velocidades: [],
  lesiones: [],
  files: { fotos: [], otros: [] },
};

export function CaseWizard() {
  const router = useRouter();
  const toast = useToast();
  const iniciarUpload = useAppStore((s) => s.iniciarUpload);
  const tickUpload = useAppStore((s) => s.tickUpload);

  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [data, setData] = useState<WizardData>(initialData);
  const [showPreview, setShowPreview] = useState(false);
  const restoredRef = useRef(false);

  // Restore draft from localStorage
  useEffect(() => {
    if (restoredRef.current) return;
    restoredRef.current = true;
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      if (!raw) return;
      const draft = JSON.parse(raw);
      // Files cannot be restored
      setData({ ...draft, files: { fotos: [], otros: [] } });
    } catch (e) {
      console.warn("Could not restore draft:", e);
    }
  }, []);

  // Save draft on change
  useEffect(() => {
    if (!restoredRef.current) return;
    if (typeof window === "undefined") return;
    const timeout = setTimeout(() => {
      try {
        const { files, ...rest } = data;
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          ...rest,
          savedAt: new Date().toISOString(),
        }));
      } catch (e) {
        // localStorage full or disabled
      }
    }, 300);
    return () => clearTimeout(timeout);
  }, [data]);

  const updateEncargo = (encargo: EncargoForm) => setData({ ...data, encargo });
  const updateSiniestro = (siniestro: SiniestroForm) => setData({ ...data, siniestro });
  const updateVehiculos = (vehiculos: VehiculoForm[]) => setData({ ...data, vehiculos });
  const updateFiles = (files: FilesForm) => setData({ ...data, files });

  const handleSubmit = async () => {
    const { encargo, siniestro, vehiculos, files } = data;

    // Validation
    if (!siniestro.fecha_accidente) {
      toast.error("Missing date", "Please enter the accident date.");
      setCurrentStep(3);
      return;
    }
    const preguntasValidas = encargo.preguntas.map((p) => p.trim()).filter(Boolean);
    if (preguntasValidas.length === 0) {
      toast.error("Missing questions", "Please enter at least one question.");
      setCurrentStep(2);
      return;
    }
    const vehiculosValidos = vehiculos.filter((v) => v.marca.trim() && v.modelo.trim());
    if (vehiculosValidos.length === 0) {
      toast.error("Missing vehicles", "Please identify at least one vehicle.");
      setCurrentStep(4);
      return;
    }

    setIsSubmitting(true);
    try {
      const caso = await api.crearCaso({
        fecha_accidente: siniestro.fecha_accidente,
        tipo_colision: siniestro.tipo_colision as "frontal" | "lateral" | "alcance" | "atropello",
        ubicacion: {
          lat: siniestro.lat ? parseFloat(siniestro.lat) : 0,
          lon: siniestro.lon ? parseFloat(siniestro.lon) : 0,
          direccion: siniestro.direccion?.trim() || undefined,
        },
        encargo: {
          tipo: encargo.tipo,
          preguntas: preguntasValidas,
          solicitante: encargo.solicitante || undefined,
          parte: encargo.parte,
          procedimiento: encargo.procedimiento || undefined,
          observaciones: encargo.observaciones || undefined,
        },
        vehiculos_identificacion: vehiculosValidos.map((v) => ({
          id: v.id,
          matricula: v.matricula || undefined,
          marca: v.marca,
          modelo: v.modelo,
          anio: v.anio ? parseInt(v.anio) : undefined,
          color: v.color || undefined,
          conductor: v.conductor || undefined,
        })),
        hechos_atestado: {
          numero_atestado: data.atestado.numero_atestado || undefined,
          cuerpo_actuante: data.atestado.cuerpo_actuante || undefined,
          hay_huellas_frenada:
            data.atestado.hay_huellas_frenada === "no_consta"
              ? undefined
              : data.atestado.hay_huellas_frenada === "si",
          condiciones_meteorologicas: data.atestado.condiciones_meteorologicas || undefined,
          estado_calzada: data.atestado.estado_calzada || undefined,
          visibilidad: data.atestado.visibilidad || undefined,
          declaraciones: data.atestado.declaraciones || undefined,
          velocidades_declaradas: data.velocidades
            .filter((v) => v.valor_kmh)
            .map((v) => ({ vehiculo_id: v.vehiculo_id, valor_kmh: parseFloat(v.valor_kmh), fuente: v.fuente })),
        },
        lesiones: data.lesiones
          .filter((l) => l.ocupante.trim() && l.zona_corporal.trim())
          .map((l) => ({
            ocupante: l.ocupante,
            vehiculo_id: l.vehiculo_id || undefined,
            zona_corporal: l.zona_corporal,
            gravedad: l.gravedad,
            dias_baja: l.dias_baja ? parseInt(l.dias_baja) : undefined,
          })),
      });

      // Upload attachments in background
      const totalAdjuntos = files.fotos.length + (files.atestado ? 1 : 0);
      iniciarUpload(caso.id, totalAdjuntos, !!files.atestado);

      const subirAdjuntosEnFondo = async () => {
        if (totalAdjuntos === 0) return;
        const CONCURRENCIA = 6;
        const cola: Array<() => Promise<void>> = [];
        if (files.atestado) {
          const f = files.atestado;
          cola.push(async () => {
            try {
              await api.uploadAtestado(caso.id, f);
              tickUpload(caso.id, "atestado", true);
            } catch (e) {
              console.error("uploadAtestado:", e);
              tickUpload(caso.id, "atestado", false);
            }
          });
        }
        for (const foto of files.fotos) {
          cola.push(async () => {
            try {
              await api.uploadFoto(caso.id, foto);
              tickUpload(caso.id, foto.name, true);
            } catch (e) {
              console.error("uploadFoto:", foto.name, e);
              tickUpload(caso.id, foto.name, false);
            }
          });
        }
        let i = 0;
        const workers = Array.from({ length: Math.min(CONCURRENCIA, cola.length) }, async () => {
          while (i < cola.length) {
            const idx = i++;
            await cola[idx]();
          }
        });
        await Promise.all(workers);
      };

      subirAdjuntosEnFondo().catch((err) => console.error("uploads error:", err));
      api.generarInforme(caso.id).catch((err) => console.error("Informe error:", err));

      toast.success(
        "Case created",
        totalAdjuntos > 0
          ? `Uploading ${totalAdjuntos} files and generating report...`
          : "Generating expert report..."
      );

      localStorage.removeItem(STORAGE_KEY);
      router.push(`/casos/${caso.id}`);
    } catch (error) {
      console.error("Error creating caso:", error);
      toast.error("Error creating case", "Please verify the data and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => setCurrentStep((s) => Math.min(s + 1, 5));
  const prevStep = () => setCurrentStep((s) => Math.max(s - 1, 1));

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-xl border-b border-veridict-green-700/30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-veridict-lime/20 to-veridict-lime/5 border border-veridict-lime/30 flex items-center justify-center">
                <Scale className="w-5 h-5 text-veridict-lime" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-veridict-white">New Expert Report</h1>
                <p className="text-xs text-veridict-gray">Veridict AI Analysis</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Mobile preview toggle */}
              <button
                type="button"
                onClick={() => setShowPreview(!showPreview)}
                className="lg:hidden p-2 rounded-lg bg-veridict-green-800/50 border border-veridict-green-700/50 text-veridict-gray hover:text-veridict-white transition-colors"
              >
                {showPreview ? <X className="w-5 h-5" /> : <Scale className="w-5 h-5" />}
              </button>

              {/* Import JSON */}
              <label className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl bg-veridict-green-800/50 border border-veridict-green-700/50 text-sm text-veridict-gray hover:text-veridict-white hover:border-veridict-green-600 transition-all cursor-pointer">
                <Upload className="w-4 h-4" />
                Import JSON
                <input
                  type="file"
                  accept="application/json,.json"
                  className="hidden"
                  onChange={(e) => {
                    // Import logic here
                    const f = e.target.files?.[0];
                    if (f) {
                      f.text().then((text) => {
                        try {
                          const imported = JSON.parse(text);
                          // Map imported data to wizard format
                          // This is a simplified import - extend as needed
                          if (imported.encargo) setData((d) => ({ ...d, encargo: { ...d.encargo, ...imported.encargo } }));
                          toast.success("JSON imported", "Review and adjust the data as needed.");
                        } catch {
                          toast.error("Invalid JSON", "Could not parse the file.");
                        }
                      });
                    }
                    e.target.value = "";
                  }}
                />
              </label>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Step indicator */}
        <StepIndicator
          currentStep={currentStep}
          onStepClick={(step) => step <= currentStep && setCurrentStep(step)}
        />

        {/* Split layout */}
        <div className="flex gap-8">
          {/* Left: Preview (desktop) */}
          <aside className="hidden lg:block w-80 xl:w-96 flex-shrink-0">
            <div className="sticky top-32">
              <CasePreview data={data} currentStep={currentStep} />
            </div>
          </aside>

          {/* Right: Wizard steps */}
          <div className="flex-1 min-w-0">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {currentStep === 1 && (
                  <Step1Assignment
                    encargo={data.encargo}
                    onChange={updateEncargo}
                    onNext={nextStep}
                  />
                )}
                {currentStep === 2 && (
                  <Step2Questions
                    encargo={data.encargo}
                    onChange={updateEncargo}
                    onNext={nextStep}
                    onBack={prevStep}
                  />
                )}
                {currentStep === 3 && (
                  <Step3Incident
                    siniestro={data.siniestro}
                    onChange={updateSiniestro}
                    onNext={nextStep}
                    onBack={prevStep}
                  />
                )}
                {currentStep === 4 && (
                  <Step4Vehicles
                    vehiculos={data.vehiculos}
                    onChange={updateVehiculos}
                    onNext={nextStep}
                    onBack={prevStep}
                  />
                )}
                {currentStep === 5 && (
                  <Step5Evidence
                    files={data.files}
                    onChange={updateFiles}
                    onSubmit={handleSubmit}
                    onBack={prevStep}
                    isSubmitting={isSubmitting}
                  />
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Mobile preview drawer */}
      <AnimatePresence>
        {showPreview && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 lg:hidden"
          >
            <div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowPreview(false)}
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25 }}
              className="absolute right-0 top-0 bottom-0 w-80 bg-background border-l border-veridict-green-700/50 p-6 overflow-y-auto"
            >
              <CasePreview data={data} currentStep={currentStep} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

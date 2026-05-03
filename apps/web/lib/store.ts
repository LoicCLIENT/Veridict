import { create } from "zustand";
import type { Caso } from "./api";

interface AppState {
  // Caso actual
  casoActual: Caso | null;
  setCasoActual: (caso: Caso | null) => void;

  // Estado de procesamiento
  procesando: boolean;
  progreso: number;
  etapaActual: string;
  setProcesando: (procesando: boolean) => void;
  setProgreso: (progreso: number, etapa?: string) => void;

  // Timeline
  tiempoActual: number;
  setTiempoActual: (tiempo: number) => void;

  // UI
  panelActivo: "informe" | "simulacion" | "cronologia" | "calculos" | "legal" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs";
  setPanelActivo: (panel: "informe" | "simulacion" | "cronologia" | "calculos" | "legal" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs") => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Caso actual
  casoActual: null,
  setCasoActual: (caso) => set({ casoActual: caso }),

  // Estado de procesamiento
  procesando: false,
  progreso: 0,
  etapaActual: "",
  setProcesando: (procesando) => set({ procesando }),
  setProgreso: (progreso, etapa) =>
    set({ progreso, ...(etapa ? { etapaActual: etapa } : {}) }),

  // Timeline
  tiempoActual: 0,
  setTiempoActual: (tiempo) => set({ tiempoActual: tiempo }),

  // UI
  panelActivo: "informe",
  setPanelActivo: (panel) => set({ panelActivo: panel }),
}));

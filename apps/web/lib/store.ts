import { create } from "zustand";
import type { Caso } from "./api";

interface UploadProgress {
  total: number;
  completed: number;
  failed: string[];
  hasAtestado: boolean;
}

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
  panelActivo: "informe" | "razonamiento" | "simulacion" | "cronologia" | "calculos" | "legal" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs";
  setPanelActivo: (panel: "informe" | "razonamiento" | "simulacion" | "cronologia" | "calculos" | "legal" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs") => void;

  // Upload progress tracking
  uploadsPorCaso: Record<string, UploadProgress>;
  iniciarUpload: (casoId: string, total: number, hasAtestado: boolean) => void;
  tickUpload: (casoId: string, fileName: string, success: boolean) => void;
  limpiarUpload: (casoId: string) => void;
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

  // Upload progress tracking
  uploadsPorCaso: {},
  iniciarUpload: (casoId, total, hasAtestado) =>
    set((state) => ({
      uploadsPorCaso: {
        ...state.uploadsPorCaso,
        [casoId]: { total, completed: 0, failed: [], hasAtestado },
      },
    })),
  tickUpload: (casoId, fileName, success) =>
    set((state) => {
      const current = state.uploadsPorCaso[casoId];
      if (!current) return state;
      return {
        uploadsPorCaso: {
          ...state.uploadsPorCaso,
          [casoId]: {
            ...current,
            completed: current.completed + 1,
            failed: success ? current.failed : [...current.failed, fileName],
          },
        },
      };
    }),
  limpiarUpload: (casoId) =>
    set((state) => {
      const { [casoId]: _, ...rest } = state.uploadsPorCaso;
      return { uploadsPorCaso: rest };
    }),
}));

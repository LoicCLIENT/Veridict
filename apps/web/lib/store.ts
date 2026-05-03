import { create } from "zustand";
import type { Caso } from "./api";

/** Estado de subida de adjuntos en background, por caso. */
export interface UploadEstado {
  total: number;        // fotos esperadas + atestado si hay
  completados: number;  // adjuntos finalizados (ok o error)
  fallidos: number;
  ultimo: string;       // nombre del último completado
  finalizado: boolean;  // true cuando completados === total
  conAtestado: boolean;
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
  panelActivo: "informe" | "razonamiento" | "mapa" | "cronologia" | "calculos" | "legal" | "dictamen" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs";
  setPanelActivo: (panel: "informe" | "razonamiento" | "mapa" | "cronologia" | "calculos" | "legal" | "dictamen" | "confrontacion" | "contexto" | "vehiculos" | "escena" | "docs") => void;

  // Subidas de adjuntos en background, indexadas por caso_id
  uploadsPorCaso: Record<string, UploadEstado>;
  iniciarUpload: (casoId: string, total: number, conAtestado: boolean) => void;
  tickUpload: (casoId: string, nombre: string, ok: boolean) => void;
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

  // Uploads en background
  uploadsPorCaso: {},
  iniciarUpload: (casoId, total, conAtestado) =>
    set((s) => ({
      uploadsPorCaso: {
        ...s.uploadsPorCaso,
        [casoId]: {
          total,
          completados: 0,
          fallidos: 0,
          ultimo: "",
          finalizado: total === 0,
          conAtestado,
        },
      },
    })),
  tickUpload: (casoId, nombre, ok) =>
    set((s) => {
      const prev = s.uploadsPorCaso[casoId];
      if (!prev) return s;
      const completados = prev.completados + 1;
      const fallidos = prev.fallidos + (ok ? 0 : 1);
      return {
        uploadsPorCaso: {
          ...s.uploadsPorCaso,
          [casoId]: {
            ...prev,
            completados,
            fallidos,
            ultimo: nombre,
            finalizado: completados >= prev.total,
          },
        },
      };
    }),
  limpiarUpload: (casoId) =>
    set((s) => {
      const next = { ...s.uploadsPorCaso };
      delete next[casoId];
      return { uploadsPorCaso: next };
    }),
}));

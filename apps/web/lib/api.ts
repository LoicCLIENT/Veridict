const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Caso {
  id: string;
  estado: "creado" | "procesando" | "completado" | "escalado_humano";
  fecha_accidente: string;
  ubicacion: { lat: number; lon: number };
  tipo_colision: "frontal" | "lateral" | "alcance" | "atropello";
  vehiculos: Vehiculo[];
  documentos: Documento[];
  fotos: Foto[];
  contexto?: Contexto;
  resultado?: Resultado;
}

export interface Vehiculo {
  id: "A" | "B";
  matricula: string;
  modelo: string;
  masa_kg: number;
  coef_rigidez_a: number;
  coef_rigidez_b: number;
  mediciones_C: [number, number, number, number, number, number];
  ancho_zona_danada_cm: number;
  version_conductor: string;
}

export interface Documento {
  id: string;
  tipo: "atestado" | "parte_amistoso";
  url: string;
  texto_extraido?: string;
}

export interface Foto {
  id: string;
  url: string;
  analisis?: string;
}

export interface Contexto {
  meteo: Record<string, unknown>;
  via: Record<string, unknown>;
  sol: Record<string, unknown>;
}

export interface Resultado {
  cronologia: Evento[];
  calculos: CalculoFisico[];
  infracciones: Infraccion[];
  veredicto: {
    culpa_a: number;
    culpa_b: number;
    confidence: number;
  };
  compatibilidad_versiones: {
    a: boolean;
    b: boolean;
    justificacion: string;
  };
  devils_advocate_passed: boolean;
  pdf_url: string;
  sigstore_hash: string;
}

export interface Evento {
  timestamp: number;
  descripcion: string;
  posicion?: { lat: number; lon: number };
}

export interface CalculoFisico {
  nombre: string;
  formula: string;
  valor: number;
  unidad: string;
  justificacion: string;
}

export interface Infraccion {
  articulo: string;
  descripcion: string;
  vehiculo: "A" | "B";
  fuente: string;
}

// API Client
export const api = {
  // Casos
  async getCasos(): Promise<Caso[]> {
    const res = await fetch(`${API_BASE}/api/casos`);
    if (!res.ok) throw new Error("Error fetching casos");
    return res.json();
  },

  async getCaso(id: string): Promise<Caso> {
    const res = await fetch(`${API_BASE}/api/casos/${id}`);
    if (!res.ok) throw new Error("Error fetching caso");
    return res.json();
  },

  async crearCaso(data: Partial<Caso>): Promise<Caso> {
    const res = await fetch(`${API_BASE}/api/casos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Error creating caso");
    return res.json();
  },

  // Upload
  async uploadAtestado(casoId: string, file: File): Promise<void> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/upload/atestado`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Error uploading atestado");
  },

  async uploadFoto(casoId: string, file: File): Promise<void> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/upload/foto`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Error uploading foto");
  },

  // Analisis
  async analizarCaso(casoId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/analizar`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Error starting analysis");
  },

  async getEstado(casoId: string): Promise<{ estado: string; progreso: number }> {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/estado`);
    if (!res.ok) throw new Error("Error fetching estado");
    return res.json();
  },

  async getDictamen(casoId: string): Promise<Resultado> {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/dictamen`);
    if (!res.ok) throw new Error("Error fetching dictamen");
    return res.json();
  },

  async downloadPdf(casoId: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/pdf`);
    if (!res.ok) throw new Error("Error downloading PDF");
    return res.blob();
  },

  // Demo
  async getDemoCasos(): Promise<Caso[]> {
    const res = await fetch(`${API_BASE}/api/demo/casos`);
    if (!res.ok) throw new Error("Error fetching demo casos");
    return res.json();
  },

  async resetDemoCaso(casoId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/demo/casos/${casoId}/reset`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Error resetting demo caso");
  },
};

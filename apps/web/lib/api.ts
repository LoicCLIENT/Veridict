import type {
  Caso,
  CasoCreate,
  Resultado,
  EstadoAnalisis,
  InformePericial as InformePericialT,
  RazonamientoOrquestador as RazonamientoOrquestadorT,
} from "@veridict/types";

export type {
  Caso,
  CasoCreate,
  Resultado,
  EstadoAnalisis,
  Vehiculo,
  Documento,
  Foto,
  Evento,
  CalculoFisico,
  Infraccion,
  Veredicto,
  CompatibilidadVersiones,
  VerificacionAdversarial,
  ContrastVersiones,
  NexoCausal,
  GravedadInfraccion,
  TipoNexo,
  Contexto,
  MeteoData,
  ViaData,
  SolData,
  EstadoCaso,
  TipoColision,
  Ubicacion,
  HuellaCalzada,
  DanoSecundario,
  EscenaAccidente,
  TipoHuella,
  CurvaturaHuella,
  TipoDanoSecundario,
  Encargo,
  TipoEncargo,
  ParteSolicitante,
  IdentificacionVehiculo,
  HechosAtestado,
  VelocidadDeclarada,
  Lesion,
  GravedadLesion,
  InformePericial,
  RespuestaPregunta,
  InfoFaltante,
  PrioridadInfoFaltante,
  FichaTecnicaVehiculo,
  FuenteNormativa,
  MensajeChat,
  Cita,
  RespuestaPeritoInput,
} from "@veridict/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handle<T>(res: Response, msg: string): Promise<T> {
  if (!res.ok) throw new Error(`${msg} (${res.status})`);
  return res.json() as Promise<T>;
}

export const api = {
  // Casos
  getCasos: (): Promise<Caso[]> =>
    fetch(`${API_BASE}/api/casos`).then((r) => handle<Caso[]>(r, "Error fetching casos")),

  getCaso: (id: string): Promise<Caso> =>
    fetch(`${API_BASE}/api/casos/${id}`).then((r) => handle<Caso>(r, "Error fetching caso")),

  crearCaso: (data: CasoCreate): Promise<Caso> =>
    fetch(`${API_BASE}/api/casos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => handle<Caso>(r, "Error creating caso")),

  importarCasoJson: async (file: File): Promise<Caso> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/casos/import-json`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      let detail = "";
      try { detail = (await res.json()).detail || ""; } catch {}
      throw new Error(`Error importando JSON (${res.status})${detail ? `: ${detail}` : ""}`);
    }
    return res.json();
  },

  // Upload
  uploadAtestado: async (casoId: string, file: File): Promise<void> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/upload/atestado`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Error uploading atestado (${res.status})`);
  },

  uploadFoto: async (casoId: string, file: File): Promise<{
    foto_id: string; url: string; tipo?: string | null;
    vehiculo_id?: string | null; descripcion?: string | null;
    tags?: string[]; indexada?: boolean;
  }> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/upload/foto`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Error uploading foto (${res.status})`);
    return res.json();
  },

  // Análisis
  iniciarAnalisis: async (casoId: string): Promise<void> => {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/analizar`, { method: "POST" });
    if (!res.ok) throw new Error(`Error starting analysis (${res.status})`);
  },

  getEstado: (casoId: string): Promise<EstadoAnalisis> =>
    fetch(`${API_BASE}/api/casos/${casoId}/estado`).then((r) =>
      handle<EstadoAnalisis>(r, "Error fetching estado")
    ),

  getDictamen: (casoId: string): Promise<Resultado> =>
    fetch(`${API_BASE}/api/casos/${casoId}/dictamen`).then((r) =>
      handle<Resultado>(r, "Error fetching dictamen")
    ),

  downloadPdf: async (casoId: string): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/api/casos/${casoId}/pdf`);
    if (!res.ok) throw new Error(`Error downloading PDF (${res.status})`);
    return res.blob();
  },

  // ── Peritaje v2: informe estructurado + chat info faltante ────────────────
  generarInforme: (casoId: string): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/informe`, { method: "POST" }).then((r) =>
      handle<InformePericialT>(r, "Error generando informe")
    ),

  getInforme: (casoId: string): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/informe`).then((r) =>
      handle<InformePericialT>(r, "Error obteniendo informe")
    ),

  regenerarSimulacion: (casoId: string): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/simulacion`, { method: "POST" }).then((r) =>
      handle<InformePericialT>(r, "Error regenerando simulación")
    ),

  getRazonamiento: (casoId: string): Promise<RazonamientoOrquestadorT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/razonamiento`).then((r) =>
      handle<RazonamientoOrquestadorT>(r, "Error obteniendo razonamiento")
    ),

  responderInfoFaltante: (
    casoId: string,
    infoId: string,
    respuesta: string
  ): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/responder-incremental`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ info_id: infoId, respuesta }),
    }).then((r) => handle<InformePericialT>(r, "Error enviando respuesta")),

  // Flujo incremental por pasos (con progreso visible en UI)
  iniciarRespuestaIncremental: (
    casoId: string,
    infoId: string,
    respuesta: string
  ): Promise<{ informe: InformePericialT; afecta_a: string[] }> =>
    fetch(`${API_BASE}/api/casos/${casoId}/responder-start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ info_id: infoId, respuesta }),
    }).then((r) =>
      handle<{ informe: InformePericialT; afecta_a: string[] }>(
        r,
        "Error iniciando respuesta"
      )
    ),

  editarPasoIncremental: (
    casoId: string,
    infoId: string,
    preguntaId: string
  ): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/responder-edit-step`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ info_id: infoId, pregunta_id: preguntaId }),
    }).then((r) => handle<InformePericialT>(r, "Error editando respuesta")),

  // Edición manual del perito sobre una respuesta del informe (sin LLM)
  editarRespuesta: (
    casoId: string,
    preguntaId: string,
    cambios: { respuesta?: string; confianza?: number },
  ): Promise<InformePericialT> =>
    fetch(`${API_BASE}/api/casos/${casoId}/informe/respuesta/${preguntaId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cambios),
    }).then((r) => handle<InformePericialT>(r, "Error editando respuesta")),

  health: async (): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
      return res.ok;
    } catch {
      return false;
    }
  },
};

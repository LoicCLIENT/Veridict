// Wizard Types - Veridict Case Creation
export type TipoEncargoUI =
  | "responsabilidad_trafico"
  | "velocidad_impacto"
  | "seguridad_pasiva"
  | "mecanica_fallo"
  | "atropello"
  | "cuantia_danos"
  | "otro";

export type ParteUI = "demandante" | "demandado" | "imparcial" | "aseguradora";

export type FuenteVelocidad = "declaracion_conductor" | "tacografo" | "edr" | "testigo" | "otro";

export interface VehiculoForm {
  id: string;
  matricula: string;
  marca: string;
  modelo: string;
  anio: string;
  color: string;
  conductor: string;
}

export interface VelocidadForm {
  vehiculo_id: string;
  valor_kmh: string;
  fuente: FuenteVelocidad;
}

export interface LesionForm {
  ocupante: string;
  vehiculo_id: string;
  zona_corporal: string;
  gravedad: "leve" | "moderada" | "grave" | "muy_grave" | "fallecimiento";
  dias_baja: string;
}

export interface EncargoForm {
  tipo: TipoEncargoUI;
  preguntas: string[];
  solicitante: string;
  parte: ParteUI;
  procedimiento: string;
  observaciones: string;
}

export interface SiniestroForm {
  fecha_accidente: string;
  hora_accidente: string;
  tipo_colision: string;
  direccion: string;
  lat: string;
  lon: string;
}

export interface AtestadoForm {
  numero_atestado: string;
  cuerpo_actuante: string;
  hay_huellas_frenada: "si" | "no" | "no_consta";
  condiciones_meteorologicas: string;
  estado_calzada: string;
  visibilidad: string;
  declaraciones: string;
}

export interface FilesForm {
  atestado?: File;
  fotos: File[];
  informeMedico?: File;
  presupuesto?: File;
  otros: File[];
}

export interface WizardData {
  encargo: EncargoForm;
  siniestro: SiniestroForm;
  vehiculos: VehiculoForm[];
  atestado: AtestadoForm;
  velocidades: VelocidadForm[];
  lesiones: LesionForm[];
  files: FilesForm;
}

export const ENCARGO_PRESETS: Record<TipoEncargoUI, {
  label: string;
  labelEs: string;
  icon: string;
  description: string;
  preguntasSugeridas: string[]
}> = {
  responsabilidad_trafico: {
    label: "Liability",
    labelEs: "Responsabilidad",
    icon: "⚖️",
    description: "Determine which party caused the accident",
    preguntasSugeridas: [
      "Which vehicle committed the violation that caused the accident?",
      "Which traffic regulations are applicable?",
    ],
  },
  velocidad_impacto: {
    label: "Impact Speed",
    labelEs: "Velocidad",
    icon: "🚀",
    description: "Calculate collision speed from evidence",
    preguntasSugeridas: [
      "At what speed was each vehicle traveling at the time of collision?",
      "Is the declared speed compatible with the observed dynamics?",
    ],
  },
  seguridad_pasiva: {
    label: "Safety Systems",
    labelEs: "Seguridad Pasiva",
    icon: "🛡️",
    description: "Airbag deployment, seatbelt analysis",
    preguntasSugeridas: [
      "Should the airbag have deployed?",
      "Would the injuries have been different if it had functioned properly?",
    ],
  },
  mecanica_fallo: {
    label: "Mechanical Failure",
    labelEs: "Fallo Mecánico",
    icon: "🔧",
    description: "Pre-accident mechanical defects",
    preguntasSugeridas: ["Is there evidence of a mechanical failure prior to the accident?"],
  },
  atropello: {
    label: "Pedestrian",
    labelEs: "Atropello",
    icon: "🚶",
    description: "Pedestrian collision reconstruction",
    preguntasSugeridas: [
      "At what speed did the pedestrian collision occur?",
      "Was the collision avoidable under diligent driving conditions?",
    ],
  },
  cuantia_danos: {
    label: "Damage Assessment",
    labelEs: "Cuantía de Daños",
    icon: "💰",
    description: "Repair cost proportionality analysis",
    preguntasSugeridas: ["Is the repair estimate proportional to the observed damage?"],
  },
  otro: {
    label: "Other",
    labelEs: "Otro",
    icon: "📋",
    description: "Custom expert analysis",
    preguntasSugeridas: [],
  },
};

export const WIZARD_STEPS = [
  { id: 1, title: "Assignment", titleEs: "Encargo", description: "Type of expertise" },
  { id: 2, title: "Questions", titleEs: "Preguntas", description: "What to analyze" },
  { id: 3, title: "Incident", titleEs: "Siniestro", description: "When and where" },
  { id: 4, title: "Vehicles", titleEs: "Vehículos", description: "Parties involved" },
  { id: 5, title: "Evidence", titleEs: "Evidencias", description: "Photos & documents" },
] as const;

/**
 * Shared TypeScript types for Veridict AI.
 * Aligned with apps/api/models.py (Pydantic).
 */

export type EstadoCaso = 'creado' | 'procesando' | 'completado' | 'escalado_humano';

export type TipoColision = 'frontal' | 'lateral' | 'alcance' | 'atropello';

export interface Ubicacion {
  lat: number;
  lon: number;
}

export interface Vehiculo {
  id: 'A' | 'B' | string;
  matricula: string;
  modelo: string;
  masa_kg: number;
  coef_rigidez_a: number;
  coef_rigidez_b: number;
  mediciones_C: number[];
  ancho_zona_danada_cm: number;
  longitud_frenada_m?: number | null;
  longitud_huellas_post_impacto_m?: number | null;
  version_conductor: string;
  posicion_final?: [number, number] | null;
  airbag_desplegado?: boolean | null;
  edr_velocidad_kmh?: number | null;
  angulo_aproximacion_deg?: number | null;
}

export interface Documento {
  id: string;
  tipo: 'atestado' | 'parte_amistoso' | string;
  url: string;
  numero_atestado?: string | null;
  texto_extraido?: string | null;
}

export interface Foto {
  id: string;
  url: string;
  descripcion?: string | null;
  analisis?: string | null;
}

export interface Evento {
  timestamp: number;
  descripcion: string;
  posicion?: Ubicacion | null;
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
  vehiculo: 'A' | 'B' | string;
  fuente: string;
}

export interface ContrastVersiones {
  vehiculo_id: string;
  velocidad_declarada_kmh?: number | null;
  velocidad_calculada_kmh?: number | null;
  compatible: boolean;
  observacion: string;
}

export type GravedadInfraccion = 'muy_grave' | 'grave' | 'leve' | string;
export type TipoNexo = 'causa_eficiente' | 'concurrente' | 'sin_nexo' | string;

export interface NexoCausal {
  vehiculo: 'A' | 'B' | string;
  articulo: string;
  gravedad: GravedadInfraccion;
  nexo: TipoNexo;
  justificacion: string;
}

export interface Veredicto {
  culpa_a: number;
  culpa_b: number;
  confidence: number;
  razonamiento?: string;
  advertencia_personal?: boolean;
  nexo_causal?: NexoCausal[];
}

export interface CompatibilidadVersiones {
  a: boolean;
  b: boolean;
  justificacion: string;
}

export interface VerificacionAdversarial {
  passed: boolean;
  failures: string[];
}

// ── Contexto externo ─────────────────────────────────────────────────────────

export interface MeteoData {
  temperatura?: number | null;
  humedad?: number | null;
  precipitacion?: number | null;
  viento_velocidad?: number | null;
  viento_direccion?: string | null;
  visibilidad?: string | null;
  nubosidad?: string | null;
  estado_tiempo?: string | null;
  fuente?: string | null;
}

export interface ViaData {
  tipo_via?: string | null;
  nombre_via?: string | null;
  velocidad_maxima?: number | null;
  num_carriles?: number | null;
  superficie?: string | null;
  iluminacion?: string | null;
  fuente?: string | null;
}

export interface SolData {
  azimuth?: number | null;
  altitude?: number | null;
  es_dia?: boolean | null;
  hora_amanecer?: string | null;
  hora_atardecer?: string | null;
  deslumbramiento_posible?: boolean | null;
}

export interface Contexto {
  direccion?: string | null;
  municipio?: string | null;
  provincia?: string | null;
  meteo?: MeteoData | null;
  via?: ViaData | null;
  sol?: SolData | null;
}

// ── Resultado ────────────────────────────────────────────────────────────────

export interface Resultado {
  cronologia: Evento[];
  calculos: CalculoFisico[];
  infracciones: Infraccion[];
  contraste_versiones?: ContrastVersiones[];
  veredicto?: Veredicto;
  compatibilidad_versiones?: CompatibilidadVersiones;
  verificacion_adversarial?: VerificacionAdversarial;
  contexto?: Contexto;
  pdf_url?: string | null;
  sigstore_hash?: string | null;
}

// ── Escena (huellas, daños secundarios) ──────────────────────────────────────

export type TipoHuella = 'frenada' | 'derrape' | 'arrastre' | 'aceleracion' | string;
export type CurvaturaHuella = 'recta' | 'curva_derecha' | 'curva_izquierda' | string;

export interface HuellaCalzada {
  vehiculo_id: string;
  tipo: TipoHuella;
  longitud_m: number;
  curvatura: CurvaturaHuella;
  inicio: [number, number];
  fin: [number, number];
  ancho_cm?: number | null;
  observaciones?: string | null;
}

export type TipoDanoSecundario =
  | 'vehiculo_aparcado'
  | 'valla'
  | 'arbol'
  | 'bordillo'
  | 'señal'
  | 'muro'
  | 'otro'
  | string;

export interface DanoSecundario {
  tipo: TipoDanoSecundario;
  posicion: [number, number];
  lado_calzada: 'izquierda' | 'derecha' | 'mediana' | string;
  descripcion: string;
  vehiculo_causante?: string | null;
}

export interface EscenaAccidente {
  punto_impacto_lat?: number | null;
  punto_impacto_lon?: number | null;
  angulo_impacto_deg?: number | null;
  ancho_carril_m?: number | null;
  distancia_visibilidad_m?: number | null;
  estado_asfalto?: string | null;
  señalizacion_visible?: string | null;
  observaciones_perito?: string | null;
  orientacion_final_a_deg?: number | null;
  orientacion_final_b_deg?: number | null;
  huellas: HuellaCalzada[];
  daños_secundarios: DanoSecundario[];
}

// ── Caso ─────────────────────────────────────────────────────────────────────

export interface Caso {
  id: string;
  estado: EstadoCaso;
  fecha_accidente: string;
  ubicacion: Ubicacion;
  tipo_colision: TipoColision;
  vehiculos: Vehiculo[];
  documentos: Documento[];
  fotos: Foto[];
  escena?: EscenaAccidente | null;
  contexto?: Contexto | null;
  resultado?: Resultado | null;
  created_at?: string;
  updated_at?: string;
}

export interface CasoCreate {
  fecha_accidente: string;
  ubicacion: Ubicacion;
  tipo_colision: TipoColision;
}

export interface EstadoAnalisis {
  estado: string;
  progreso: number;
  etapa_actual?: string | null;
}

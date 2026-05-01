/**
 * Shared TypeScript types for Veridict AI
 */

export type EstadoCaso = 'creado' | 'procesando' | 'completado' | 'escalado_humano';

export type TipoColision = 'frontal' | 'lateral' | 'alcance' | 'atropello';

export interface Ubicacion {
  lat: number;
  lon: number;
}

export interface Vehiculo {
  id: 'A' | 'B';
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
  tipo: 'atestado' | 'parte_amistoso';
  url: string;
  texto_extraido?: string;
}

export interface Foto {
  id: string;
  url: string;
  analisis?: string;
}

export interface Evento {
  timestamp: number;
  descripcion: string;
  posicion?: Ubicacion;
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
  vehiculo: 'A' | 'B';
  fuente: string;
}

export interface Veredicto {
  culpa_a: number;
  culpa_b: number;
  confidence: number;
}

export interface CompatibilidadVersiones {
  a: boolean;
  b: boolean;
  justificacion: string;
}

export interface MeteoData {
  temperatura?: number;
  humedad?: number;
  precipitacion?: number;
  viento_velocidad?: number;
  viento_direccion?: string;
  visibilidad?: string;
}

export interface ViaData {
  tipo_via?: string;
  velocidad_maxima?: number;
  num_carriles?: number;
  estado_pavimento?: string;
  iluminacion?: string;
}

export interface SolData {
  azimuth?: number;
  altitude?: number;
  es_dia?: boolean;
}

export interface Contexto {
  meteo?: MeteoData;
  via?: ViaData;
  sol?: SolData;
}

export interface Resultado {
  cronologia: Evento[];
  calculos: CalculoFisico[];
  infracciones: Infraccion[];
  veredicto?: Veredicto;
  compatibilidad_versiones?: CompatibilidadVersiones;
  devils_advocate_passed: boolean;
  pdf_url?: string;
  sigstore_hash?: string;
}

export interface Caso {
  id: string;
  estado: EstadoCaso;
  fecha_accidente: string;
  ubicacion: Ubicacion;
  tipo_colision: TipoColision;
  vehiculos: Vehiculo[];
  documentos: Documento[];
  fotos: Foto[];
  contexto?: Contexto;
  resultado?: Resultado;
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
  etapa_actual?: string;
}

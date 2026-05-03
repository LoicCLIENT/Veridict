/**
 * Shared TypeScript types for Veridict AI.
 * Aligned with apps/api/models.py (Pydantic).
 */

export type EstadoCaso = 'creado' | 'procesando' | 'completado' | 'escalado_humano';

export type TipoColision = 'frontal' | 'lateral' | 'alcance' | 'atropello';

export interface Ubicacion {
  lat: number;
  lon: number;
  direccion?: string | null;
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

export type TipoFoto =
  | 'vehiculo_frontal'
  | 'vehiculo_trasero'
  | 'vehiculo_lateral_izq'
  | 'vehiculo_lateral_dch'
  | 'vehiculo_detalle_dano'
  | 'vehiculo_interior'
  | 'vehiculo_general'
  | 'escena_general'
  | 'escena_huellas'
  | 'escena_senalizacion'
  | 'atestado_pagina'
  | 'croquis'
  | 'lesion'
  | 'otro';

export interface Foto {
  id: string;
  url: string;
  descripcion?: string | null;
  analisis?: string | null;
  tipo?: TipoFoto | null;
  tags?: string[];
  vehiculo_id?: string | null;
  elementos_visibles?: string[];
  calidad?: string | null;
  indexada?: boolean;
  error_indexacion?: string | null;
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
  // ── Input v2 ────────────────────────────────────────────────────────
  encargo?: Encargo | null;
  vehiculos_identificacion?: IdentificacionVehiculo[];
  hechos_atestado?: HechosAtestado | null;
  lesiones?: Lesion[];
  // ── Output v2 ───────────────────────────────────────────────────────
  informe?: InformePericial | null;
  // ── Metadatos ───────────────────────────────────────────────────────
  created_at?: string;
  updated_at?: string;
  // Payload original del formulario / import JSON (forma de CasoCreate)
  formulario_origen?: CasoCreate | null;
}

export interface CasoCreate {
  fecha_accidente: string;
  ubicacion: Ubicacion;
  tipo_colision: TipoColision;
  encargo?: Encargo;
  vehiculos_identificacion?: IdentificacionVehiculo[];
  hechos_atestado?: HechosAtestado;
  lesiones?: Lesion[];
}

// ── Encargo pericial ─────────────────────────────────────────────────────────

export type TipoEncargo =
  | 'responsabilidad_trafico'
  | 'velocidad_impacto'
  | 'seguridad_pasiva'
  | 'mecanica_fallo'
  | 'atropello'
  | 'cuantia_danos'
  | 'otro';

export type ParteSolicitante = 'demandante' | 'demandado' | 'imparcial' | 'aseguradora';

export interface Encargo {
  tipo: TipoEncargo;
  preguntas: string[];
  solicitante?: string;
  parte?: ParteSolicitante;
  procedimiento?: string;
  observaciones?: string;
}

// ── Identificación mínima del vehículo (lo que el perito SÍ aporta) ──────────

export interface IdentificacionVehiculo {
  id: 'A' | 'B' | string;
  matricula?: string;
  marca: string;
  modelo: string;
  anio?: number;
  color?: string;
  conductor?: string;
}

// ── Hechos verificables del atestado ─────────────────────────────────────────

export interface VelocidadDeclarada {
  vehiculo_id: string;
  valor_kmh: number;
  fuente: 'declaracion_conductor' | 'tacografo' | 'edr' | 'testigo' | 'otro';
}

export interface HechosAtestado {
  numero_atestado?: string;
  cuerpo_actuante?: 'guardia_civil' | 'policia_local' | 'policia_nacional' | 'mossos' | 'ertzaintza' | string;
  velocidades_declaradas?: VelocidadDeclarada[];
  hay_huellas_frenada?: boolean;
  condiciones_meteorologicas?: string;
  estado_calzada?: string;
  visibilidad?: string;
  declaraciones?: string;
  observaciones?: string;
}

// ── Lesiones ─────────────────────────────────────────────────────────────────

export type GravedadLesion = 'leve' | 'moderada' | 'grave' | 'muy_grave' | 'fallecimiento';

export interface Lesion {
  ocupante: string;
  vehiculo_id?: string;
  zona_corporal: string;
  gravedad: GravedadLesion;
  dias_baja?: number;
  secuelas?: string;
}

// ── Informe pericial v2 (output) ─────────────────────────────────────────────

export interface FichaTecnicaVehiculo {
  vehiculo_id: string;
  marca: string;
  modelo: string;
  anio?: number | null;
  masa_kg?: number | null;
  longitud_m?: number | null;
  ancho_m?: number | null;
  altura_m?: number | null;
  altura_parachoques_m?: [number, number] | null;
  altura_largueros_m?: number | null;
  rigidez_a?: number | null;
  rigidez_b?: number | null;
  sistemas_seguridad: string[];
  fuente?: string | null;
  notas?: string | null;
}

export interface FuenteNormativa {
  referencia: string;
  titulo: string;
  boe?: string | null;
  extracto?: string | null;
}

export interface Cita {
  tipo: 'calculo' | 'normativa' | 'ficha_tecnica' | 'hecho' | string;
  referencia: string;
  extracto?: string | null;
}

export interface RespuestaPregunta {
  pregunta_id: string;       // "C1", "C2"
  pregunta: string;
  respuesta: string;
  confianza: number;
  citas: Cita[];
}

export type PrioridadInfoFaltante = 'bloqueante' | 'recomendable' | 'mejora';

export interface InfoFaltante {
  id: string;                // "Q1", "Q2"
  pregunta: string;
  motivo: string;
  prioridad: PrioridadInfoFaltante;
  afecta_a: string[];        // ids de respuestas afectadas
  respondida: boolean;
  respuesta_perito?: string | null;
  requiere_foto?: boolean;
}

export interface MensajeChat {
  rol: 'claude' | 'perito' | string;
  contenido: string;
  timestamp?: string;
  referencia_info_id?: string | null;
}

export interface ImagenAnalizada {
  url?: string | null;
  thumb_url?: string | null;
  descripcion?: string | null;
  fuente: string;
  captured_at?: string | null;
  compass_angle?: number | null;
  lat?: number | null;
  lon?: number | null;
  relevancia?: string | null;
}

export interface ToolCallLog {
  id: string;
  agente: string;
  pregunta: string;
  inputs: Record<string, unknown>;
  resultado_resumen?: string | null;
  fuentes_consultadas: string[];
  imagenes: ImagenAnalizada[];
  falta_info?: string | null;
  requiere_foto: boolean;
  duracion_ms?: number | null;
  timestamp?: string;
}

// ── SimulationAgent: escena cenital animable ─────────────────────────────────

export type TipoActorSimulacion =
  | 'turismo'
  | 'motocicleta'
  | 'bicicleta'
  | 'peaton'
  | 'ciclomotor'
  | 'camion'
  | 'autobus'
  | 'mobiliario_urbano';

export type TipoViaSimulacion =
  | 'recta'
  | 'curva'
  | 'interseccion'
  | 'urbana_estrecha'
  | 'autovia';

export type TipoObstaculoEscena =
  | 'edificio'
  | 'muro'
  | 'zona_terriza'
  | 'talud'
  | 'poste'
  | 'farola'
  | 'senal'
  | 'vegetacion'
  | 'acera'
  | 'bordillo'
  | 'quitamiedos'
  | 'barrera'
  | 'otro';

export interface TrayectoriaPunto {
  x: number;
  y: number;
  t: number;          // segundos
  v_kmh: number;
  rotation_deg?: number | null;
  frenando?: boolean | null;
}

export interface ActorSimulacion {
  id: string;
  tipo: TipoActorSimulacion;
  etiqueta: string;
  color?: string | null;
  largo_m: number;
  ancho_m: number;
  masa_kg?: number | null;
  trayectoria: TrayectoriaPunto[];
  velocidad_inicial_kmh?: number | null;
  velocidad_impacto_kmh?: number | null;
  frena_desde_t?: number | null;
}

export interface ObstaculoEscena {
  tipo: TipoObstaculoEscena;
  poligono: Array<[number, number]>;
  altura_m?: number | null;
  limita_visibilidad?: boolean;
  descripcion?: string | null;
}

export interface HuellaSimulacion {
  actor_id?: string | null;
  tipo: 'frenada' | 'derrape' | 'arrastre' | string;
  inicio: [number, number];
  fin: [number, number];
  longitud_m?: number | null;
}

export interface ViaSimulacion {
  tipo: TipoViaSimulacion;
  carriles: number;
  ancho_carril_m: number;
  ancho_total_m?: number | null;
  limite_kmh: number;
  pendiente_pct?: number | null;
  superficie?: string | null;
  sentido_unico?: boolean | null;
  /** Eje central de la calzada. Si tiene ≥2 puntos, el renderer dibuja la
   *  vía siguiendo este path con stroke-width = ancho_total_m. Vacío = recta horizontal. */
  eje_via?: Array<[number, number]>;
}

export interface ImpactoSimulacion {
  x: number;
  y: number;
  t: number;
  angulo_deg: number;
  delta_v_por_actor: Record<string, number>;
}

export interface MetaEscenaSimulacion {
  meteo?: string | null;
  condicion_calzada?: string | null;
  visibilidad_m?: number | null;
  direccion?: string | null;
  lat?: number | null;
  lon?: number | null;
  es_dia?: boolean | null;
}

export interface EscenaSimulacionData {
  via: ViaSimulacion;
  actores: ActorSimulacion[];
  impacto?: ImpactoSimulacion | null;
  obstaculos?: ObstaculoEscena[];
  huellas?: HuellaSimulacion[];
  meta: MetaEscenaSimulacion;
  duracion_s: number;
  falta_info?: string[];
  descripcion?: string | null;
}

export interface InformePericial {
  resumen_caso: string;
  fichas_tecnicas: FichaTecnicaVehiculo[];
  normativa_aplicable: FuenteNormativa[];
  bibliografia: string[];
  calculos: CalculoFisico[];
  cronologia: Evento[];
  respuestas: RespuestaPregunta[];
  info_faltante: InfoFaltante[];
  chat: MensajeChat[];
  tool_calls: ToolCallLog[];
  imagenes: ImagenAnalizada[];
  simulacion_escena?: EscenaSimulacionData | null;
  confianza_global: number;
  pdf_url?: string | null;
  sigstore_hash?: string | null;
}

export interface RespuestaPeritoInput {
  info_id: string;
  respuesta: string;
}

// ── Razonamiento del orquestador (trace turno a turno) ───────────────────────

export interface ToolCallTrace {
  tool: string;
  inputs: Record<string, unknown>;
  respuesta_resumen?: string | null;
  respuesta_completa?: Record<string, unknown> | null;
}

export interface TurnoOrquestador {
  turno: number;
  razonamiento: string;
  tools_pedidas: ToolCallTrace[];
  stop_reason?: string | null;
}

export type EstadoRazonamiento =
  | "iniciando"
  | "contexto_listo"
  | "llamando_perito"
  | "dispatch"
  | "cerrando"
  | "completado"
  | "error";

export interface RazonamientoOrquestador {
  caso_id: string;
  estado?: EstadoRazonamiento;
  mensaje?: string;
  error?: string | null;
  started_at?: string | null;
  updated_at?: string | null;
  en_vivo?: boolean;
  n_turnos: number;
  n_tool_calls: number;
  turnos: TurnoOrquestador[];
  /** JSON parcial del informe que va devolviendo el orquestador en su turno final.
   * Se rellena solo cuando el orquestador termina la fase de investigación. */
  informe_borrador?: Record<string, unknown> | null;
}

export interface EstadoAnalisis {
  estado: string;
  progreso: number;
  etapa_actual?: string | null;
}

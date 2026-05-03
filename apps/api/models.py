"""Pydantic models for the API."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EstadoCaso(str, Enum):
    CREADO = "creado"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ESCALADO_HUMANO = "escalado_humano"


class TipoColision(str, Enum):
    FRONTAL = "frontal"
    LATERAL = "lateral"
    ALCANCE = "alcance"
    ATROPELLO = "atropello"


class Ubicacion(BaseModel):
    lat: float
    lon: float
    direccion: Optional[str] = None  # "AP-9, p.k. 67,400 sentido Vigo"


class Vehiculo(BaseModel):
    id: str                          # "A" o "B"
    matricula: str = ""
    modelo: str = ""
    masa_kg: float = 0
    coef_rigidez_a: float = 0        # kPa — auto-lookup si es 0
    coef_rigidez_b: float = 0        # kPa/m — auto-lookup si es 0
    mediciones_C: list[float] = Field(default_factory=lambda: [0.0] * 6)  # C1-C6 en cm
    ancho_zona_danada_cm: float = 0
    longitud_frenada_m: Optional[float] = None   # para Stannard Baker
    longitud_huellas_post_impacto_m: Optional[float] = None  # recorrido tras el golpe
    version_conductor: str = ""
    # Datos de escena (perito)
    posicion_final: Optional[tuple[float, float]] = None   # (x, y) en metros desde PDI
    airbag_desplegado: Optional[bool] = None
    edr_velocidad_kmh: Optional[float] = None              # caja negra, si disponible
    angulo_aproximacion_deg: Optional[float] = None        # ángulo de llegada al impacto


class Documento(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tipo: str   # "atestado" | "parte_amistoso"
    url: str
    numero_atestado: Optional[str] = None
    texto_extraido: Optional[str] = None


class TipoFoto(str, Enum):
    VEHICULO_FRONTAL = "vehiculo_frontal"
    VEHICULO_TRASERO = "vehiculo_trasero"
    VEHICULO_LATERAL_IZQ = "vehiculo_lateral_izq"
    VEHICULO_LATERAL_DCH = "vehiculo_lateral_dch"
    VEHICULO_DETALLE_DANO = "vehiculo_detalle_dano"
    VEHICULO_INTERIOR = "vehiculo_interior"
    VEHICULO_GENERAL = "vehiculo_general"
    ESCENA_GENERAL = "escena_general"
    ESCENA_HUELLAS = "escena_huellas"
    ESCENA_SENALIZACION = "escena_senalizacion"
    ATESTADO_PAGINA = "atestado_pagina"
    CROQUIS = "croquis"
    LESION = "lesion"
    OTRO = "otro"


class Foto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    descripcion: Optional[str] = None
    analisis: Optional[str] = None
    # ── Indexación automática (visión Claude al subir) ─────────────────────
    tipo: Optional[TipoFoto] = None
    tags: list[str] = Field(default_factory=list)        # parabrisas_danado, capo_hundido…
    vehiculo_id: Optional[str] = None                    # "A", "B" o None
    elementos_visibles: list[str] = Field(default_factory=list)
    calidad: Optional[str] = None                        # alta | media | baja
    indexada: bool = False
    error_indexacion: Optional[str] = None


class Evento(BaseModel):
    timestamp: float       # segundos desde T0 (escala libre del relato)
    descripcion: str
    posicion: Optional[Ubicacion] = None
    # ── Anclaje visual a la simulación cenital ─────────────────────────────
    # Si el evento corresponde a un instante concreto de la EscenaSimulacionData,
    # `t_simulacion_s` lo alinea con su scrubber (0..duracion_s) y `frame_url`
    # apunta al SVG estático generado por el snapshot specialist.
    t_simulacion_s: Optional[float] = None
    frame_url: Optional[str] = None
    descripcion_visual: Optional[str] = None  # qué se está mostrando en el frame
    actor_principal_id: Optional[str] = None  # actor protagonista del evento


class TipoFuenteDato(str, Enum):
    ATESTADO = "atestado"
    EDR = "edr"
    TACOGRAFO = "tacografo"
    DECLARACION_CONDUCTOR = "declaracion_conductor"
    DECLARACION_TESTIGO = "declaracion_testigo"
    MEDICION_ESCENA = "medicion_escena"
    FOTO_ANALISIS = "foto_analisis"
    FICHA_TECNICA_DGT = "ficha_tecnica_dgt"
    FICHA_TECNICA_FABRICANTE = "ficha_tecnica_fabricante"
    BASE_DATOS_CRASH3 = "base_datos_crash3"
    CATALOGO_EUROPEO = "catalogo_europeo"
    CALCULO_DERIVADO = "calculo_derivado"
    ESTIMACION_PERICIAL = "estimacion_pericial"
    OTRO = "otro"


class CategoriaCalculo(str, Enum):
    VELOCIDAD = "velocidad"
    ENERGIA = "energia"
    FUERZA = "fuerza"
    TIEMPO = "tiempo"
    DISTANCIA = "distancia"
    MASA = "masa"
    OTRO = "otro"


class TipoReferencia(str, Enum):
    NORMATIVA = "normativa"
    PAPER = "paper"
    LIBRO = "libro"
    MANUAL = "manual"
    BASE_DATOS = "base_datos"


class DatoEntrada(BaseModel):
    """Input data point used in a calculation with source traceability."""
    nombre: str                     # "Masa vehículo A", "Longitud huella frenada"
    valor: float | str              # 1350 or "Sin ABS"
    unidad: Optional[str] = None    # "kg", "m"
    fuente: TipoFuenteDato = TipoFuenteDato.OTRO
    fuente_detalle: Optional[str] = None  # "Atestado nº 2024/1234, pág. 3"
    confianza: Optional[float] = None     # 0-1
    foto_id: Optional[str] = None         # Associated photo ID if applicable


class PasoMetodologico(BaseModel):
    """Step in the calculation methodology."""
    orden: int
    descripcion: str
    formula_parcial: Optional[str] = None
    resultado_parcial: Optional[str] = None
    notas: Optional[str] = None


class ReferenciaCalculo(BaseModel):
    """Scientific/normative reference for a calculation."""
    tipo: TipoReferencia = TipoReferencia.LIBRO
    titulo: str
    autores: Optional[str] = None
    anio: Optional[int] = None
    url: Optional[str] = None
    boe: Optional[str] = None       # For Spanish regulations
    extracto: Optional[str] = None  # Relevant excerpt
    pagina: Optional[str] = None


class CalculoFisico(BaseModel):
    """Physical calculation with full methodology traceability."""
    nombre: str
    formula: str
    valor: float
    unidad: str
    justificacion: str
    # ── Extended fields (optional for backwards compatibility) ──
    categoria: Optional[CategoriaCalculo] = None
    confianza: Optional[float] = None           # 0-1, confidence level
    metodo: Optional[str] = None                # "CRASH3", "Momentum conservation"
    datos_entrada: list[DatoEntrada] = Field(default_factory=list)
    pasos: list[PasoMetodologico] = Field(default_factory=list)
    referencias: list[ReferenciaCalculo] = Field(default_factory=list)
    validaciones: list[str] = Field(default_factory=list)   # Checks performed
    limitaciones: list[str] = Field(default_factory=list)   # Possible error sources
    sensibilidad: Optional[str] = None          # E.g., "±5% due to friction uncertainty"
    alternativas_consideradas: Optional[str] = None
    foto_ids: list[str] = Field(default_factory=list)  # Photos used in analysis
    timestamp: Optional[str] = None             # When the calculation was performed


class Infraccion(BaseModel):
    articulo: str
    descripcion: str
    vehiculo: str          # "A" o "B"
    fuente: str            # referencia BOE


class ContrastVersiones(BaseModel):
    """Contraste técnico entre la declaración del conductor y la evidencia física."""
    vehiculo_id: str
    velocidad_declarada_kmh: Optional[float] = None
    velocidad_calculada_kmh: Optional[float] = None
    compatible: bool
    observacion: str       # conclusión técnica objetiva, sin atribución de culpa


class NexoCausal(BaseModel):
    vehiculo: str           # "A" o "B"
    articulo: str
    gravedad: str           # "muy_grave" | "grave" | "leve"
    nexo: str               # "causa_eficiente" | "concurrente" | "sin_nexo"
    justificacion: str


class Veredicto(BaseModel):
    culpa_a: float          # 0.0 – 1.0 (proporción de responsabilidad)
    culpa_b: float          # culpa_a + culpa_b == 1.0
    confidence: float       # 0.0 – 0.95
    razonamiento: str = ""  # párrafo técnico-jurídico con base legal citada
    advertencia_personal: bool = False  # True → aplicar regla 100/100 TS daños personales
    nexo_causal: list[NexoCausal] = Field(default_factory=list)


class CompatibilidadVersiones(BaseModel):
    a: bool                 # True si la declaración de A es compatible con la física
    b: bool
    justificacion: str


class VerificacionAdversarial(BaseModel):
    passed: bool
    failures: list[str] = Field(default_factory=list)


# ── Datos de contexto externo ─────────────────────────────────────────────────

class MeteoData(BaseModel):
    temperatura: Optional[float] = None       # °C
    humedad: Optional[float] = None           # %
    precipitacion: Optional[float] = None     # mm/h
    viento_velocidad: Optional[float] = None  # km/h
    viento_direccion: Optional[str] = None    # N, NE, E...
    visibilidad: Optional[str] = None         # texto descriptivo
    nubosidad: Optional[str] = None           # % nubosidad
    estado_tiempo: Optional[str] = None       # "lluvia ligera", "despejado"...
    fuente: Optional[str] = None


class ViaData(BaseModel):
    tipo_via: Optional[str] = None
    nombre_via: Optional[str] = None
    velocidad_maxima: Optional[int] = None    # km/h
    num_carriles: Optional[int] = None
    superficie: Optional[str] = None         # asfalto, hormigón...
    iluminacion: Optional[str] = None
    fuente: Optional[str] = None


class SolData(BaseModel):
    azimuth: Optional[float] = None           # grados
    altitude: Optional[float] = None          # grados sobre el horizonte
    es_dia: Optional[bool] = None
    hora_amanecer: Optional[str] = None
    hora_atardecer: Optional[str] = None
    deslumbramiento_posible: Optional[bool] = None


class Contexto(BaseModel):
    direccion: Optional[str] = None           # "Calle X, 12, Madrid" (Nominatim)
    municipio: Optional[str] = None
    provincia: Optional[str] = None
    meteo: Optional[MeteoData] = None
    via: Optional[ViaData] = None
    sol: Optional[SolData] = None


# ── Resultado del análisis ────────────────────────────────────────────────────

class Resultado(BaseModel):
    cronologia: list[Evento] = Field(default_factory=list)
    calculos: list[CalculoFisico] = Field(default_factory=list)
    infracciones: list[Infraccion] = Field(default_factory=list)
    contraste_versiones: list[ContrastVersiones] = Field(default_factory=list)
    veredicto: Optional[Veredicto] = None
    compatibilidad_versiones: Optional[CompatibilidadVersiones] = None
    verificacion_adversarial: Optional[VerificacionAdversarial] = None
    contexto: Optional[Contexto] = None
    pdf_url: Optional[str] = None
    sigstore_hash: Optional[str] = None


# ── Caso ──────────────────────────────────────────────────────────────────────

class TipoHuella(str, Enum):
    FRENADA = "frenada"           # neumático bloqueado, línea recta
    DERRAPE = "derrape"           # yaw mark, curva — indica pérdida de control lateral
    ARRASTRE = "arrastre"         # post-impacto, vehículo desplazado sin rodar
    ACELERACION = "aceleracion"   # quemada de neumático, salida rápida


class CurvaturaHuella(str, Enum):
    RECTA = "recta"
    CURVA_DERECHA = "curva_derecha"
    CURVA_IZQUIERDA = "curva_izquierda"


class HuellaCalzada(BaseModel):
    """Marca dejada en el asfalto — clave para reconstruir la trayectoria real."""
    vehiculo_id: str                          # "A", "B" o "desconocido"
    tipo: TipoHuella
    longitud_m: float
    curvatura: CurvaturaHuella = CurvaturaHuella.RECTA
    inicio: tuple[float, float] = (0.0, 0.0)  # metros desde PDI
    fin: tuple[float, float] = (0.0, 0.0)
    ancho_cm: Optional[float] = None           # ancho de la huella (identifica eje)
    observaciones: Optional[str] = None


class TipoDañoSecundario(str, Enum):
    VEHICULO_APARCADO = "vehiculo_aparcado"
    VALLA = "valla"
    ARBOL = "arbol"
    BORDILLO = "bordillo"
    SEÑAL = "señal"
    MURO = "muro"
    OTRO = "otro"


class DañoSecundario(BaseModel):
    """Daño en elemento distinto a los vehículos principales — revela trayectoria post-impacto."""
    tipo: TipoDañoSecundario
    posicion: tuple[float, float]              # metros desde PDI
    lado_calzada: str                          # "izquierda" | "derecha" | "mediana"
    descripcion: str
    vehiculo_causante: Optional[str] = None    # "A", "B" o None si no está claro


class EscenaAccidente(BaseModel):
    """Datos recogidos por el perito en la escena del accidente."""
    punto_impacto_lat: Optional[float] = None
    punto_impacto_lon: Optional[float] = None
    angulo_impacto_deg: Optional[float] = None
    ancho_carril_m: Optional[float] = None
    distancia_visibilidad_m: Optional[float] = None
    estado_asfalto: Optional[str] = None
    señalizacion_visible: Optional[str] = None
    observaciones_perito: Optional[str] = None
    orientacion_final_a_deg: Optional[float] = None   # heading del vehículo A al detenerse
    orientacion_final_b_deg: Optional[float] = None   # heading del vehículo B al detenerse
    huellas: list[HuellaCalzada] = Field(default_factory=list)
    daños_secundarios: list[DañoSecundario] = Field(default_factory=list)


class Caso(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    estado: EstadoCaso = EstadoCaso.CREADO
    fecha_accidente: datetime
    ubicacion: Ubicacion
    tipo_colision: TipoColision
    vehiculos: list[Vehiculo] = Field(default_factory=list)
    documentos: list[Documento] = Field(default_factory=list)
    fotos: list[Foto] = Field(default_factory=list)
    escena: Optional[EscenaAccidente] = None
    resultado: Optional[Resultado] = None
    # ── Input v2 ────────────────────────────────────────────────────────────
    encargo: Optional["Encargo"] = None
    vehiculos_identificacion: list["IdentificacionVehiculo"] = Field(default_factory=list)
    hechos_atestado: Optional["HechosAtestado"] = None
    lesiones: list["Lesion"] = Field(default_factory=list)
    # ── Output v2 ───────────────────────────────────────────────────────────
    informe: Optional["InformePericial"] = None
    # ── Metadatos ───────────────────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Payload original del formulario (CasoCreate completo) tal cual lo envió
    # el frontend o el import JSON. Se conserva para poder revisarlo desde la UI.
    formulario_origen: Optional[dict] = None


# ── Request/Response helpers ──────────────────────────────────────────────────

# ── Encargo, identificación, hechos, lesiones (input v2) ──────────────────────

class TipoEncargo(str, Enum):
    RESPONSABILIDAD_TRAFICO = "responsabilidad_trafico"
    VELOCIDAD_IMPACTO = "velocidad_impacto"
    SEGURIDAD_PASIVA = "seguridad_pasiva"
    MECANICA_FALLO = "mecanica_fallo"
    ATROPELLO = "atropello"
    CUANTIA_DANOS = "cuantia_danos"
    OTRO = "otro"


class ParteSolicitante(str, Enum):
    DEMANDANTE = "demandante"
    DEMANDADO = "demandado"
    IMPARCIAL = "imparcial"
    ASEGURADORA = "aseguradora"


class Encargo(BaseModel):
    tipo: TipoEncargo = TipoEncargo.RESPONSABILIDAD_TRAFICO
    preguntas: list[str] = Field(default_factory=list)
    solicitante: Optional[str] = None
    parte: Optional[ParteSolicitante] = None
    procedimiento: Optional[str] = None
    observaciones: Optional[str] = None


class IdentificacionVehiculo(BaseModel):
    id: str = "A"
    matricula: Optional[str] = None
    marca: str
    modelo: str
    anio: Optional[int] = None
    color: Optional[str] = None
    conductor: Optional[str] = None


class FuenteVelocidad(str, Enum):
    DECLARACION = "declaracion_conductor"
    TACOGRAFO = "tacografo"
    EDR = "edr"
    TESTIGO = "testigo"
    OTRO = "otro"


class VelocidadDeclarada(BaseModel):
    vehiculo_id: str
    valor_kmh: float
    fuente: FuenteVelocidad = FuenteVelocidad.DECLARACION


class HechosAtestado(BaseModel):
    numero_atestado: Optional[str] = None
    cuerpo_actuante: Optional[str] = None
    velocidades_declaradas: list[VelocidadDeclarada] = Field(default_factory=list)
    hay_huellas_frenada: Optional[bool] = None
    condiciones_meteorologicas: Optional[str] = None
    estado_calzada: Optional[str] = None
    visibilidad: Optional[str] = None
    declaraciones: Optional[str] = None
    observaciones: Optional[str] = None


class GravedadLesion(str, Enum):
    LEVE = "leve"
    MODERADA = "moderada"
    GRAVE = "grave"
    MUY_GRAVE = "muy_grave"
    FALLECIMIENTO = "fallecimiento"


class Lesion(BaseModel):
    ocupante: str
    vehiculo_id: Optional[str] = None
    zona_corporal: str
    gravedad: GravedadLesion = GravedadLesion.LEVE
    dias_baja: Optional[int] = None
    secuelas: Optional[str] = None


# ── Output del peritaje (Informe v2) ─────────────────────────────────────────

class FichaTecnicaVehiculo(BaseModel):
    """Datos enriquecidos automáticamente desde la base de fichas técnicas."""
    vehiculo_id: str
    marca: str
    modelo: str
    anio: Optional[int] = None
    tipo_vehiculo: Optional[str] = None   # 'turismo', 'furgoneta', 'camion', 'bicicleta', 'motocicleta', 'peaton'
    masa_kg: Optional[float] = None
    longitud_m: Optional[float] = None
    ancho_m: Optional[float] = None
    altura_m: Optional[float] = None
    altura_parachoques_m: Optional[tuple[float, float]] = None  # (inf, sup)
    altura_largueros_m: Optional[float] = None
    rigidez_a: Optional[float] = None
    rigidez_b: Optional[float] = None
    sistemas_seguridad: list[str] = Field(default_factory=list)
    # Campos específicos de bicicleta (resto None si no aplica)
    altura_sillin_m: Optional[float] = None
    anchura_manillar_m: Optional[float] = None
    masa_ciclista_estimada_kg: Optional[float] = None
    fuente: Optional[str] = None
    notas: Optional[str] = None


class FuenteNormativa(BaseModel):
    referencia: str          # "Art. 74.1 RGC"
    titulo: str              # texto descriptivo
    boe: Optional[str] = None
    extracto: Optional[str] = None


class Cita(BaseModel):
    tipo: str                # "calculo" | "normativa" | "ficha_tecnica" | "hecho"
    referencia: str          # id del cálculo, art., etc.
    extracto: Optional[str] = None


class RespuestaPregunta(BaseModel):
    pregunta_id: str         # "C1", "C2", ...
    pregunta: str
    respuesta: str           # redacción pericial
    confianza: float = 0.0   # 0-1
    citas: list[Cita] = Field(default_factory=list)


class PrioridadInfoFaltante(str, Enum):
    BLOQUEANTE = "bloqueante"
    RECOMENDABLE = "recomendable"
    MEJORA = "mejora"


class InfoFaltante(BaseModel):
    """Pregunta que Claude le hace al perito para mejorar el informe."""
    id: str                                     # "Q1", "Q2"...
    pregunta: str
    motivo: str                                 # por qué le hace falta
    prioridad: PrioridadInfoFaltante = PrioridadInfoFaltante.RECOMENDABLE
    afecta_a: list[str] = Field(default_factory=list)   # ["C1", "C2"] preguntas afectadas
    respondida: bool = False
    respuesta_perito: Optional[str] = None
    requiere_foto: bool = False                # si True, el chat ofrece upload


class MensajeChat(BaseModel):
    rol: str                                    # "claude" | "perito"
    contenido: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    referencia_info_id: Optional[str] = None    # id de InfoFaltante al que responde


class ImagenAnalizada(BaseModel):
    """Imagen consultada/analizada por un agente — Mapillary, foto del perito, etc."""
    url: Optional[str] = None
    thumb_url: Optional[str] = None
    descripcion: Optional[str] = None      # qué se ve, según análisis del agente
    fuente: str = ""                       # "Mapillary", "perito", "atestado"...
    captured_at: Optional[str] = None
    compass_angle: Optional[float] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    relevancia: Optional[str] = None       # por qué se incluye en el informe


class ToolCallLog(BaseModel):
    """Registro de cada invocación que el Perito hace a un specialist."""
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    agente: str                            # "EscenaAgent", "FichaAgent"...
    pregunta: str                          # qué le ha pedido el Perito (resumido)
    inputs: dict = Field(default_factory=dict)
    resultado_resumen: Optional[str] = None
    fuentes_consultadas: list[str] = Field(default_factory=list)
    imagenes: list[ImagenAnalizada] = Field(default_factory=list)
    falta_info: Optional[str] = None       # si el agente no pudo, qué pide al perito
    requiere_foto: bool = False
    duracion_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WADResultado(BaseModel):
    zona_impacto: str
    altura_m: tuple[float, float]
    velocidad_min_kmh: float
    velocidad_max_kmh: float
    fuente: Optional[str] = None


class MecanismoLesivo(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    razon: Optional[str] = None


class ImpactoSucesivo(BaseModel):
    orden: int
    descripcion: str


class TipoLesionCraneal(BaseModel):
    nombre: str
    mecanismo: str


class AnalisisCraneal(BaseModel):
    mecanismo_general: str
    tipos_compatibles: list[TipoLesionCraneal] = Field(default_factory=list)
    consideracion_clinica: Optional[str] = None


class AceleracionTipo(BaseModel):
    situacion: str
    tiempo_parada: str
    aceleracion_g: float
    fuerza_n_1200kg: float


class AnalisisBiomecanico(BaseModel):
    """Salida estructurada del BiomecanicaAgent persistida en el informe."""
    wad: Optional[WADResultado] = None
    energia_cinetica_kj: Optional[float] = None
    probabilidad_ais3_pct: Optional[int] = None
    mecanismos_lesivos_compatibles: list[MecanismoLesivo] = Field(default_factory=list)
    cadena_4_impactos_sucesivos: list[ImpactoSucesivo] = Field(default_factory=list)
    analisis_craneal: Optional[AnalisisCraneal] = None
    compatibilidad_velocidad_lesion: Optional[str] = None
    tabla_aceleraciones_tipo: list[AceleracionTipo] = Field(default_factory=list)
    fuentes: list[str] = Field(default_factory=list)


class ContextoEscenaResumen(BaseModel):
    """Resumen estructurado de lo que devolvió EscenaAgent (OSM + Open-Elevation + Mapillary)."""
    direccion_resuelta: Optional[str] = None
    lat_resuelta: Optional[float] = None
    lon_resuelta: Optional[float] = None
    via_principal_nombre: Optional[str] = None
    via_principal_tipo: Optional[str] = None      # primary/secondary/residential…
    velocidad_maxima_kmh: Optional[int] = None    # de OSM maxspeed
    num_carriles: Optional[int] = None
    anchura_m: Optional[float] = None
    superficie: Optional[str] = None
    tiene_carril_bici: bool = False
    pasos_peatones_proximos: int = 0
    senales: list[dict] = Field(default_factory=list)
    pendiente_pct: Optional[float] = None
    pendiente_descartada_pct: Optional[float] = None  # DEM dio valor inverosímil (>30 %)
    elevacion_m: Optional[float] = None
    visibilidad_efectiva_m: Optional[float] = None    # medición in situ aportada por perito
    visibilidad_efectiva_fuente: Optional[str] = None  # 'in_situ', 'laser_3d', 'atestado'…
    n_imagenes_mapillary: int = 0
    fuentes: list[str] = Field(default_factory=list)


class ContextoMeteoResumen(BaseModel):
    temperatura_c: Optional[float] = None
    precipitacion_mm: Optional[float] = None
    viento_kmh: Optional[float] = None
    visibilidad_m: Optional[float] = None
    estado_tiempo: Optional[str] = None
    calzada_estimada: Optional[str] = None
    es_dia: Optional[bool] = None
    amanecer: Optional[str] = None
    atardecer: Optional[str] = None
    fuente: Optional[str] = None


class IncongruenciaAtestado(BaseModel):
    severidad: str                          # "alta" | "media" | "baja"
    titulo: str
    descripcion: str


class AnalisisConformidadAtestado(BaseModel):
    """Crítica metodológica del atestado policial."""
    incongruencias: list[IncongruenciaAtestado] = Field(default_factory=list)
    elementos_omitidos: list[str] = Field(default_factory=list)   # cosas que el atestado debió recoger
    valoracion_global: Optional[str] = None    # "satisfactorio" | "incompleto" | "deficiente"
    recomendaciones: list[str] = Field(default_factory=list)


class TipoActorSimulacion(str, Enum):
    TURISMO = "turismo"
    MOTOCICLETA = "motocicleta"
    BICICLETA = "bicicleta"
    PEATON = "peaton"
    CICLOMOTOR = "ciclomotor"
    CAMION = "camion"
    AUTOBUS = "autobus"
    MOBILIARIO_URBANO = "mobiliario_urbano"


class TipoViaSimulacion(str, Enum):
    RECTA = "recta"
    CURVA = "curva"
    INTERSECCION = "interseccion"
    URBANA_ESTRECHA = "urbana_estrecha"
    AUTOVIA = "autovia"


class TipoObstaculoEscena(str, Enum):
    EDIFICIO = "edificio"
    MURO = "muro"
    ZONA_TERRIZA = "zona_terriza"
    TALUD = "talud"
    POSTE = "poste"
    FAROLA = "farola"
    SENAL = "senal"
    VEGETACION = "vegetacion"
    ACERA = "acera"
    BORDILLO = "bordillo"
    QUITAMIEDOS = "quitamiedos"
    BARRERA = "barrera"
    OTRO = "otro"


class TrayectoriaPunto(BaseModel):
    """Un instante en la trayectoria de un actor (vista cenital, m/s/km/h)."""
    x: float                           # metros, eje E-O (norte = +Y)
    y: float                           # metros, eje N-S
    t: float                           # segundos desde t=0 (inicio animación)
    v_kmh: float                       # módulo velocidad
    rotation_deg: Optional[float] = None  # heading en grados (0 = +X / este)
    frenando: Optional[bool] = None


class ActorSimulacion(BaseModel):
    """Un interviniente con su geometría y trayectoria temporal."""
    id: str                                            # "turismo_seat", "ciclista_iurgi"
    tipo: TipoActorSimulacion
    etiqueta: str                                      # "SEAT Ibiza 3526-BKL"
    color: Optional[str] = None
    largo_m: float = 0.0
    ancho_m: float = 0.0
    masa_kg: Optional[float] = None
    trayectoria: list[TrayectoriaPunto] = Field(default_factory=list)
    velocidad_inicial_kmh: Optional[float] = None
    velocidad_impacto_kmh: Optional[float] = None
    frena_desde_t: Optional[float] = None              # segundos, primer instante con freno


class ObstaculoEscena(BaseModel):
    """Elemento estático que forma la escena (edificios, terrizas, mobiliario)."""
    tipo: TipoObstaculoEscena
    poligono: list[tuple[float, float]] = Field(default_factory=list)
    altura_m: Optional[float] = None
    limita_visibilidad: bool = False
    descripcion: Optional[str] = None


class HuellaSimulacion(BaseModel):
    """Marca en calzada para pintar (frenada, derrape, arrastre)."""
    actor_id: Optional[str] = None
    tipo: str                                          # frenada / derrape / arrastre
    inicio: tuple[float, float]
    fin: tuple[float, float]
    longitud_m: Optional[float] = None


class ViaSimulacion(BaseModel):
    tipo: TipoViaSimulacion = TipoViaSimulacion.RECTA
    carriles: int = 2
    ancho_carril_m: float = 3.5
    ancho_total_m: Optional[float] = None              # útil en urbana estrecha
    limite_kmh: int = 50
    pendiente_pct: Optional[float] = None              # signo: + ascendente para +X
    superficie: Optional[str] = None                   # asfalto, hormigón…
    sentido_unico: Optional[bool] = None
    # Eje central de la calzada. Lista de puntos `(x, y)` por los que pasa la
    # línea media de la vía. Cuando hay ≥2 puntos, el frontend dibuja la vía
    # siguiendo este path con `stroke-width = ancho_total_m`. Imprescindible
    # para curvas y trazados sinuosos. Si está vacío, el frontend asume vía
    # recta horizontal centrada en y=0.
    eje_via: list[tuple[float, float]] = Field(default_factory=list)


class ImpactoSimulacion(BaseModel):
    x: float
    y: float
    t: float                                           # segundos
    angulo_deg: float = 0.0
    delta_v_por_actor: dict[str, float] = Field(default_factory=dict)


class MetaEscenaSimulacion(BaseModel):
    meteo: Optional[str] = None
    condicion_calzada: Optional[str] = None
    visibilidad_m: Optional[float] = None
    direccion: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    es_dia: Optional[bool] = None


class EscenaSimulacionData(BaseModel):
    """Reconstrucción cenital animable del siniestro.

    La produce el SimulationAgent (LLM) tras el cierre del Perito y la
    consume `AccidentScene2D` en frontend para animar trayectorias con
    scrubber. Cada actor (turismo/bici/peatón/mobiliario) lleva su
    `trayectoria` por puntos `(x,y,t,v_kmh)` que el frontend interpola.
    """
    via: ViaSimulacion = Field(default_factory=ViaSimulacion)
    actores: list[ActorSimulacion] = Field(default_factory=list)
    impacto: Optional[ImpactoSimulacion] = None
    obstaculos: list[ObstaculoEscena] = Field(default_factory=list)
    huellas: list[HuellaSimulacion] = Field(default_factory=list)
    meta: MetaEscenaSimulacion = Field(default_factory=MetaEscenaSimulacion)
    duracion_s: float = 4.0                            # tiempo total de animación
    falta_info: list[str] = Field(default_factory=list)
    descripcion: Optional[str] = None                  # resumen 1-2 frases para tooltip


class InformePericial(BaseModel):
    """Resultado del peritaje v2: estructurado por preguntas del encargo."""
    resumen_caso: str = ""
    fichas_tecnicas: list[FichaTecnicaVehiculo] = Field(default_factory=list)
    normativa_aplicable: list[FuenteNormativa] = Field(default_factory=list)
    bibliografia: list[str] = Field(default_factory=list)
    calculos: list[CalculoFisico] = Field(default_factory=list)
    cronologia: list[Evento] = Field(default_factory=list)
    respuestas: list[RespuestaPregunta] = Field(default_factory=list)
    info_faltante: list[InfoFaltante] = Field(default_factory=list)
    chat: list[MensajeChat] = Field(default_factory=list)
    tool_calls: list[ToolCallLog] = Field(default_factory=list)
    imagenes: list[ImagenAnalizada] = Field(default_factory=list)
    analisis_biomecanico: Optional[AnalisisBiomecanico] = None
    contexto_escena: Optional[ContextoEscenaResumen] = None
    contexto_meteo: Optional[ContextoMeteoResumen] = None
    conformidad_atestado: Optional[AnalisisConformidadAtestado] = None
    simulacion_escena: Optional[EscenaSimulacionData] = None
    # Razonamiento completo del orquestador-perito y de cada specialist:
    # {"razonamiento_perito": [...turnos], "datos_completos": [...tool calls]}.
    # Se persiste en casos.json para poder revisar el trace tras reinicios.
    trace: Optional[dict] = None
    confianza_global: float = 0.0
    pdf_url: Optional[str] = None
    sigstore_hash: Optional[str] = None


# ── CRUD ────────────────────────────────────────────────────────────────────

class CasoCreate(BaseModel):
    fecha_accidente: datetime
    ubicacion: Ubicacion
    tipo_colision: TipoColision
    encargo: Optional[Encargo] = None
    vehiculos_identificacion: list[IdentificacionVehiculo] = Field(default_factory=list)
    hechos_atestado: Optional[HechosAtestado] = None
    lesiones: list[Lesion] = Field(default_factory=list)


class CasoUpdate(BaseModel):
    estado: Optional[EstadoCaso] = None
    vehiculos: Optional[list[Vehiculo]] = None


class RespuestaPeritoInput(BaseModel):
    """Lo que el perito responde al chat de info faltante."""
    info_id: str
    respuesta: str


class EstadoAnalisis(BaseModel):
    estado: str
    progreso: float        # 0-100
    etapa_actual: Optional[str] = None


class MedicionesInput(BaseModel):
    vehiculo_id: str
    mediciones_C: list[float]          # C1-C6 en cm
    longitud_frenada_m: Optional[float] = None
    ancho_zona_danada_cm: float

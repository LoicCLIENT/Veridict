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


class Foto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    descripcion: Optional[str] = None
    analisis: Optional[str] = None


class Evento(BaseModel):
    timestamp: float       # segundos desde T0
    descripcion: str
    posicion: Optional[Ubicacion] = None


class CalculoFisico(BaseModel):
    nombre: str
    formula: str
    valor: float
    unidad: str
    justificacion: str


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Request/Response helpers ──────────────────────────────────────────────────

class CasoCreate(BaseModel):
    fecha_accidente: datetime
    ubicacion: Ubicacion
    tipo_colision: TipoColision


class CasoUpdate(BaseModel):
    estado: Optional[EstadoCaso] = None
    vehiculos: Optional[list[Vehiculo]] = None


class EstadoAnalisis(BaseModel):
    estado: str
    progreso: float        # 0-100
    etapa_actual: Optional[str] = None


class MedicionesInput(BaseModel):
    vehiculo_id: str
    mediciones_C: list[float]          # C1-C6 en cm
    longitud_frenada_m: Optional[float] = None
    ancho_zona_danada_cm: float

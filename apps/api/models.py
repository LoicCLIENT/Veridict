"""Pydantic models for the API."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

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
    id: str  # "A" or "B"
    matricula: str = ""
    modelo: str = ""
    masa_kg: float = 0
    coef_rigidez_a: float = 0
    coef_rigidez_b: float = 0
    mediciones_C: list[float] = Field(default_factory=lambda: [0] * 6)  # C1-C6
    ancho_zona_danada_cm: float = 0
    version_conductor: str = ""


class Documento(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tipo: str  # "atestado" | "parte_amistoso"
    url: str
    texto_extraido: Optional[str] = None


class Foto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    analisis: Optional[str] = None


class Evento(BaseModel):
    timestamp: float  # segundos desde T0
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
    vehiculo: str  # "A" or "B"
    fuente: str


class Veredicto(BaseModel):
    culpa_a: float
    culpa_b: float
    confidence: float


class CompatibilidadVersiones(BaseModel):
    a: bool
    b: bool
    justificacion: str


class MeteoData(BaseModel):
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    precipitacion: Optional[float] = None
    viento_velocidad: Optional[float] = None
    viento_direccion: Optional[str] = None
    visibilidad: Optional[str] = None


class ViaData(BaseModel):
    tipo_via: Optional[str] = None
    velocidad_maxima: Optional[int] = None
    num_carriles: Optional[int] = None
    estado_pavimento: Optional[str] = None
    iluminacion: Optional[str] = None


class SolData(BaseModel):
    azimuth: Optional[float] = None
    altitude: Optional[float] = None
    es_dia: Optional[bool] = None


class Contexto(BaseModel):
    meteo: Optional[MeteoData] = None
    via: Optional[ViaData] = None
    sol: Optional[SolData] = None


class Resultado(BaseModel):
    cronologia: list[Evento] = Field(default_factory=list)
    calculos: list[CalculoFisico] = Field(default_factory=list)
    infracciones: list[Infraccion] = Field(default_factory=list)
    veredicto: Optional[Veredicto] = None
    compatibilidad_versiones: Optional[CompatibilidadVersiones] = None
    devils_advocate_passed: bool = False
    pdf_url: Optional[str] = None
    sigstore_hash: Optional[str] = None


class Caso(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    estado: EstadoCaso = EstadoCaso.CREADO
    fecha_accidente: datetime
    ubicacion: Ubicacion
    tipo_colision: TipoColision
    vehiculos: list[Vehiculo] = Field(default_factory=list)
    documentos: list[Documento] = Field(default_factory=list)
    fotos: list[Foto] = Field(default_factory=list)
    contexto: Optional[Contexto] = None
    resultado: Optional[Resultado] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CasoCreate(BaseModel):
    fecha_accidente: datetime
    ubicacion: Ubicacion
    tipo_colision: TipoColision


class CasoUpdate(BaseModel):
    estado: Optional[EstadoCaso] = None
    vehiculos: Optional[list[Vehiculo]] = None


class EstadoAnalisis(BaseModel):
    estado: str
    progreso: float  # 0-100
    etapa_actual: Optional[str] = None


class MedicionesInput(BaseModel):
    vehiculo_id: str
    mediciones_C: list[float]  # C1-C6 en cm
    longitud_frenada: Optional[float] = None  # metros
    ancho_zona_danada_cm: float

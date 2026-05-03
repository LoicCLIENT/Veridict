"""
Router de Visualización - Generación de escenas 2D parametrizadas.

Endpoints para generar AccidentSceneData desde datos de caso y capturar screenshots.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
import os

from agents.visualization.scene import (
    DatosCaso,
    SceneComposer,
    generar_escena_desde_caso,
    validate_scene,
    validate_and_fix,
    generar_screenshots_caso,
    ValidationResult,
)

router = APIRouter()


# ── Request/Response Models ────────────────────────────────────────────────────

class GenerarEscenaRequest(BaseModel):
    """Request para generar una escena de accidente."""

    # Tipo de colisión
    tipo_colision: Literal["lateral", "alcance", "frontal", "atropello"]
    tipo_via: Literal["recta", "curva", "interseccion", "autopista"] = "recta"

    # Vehículo A
    vehiculo_a_velocidad_inicial: float = Field(..., ge=0, le=250, description="km/h")
    vehiculo_a_huella_frenada: float = Field(0, ge=0, description="metros")
    vehiculo_a_tipo: Literal["sedan", "suv", "moto", "camion", "peaton"] = "sedan"
    vehiculo_a_carril: int = Field(1, ge=1, le=4)

    # Vehículo B
    vehiculo_b_velocidad_inicial: float = Field(..., ge=0, le=250, description="km/h")
    vehiculo_b_huella_frenada: float = Field(0, ge=0, description="metros")
    vehiculo_b_tipo: Literal["sedan", "suv", "moto", "camion", "peaton"] = "sedan"
    vehiculo_b_carril: int = Field(2, ge=1, le=4)

    # Parámetros del impacto (opcionales - se calculan si no se proveen)
    angulo_impacto: Optional[float] = Field(None, ge=0, le=360, description="grados")
    delta_v_a: Optional[float] = Field(None, ge=0, description="km/h")
    delta_v_b: Optional[float] = Field(None, ge=0, description="km/h")

    # Condiciones
    condicion_via: Literal["seco", "mojado", "hielo", "gravilla", "nieve"] = "seco"

    # Configuración de vía
    num_carriles: int = Field(2, ge=1, le=4)
    limite_velocidad: int = Field(50, ge=20, le=140, description="km/h")

    # Metadatos opcionales
    condicion_meteorologica: Optional[str] = "Despejado"
    visibilidad: Optional[str] = "Buena"


class ScreenshotRequest(BaseModel):
    """Request para generar screenshots de una escena."""
    scene_data: Dict[str, Any]
    case_id: Optional[str] = None
    output_dir: Optional[str] = None


class ScreenshotResponse(BaseModel):
    """Response con los screenshots generados."""
    screenshots: List[Dict[str, Any]]
    output_directory: str


class SceneResponse(BaseModel):
    """Response con la escena generada y validación."""
    scene_data: Dict[str, Any]
    validation: Dict[str, Any]
    is_valid: bool


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/generar", response_model=SceneResponse)
async def generar_escena(request: GenerarEscenaRequest) -> SceneResponse:
    """
    Genera AccidentSceneData parametrizado desde datos del caso.

    Usa física determinista para calcular trayectorias, frenadas y posiciones.
    Valida la coherencia física antes de devolver.
    """
    try:
        # Construir DatosCaso desde el request
        # Mapear tipos de vehículos del frontend al backend
        tipo_map = {
            "sedan": "turismo",
            "suv": "turismo",
            "moto": "moto",
            "camion": "camion",
            "peaton": "peaton",
        }

        datos = DatosCaso(
            tipo_colision=request.tipo_colision,
            tipo_via=request.tipo_via,
            vehiculo_a_velocidad_inicial=request.vehiculo_a_velocidad_inicial,
            vehiculo_a_huella_frenada=request.vehiculo_a_huella_frenada,
            vehiculo_a_tipo=tipo_map.get(request.vehiculo_a_tipo, "turismo"),
            vehiculo_a_carril=request.vehiculo_a_carril,
            vehiculo_b_velocidad_inicial=request.vehiculo_b_velocidad_inicial,
            vehiculo_b_huella_frenada=request.vehiculo_b_huella_frenada,
            vehiculo_b_tipo=tipo_map.get(request.vehiculo_b_tipo, "turismo"),
            vehiculo_b_carril=request.vehiculo_b_carril,
            angulo_impacto=request.angulo_impacto or 0.0,
            delta_v_a=request.delta_v_a or 20.0,
            delta_v_b=request.delta_v_b or 20.0,
            condicion_via=request.condicion_via,
            num_carriles=request.num_carriles,
            limite_velocidad=request.limite_velocidad,
            clima=request.condicion_meteorologica or "Despejado",
            visibilidad=request.visibilidad or "Buena",
        )

        # Generar escena
        scene_data = generar_escena_desde_caso(datos)

        # Validar y corregir si es necesario
        scene_data, validation = validate_and_fix(scene_data)

        return SceneResponse(
            scene_data=scene_data,
            validation={
                "is_valid": validation.is_valid,
                "warnings": validation.warnings,
                "errors": validation.errors,
                "corrections_applied": validation.corrections_applied,
            },
            is_valid=validation.is_valid,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando escena: {str(e)}"
        )


@router.post("/validar")
async def validar_escena(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida la coherencia física de una escena existente.

    Útil para verificar datos importados o modificados manualmente.
    """
    try:
        result = validate_scene(scene_data)
        return {
            "is_valid": result.is_valid,
            "warnings": result.warnings,
            "errors": result.errors,
            "corrections_applied": result.corrections_applied,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validando escena: {str(e)}"
        )


@router.post("/screenshots", response_model=ScreenshotResponse)
async def generar_screenshots(request: ScreenshotRequest) -> ScreenshotResponse:
    """
    Genera screenshots SVG/PNG de momentos clave de la escena.

    Momentos capturados:
    - inicio: Estado inicial antes de cualquier maniobra
    - pre_frenada: Justo antes de iniciar frenada
    - frenada: Durante la frenada
    - pre_impacto: Momento inmediatamente anterior al impacto
    - impacto: Momento del impacto
    """
    try:
        output_dir = request.output_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "uploads",
            "_screenshots"
        )

        screenshots = generar_screenshots_caso(
            scene_data=request.scene_data,
            case_id=request.case_id,
            output_dir=output_dir,
        )

        return ScreenshotResponse(
            screenshots=screenshots,
            output_directory=output_dir,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando screenshots: {str(e)}"
        )


@router.post("/caso/{caso_id}/escena", response_model=SceneResponse)
async def generar_escena_desde_caso_id(caso_id: str) -> SceneResponse:
    """
    Genera escena desde un caso existente en el sistema.

    Extrae automáticamente los datos del caso (tipo colisión, vehículos, huellas)
    y genera la escena correspondiente.
    """
    # Import aquí para evitar circular imports
    from routers.casos import casos_db

    if caso_id not in casos_db:
        raise HTTPException(status_code=404, detail="Caso not found")

    caso = casos_db[caso_id]

    try:
        # Extraer datos del caso
        tipo_colision_map = {
            "frontal": "frontal",
            "lateral": "lateral",
            "alcance": "alcance",
            "atropello": "atropello",
        }
        tipo_colision = tipo_colision_map.get(caso.tipo_colision.value, "lateral")

        # Obtener datos de vehículos
        vehiculo_a = None
        vehiculo_b = None

        for v in caso.vehiculos:
            if v.id == "A":
                vehiculo_a = v
            elif v.id == "B":
                vehiculo_b = v

        # Valores por defecto si no hay vehículos definidos
        vel_a = vehiculo_a.edr_velocidad_kmh if vehiculo_a and vehiculo_a.edr_velocidad_kmh else 50.0
        vel_b = vehiculo_b.edr_velocidad_kmh if vehiculo_b and vehiculo_b.edr_velocidad_kmh else 40.0
        frenada_a = vehiculo_a.longitud_frenada_m if vehiculo_a and vehiculo_a.longitud_frenada_m else 0.0
        frenada_b = vehiculo_b.longitud_frenada_m if vehiculo_b and vehiculo_b.longitud_frenada_m else 0.0

        # Extraer condición del asfalto
        condicion = "seco"
        if caso.hechos_atestado and caso.hechos_atestado.estado_calzada:
            estado = caso.hechos_atestado.estado_calzada.lower()
            if "mojad" in estado:
                condicion = "mojado"
            elif "hielo" in estado or "helad" in estado:
                condicion = "hielo"
            elif "grav" in estado:
                condicion = "gravilla"

        # Construir DatosCaso
        datos = DatosCaso(
            tipo_colision=tipo_colision,
            tipo_via="recta",
            vehiculo_a_velocidad_inicial=vel_a,
            vehiculo_a_huella_frenada=frenada_a,
            vehiculo_a_tipo="turismo",
            vehiculo_a_carril=1,
            vehiculo_b_velocidad_inicial=vel_b,
            vehiculo_b_huella_frenada=frenada_b,
            vehiculo_b_tipo="peaton" if tipo_colision == "atropello" else "turismo",
            vehiculo_b_carril=2,
            condicion_via=condicion,
            num_carriles=2,
            limite_velocidad=50,
        )

        # Generar escena
        scene_data = generar_escena_desde_caso(datos)
        scene_data, validation = validate_and_fix(scene_data)

        return SceneResponse(
            scene_data=scene_data,
            validation={
                "is_valid": validation.is_valid,
                "warnings": validation.warnings,
                "errors": validation.errors,
                "corrections_applied": validation.corrections_applied,
            },
            is_valid=validation.is_valid,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando escena desde caso: {str(e)}"
        )

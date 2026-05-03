"""
Scene Generation Module - Generación de escenas de accidente parametrizadas.

Este módulo proporciona:
- trajectory_calculator: Cálculos físicos para trayectorias
- scene_composer: Composición de escenas según tipo de colisión
- scene_validator: Validación de coherencia física
- screenshot_generator: Generación de capturas en momentos clave
"""

from .trajectory_calculator import (
    TrajectoryPoint,
    VehicleTrajectory,
    TrajectoryParams,
    calcular_trayectoria_recta,
    calcular_trayectoria_cambio_carril,
    calcular_trayectoria_peaton,
    calcular_distancia_frenado,
    calcular_tiempo_frenado,
    calcular_velocidad_desde_huella,
    COEF_FRICCION,
    ANCHO_CARRIL,
)

from .scene_composer import (
    DatosCaso,
    AccidentSceneData,
    SceneComposer,
    generar_escena_desde_caso,
)

from .scene_validator import (
    ValidationResult,
    SceneValidator,
    validate_scene,
    validate_and_fix,
)

from .screenshot_generator import (
    MomentoCaptura,
    SceneScreenshotGenerator,
    generar_screenshots_caso,
)


__all__ = [
    # Trajectory Calculator
    "TrajectoryPoint",
    "VehicleTrajectory",
    "TrajectoryParams",
    "calcular_trayectoria_recta",
    "calcular_trayectoria_cambio_carril",
    "calcular_trayectoria_peaton",
    "calcular_distancia_frenado",
    "calcular_tiempo_frenado",
    "calcular_velocidad_desde_huella",
    "COEF_FRICCION",
    "ANCHO_CARRIL",
    # Scene Composer
    "DatosCaso",
    "AccidentSceneData",
    "SceneComposer",
    "generar_escena_desde_caso",
    # Validator
    "ValidationResult",
    "SceneValidator",
    "validate_scene",
    "validate_and_fix",
    # Screenshot Generator
    "MomentoCaptura",
    "SceneScreenshotGenerator",
    "generar_screenshots_caso",
]

"""
Scene Validator - Valida coherencia física de las escenas generadas.

Verifica que los datos generados sean físicamente posibles y coherentes
antes de enviarlos al renderizador.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import math

from .trajectory_calculator import (
    calcular_distancia_frenado,
    COEF_FRICCION,
)


@dataclass
class ValidationResult:
    """Resultado de la validación."""
    is_valid: bool
    warnings: List[str]
    errors: List[str]
    corrections_applied: List[str]


class SceneValidator:
    """Validador de escenas de accidente."""

    # Límites físicos razonables
    MAX_VELOCIDAD_KMH = 250.0
    MIN_VELOCIDAD_KMH = 0.0
    MAX_DELTA_V_KMH = 150.0
    MAX_DISTANCIA_FRENADO_M = 300.0
    MAX_TIEMPO_ESCENA_S = 30.0
    MIN_TIEMPO_ESCENA_S = 0.5

    # Límites de escena
    SCENE_X_MIN = -50.0
    SCENE_X_MAX = 200.0
    SCENE_Y_MIN = -50.0
    SCENE_Y_MAX = 50.0

    def __init__(self, scene_data: Dict[str, Any]):
        self.scene = scene_data
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.corrections: List[str] = []

    def validate(self) -> ValidationResult:
        """
        Ejecuta todas las validaciones.

        Returns:
            ValidationResult con el resultado de la validación
        """
        self._validate_road()
        self._validate_vehicle("vehicleA", "A")
        self._validate_vehicle("vehicleB", "B")
        self._validate_impact()
        self._validate_trajectories_convergence()
        self._validate_physics_consistency()

        return ValidationResult(
            is_valid=len(self.errors) == 0,
            warnings=self.warnings,
            errors=self.errors,
            corrections_applied=self.corrections,
        )

    def _validate_road(self) -> None:
        """Valida la configuración de carretera."""
        road = self.scene.get("road", {})

        # Verificar campos requeridos
        required_fields = ["type", "lanes", "laneWidth", "speedLimit"]
        for field in required_fields:
            if field not in road:
                self.errors.append(f"Campo 'road.{field}' faltante")

        # Validar valores
        lanes = road.get("lanes", 2)
        if not 1 <= lanes <= 8:
            self.warnings.append(f"Número de carriles inusual: {lanes}")
            if lanes < 1:
                road["lanes"] = 2
                self.corrections.append("Corregido número de carriles a 2")

        lane_width = road.get("laneWidth", 3.5)
        if not 2.5 <= lane_width <= 5.0:
            self.warnings.append(f"Ancho de carril inusual: {lane_width}m")

        speed_limit = road.get("speedLimit", 50)
        if not 20 <= speed_limit <= 140:
            self.warnings.append(f"Límite de velocidad inusual: {speed_limit} km/h")

    def _validate_vehicle(self, key: str, vehicle_id: str) -> None:
        """Valida los datos de un vehículo."""
        vehicle = self.scene.get(key, {})

        # Verificar trayectoria
        trajectory = vehicle.get("trajectory", [])
        if not trajectory:
            self.errors.append(f"Vehículo {vehicle_id} sin trayectoria")
            return

        # Validar puntos de trayectoria
        for i, point in enumerate(trajectory):
            # Verificar campos
            if not all(k in point for k in ["x", "y", "time", "speed"]):
                self.errors.append(f"Punto {i} de vehículo {vehicle_id} incompleto")
                continue

            # Validar velocidad
            speed = point.get("speed", 0)
            if speed < self.MIN_VELOCIDAD_KMH:
                point["speed"] = 0
                self.corrections.append(f"Velocidad negativa corregida a 0 en vehículo {vehicle_id}")
            elif speed > self.MAX_VELOCIDAD_KMH:
                self.warnings.append(f"Velocidad muy alta ({speed} km/h) en vehículo {vehicle_id}")

            # Validar posición dentro de escena
            x, y = point.get("x", 0), point.get("y", 0)
            if not self.SCENE_X_MIN <= x <= self.SCENE_X_MAX:
                self.warnings.append(f"Vehículo {vehicle_id} fuera de límites X en t={point.get('time', 0)}")
            if not self.SCENE_Y_MIN <= y <= self.SCENE_Y_MAX:
                self.warnings.append(f"Vehículo {vehicle_id} fuera de límites Y en t={point.get('time', 0)}")

            # Validar tiempo positivo
            time = point.get("time", 0)
            if time < 0:
                self.errors.append(f"Tiempo negativo en vehículo {vehicle_id}")

        # Validar velocidades iniciales y de impacto
        initial_speed = vehicle.get("initialSpeed", 0)
        impact_speed = vehicle.get("impactSpeed", 0)

        if initial_speed < 0:
            vehicle["initialSpeed"] = abs(initial_speed)
            self.corrections.append(f"Velocidad inicial negativa corregida en {vehicle_id}")

        if impact_speed < 0:
            vehicle["impactSpeed"] = 0
            self.corrections.append(f"Velocidad de impacto negativa corregida en {vehicle_id}")

        if impact_speed > initial_speed * 1.1:  # 10% margen
            self.warnings.append(
                f"Vehículo {vehicle_id}: velocidad de impacto ({impact_speed}) > inicial ({initial_speed})"
            )

        # Validar distancia de frenado
        brake_distance = vehicle.get("brakeDistance", 0)
        if brake_distance < 0:
            vehicle["brakeDistance"] = 0
            self.corrections.append(f"Distancia de frenado negativa corregida en {vehicle_id}")
        elif brake_distance > self.MAX_DISTANCIA_FRENADO_M:
            self.warnings.append(f"Distancia de frenado muy larga ({brake_distance}m) en {vehicle_id}")

    def _validate_impact(self) -> None:
        """Valida los datos del impacto."""
        impact = self.scene.get("impact", {})

        # Verificar campos requeridos
        required_fields = ["x", "y", "time", "angle", "deltaV_A", "deltaV_B"]
        for field in required_fields:
            if field not in impact:
                self.errors.append(f"Campo 'impact.{field}' faltante")

        # Validar tiempo de impacto
        time = impact.get("time", 0)
        if time < self.MIN_TIEMPO_ESCENA_S:
            self.warnings.append(f"Tiempo de impacto muy corto: {time}s")
        elif time > self.MAX_TIEMPO_ESCENA_S:
            self.warnings.append(f"Tiempo de impacto muy largo: {time}s")

        # Validar Delta-V
        for key in ["deltaV_A", "deltaV_B"]:
            delta_v = impact.get(key, 0)
            if delta_v < 0:
                impact[key] = abs(delta_v)
                self.corrections.append(f"{key} negativo corregido")
            elif delta_v > self.MAX_DELTA_V_KMH:
                self.warnings.append(f"{key} muy alto: {delta_v} km/h")

        # Validar posición de impacto dentro de escena
        x, y = impact.get("x", 0), impact.get("y", 0)
        if not self.SCENE_X_MIN <= x <= self.SCENE_X_MAX:
            self.warnings.append(f"Punto de impacto fuera de límites X: {x}")
        if not self.SCENE_Y_MIN <= y <= self.SCENE_Y_MAX:
            self.warnings.append(f"Punto de impacto fuera de límites Y: {y}")

    def _validate_trajectories_convergence(self) -> None:
        """Verifica que las trayectorias converjan en el punto de impacto."""
        impact = self.scene.get("impact", {})
        impact_x = impact.get("x", 0)
        impact_y = impact.get("y", 0)
        impact_time = impact.get("time", 0)

        for key, vehicle_id in [("vehicleA", "A"), ("vehicleB", "B")]:
            vehicle = self.scene.get(key, {})
            trajectory = vehicle.get("trajectory", [])

            if not trajectory:
                continue

            # Encontrar el punto más cercano al tiempo de impacto
            closest_point = min(
                trajectory,
                key=lambda p: abs(p.get("time", 0) - impact_time)
            )

            # Calcular distancia al punto de impacto
            dx = closest_point.get("x", 0) - impact_x
            dy = closest_point.get("y", 0) - impact_y
            dist = math.sqrt(dx**2 + dy**2)

            # Tolerancia de 5 metros
            if dist > 5.0:
                self.warnings.append(
                    f"Vehículo {vehicle_id} no converge bien al impacto "
                    f"(distancia: {dist:.1f}m)"
                )

    def _validate_physics_consistency(self) -> None:
        """Valida la consistencia física entre velocidad, frenado y distancias."""
        road = self.scene.get("road", {})
        metadata = self.scene.get("metadata", {})

        # Determinar coeficiente de fricción
        road_condition = metadata.get("roadCondition", "Seco").lower()
        condition_map = {
            "seco": "seco",
            "mojado": "mojado",
            "hielo": "hielo",
            "gravilla": "gravilla",
            "nieve": "nieve",
        }
        condition_key = condition_map.get(road_condition, "seco")
        coef = COEF_FRICCION.get(condition_key, 0.75)

        for key, vehicle_id in [("vehicleA", "A"), ("vehicleB", "B")]:
            vehicle = self.scene.get(key, {})

            initial_speed = vehicle.get("initialSpeed", 0)
            brake_distance = vehicle.get("brakeDistance", 0)

            if brake_distance > 0:
                # Calcular distancia de frenado teórica
                theoretical_brake_dist = calcular_distancia_frenado(initial_speed, coef)

                # Permitir 30% de margen
                if brake_distance > theoretical_brake_dist * 1.3:
                    self.warnings.append(
                        f"Distancia de frenado de {vehicle_id} ({brake_distance:.1f}m) "
                        f"mayor que la teórica ({theoretical_brake_dist:.1f}m) para {road_condition}"
                    )
                elif brake_distance < theoretical_brake_dist * 0.5:
                    self.warnings.append(
                        f"Distancia de frenado de {vehicle_id} ({brake_distance:.1f}m) "
                        f"menor que la teórica ({theoretical_brake_dist:.1f}m) - posible frenado parcial"
                    )


def validate_scene(scene_data: Dict[str, Any]) -> ValidationResult:
    """
    Función principal para validar una escena.

    Args:
        scene_data: Diccionario con los datos de la escena

    Returns:
        ValidationResult con errores, warnings y correcciones
    """
    validator = SceneValidator(scene_data)
    return validator.validate()


def validate_and_fix(scene_data: Dict[str, Any]) -> Tuple[Dict[str, Any], ValidationResult]:
    """
    Valida y corrige automáticamente una escena.

    Args:
        scene_data: Diccionario con los datos de la escena

    Returns:
        Tupla con (escena_corregida, resultado_validación)
    """
    validator = SceneValidator(scene_data)
    result = validator.validate()

    # Las correcciones ya se aplicaron in-place durante la validación
    return scene_data, result

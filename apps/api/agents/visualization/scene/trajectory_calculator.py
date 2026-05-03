"""
Trajectory Calculator - Cálculos físicos puros para reconstrucción de accidentes.

Este módulo NO usa LLM. Todas las trayectorias se calculan con fórmulas físicas
deterministas basadas en los datos reales del caso.

Fórmulas principales:
- Distancia frenado: d = v² / (2 × μ × g)
- Tiempo frenado: t = v / (μ × g)
- Velocidad en punto t: v(t) = v₀ - (μ × g × t)
- Cinemática: x(t) = x₀ + v₀t - ½at²
"""

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple
import math

# Constantes físicas
G = 9.81  # Aceleración gravitacional (m/s²)

# Coeficientes de fricción según condición de vía
COEF_FRICCION = {
    "seco": 0.75,
    "mojado": 0.45,
    "hielo": 0.15,
    "gravilla": 0.35,
    "nieve": 0.20,
}

# Ancho de carril según tipo de vía (metros)
ANCHO_CARRIL = {
    "autopista": 3.75,
    "autovia": 3.75,
    "nacional": 3.50,
    "urbana": 3.25,
    "residencial": 3.00,
    "default": 3.50,
}

# Velocidades típicas para peatones y ciclistas (km/h)
VELOCIDAD_PEATON = 5.0
VELOCIDAD_CICLISTA = 20.0
VELOCIDAD_PEATON_CORRIENDO = 12.0


@dataclass
class TrajectoryPoint:
    """Punto en una trayectoria con posición, tiempo y velocidad."""
    x: float
    y: float
    time: float
    speed: float  # km/h


@dataclass
class VehicleTrajectory:
    """Trayectoria completa de un vehículo."""
    points: List[TrajectoryPoint]
    brake_start_time: float
    brake_distance: float
    initial_speed: float  # km/h
    impact_speed: float  # km/h

    def to_dict(self) -> dict:
        """Convierte a formato compatible con AccidentSceneData."""
        return {
            "trajectory": [
                {"x": p.x, "y": p.y, "time": p.time, "speed": p.speed}
                for p in self.points
            ],
            "brakeStartTime": self.brake_start_time,
            "brakeDistance": self.brake_distance,
            "initialSpeed": self.initial_speed,
            "impactSpeed": self.impact_speed,
        }


@dataclass
class TrajectoryParams:
    """Parámetros para calcular una trayectoria."""
    # Posición inicial
    x0: float
    y0: float

    # Velocidad inicial (km/h)
    velocidad_inicial: float

    # Dirección inicial (grados, 0 = hacia derecha/Este)
    direccion: float = 0.0

    # Frenada
    huella_frenada: float = 0.0  # metros (0 = no frenó)
    tiempo_reaccion: float = 0.0  # segundos antes de frenar

    # Condición de vía para coeficiente de fricción
    condicion_via: str = "seco"

    # Para cambios de carril
    cambio_carril: bool = False
    carril_destino_offset: float = 0.0  # metros (positivo = izquierda)
    tiempo_cambio_carril: float = 2.0  # segundos para completar cambio

    # Tiempo total de simulación (se calcula si no se proporciona)
    tiempo_total: Optional[float] = None

    # Punto de impacto (para calcular cuándo terminar)
    punto_impacto: Optional[Tuple[float, float]] = None


def kmh_to_ms(kmh: float) -> float:
    """Convierte km/h a m/s."""
    return kmh / 3.6


def ms_to_kmh(ms: float) -> float:
    """Convierte m/s a km/h."""
    return ms * 3.6


def calcular_distancia_frenado(velocidad_kmh: float, coef_friccion: float) -> float:
    """
    Calcula la distancia de frenado teórica.

    d = v² / (2 × μ × g)

    Args:
        velocidad_kmh: Velocidad inicial en km/h
        coef_friccion: Coeficiente de fricción (0-1)

    Returns:
        Distancia de frenado en metros
    """
    if coef_friccion <= 0:
        return float('inf')

    v_ms = kmh_to_ms(velocidad_kmh)
    return (v_ms ** 2) / (2 * coef_friccion * G)


def calcular_tiempo_frenado(velocidad_kmh: float, coef_friccion: float) -> float:
    """
    Calcula el tiempo para detenerse completamente.

    t = v / (μ × g)

    Args:
        velocidad_kmh: Velocidad inicial en km/h
        coef_friccion: Coeficiente de fricción (0-1)

    Returns:
        Tiempo de frenado en segundos
    """
    if coef_friccion <= 0:
        return float('inf')

    v_ms = kmh_to_ms(velocidad_kmh)
    return v_ms / (coef_friccion * G)


def calcular_velocidad_desde_huella(huella_metros: float, coef_friccion: float) -> float:
    """
    Calcula la velocidad inicial a partir de la huella de frenado.

    v = √(2 × μ × g × d)

    Args:
        huella_metros: Longitud de la huella de frenado en metros
        coef_friccion: Coeficiente de fricción

    Returns:
        Velocidad en km/h
    """
    if huella_metros <= 0:
        return 0.0

    v_ms = math.sqrt(2 * coef_friccion * G * huella_metros)
    return ms_to_kmh(v_ms)


def calcular_velocidad_en_tiempo(
    velocidad_inicial_kmh: float,
    tiempo: float,
    tiempo_inicio_frenada: float,
    coef_friccion: float
) -> float:
    """
    Calcula la velocidad en un momento dado.

    Si t < tiempo_inicio_frenada: v = v₀ (constante)
    Si t >= tiempo_inicio_frenada: v = v₀ - μ × g × (t - t_brake)

    Args:
        velocidad_inicial_kmh: Velocidad inicial en km/h
        tiempo: Tiempo actual en segundos
        tiempo_inicio_frenada: Tiempo cuando empieza a frenar
        coef_friccion: Coeficiente de fricción

    Returns:
        Velocidad en km/h (nunca negativa)
    """
    if tiempo < tiempo_inicio_frenada:
        return velocidad_inicial_kmh

    tiempo_frenando = tiempo - tiempo_inicio_frenada
    deceleracion = coef_friccion * G  # m/s²

    v_ms = kmh_to_ms(velocidad_inicial_kmh) - deceleracion * tiempo_frenando
    return max(0.0, ms_to_kmh(v_ms))


def calcular_trayectoria_recta(params: TrajectoryParams, dt: float = 0.1) -> VehicleTrajectory:
    """
    Calcula una trayectoria recta con posible frenada.

    Args:
        params: Parámetros de la trayectoria
        dt: Incremento de tiempo entre puntos (segundos)

    Returns:
        VehicleTrajectory con todos los puntos calculados
    """
    coef = COEF_FRICCION.get(params.condicion_via, COEF_FRICCION["seco"])

    # Calcular tiempo de inicio de frenada
    if params.huella_frenada > 0:
        # Velocidad al inicio de la frenada (puede ser diferente a la inicial si hubo reacción)
        velocidad_al_frenar = params.velocidad_inicial
        tiempo_frenado_total = calcular_tiempo_frenado(velocidad_al_frenar, coef)
        brake_start_time = params.tiempo_reaccion
    else:
        brake_start_time = float('inf')  # No frena
        tiempo_frenado_total = 0

    # Calcular tiempo total si no se proporciona
    if params.tiempo_total is not None:
        tiempo_total = params.tiempo_total
    elif params.punto_impacto is not None:
        # Estimar tiempo hasta el punto de impacto
        dx = params.punto_impacto[0] - params.x0
        dy = params.punto_impacto[1] - params.y0
        distancia = math.sqrt(dx**2 + dy**2)
        velocidad_media_ms = kmh_to_ms(params.velocidad_inicial) * 0.7  # Aproximación
        tiempo_total = distancia / max(velocidad_media_ms, 1.0)
    else:
        tiempo_total = brake_start_time + tiempo_frenado_total + 1.0

    # Dirección en radianes
    theta = math.radians(params.direccion)

    points: List[TrajectoryPoint] = []
    x, y = params.x0, params.y0
    t = 0.0

    while t <= tiempo_total:
        # Calcular velocidad actual
        velocidad = calcular_velocidad_en_tiempo(
            params.velocidad_inicial, t, brake_start_time, coef
        )

        points.append(TrajectoryPoint(x=x, y=y, time=t, speed=velocidad))

        # Si velocidad es 0, detenerse
        if velocidad <= 0.1:
            break

        # Avanzar posición
        v_ms = kmh_to_ms(velocidad)
        x += v_ms * math.cos(theta) * dt
        y += v_ms * math.sin(theta) * dt
        t += dt

    # Calcular velocidad de impacto (velocidad al final)
    impact_speed = points[-1].speed if points else 0.0

    return VehicleTrajectory(
        points=points,
        brake_start_time=brake_start_time,
        brake_distance=params.huella_frenada,
        initial_speed=params.velocidad_inicial,
        impact_speed=impact_speed,
    )


def calcular_trayectoria_cambio_carril(
    params: TrajectoryParams,
    dt: float = 0.1
) -> VehicleTrajectory:
    """
    Calcula una trayectoria con cambio de carril (curva suave).

    Usa una función sigmoidea para el desplazamiento lateral.

    Args:
        params: Parámetros de la trayectoria
        dt: Incremento de tiempo entre puntos

    Returns:
        VehicleTrajectory con cambio de carril
    """
    coef = COEF_FRICCION.get(params.condicion_via, COEF_FRICCION["seco"])

    # Tiempo de inicio de frenada
    if params.huella_frenada > 0:
        brake_start_time = params.tiempo_reaccion
        tiempo_frenado_total = calcular_tiempo_frenado(params.velocidad_inicial, coef)
    else:
        brake_start_time = float('inf')
        tiempo_frenado_total = 0

    # Tiempo total
    if params.tiempo_total is not None:
        tiempo_total = params.tiempo_total
    else:
        tiempo_total = max(params.tiempo_cambio_carril + 2.0, brake_start_time + tiempo_frenado_total + 1.0)

    # Dirección base en radianes
    theta_base = math.radians(params.direccion)

    points: List[TrajectoryPoint] = []
    x, y = params.x0, params.y0
    t = 0.0

    # Parámetros del cambio de carril
    t_inicio_cambio = 0.5  # Empezar cambio después de 0.5s
    t_fin_cambio = t_inicio_cambio + params.tiempo_cambio_carril

    while t <= tiempo_total:
        velocidad = calcular_velocidad_en_tiempo(
            params.velocidad_inicial, t, brake_start_time, coef
        )

        points.append(TrajectoryPoint(x=x, y=y, time=t, speed=velocidad))

        if velocidad <= 0.1:
            break

        # Calcular desplazamiento lateral (sigmoidea)
        if t < t_inicio_cambio:
            lateral_progress = 0.0
        elif t > t_fin_cambio:
            lateral_progress = 1.0
        else:
            # Sigmoidea suave
            normalized_t = (t - t_inicio_cambio) / params.tiempo_cambio_carril
            lateral_progress = 0.5 * (1 + math.tanh(4 * (normalized_t - 0.5)))

        # Velocidad lateral durante el cambio
        if t_inicio_cambio <= t <= t_fin_cambio:
            v_lateral = params.carril_destino_offset / params.tiempo_cambio_carril
        else:
            v_lateral = 0.0

        # Avanzar posición
        v_ms = kmh_to_ms(velocidad)
        x += v_ms * math.cos(theta_base) * dt
        y += v_ms * math.sin(theta_base) * dt + v_lateral * dt
        t += dt

    impact_speed = points[-1].speed if points else 0.0

    return VehicleTrajectory(
        points=points,
        brake_start_time=brake_start_time,
        brake_distance=params.huella_frenada,
        initial_speed=params.velocidad_inicial,
        impact_speed=impact_speed,
    )


def calcular_trayectoria_peaton(
    x0: float,
    y0: float,
    direccion: float,
    tiempo_total: float,
    velocidad_kmh: float = VELOCIDAD_PEATON,
    dt: float = 0.1,
) -> VehicleTrajectory:
    """
    Calcula la trayectoria de un peatón (velocidad constante, sin frenada).

    Args:
        x0, y0: Posición inicial
        direccion: Dirección en grados
        tiempo_total: Duración de la simulación
        velocidad_kmh: Velocidad del peatón
        dt: Incremento de tiempo

    Returns:
        VehicleTrajectory del peatón
    """
    theta = math.radians(direccion)
    points: List[TrajectoryPoint] = []
    x, y = x0, y0
    t = 0.0

    while t <= tiempo_total:
        points.append(TrajectoryPoint(x=x, y=y, time=t, speed=velocidad_kmh))

        v_ms = kmh_to_ms(velocidad_kmh)
        x += v_ms * math.cos(theta) * dt
        y += v_ms * math.sin(theta) * dt
        t += dt

    return VehicleTrajectory(
        points=points,
        brake_start_time=99999,  # No frena
        brake_distance=0,
        initial_speed=velocidad_kmh,
        impact_speed=0,  # Se detiene en impacto
    )


def calcular_punto_impacto(
    traj_a: VehicleTrajectory,
    traj_b: VehicleTrajectory,
    tolerancia: float = 3.0,
) -> Optional[Tuple[float, float, float]]:
    """
    Encuentra el punto donde dos trayectorias se cruzan (impacto).

    Args:
        traj_a: Trayectoria del vehículo A
        traj_b: Trayectoria del vehículo B
        tolerancia: Distancia máxima para considerar impacto (metros)

    Returns:
        Tupla (x, y, tiempo) del impacto, o None si no hay
    """
    for pa in traj_a.points:
        for pb in traj_b.points:
            if abs(pa.time - pb.time) > 0.2:
                continue

            dist = math.sqrt((pa.x - pb.x)**2 + (pa.y - pb.y)**2)
            if dist <= tolerancia:
                return (
                    (pa.x + pb.x) / 2,
                    (pa.y + pb.y) / 2,
                    (pa.time + pb.time) / 2,
                )

    return None


def sincronizar_trayectorias_a_impacto(
    traj_a: VehicleTrajectory,
    traj_b: VehicleTrajectory,
    punto_impacto: Tuple[float, float],
    tiempo_impacto: float,
) -> Tuple[VehicleTrajectory, VehicleTrajectory]:
    """
    Ajusta las trayectorias para que converjan en el punto de impacto.

    Args:
        traj_a, traj_b: Trayectorias originales
        punto_impacto: Coordenadas (x, y) del impacto
        tiempo_impacto: Tiempo del impacto

    Returns:
        Trayectorias ajustadas
    """
    # Recortar trayectorias al tiempo de impacto
    points_a = [p for p in traj_a.points if p.time <= tiempo_impacto]
    points_b = [p for p in traj_b.points if p.time <= tiempo_impacto]

    # Ajustar último punto al punto de impacto
    if points_a:
        last_a = points_a[-1]
        points_a[-1] = TrajectoryPoint(
            x=punto_impacto[0],
            y=punto_impacto[1],
            time=tiempo_impacto,
            speed=last_a.speed * 0.9,  # Ligera reducción por impacto
        )

    if points_b:
        last_b = points_b[-1]
        points_b[-1] = TrajectoryPoint(
            x=punto_impacto[0],
            y=punto_impacto[1],
            time=tiempo_impacto,
            speed=last_b.speed * 0.9,
        )

    return (
        VehicleTrajectory(
            points=points_a,
            brake_start_time=traj_a.brake_start_time,
            brake_distance=traj_a.brake_distance,
            initial_speed=traj_a.initial_speed,
            impact_speed=points_a[-1].speed if points_a else 0,
        ),
        VehicleTrajectory(
            points=points_b,
            brake_start_time=traj_b.brake_start_time,
            brake_distance=traj_b.brake_distance,
            initial_speed=traj_b.initial_speed,
            impact_speed=points_b[-1].speed if points_b else 0,
        ),
    )

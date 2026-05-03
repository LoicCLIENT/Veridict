"""
Scene Composer - Ensambla escenas de accidente según el tipo de colisión.

Este módulo toma los datos del caso y genera un AccidentSceneData completo
usando los cálculos físicos de trajectory_calculator.

Tipos de colisión soportados:
- lateral: Cambio de carril / colisión lateral
- alcance: Colisión por alcance (rear-end)
- frontal: Colisión frontal
- atropello: Atropello de peatón o ciclista
"""

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict, Any, Tuple
import math

from .trajectory_calculator import (
    TrajectoryParams,
    VehicleTrajectory,
    calcular_trayectoria_recta,
    calcular_trayectoria_cambio_carril,
    calcular_trayectoria_peaton,
    sincronizar_trayectorias_a_impacto,
    COEF_FRICCION,
    ANCHO_CARRIL,
    VELOCIDAD_PEATON,
    VELOCIDAD_CICLISTA,
)


# Tipos de colisión soportados
TipoColision = Literal["lateral", "alcance", "frontal", "atropello"]
TipoVia = Literal["recta", "curva", "interseccion", "autopista"]
CondicionVia = Literal["seco", "mojado", "hielo", "gravilla", "nieve"]


@dataclass
class DatosCaso:
    """Datos de entrada del caso para generar la escena."""

    # Tipo de accidente
    tipo_colision: TipoColision

    # Carretera
    tipo_via: TipoVia = "recta"
    num_carriles: int = 2
    limite_velocidad: int = 50
    condicion_via: CondicionVia = "seco"

    # Vehículo A
    vehiculo_a_tipo: str = "turismo"
    vehiculo_a_velocidad_inicial: float = 50.0  # km/h
    vehiculo_a_huella_frenada: float = 0.0  # metros
    vehiculo_a_carril: int = 1  # 1 = derecho, 2 = izquierdo, etc.
    vehiculo_a_masa: float = 1400.0  # kg

    # Vehículo B
    vehiculo_b_tipo: str = "turismo"
    vehiculo_b_velocidad_inicial: float = 50.0  # km/h
    vehiculo_b_huella_frenada: float = 0.0  # metros
    vehiculo_b_carril: int = 2
    vehiculo_b_masa: float = 1400.0  # kg

    # Datos de impacto (calculados externamente por CRASH3 o similar)
    delta_v_a: float = 20.0  # km/h
    delta_v_b: float = 20.0  # km/h
    angulo_impacto: float = 0.0  # grados

    # Metadatos
    clima: str = "Despejado"
    visibilidad: str = "Buena"


@dataclass
class AccidentSceneData:
    """Estructura de datos de escena compatible con el frontend."""

    road: Dict[str, Any]
    vehicleA: Dict[str, Any]
    vehicleB: Dict[str, Any]
    impact: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON."""
        return {
            "road": self.road,
            "vehicleA": self.vehicleA,
            "vehicleB": self.vehicleB,
            "impact": self.impact,
            "metadata": self.metadata,
        }


class SceneComposer:
    """Compositor de escenas de accidente."""

    def __init__(self, datos: DatosCaso):
        self.datos = datos
        self.ancho_carril = self._get_ancho_carril()

    def _get_ancho_carril(self) -> float:
        """Obtiene el ancho de carril según tipo de vía."""
        mapping = {
            "autopista": ANCHO_CARRIL["autopista"],
            "autovia": ANCHO_CARRIL["autopista"],
            "recta": ANCHO_CARRIL["nacional"],
            "curva": ANCHO_CARRIL["nacional"],
            "interseccion": ANCHO_CARRIL["urbana"],
        }
        return mapping.get(self.datos.tipo_via, ANCHO_CARRIL["default"])

    def _calcular_posicion_carril(self, carril: int) -> float:
        """
        Calcula la posición Y del centro de un carril.

        Carril 1 = más a la derecha (Y negativo)
        Carril 2 = siguiente a la izquierda
        etc.

        El centro de la carretera es Y=0.
        """
        # Offset desde el centro
        total_carriles = self.datos.num_carriles
        # Posición del carril 1 (más a la derecha)
        y_carril_1 = -((total_carriles - 1) / 2) * self.ancho_carril

        return y_carril_1 + (carril - 1) * self.ancho_carril

    def _crear_road_config(self) -> Dict[str, Any]:
        """Crea la configuración de carretera."""
        road_type_mapping = {
            "recta": "straight",
            "curva": "curve",
            "interseccion": "intersection",
            "autopista": "highway",
        }

        return {
            "type": road_type_mapping.get(self.datos.tipo_via, "straight"),
            "lanes": self.datos.num_carriles,
            "laneWidth": self.ancho_carril,
            "speedLimit": self.datos.limite_velocidad,
        }

    def _crear_metadata(self) -> Dict[str, Any]:
        """Crea los metadatos de la escena."""
        condicion_mapping = {
            "seco": "Seco",
            "mojado": "Mojado",
            "hielo": "Hielo",
            "gravilla": "Gravilla",
            "nieve": "Nieve",
        }

        return {
            "scaleMetersPerUnit": 1,
            "weatherCondition": self.clima_to_spanish(self.datos.clima),
            "roadCondition": condicion_mapping.get(self.datos.condicion_via, "Seco"),
            "visibility": self.datos.visibilidad,
        }

    def clima_to_spanish(self, clima: str) -> str:
        """Convierte el clima a español si es necesario."""
        mapping = {
            "clear": "Despejado",
            "rain": "Lluvia",
            "fog": "Niebla",
            "snow": "Nieve",
        }
        return mapping.get(clima.lower(), clima)

    def componer_escena_lateral(self) -> AccidentSceneData:
        """
        Compone una escena de colisión lateral (cambio de carril).

        Vehículo A: Va recto en su carril
        Vehículo B: Cambia de carril e impacta con A
        """
        # Posiciones Y de los carriles
        y_carril_a = self._calcular_posicion_carril(self.datos.vehiculo_a_carril)
        y_carril_b = self._calcular_posicion_carril(self.datos.vehiculo_b_carril)

        # Calcular tiempo total aproximado (para que converjan)
        tiempo_total = 4.0  # segundos

        # Punto de impacto estimado
        # Vehículo A avanza más, B viene desde atrás cambiando carril
        v_a_ms = self.datos.vehiculo_a_velocidad_inicial / 3.6
        distancia_a = v_a_ms * tiempo_total * 0.7  # 70% del tiempo a velocidad inicial
        x_impacto = -10 + distancia_a  # Empieza en x=-10
        y_impacto = y_carril_a  # Impacta en el carril de A

        # Trayectoria A: recta con posible frenada
        params_a = TrajectoryParams(
            x0=-10,
            y0=y_carril_a,
            velocidad_inicial=self.datos.vehiculo_a_velocidad_inicial,
            direccion=0,  # Hacia la derecha
            huella_frenada=self.datos.vehiculo_a_huella_frenada,
            tiempo_reaccion=2.0,  # Reacciona tarde
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_a = calcular_trayectoria_recta(params_a)

        # Trayectoria B: cambio de carril
        offset_carril = y_carril_a - y_carril_b  # Hacia dónde se mueve

        params_b = TrajectoryParams(
            x0=5,  # Empieza más adelante
            y0=y_carril_b,
            velocidad_inicial=self.datos.vehiculo_b_velocidad_inicial,
            direccion=0,
            huella_frenada=self.datos.vehiculo_b_huella_frenada,
            tiempo_reaccion=3.0,
            condicion_via=self.datos.condicion_via,
            cambio_carril=True,
            carril_destino_offset=offset_carril,
            tiempo_cambio_carril=2.5,
            tiempo_total=tiempo_total,
        )
        traj_b = calcular_trayectoria_cambio_carril(params_b)

        # Sincronizar al punto de impacto
        traj_a, traj_b = sincronizar_trayectorias_a_impacto(
            traj_a, traj_b,
            punto_impacto=(x_impacto, y_impacto),
            tiempo_impacto=tiempo_total,
        )

        return AccidentSceneData(
            road=self._crear_road_config(),
            vehicleA=traj_a.to_dict(),
            vehicleB=traj_b.to_dict(),
            impact={
                "x": x_impacto,
                "y": y_impacto,
                "time": tiempo_total,
                "angle": self.datos.angulo_impacto or 15,
                "deltaV_A": self.datos.delta_v_a,
                "deltaV_B": self.datos.delta_v_b,
            },
            metadata=self._crear_metadata(),
        )

    def componer_escena_alcance(self) -> AccidentSceneData:
        """
        Compone una escena de colisión por alcance (rear-end).

        Vehículo A: Delante, frenando
        Vehículo B: Detrás, alcanza a A
        """
        y_carril = self._calcular_posicion_carril(self.datos.vehiculo_a_carril)

        tiempo_total = 4.0

        # A empieza adelante y frena fuerte
        params_a = TrajectoryParams(
            x0=30,
            y0=y_carril,
            velocidad_inicial=self.datos.vehiculo_a_velocidad_inicial,
            direccion=0,
            huella_frenada=self.datos.vehiculo_a_huella_frenada or 30,
            tiempo_reaccion=0.5,  # Frena pronto
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_a = calcular_trayectoria_recta(params_a)

        # B viene desde atrás, reacciona tarde
        params_b = TrajectoryParams(
            x0=-10,
            y0=y_carril,
            velocidad_inicial=self.datos.vehiculo_b_velocidad_inicial,
            direccion=0,
            huella_frenada=self.datos.vehiculo_b_huella_frenada or 20,
            tiempo_reaccion=2.5,  # Reacciona tarde (distraído)
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_b = calcular_trayectoria_recta(params_b)

        # Encontrar punto de impacto
        x_impacto = traj_a.points[-1].x if traj_a.points else 70
        y_impacto = y_carril

        traj_a, traj_b = sincronizar_trayectorias_a_impacto(
            traj_a, traj_b,
            punto_impacto=(x_impacto, y_impacto),
            tiempo_impacto=tiempo_total,
        )

        return AccidentSceneData(
            road=self._crear_road_config(),
            vehicleA=traj_a.to_dict(),
            vehicleB=traj_b.to_dict(),
            impact={
                "x": x_impacto,
                "y": y_impacto,
                "time": tiempo_total,
                "angle": 0,  # Alcance es 0 grados
                "deltaV_A": self.datos.delta_v_a,
                "deltaV_B": self.datos.delta_v_b,
            },
            metadata=self._crear_metadata(),
        )

    def componer_escena_frontal(self) -> AccidentSceneData:
        """
        Compone una escena de colisión frontal.

        Vehículo A: Viene de la izquierda
        Vehículo B: Viene de la derecha (sentido contrario)
        """
        y_carril_a = self._calcular_posicion_carril(1)  # Carril derecho
        y_carril_b = self._calcular_posicion_carril(2)  # Carril izquierdo

        tiempo_total = 3.5

        x_impacto = 50
        y_impacto = (y_carril_a + y_carril_b) / 2  # Centro

        # A viene de la izquierda
        params_a = TrajectoryParams(
            x0=-10,
            y0=y_carril_a,
            velocidad_inicial=self.datos.vehiculo_a_velocidad_inicial,
            direccion=0,
            huella_frenada=self.datos.vehiculo_a_huella_frenada,
            tiempo_reaccion=2.0,
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_a = calcular_trayectoria_recta(params_a)

        # B viene de la derecha (dirección opuesta)
        params_b = TrajectoryParams(
            x0=110,
            y0=y_carril_b,
            velocidad_inicial=self.datos.vehiculo_b_velocidad_inicial,
            direccion=180,  # Hacia la izquierda
            huella_frenada=self.datos.vehiculo_b_huella_frenada,
            tiempo_reaccion=2.0,
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_b = calcular_trayectoria_recta(params_b)

        traj_a, traj_b = sincronizar_trayectorias_a_impacto(
            traj_a, traj_b,
            punto_impacto=(x_impacto, y_impacto),
            tiempo_impacto=tiempo_total,
        )

        return AccidentSceneData(
            road=self._crear_road_config(),
            vehicleA=traj_a.to_dict(),
            vehicleB=traj_b.to_dict(),
            impact={
                "x": x_impacto,
                "y": y_impacto,
                "time": tiempo_total,
                "angle": 180,  # Frontal
                "deltaV_A": self.datos.delta_v_a,
                "deltaV_B": self.datos.delta_v_b,
            },
            metadata=self._crear_metadata(),
        )

    def componer_escena_atropello(self) -> AccidentSceneData:
        """
        Compone una escena de atropello de peatón o ciclista.

        Vehículo A: Vehículo que atropella
        Vehículo B: Peatón o ciclista
        """
        y_carril = self._calcular_posicion_carril(self.datos.vehiculo_a_carril)

        tiempo_total = 4.0

        # Velocidad del peatón/ciclista
        if "cicl" in self.datos.vehiculo_b_tipo.lower():
            velocidad_b = VELOCIDAD_CICLISTA
        else:
            velocidad_b = VELOCIDAD_PEATON

        # Punto de impacto en paso de peatones (si es intersección)
        if self.datos.tipo_via == "interseccion":
            x_impacto = 60
        else:
            x_impacto = 50

        y_impacto = y_carril

        # Vehículo A
        params_a = TrajectoryParams(
            x0=-15,
            y0=y_carril,
            velocidad_inicial=self.datos.vehiculo_a_velocidad_inicial,
            direccion=0,
            huella_frenada=self.datos.vehiculo_a_huella_frenada,
            tiempo_reaccion=2.0,
            condicion_via=self.datos.condicion_via,
            tiempo_total=tiempo_total,
        )
        traj_a = calcular_trayectoria_recta(params_a)

        # Peatón/ciclista cruza perpendicular
        traj_b = calcular_trayectoria_peaton(
            x0=x_impacto,
            y0=20,  # Viene desde arriba (acera)
            direccion=-90,  # Hacia abajo (cruzando)
            tiempo_total=tiempo_total,
            velocidad_kmh=velocidad_b,
        )

        traj_a, traj_b = sincronizar_trayectorias_a_impacto(
            traj_a, traj_b,
            punto_impacto=(x_impacto, y_impacto),
            tiempo_impacto=tiempo_total - 0.5,
        )

        # El peatón se detiene en el impacto
        if traj_b.points:
            traj_b.points[-1].speed = 0

        return AccidentSceneData(
            road=self._crear_road_config(),
            vehicleA=traj_a.to_dict(),
            vehicleB=traj_b.to_dict(),
            impact={
                "x": x_impacto,
                "y": y_impacto,
                "time": tiempo_total - 0.5,
                "angle": 90,  # Perpendicular
                "deltaV_A": self.datos.delta_v_a,
                "deltaV_B": self.datos.delta_v_b,
            },
            metadata=self._crear_metadata(),
        )

    def componer(self) -> AccidentSceneData:
        """
        Compone la escena según el tipo de colisión.

        Returns:
            AccidentSceneData lista para renderizar
        """
        composers = {
            "lateral": self.componer_escena_lateral,
            "alcance": self.componer_escena_alcance,
            "frontal": self.componer_escena_frontal,
            "atropello": self.componer_escena_atropello,
        }

        composer_fn = composers.get(self.datos.tipo_colision)
        if composer_fn is None:
            # Default a lateral
            return self.componer_escena_lateral()

        return composer_fn()


def generar_escena_desde_caso(datos: DatosCaso) -> Dict[str, Any]:
    """
    Función principal para generar una escena desde datos del caso.

    Args:
        datos: DatosCaso con toda la información del accidente

    Returns:
        Diccionario compatible con AccidentSceneData del frontend
    """
    composer = SceneComposer(datos)
    escena = composer.componer()
    return escena.to_dict()

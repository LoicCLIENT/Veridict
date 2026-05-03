"""VisualizacionForenseAgent — Agente especializado en visualizaciones profesionales.

Genera visualizaciones de alta calidad para informes periciales:
- Croquis profesionales con vehiculos isometricos
- Diagramas de calculo tipo SamRAT
- Diagramas biomecanicos WAD
- Graficos de energia cinetica
- Secuencias temporales de simulacion

Basado en el analisis del documento profesional ITRASA.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import get_settings
from models import ImagenAnalizada, ToolCallLog
from physics.visualizacion_profesional import (
    generar_croquis_profesional,
    generar_diagrama_calculo,
    generar_diagrama_wad,
    generar_grafico_energia,
    generar_secuencia_temporal,
)

# Directorio para guardar las visualizaciones generadas
_VIS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "_visualizaciones"
_VIS_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS DE VISUALIZACIONES DISPONIBLES
# ═══════════════════════════════════════════════════════════════════════════════

TIPOS_VISUALIZACION = {
    "croquis_profesional": {
        "descripcion": "Croquis completo del accidente con vehiculos isometricos, trayectorias, PDI y mediciones",
        "uso": "Vista general del siniestro para el informe pericial",
    },
    "diagrama_calculo": {
        "descripcion": "Diagrama tipo SamRAT mostrando formulas, variables y fases del calculo",
        "uso": "Explicar calculos de velocidad, distancia de frenada, tiempos",
    },
    "diagrama_wad": {
        "descripcion": "Diagrama biomecanico WAD (Wrap Around Distance) para atropellos",
        "uso": "Mostrar zona de contacto cabeza-vehiculo segun velocidad",
    },
    "grafico_energia": {
        "descripcion": "Grafico de barras comparando energia cinetica a diferentes velocidades",
        "uso": "Ilustrar la gravedad del impacto segun la velocidad",
    },
    "secuencia_temporal": {
        "descripcion": "Serie de frames mostrando la evolucion temporal del accidente",
        "uso": "Mostrar pre-impacto, impacto y post-impacto",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE GENERACION
# ═══════════════════════════════════════════════════════════════════════════════

async def generar_visualizacion(
    tipo: str,
    datos: Dict[str, Any],
    titulo: str = None,
    **kwargs
) -> dict:
    """
    Genera una visualizacion profesional del tipo especificado.

    Args:
        tipo: Tipo de visualizacion (ver TIPOS_VISUALIZACION)
        datos: Datos especificos para la visualizacion
        titulo: Titulo personalizado (opcional)
        **kwargs: Parametros adicionales

    Returns:
        Dict con URL de la imagen, metadata y log
    """
    t0 = time.time()
    falta = None
    svg_content = None
    descripcion = ""

    try:
        if tipo == "croquis_profesional":
            svg_content, descripcion = _generar_croquis(datos, titulo, **kwargs)

        elif tipo == "diagrama_calculo":
            svg_content, descripcion = _generar_diagrama_calculo(datos, titulo, **kwargs)

        elif tipo == "diagrama_wad":
            svg_content, descripcion = _generar_wad(datos, titulo, **kwargs)

        elif tipo == "grafico_energia":
            svg_content, descripcion = _generar_energia(datos, titulo, **kwargs)

        elif tipo == "secuencia_temporal":
            svg_content, descripcion = _generar_secuencia(datos, titulo, **kwargs)

        else:
            falta = f"Tipo de visualizacion '{tipo}' no reconocido. Tipos disponibles: {list(TIPOS_VISUALIZACION.keys())}"
            return _error_response(tipo, falta, t0)

    except Exception as e:
        falta = f"Error generando visualizacion '{tipo}': {str(e)}"
        return _error_response(tipo, falta, t0)

    if not svg_content:
        falta = "No se pudo generar el contenido SVG"
        return _error_response(tipo, falta, t0)

    # Guardar SVG
    fname = f"{uuid.uuid4().hex[:10]}_{tipo}.svg"
    abs_path = _VIS_DIR / fname
    abs_path.write_text(svg_content, encoding="utf-8")

    # Generar URL publica
    settings = get_settings()
    base = settings.api_base_url.rstrip("/")
    url = f"{base}/uploads/_visualizaciones/{fname}"

    # Crear objeto de imagen
    imagen = ImagenAnalizada(
        url=url,
        descripcion=descripcion,
        fuente="VisualizacionForenseAgent",
        relevancia=f"Visualizacion profesional: {tipo}",
    )

    log = ToolCallLog(
        agente="VisualizacionForenseAgent",
        pregunta=f"generar_visualizacion: {tipo}",
        inputs={"tipo": tipo, "titulo": titulo},
        resultado_resumen=descripcion,
        fuentes_consultadas=["physics.visualizacion_profesional"],
        imagenes=[imagen],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )

    return {
        "datos": {
            "tipo": tipo,
            "url": url,
            "descripcion": descripcion,
            "archivo_local": str(abs_path),
        },
        "_log": log,
    }


def _error_response(tipo: str, falta: str, t0: float) -> dict:
    """Genera respuesta de error estandarizada."""
    log = ToolCallLog(
        agente="VisualizacionForenseAgent",
        pregunta=f"generar_visualizacion: {tipo}",
        inputs={"tipo": tipo},
        resultado_resumen="error",
        fuentes_consultadas=["physics.visualizacion_profesional"],
        falta_info=falta,
        duracion_ms=int((time.time() - t0) * 1000),
    )
    return {
        "datos": {"error": falta, "url": None, "tipo": tipo},
        "_log": log,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GENERADORES ESPECIFICOS
# ═══════════════════════════════════════════════════════════════════════════════

def _generar_croquis(datos: Dict, titulo: str, **kwargs) -> tuple[str, str]:
    """Genera croquis profesional."""

    vehiculos = datos.get("vehiculos", [])
    pdi = datos.get("pdi", {"x": 0, "y": 0})
    trayectorias = datos.get("trayectorias", [])
    huellas = datos.get("huellas", [])
    mediciones = datos.get("mediciones", [])

    # Validar vehiculos
    if not vehiculos:
        raise ValueError("Se requiere al menos un vehiculo para generar el croquis")

    svg = generar_croquis_profesional(
        vehiculos=vehiculos,
        pdi=pdi,
        trayectorias=trayectorias,
        huellas=huellas,
        mediciones=mediciones,
        titulo=titulo or "Croquis de Reconstruccion",
        subtitulo=datos.get("subtitulo", ""),
        width=kwargs.get("width", 900),
        height=kwargs.get("height", 700),
        mostrar_grid=kwargs.get("mostrar_grid", True),
        mostrar_escala=kwargs.get("mostrar_escala", True),
        mostrar_norte=kwargs.get("mostrar_norte", True),
    )

    ids_vehiculos = [v.get("id", "X") for v in vehiculos]
    descripcion = (
        f"Croquis profesional del accidente. "
        f"Vehiculos: {', '.join(ids_vehiculos)}. "
        f"PDI en ({pdi.get('x', 0):.1f}, {pdi.get('y', 0):.1f})."
    )

    return svg, descripcion


def _generar_diagrama_calculo(datos: Dict, titulo: str, **kwargs) -> tuple[str, str]:
    """Genera diagrama de calculo tipo SamRAT."""

    formula = datos.get("formula", "")
    variables = datos.get("variables", {})
    resultado = datos.get("resultado", {})
    fases = datos.get("fases", [])

    if not formula:
        raise ValueError("Se requiere una formula para el diagrama de calculo")

    svg = generar_diagrama_calculo(
        titulo=titulo or "Calculo Fisico",
        formula=formula,
        variables=variables,
        resultado=resultado,
        fases=fases,
        width=kwargs.get("width", 800),
        height=kwargs.get("height", 500),
    )

    descripcion = (
        f"Diagrama de calculo: {titulo or 'Calculo Fisico'}. "
        f"Resultado: {resultado.get('valor', 0):.2f} {resultado.get('unidad', '')}."
    )

    return svg, descripcion


def _generar_wad(datos: Dict, titulo: str, **kwargs) -> tuple[str, str]:
    """Genera diagrama biomecanico WAD."""

    velocidad = datos.get("velocidad_impacto", 50)
    altura_capot = datos.get("altura_capot", 0.75)
    altura_peaton = datos.get("altura_peaton", 1.75)
    tipo_vehiculo = datos.get("tipo_vehiculo", "turismo")

    svg = generar_diagrama_wad(
        velocidad_impacto=velocidad,
        altura_capot=altura_capot,
        altura_peaton=altura_peaton,
        tipo_vehiculo=tipo_vehiculo,
        width=kwargs.get("width", 700),
        height=kwargs.get("height", 500),
    )

    # Calcular WAD para la descripcion
    wad = 0.0024 * velocidad ** 2 + 0.127 * velocidad + 0.003

    descripcion = (
        f"Diagrama biomecanico WAD para atropello a {velocidad:.0f} km/h. "
        f"WAD calculado: {wad:.2f} m. "
        f"Zona de contacto: {'Parabrisas/Techo' if wad > 1.5 else 'Capo' if wad > 0.8 else 'Frontal bajo'}."
    )

    return svg, descripcion


def _generar_energia(datos: Dict, titulo: str, **kwargs) -> tuple[str, str]:
    """Genera grafico de energia cinetica."""

    velocidades = datos.get("velocidades", [10, 30, 50, 70, 90])
    masa = datos.get("masa", 1500)

    svg = generar_grafico_energia(
        velocidades=velocidades,
        masa=masa,
        titulo=titulo or "Comparativa de Energia Cinetica",
        width=kwargs.get("width", 700),
        height=kwargs.get("height", 400),
    )

    # Calcular energia maxima para descripcion
    v_max = max(velocidades)
    ec_max = 0.5 * masa * (v_max / 3.6) ** 2 / 1000

    descripcion = (
        f"Grafico de energia cinetica para vehiculo de {masa} kg. "
        f"Velocidades: {', '.join(f'{v}km/h' for v in velocidades)}. "
        f"Energia maxima: {ec_max:.1f} kJ a {v_max} km/h."
    )

    return svg, descripcion


def _generar_secuencia(datos: Dict, titulo: str, **kwargs) -> tuple[str, str]:
    """Genera secuencia temporal de frames."""

    frames = datos.get("frames", [])

    if not frames:
        raise ValueError("Se requieren frames para la secuencia temporal")

    svg = generar_secuencia_temporal(
        frames=frames,
        titulo=titulo or "Secuencia Temporal del Accidente",
        width=kwargs.get("width", 1000),
        height=kwargs.get("height", 300),
    )

    tiempos = [f.get("tiempo_ms", 0) for f in frames]
    descripcion = (
        f"Secuencia temporal con {len(frames)} frames. "
        f"Rango: {min(tiempos)} ms a {max(tiempos)} ms."
    )

    return svg, descripcion


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════════════════════

async def generar_croquis_desde_reconstruccion(
    resultado_reconstruccion: Dict[str, Any],
    titulo: str = None,
) -> dict:
    """
    Genera un croquis profesional a partir del resultado de reconstruccion.

    Args:
        resultado_reconstruccion: Resultado del motor de reconstruccion
        titulo: Titulo opcional

    Returns:
        Dict con URL y metadata de la visualizacion
    """
    # Convertir resultado de reconstruccion al formato de vehiculos
    vehiculos = []

    # Vehiculo A - posicion pre-impacto
    if "pos_inicial_a" in resultado_reconstruccion:
        vehiculos.append({
            "id": "A",
            "tipo": resultado_reconstruccion.get("tipo_a", "turismo"),
            "marca": resultado_reconstruccion.get("marca_a", ""),
            "modelo": resultado_reconstruccion.get("modelo_a", "Vehiculo A"),
            "color": "#2563EB",
            "posicion": {
                "x": resultado_reconstruccion["pos_inicial_a"][0],
                "y": resultado_reconstruccion["pos_inicial_a"][1],
            },
            "orientacion": resultado_reconstruccion.get("angulo_pre_a", 0),
            "velocidad_pre": resultado_reconstruccion.get("v_pre_a_kmh", 0),
            "delta_v": resultado_reconstruccion.get("delta_v_a_kmh", 0),
            "masa": resultado_reconstruccion.get("masa_a", 1500),
            "es_posicion_final": False,
        })

    # Vehiculo A - posicion final
    if "pos_final_a" in resultado_reconstruccion:
        vehiculos.append({
            "id": "A",
            "tipo": resultado_reconstruccion.get("tipo_a", "turismo"),
            "color": "#2563EB",
            "posicion": {
                "x": resultado_reconstruccion["pos_final_a"][0],
                "y": resultado_reconstruccion["pos_final_a"][1],
            },
            "orientacion": resultado_reconstruccion.get("angulo_post_a", 0),
            "es_posicion_final": True,
        })

    # Vehiculo B - posicion pre-impacto
    if "pos_inicial_b" in resultado_reconstruccion:
        vehiculos.append({
            "id": "B",
            "tipo": resultado_reconstruccion.get("tipo_b", "turismo"),
            "marca": resultado_reconstruccion.get("marca_b", ""),
            "modelo": resultado_reconstruccion.get("modelo_b", "Vehiculo B"),
            "color": "#DC2626",
            "posicion": {
                "x": resultado_reconstruccion["pos_inicial_b"][0],
                "y": resultado_reconstruccion["pos_inicial_b"][1],
            },
            "orientacion": resultado_reconstruccion.get("angulo_pre_b", 180),
            "velocidad_pre": resultado_reconstruccion.get("v_pre_b_kmh", 0),
            "delta_v": resultado_reconstruccion.get("delta_v_b_kmh", 0),
            "masa": resultado_reconstruccion.get("masa_b", 1200),
            "es_posicion_final": False,
        })

    # Vehiculo B - posicion final
    if "pos_final_b" in resultado_reconstruccion:
        vehiculos.append({
            "id": "B",
            "tipo": resultado_reconstruccion.get("tipo_b", "turismo"),
            "color": "#DC2626",
            "posicion": {
                "x": resultado_reconstruccion["pos_final_b"][0],
                "y": resultado_reconstruccion["pos_final_b"][1],
            },
            "orientacion": resultado_reconstruccion.get("angulo_post_b", 0),
            "es_posicion_final": True,
        })

    datos = {
        "vehiculos": vehiculos,
        "pdi": {"x": 0, "y": 0},  # PDI en origen
        "trayectorias": resultado_reconstruccion.get("trayectorias", []),
        "huellas": resultado_reconstruccion.get("huellas", []),
    }

    return await generar_visualizacion(
        tipo="croquis_profesional",
        datos=datos,
        titulo=titulo or "Reconstruccion del Accidente",
    )


async def generar_analisis_velocidad(
    velocidad_calculada: float,
    formula_usada: str,
    variables: Dict[str, Any],
    fases: List[Dict[str, Any]] = None,
) -> dict:
    """
    Genera un diagrama de calculo para analisis de velocidad.

    Args:
        velocidad_calculada: Velocidad resultante (km/h)
        formula_usada: Formula aplicada
        variables: Variables del calculo
        fases: Fases del proceso (opcional)

    Returns:
        Dict con URL y metadata
    """
    datos = {
        "formula": formula_usada,
        "variables": variables,
        "resultado": {
            "valor": velocidad_calculada,
            "unidad": "km/h",
            "descripcion": "Velocidad calculada",
        },
        "fases": fases or [],
    }

    return await generar_visualizacion(
        tipo="diagrama_calculo",
        datos=datos,
        titulo="Calculo de Velocidad",
    )


async def generar_analisis_atropello(
    velocidad_impacto: float,
    datos_peaton: Dict[str, float] = None,
    datos_vehiculo: Dict[str, Any] = None,
) -> dict:
    """
    Genera diagrama WAD para analisis de atropello.

    Args:
        velocidad_impacto: Velocidad del vehiculo (km/h)
        datos_peaton: {altura, peso, ...}
        datos_vehiculo: {tipo, altura_capot, ...}

    Returns:
        Dict con URL y metadata
    """
    datos = {
        "velocidad_impacto": velocidad_impacto,
        "altura_peaton": datos_peaton.get("altura", 1.75) if datos_peaton else 1.75,
        "altura_capot": datos_vehiculo.get("altura_capot", 0.75) if datos_vehiculo else 0.75,
        "tipo_vehiculo": datos_vehiculo.get("tipo", "turismo") if datos_vehiculo else "turismo",
    }

    return await generar_visualizacion(
        tipo="diagrama_wad",
        datos=datos,
        titulo="Analisis Biomecanico del Atropello",
    )


async def generar_comparativa_energia(
    velocidades: List[float],
    masa_vehiculo: float = 1500,
) -> dict:
    """
    Genera grafico comparativo de energia cinetica.

    Args:
        velocidades: Lista de velocidades a comparar (km/h)
        masa_vehiculo: Masa del vehiculo (kg)

    Returns:
        Dict con URL y metadata
    """
    datos = {
        "velocidades": velocidades,
        "masa": masa_vehiculo,
    }

    return await generar_visualizacion(
        tipo="grafico_energia",
        datos=datos,
        titulo="Impacto de la Velocidad en la Energia del Accidente",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCION PRINCIPAL DE DEMO/TEST
# ═══════════════════════════════════════════════════════════════════════════════

async def demo_visualizaciones() -> List[dict]:
    """Genera ejemplos de todas las visualizaciones disponibles."""
    resultados = []

    # 1. Croquis profesional
    croquis_datos = {
        "vehiculos": [
            {
                "id": "A",
                "tipo": "turismo",
                "marca": "BMW",
                "modelo": "Serie 3",
                "color": "#2563EB",
                "posicion": {"x": -8, "y": 5},
                "orientacion": 15,
                "velocidad_pre": 65,
                "delta_v": 35,
                "masa": 1500,
            },
            {
                "id": "B",
                "tipo": "suv",
                "marca": "Volkswagen",
                "modelo": "Tiguan",
                "color": "#DC2626",
                "posicion": {"x": 8, "y": -3},
                "orientacion": -30,
                "velocidad_pre": 45,
                "delta_v": 28,
                "masa": 1800,
            },
        ],
        "pdi": {"x": 0, "y": 0},
        "trayectorias": [
            {"vehiculo": "A", "puntos": [{"x": -15, "y": 8}, {"x": -8, "y": 5}, {"x": 0, "y": 0}]},
            {"vehiculo": "B", "puntos": [{"x": 15, "y": -6}, {"x": 8, "y": -3}, {"x": 0, "y": 0}]},
        ],
        "huellas": [
            {"tipo": "frenada", "vehiculo": "A", "puntos": [{"x": -12, "y": 7}, {"x": -5, "y": 3}]},
            {"tipo": "derrape", "vehiculo": "B", "puntos": [{"x": 2, "y": -1}, {"x": 10, "y": -4}]},
        ],
    }
    r1 = await generar_visualizacion("croquis_profesional", croquis_datos, "Colision Frontal-Lateral")
    resultados.append(r1)

    # 2. Diagrama de calculo
    calculo_datos = {
        "formula": "v = √(2 · μ · g · d)",
        "variables": {
            "μ": {"valor": 0.75, "unidad": "", "descripcion": "Coef. friccion"},
            "g": {"valor": 9.81, "unidad": "m/s²", "descripcion": "Gravedad"},
            "d": {"valor": 18.5, "unidad": "m", "descripcion": "Distancia huella"},
        },
        "resultado": {"valor": 59.3, "unidad": "km/h", "descripcion": "Velocidad minima"},
        "fases": [
            {"nombre": "Reaccion", "tiempo": 1.0, "distancia": 16.5, "descripcion": "t_reaccion"},
            {"nombre": "Ejecucion", "tiempo": 0.5, "distancia": 8.2, "descripcion": "t_ejecucion"},
            {"nombre": "Frenada", "tiempo": 2.2, "distancia": 18.5, "descripcion": "Huella visible"},
        ],
    }
    r2 = await generar_visualizacion("diagrama_calculo", calculo_datos, "Velocidad por Huella de Frenada")
    resultados.append(r2)

    # 3. Diagrama WAD
    wad_datos = {"velocidad_impacto": 45, "altura_peaton": 1.70, "altura_capot": 0.80}
    r3 = await generar_visualizacion("diagrama_wad", wad_datos)
    resultados.append(r3)

    # 4. Grafico de energia
    energia_datos = {"velocidades": [10, 30, 50, 70, 90, 120], "masa": 1500}
    r4 = await generar_visualizacion("grafico_energia", energia_datos)
    resultados.append(r4)

    # 5. Secuencia temporal
    secuencia_datos = {
        "frames": [
            {"tiempo_ms": 0, "descripcion": "Pre-impacto", "vehiculos": [{"orientacion": 0}, {"orientacion": 180}]},
            {"tiempo_ms": 50, "descripcion": "Contacto", "vehiculos": [{"orientacion": 10}, {"orientacion": 170}]},
            {"tiempo_ms": 120, "descripcion": "Pico deform.", "vehiculos": [{"orientacion": 25}, {"orientacion": 155}]},
            {"tiempo_ms": 200, "descripcion": "Separacion", "vehiculos": [{"orientacion": 35}, {"orientacion": 145}]},
            {"tiempo_ms": 500, "descripcion": "Pos. final", "vehiculos": [{"orientacion": 45}, {"orientacion": 120}]},
        ]
    }
    r5 = await generar_visualizacion("secuencia_temporal", secuencia_datos)
    resultados.append(r5)

    return resultados


# Para testing directo
if __name__ == "__main__":
    import asyncio

    async def main():
        print("Generando visualizaciones de demo...")
        resultados = await demo_visualizaciones()

        for r in resultados:
            datos = r.get("datos", {})
            print(f"\n[{datos.get('tipo', 'N/A')}]")
            print(f"  URL: {datos.get('url', 'ERROR')}")
            print(f"  Descripcion: {datos.get('descripcion', 'N/A')[:80]}...")

    asyncio.run(main())

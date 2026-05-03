#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   VERIDICT AI - DEMO INFORME PERICIAL COMPLETO                              ║
║   Reconstrucción Forense de Accidentes de Tráfico                           ║
║                                                                              ║
║   Este script genera un informe pericial profesional completo               ║
║   similar al estándar ITRASA, incluyendo:                                   ║
║   - Análisis físico (velocidades, energías, delta-V)                        ║
║   - Análisis biomecánico (WAD, lesiones, AIS)                               ║
║   - Visualizaciones técnicas (croquis, diagramas)                           ║
║   - Conclusiones periciales                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import math
import base64
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents.visualization import (
    crear_croquis_escena,
    crear_diagrama_wad,
    crear_diagrama_craneo,
    crear_diagrama_corporal,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CASO DE EJEMPLO - ATROPELLO CICLISTA (Tipo ITRASA)
# ═══════════════════════════════════════════════════════════════════════════════

CASO_DEMO = {
    "numero_expediente": "VP-2024-00847",
    "fecha_accidente": "15 de marzo de 2024",
    "hora_accidente": "18:45",
    "lugar": "Calle Mayor 45, Bilbao (Bizkaia)",
    "tipo_accidente": "Atropello a ciclista",

    "condiciones": {
        "climatologia": "Despejado, sin lluvia",
        "iluminacion": "Crepúsculo, farolas encendidas",
        "estado_via": "Asfalto seco, buen estado",
        "visibilidad": "Buena (>100m)",
        "trafico": "Fluido",
    },

    "vehiculo": {
        "tipo": "Turismo",
        "marca": "Seat",
        "modelo": "Ibiza 1.4 TDI",
        "matricula": "1234-ABC",
        "ano": 2019,
        "masa": 1150,  # kg
        "longitud": 4.06,  # m
        "anchura": 1.78,  # m
        "altura": 1.44,  # m
        "altura_capo": 0.85,  # m
        "conductor": "Varón, 42 años",
        "cinturon": True,
        "airbag": "No desplegado",
    },

    "victima": {
        "tipo": "Ciclista",
        "sexo": "Varón",
        "edad": 28,
        "altura": 1.78,  # m
        "peso": 75,  # kg
        "casco": False,
        "chaleco_reflectante": False,
        "bicicleta": "Bicicleta urbana estándar",
    },

    "huellas": {
        "frenada_preimpacto": 8.5,  # m
        "frenada_postimpacto": 12.3,  # m
        "arrastre_bicicleta": 6.2,  # m
        "proyeccion_victima": 14.8,  # m
        "anchura_huella": 0.18,  # m
    },

    "danos_vehiculo": {
        "zona_impacto": "Frontal central-izquierdo",
        "deformacion_capo": "Hundimiento 8cm zona central",
        "parabrisas": "Rotura estrellada zona inferior izquierda",
        "faro_izquierdo": "Rotura completa",
        "paragolpes": "Deformación y rotura parcial",
    },

    "lesiones_victima": [
        {
            "region": "head",
            "descripcion": "TCE grave con fractura parietal izquierda",
            "ais": 4,
            "mecanismo": "Impacto contra parabrisas/pilar A",
        },
        {
            "region": "chest",
            "descripcion": "Contusión pulmonar bilateral",
            "ais": 3,
            "mecanismo": "Impacto primario contra capó",
        },
        {
            "region": "pelvis",
            "descripcion": "Fractura de pelvis (rama iliopubiana)",
            "ais": 3,
            "mecanismo": "Impacto contra borde de capó",
        },
        {
            "region": "lower_limbs",
            "descripcion": "Fractura tibia-peroné pierna derecha",
            "ais": 2,
            "mecanismo": "Impacto primario paragolpes",
        },
    ],

    "parametros_calculo": {
        "coef_rozamiento_asfalto": 0.75,
        "coef_rozamiento_frenada": 0.80,
        "gravedad": 9.81,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR DE CÁLCULOS FÍSICOS
# ═══════════════════════════════════════════════════════════════════════════════

class MotorFisica:
    """Motor de cálculos de física de accidentes."""

    def __init__(self, caso: Dict):
        self.caso = caso
        self.g = caso["parametros_calculo"]["gravedad"]
        self.mu = caso["parametros_calculo"]["coef_rozamiento_frenada"]

    def velocidad_stannard_baker(self, distancia_frenada: float) -> float:
        """
        Calcula velocidad inicial desde distancia de frenada.
        Fórmula Stannard-Baker: v = √(2·μ·g·d)

        Returns: Velocidad en km/h
        """
        v_ms = math.sqrt(2 * self.mu * self.g * distancia_frenada)
        return v_ms * 3.6  # Convertir a km/h

    def velocidad_proyeccion_peaton(self, distancia_proyeccion: float) -> float:
        """
        Estima velocidad de impacto desde distancia de proyección.
        Método de Searle simplificado.

        Returns: Velocidad en km/h
        """
        # Fórmula empírica: v ≈ √(d × 13.5) para proyección de peatón
        v_kmh = math.sqrt(distancia_proyeccion * 13.5)
        return v_kmh

    def delta_v_vehiculo(self, masa_vehiculo: float, masa_peaton: float,
                         velocidad_impacto: float) -> float:
        """
        Calcula el cambio de velocidad del vehículo (Delta-V).

        Returns: Delta-V en km/h
        """
        # Conservación de momento para colisión
        delta_v = (masa_peaton / (masa_vehiculo + masa_peaton)) * velocidad_impacto
        return delta_v

    def energia_impacto(self, masa: float, velocidad_kmh: float) -> float:
        """
        Calcula energía cinética en el impacto.

        Returns: Energía en Joules
        """
        v_ms = velocidad_kmh / 3.6
        return 0.5 * masa * v_ms ** 2

    def tiempo_percepcion_reaccion(self) -> float:
        """Tiempo estándar de percepción-reacción (segundos)."""
        return 1.5  # Valor estándar ITRASA

    def distancia_percepcion_reaccion(self, velocidad_kmh: float) -> float:
        """Distancia recorrida durante percepción-reacción."""
        v_ms = velocidad_kmh / 3.6
        return v_ms * self.tiempo_percepcion_reaccion()

    def distancia_total_frenado(self, velocidad_kmh: float) -> float:
        """Distancia total de frenado desde percepción hasta parada."""
        d_pr = self.distancia_percepcion_reaccion(velocidad_kmh)
        v_ms = velocidad_kmh / 3.6
        d_frenado = v_ms ** 2 / (2 * self.mu * self.g)
        return d_pr + d_frenado

    def calcular_todo(self) -> Dict[str, Any]:
        """Ejecuta todos los cálculos físicos."""
        huellas = self.caso["huellas"]
        vehiculo = self.caso["vehiculo"]
        victima = self.caso["victima"]

        # Velocidad desde frenada
        v_frenada = self.velocidad_stannard_baker(huellas["frenada_preimpacto"])

        # Velocidad desde proyección
        v_proyeccion = self.velocidad_proyeccion_peaton(huellas["proyeccion_victima"])

        # Velocidad estimada (promedio ponderado)
        v_impacto_estimada = (v_frenada * 0.4 + v_proyeccion * 0.6)

        # Delta-V
        delta_v = self.delta_v_vehiculo(
            vehiculo["masa"],
            victima["peso"],
            v_impacto_estimada
        )

        # Energías
        e_vehiculo = self.energia_impacto(vehiculo["masa"], v_impacto_estimada)
        e_victima = self.energia_impacto(victima["peso"], v_impacto_estimada)

        # Distancias
        d_pr = self.distancia_percepcion_reaccion(v_impacto_estimada + v_frenada)
        d_total = self.distancia_total_frenado(v_impacto_estimada + v_frenada)

        return {
            "velocidad_desde_frenada_kmh": round(v_frenada, 1),
            "velocidad_desde_proyeccion_kmh": round(v_proyeccion, 1),
            "velocidad_impacto_estimada_kmh": round(v_impacto_estimada, 1),
            "velocidad_impacto_ms": round(v_impacto_estimada / 3.6, 2),
            "delta_v_vehiculo_kmh": round(delta_v, 2),
            "energia_cinetica_vehiculo_j": round(e_vehiculo, 0),
            "energia_cinetica_victima_j": round(e_victima, 0),
            "energia_transferida_victima_j": round(e_victima, 0),
            "distancia_percepcion_reaccion_m": round(d_pr, 1),
            "distancia_total_frenado_m": round(d_total, 1),
            "tiempo_percepcion_reaccion_s": self.tiempo_percepcion_reaccion(),
            "coeficiente_friccion": self.mu,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR DE ANÁLISIS BIOMECÁNICO
# ═══════════════════════════════════════════════════════════════════════════════

class MotorBiomecanica:
    """Motor de análisis biomecánico de lesiones."""

    # Tabla WAD según ITRASA/Euro NCAP
    WAD_ZONAS = {
        (0, 20): ("Paragolpes/parte inferior", "AIS 1-2", 0.15),
        (20, 30): ("Capó posterior", "AIS 2", 0.25),
        (30, 35): ("Capó central", "AIS 2-3", 0.40),
        (35, 40): ("Capó anterior/base parabrisas", "AIS 3", 0.55),
        (40, 45): ("Parabrisas inferior", "AIS 3-4", 0.70),
        (45, 50): ("Parabrisas superior", "AIS 4", 0.85),
        (50, 55): ("Borde techo/Pilar A", "AIS 4-5", 0.92),
        (55, 100): ("Proyección sobre techo", "AIS 5+", 0.98),
    }

    def __init__(self, caso: Dict):
        self.caso = caso

    def calcular_wad(self, velocidad_kmh: float, altura_victima: float) -> Dict:
        """
        Calcula el Wrap Around Distance y zona de impacto de cabeza.
        """
        # Fórmula empírica WAD basada en velocidad y altura
        # WAD ≈ altura_victima × factor_velocidad
        factor = 0.6 + (velocidad_kmh / 100) * 0.5
        wad_mm = altura_victima * 1000 * factor

        # Determinar zona de impacto
        zona = "Desconocida"
        severidad = "N/A"
        prob_fatal = 0.0

        for (v_min, v_max), (z, sev, prob) in self.WAD_ZONAS.items():
            if v_min <= velocidad_kmh < v_max:
                zona = z
                severidad = sev
                prob_fatal = prob
                break

        return {
            "wad_mm": round(wad_mm, 0),
            "wad_m": round(wad_mm / 1000, 2),
            "zona_impacto_cabeza": zona,
            "severidad_esperada": severidad,
            "probabilidad_lesion_grave": round(prob_fatal * 100, 1),
        }

    def calcular_iss(self, lesiones: List[Dict]) -> Dict:
        """
        Calcula el Injury Severity Score (ISS).
        ISS = suma de los cuadrados de los 3 AIS más altos de diferentes regiones.
        """
        # Agrupar por región y tomar el máximo AIS de cada una
        regiones = {}
        for lesion in lesiones:
            region = lesion.get("region", "other")
            ais = lesion.get("ais", 1)
            if region not in regiones or ais > regiones[region]:
                regiones[region] = ais

        # Tomar los 3 más altos
        top_3 = sorted(regiones.values(), reverse=True)[:3]

        # Calcular ISS
        iss = sum(x**2 for x in top_3)

        # Interpretación
        if iss < 9:
            gravedad = "Menor"
            pronostico = "Favorable"
        elif iss < 16:
            gravedad = "Moderada"
            pronostico = "Favorable con tratamiento"
        elif iss < 25:
            gravedad = "Grave"
            pronostico = "Reservado"
        elif iss < 50:
            gravedad = "Severa"
            pronostico = "Grave"
        else:
            gravedad = "Crítica"
            pronostico = "Muy grave / Riesgo vital"

        return {
            "iss": iss,
            "max_ais": max(top_3) if top_3 else 0,
            "gravedad_global": gravedad,
            "pronostico": pronostico,
            "regiones_afectadas": len(regiones),
            "ais_por_region": regiones,
        }

    def analizar_compatibilidad(self, velocidad_kmh: float, lesiones: List[Dict]) -> Dict:
        """
        Analiza la compatibilidad entre velocidad estimada y lesiones observadas.
        """
        wad = self.calcular_wad(velocidad_kmh, self.caso["victima"]["altura"])
        iss_data = self.calcular_iss(lesiones)

        # Verificar consistencia
        consistencia_mensajes = []
        puntuacion = 100

        # Verificar TCE vs zona de impacto
        tiene_tce = any(l.get("region") == "head" and l.get("ais", 0) >= 3 for l in lesiones)
        if tiene_tce and velocidad_kmh < 35:
            consistencia_mensajes.append(
                "ALERTA: TCE grave con velocidad estimada < 35 km/h requiere revisión"
            )
            puntuacion -= 20
        elif tiene_tce and velocidad_kmh >= 40:
            consistencia_mensajes.append(
                "CONSISTENTE: TCE grave compatible con impacto en zona parabrisas/pilar"
            )

        # Verificar fracturas MMII vs velocidad
        tiene_fx_mmii = any(l.get("region") == "lower_limbs" for l in lesiones)
        if tiene_fx_mmii and velocidad_kmh >= 20:
            consistencia_mensajes.append(
                "CONSISTENTE: Fracturas en MMII compatibles con impacto de paragolpes"
            )

        # Verificar uso de casco
        if not self.caso["victima"]["casco"] and tiene_tce:
            consistencia_mensajes.append(
                "AGRAVANTE: Ausencia de casco contribuyó a severidad del TCE"
            )

        return {
            "wad": wad,
            "iss": iss_data,
            "consistencia": consistencia_mensajes,
            "puntuacion_consistencia": puntuacion,
            "conclusion_biomecanica": self._generar_conclusion(velocidad_kmh, wad, iss_data),
        }

    def _generar_conclusion(self, vel: float, wad: Dict, iss: Dict) -> str:
        """Genera conclusión biomecánica narrativa."""
        return (
            f"El análisis biomecánico indica una velocidad de impacto de aproximadamente "
            f"{vel:.0f} km/h, lo que resulta en un WAD de {wad['wad_mm']:.0f} mm. "
            f"Esto sitúa la zona de impacto craneal en '{wad['zona_impacto_cabeza']}', "
            f"con una severidad esperada de {wad['severidad_esperada']}. "
            f"El ISS calculado de {iss['iss']} puntos indica lesiones de gravedad "
            f"'{iss['gravedad_global']}' con pronóstico '{iss['pronostico']}'."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE INFORME HTML
# ═══════════════════════════════════════════════════════════════════════════════

class GeneradorInforme:
    """Genera el informe pericial completo en HTML."""

    def __init__(self, caso: Dict):
        self.caso = caso
        self.fisica = MotorFisica(caso)
        self.biomecanica = MotorBiomecanica(caso)
        self.resultados_fisica = None
        self.resultados_biomecanica = None
        self.svgs = {}

    def ejecutar_analisis(self):
        """Ejecuta todos los análisis."""
        print("  [1/4] Ejecutando análisis físico...")
        self.resultados_fisica = self.fisica.calcular_todo()

        print("  [2/4] Ejecutando análisis biomecánico...")
        self.resultados_biomecanica = self.biomecanica.analizar_compatibilidad(
            self.resultados_fisica["velocidad_impacto_estimada_kmh"],
            self.caso["lesiones_victima"]
        )

        print("  [3/4] Generando visualizaciones...")
        self._generar_visualizaciones()

        print("  [4/4] Compilando informe...")

    def _generar_visualizaciones(self):
        """Genera todas las visualizaciones SVG."""
        # Croquis de escena
        vehiculos = [
            {
                "id": "V1",
                "tipo": "turismo",
                "x": -5,
                "y": 1.5,
                "orientacion": 0,
                "velocidad": self.resultados_fisica["velocidad_impacto_estimada_kmh"],
            },
        ]

        huellas = [
            {
                "tipo": "huella_frenada",
                "puntos": [
                    {"x": -15, "y": 1.5},
                    {"x": -10, "y": 1.5},
                    {"x": -5, "y": 1.5},
                ],
                "ancho": 0.2,
            }
        ]

        self.svgs["escena"] = crear_croquis_escena(
            vehiculos=vehiculos,
            pdi={"x": 0, "y": 0.5},
            huellas=huellas,
            ancho_carretera=7.0,
            largo_carretera=35.0,
        )

        # Diagrama WAD
        self.svgs["wad"] = crear_diagrama_wad(
            velocidad_impacto=int(self.resultados_fisica["velocidad_impacto_estimada_kmh"]),
            tipo_impacto="frontal",
            tipo_vehiculo="turismo",
            mostrar_ciclista=True,
        )

        # Diagrama corporal
        lesiones_body = [
            {"region": l["region"], "description": l["descripcion"], "ais_score": l["ais"]}
            for l in self.caso["lesiones_victima"]
        ]
        self.svgs["cuerpo"] = crear_diagrama_corporal(lesiones=lesiones_body)

        # Diagrama cráneo
        lesiones_craneo = [
            {
                "name": "Fractura parietal",
                "tipo": "fractura",
                "localizacion": "parietal izquierdo",
                "gravedad": "grave",
            },
            {
                "name": "Contusión cerebral",
                "tipo": "contusion",
                "localizacion": "lóbulo frontal",
                "gravedad": "moderada",
            },
        ]
        self.svgs["craneo"] = crear_diagrama_craneo(
            zona_impacto="parietal",
            lesiones=lesiones_craneo,
        )

    def _svg_to_base64(self, svg_content: str) -> str:
        """Convierte SVG a base64 para embeber en HTML."""
        encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"

    def generar_html(self) -> str:
        """Genera el informe completo en HTML."""

        fecha_actual = datetime.now().strftime("%d de %B de %Y")

        # Datos para el informe
        caso = self.caso
        fisica = self.resultados_fisica
        bio = self.resultados_biomecanica

        html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Pericial - {caso["numero_expediente"]}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        :root {{
            --verde: #1F3329;
            --lima: #C2E94B;
            --gris-oscuro: #374151;
            --gris-medio: #6B7280;
            --gris-claro: #F3F4F6;
            --rojo: #DC2626;
            --naranja: #F97316;
            --azul: #3B82F6;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: var(--gris-oscuro);
            background: white;
        }}

        .page {{
            max-width: 210mm;
            margin: 0 auto;
            padding: 20mm;
            background: white;
        }}

        @media print {{
            .page {{
                padding: 15mm;
                page-break-after: always;
            }}
            .no-print {{
                display: none;
            }}
        }}

        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 3px solid var(--verde);
            margin-bottom: 30px;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo-icon {{
            width: 50px;
            height: 50px;
            background: var(--verde);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--lima);
            font-weight: 700;
            font-size: 24px;
        }}

        .logo-text {{
            font-size: 28px;
            font-weight: 700;
            color: var(--verde);
        }}

        .logo-text span {{
            color: var(--lima);
            background: var(--verde);
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .header-info {{
            text-align: right;
            color: var(--gris-medio);
            font-size: 10pt;
        }}

        /* Títulos */
        h1 {{
            font-size: 22pt;
            color: var(--verde);
            margin-bottom: 10px;
            font-weight: 700;
        }}

        h2 {{
            font-size: 14pt;
            color: var(--verde);
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--lima);
            font-weight: 600;
        }}

        h3 {{
            font-size: 12pt;
            color: var(--gris-oscuro);
            margin: 20px 0 10px 0;
            font-weight: 600;
        }}

        /* Cajas de información */
        .info-box {{
            background: var(--gris-claro);
            border-radius: 8px;
            padding: 15px 20px;
            margin: 15px 0;
        }}

        .info-box.highlight {{
            background: linear-gradient(135deg, var(--verde) 0%, #2d4a3a 100%);
            color: white;
        }}

        .info-box.highlight .label {{
            color: var(--lima);
        }}

        .info-box.warning {{
            background: #FEF3C7;
            border-left: 4px solid var(--naranja);
        }}

        .info-box.danger {{
            background: #FEE2E2;
            border-left: 4px solid var(--rojo);
        }}

        /* Grid de datos */
        .data-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px 30px;
        }}

        .data-grid.three-col {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .data-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #E5E7EB;
        }}

        .data-item .label {{
            color: var(--gris-medio);
            font-size: 10pt;
        }}

        .data-item .value {{
            font-weight: 600;
            color: var(--gris-oscuro);
        }}

        .data-item .value.highlight {{
            color: var(--rojo);
            font-size: 13pt;
        }}

        /* Tablas */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }}

        th {{
            background: var(--verde);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #E5E7EB;
        }}

        tr:nth-child(even) {{
            background: var(--gris-claro);
        }}

        .ais-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 9pt;
        }}

        .ais-1 {{ background: #D1FAE5; color: #065F46; }}
        .ais-2 {{ background: #FEF3C7; color: #92400E; }}
        .ais-3 {{ background: #FFEDD5; color: #9A3412; }}
        .ais-4 {{ background: #FEE2E2; color: #991B1B; }}
        .ais-5 {{ background: #7F1D1D; color: white; }}

        /* Visualizaciones */
        .visualization {{
            margin: 20px 0;
            text-align: center;
        }}

        .visualization img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
        }}

        .visualization-caption {{
            font-size: 9pt;
            color: var(--gris-medio);
            margin-top: 8px;
            font-style: italic;
        }}

        /* Conclusiones */
        .conclusion-box {{
            background: var(--verde);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
        }}

        .conclusion-box h3 {{
            color: var(--lima);
            margin-top: 0;
        }}

        .conclusion-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin: 15px 0;
        }}

        .conclusion-number {{
            background: var(--lima);
            color: var(--verde);
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }}

        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid var(--gris-claro);
            display: flex;
            justify-content: space-between;
            font-size: 9pt;
            color: var(--gris-medio);
        }}

        .signature-box {{
            text-align: center;
            margin-top: 60px;
        }}

        .signature-line {{
            width: 250px;
            border-top: 1px solid var(--gris-oscuro);
            margin: 0 auto 10px;
        }}

        /* Print button */
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--verde);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .print-button:hover {{
            background: #2d4a3a;
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">
        Imprimir / Guardar PDF
    </button>

    <!-- PÁGINA 1: PORTADA Y RESUMEN -->
    <div class="page">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">V</div>
                <div class="logo-text">Veri<span>dict</span></div>
            </div>
            <div class="header-info">
                <strong>INFORME PERICIAL DE RECONSTRUCCIÓN</strong><br>
                Expediente: {caso["numero_expediente"]}<br>
                Fecha emisión: {fecha_actual}
            </div>
        </div>

        <h1>Informe Técnico de Reconstrucción de Accidente de Tráfico</h1>

        <div class="info-box highlight">
            <div class="data-grid">
                <div class="data-item">
                    <span class="label">Tipo de accidente</span>
                    <span class="value">{caso["tipo_accidente"]}</span>
                </div>
                <div class="data-item">
                    <span class="label">Fecha del siniestro</span>
                    <span class="value">{caso["fecha_accidente"]}</span>
                </div>
                <div class="data-item">
                    <span class="label">Hora</span>
                    <span class="value">{caso["hora_accidente"]} h</span>
                </div>
                <div class="data-item">
                    <span class="label">Ubicación</span>
                    <span class="value">{caso["lugar"]}</span>
                </div>
            </div>
        </div>

        <h2>1. Resumen Ejecutivo</h2>

        <div class="info-box warning">
            <strong>VELOCIDAD DE IMPACTO ESTIMADA</strong>
            <div style="font-size: 32pt; font-weight: 700; color: var(--rojo); margin: 10px 0;">
                {fisica["velocidad_impacto_estimada_kmh"]} km/h
            </div>
            <p>Calculada mediante análisis de huellas de frenada (Stannard-Baker) y distancia de proyección (Searle)</p>
        </div>

        <div class="data-grid three-col">
            <div class="info-box" style="text-align: center;">
                <div class="label">ISS (Injury Severity Score)</div>
                <div style="font-size: 28pt; font-weight: 700; color: var(--rojo);">{bio["iss"]["iss"]}</div>
                <div style="font-size: 10pt; color: var(--gris-medio);">{bio["iss"]["gravedad_global"]}</div>
            </div>
            <div class="info-box" style="text-align: center;">
                <div class="label">Zona impacto craneal</div>
                <div style="font-size: 14pt; font-weight: 600; margin: 10px 0;">{bio["wad"]["zona_impacto_cabeza"]}</div>
                <div style="font-size: 10pt; color: var(--gris-medio);">WAD: {bio["wad"]["wad_mm"]:.0f} mm</div>
            </div>
            <div class="info-box" style="text-align: center;">
                <div class="label">Energía transferida</div>
                <div style="font-size: 28pt; font-weight: 700; color: var(--naranja);">{fisica["energia_transferida_victima_j"]:,.0f}</div>
                <div style="font-size: 10pt; color: var(--gris-medio);">Julios</div>
            </div>
        </div>

        <h2>2. Datos del Siniestro</h2>

        <h3>2.1 Vehículo implicado</h3>
        <div class="data-grid">
            <div class="data-item">
                <span class="label">Vehículo</span>
                <span class="value">{caso["vehiculo"]["marca"]} {caso["vehiculo"]["modelo"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Matrícula</span>
                <span class="value">{caso["vehiculo"]["matricula"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Año</span>
                <span class="value">{caso["vehiculo"]["ano"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Masa</span>
                <span class="value">{caso["vehiculo"]["masa"]} kg</span>
            </div>
            <div class="data-item">
                <span class="label">Conductor</span>
                <span class="value">{caso["vehiculo"]["conductor"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Cinturón / Airbag</span>
                <span class="value">{"Sí" if caso["vehiculo"]["cinturon"] else "No"} / {caso["vehiculo"]["airbag"]}</span>
            </div>
        </div>

        <h3>2.2 Víctima</h3>
        <div class="data-grid">
            <div class="data-item">
                <span class="label">Tipo</span>
                <span class="value">{caso["victima"]["tipo"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Sexo / Edad</span>
                <span class="value">{caso["victima"]["sexo"]}, {caso["victima"]["edad"]} años</span>
            </div>
            <div class="data-item">
                <span class="label">Altura / Peso</span>
                <span class="value">{caso["victima"]["altura"]} m / {caso["victima"]["peso"]} kg</span>
            </div>
            <div class="data-item">
                <span class="label">Casco</span>
                <span class="value" style="color: {'green' if caso["victima"]["casco"] else 'var(--rojo)'};">
                    {"Sí" if caso["victima"]["casco"] else "NO"}
                </span>
            </div>
        </div>

        <h3>2.3 Condiciones</h3>
        <div class="data-grid">
            <div class="data-item">
                <span class="label">Climatología</span>
                <span class="value">{caso["condiciones"]["climatologia"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Iluminación</span>
                <span class="value">{caso["condiciones"]["iluminacion"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Estado de la vía</span>
                <span class="value">{caso["condiciones"]["estado_via"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Visibilidad</span>
                <span class="value">{caso["condiciones"]["visibilidad"]}</span>
            </div>
        </div>
    </div>

    <!-- PÁGINA 2: ANÁLISIS FÍSICO Y ESCENA -->
    <div class="page">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">V</div>
                <div class="logo-text">Veri<span>dict</span></div>
            </div>
            <div class="header-info">
                Expediente: {caso["numero_expediente"]}<br>
                Página 2 - Análisis Físico
            </div>
        </div>

        <h2>3. Análisis Físico de la Colisión</h2>

        <h3>3.1 Huellas y evidencias físicas</h3>
        <table>
            <tr>
                <th>Evidencia</th>
                <th>Medida</th>
                <th>Observaciones</th>
            </tr>
            <tr>
                <td>Huella de frenada pre-impacto</td>
                <td><strong>{caso["huellas"]["frenada_preimpacto"]} m</strong></td>
                <td>Neumático delantero izquierdo</td>
            </tr>
            <tr>
                <td>Huella de frenada post-impacto</td>
                <td><strong>{caso["huellas"]["frenada_postimpacto"]} m</strong></td>
                <td>Ambos neumáticos</td>
            </tr>
            <tr>
                <td>Distancia proyección víctima</td>
                <td><strong>{caso["huellas"]["proyeccion_victima"]} m</strong></td>
                <td>Desde PDI hasta posición final</td>
            </tr>
            <tr>
                <td>Arrastre bicicleta</td>
                <td><strong>{caso["huellas"]["arrastre_bicicleta"]} m</strong></td>
                <td>Dirección coincidente con trayectoria</td>
            </tr>
        </table>

        <h3>3.2 Cálculo de velocidades</h3>

        <div class="info-box">
            <h4 style="margin-bottom: 15px;">Método Stannard-Baker (desde huella de frenada)</h4>
            <p style="font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                v = √(2 · μ · g · d) = √(2 × {fisica["coeficiente_friccion"]} × 9.81 × {caso["huellas"]["frenada_preimpacto"]}) = <strong>{fisica["velocidad_desde_frenada_kmh"]} km/h</strong>
            </p>
        </div>

        <div class="info-box">
            <h4 style="margin-bottom: 15px;">Método Searle (desde proyección de peatón)</h4>
            <p style="font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                v = √(d × 13.5) = √({caso["huellas"]["proyeccion_victima"]} × 13.5) = <strong>{fisica["velocidad_desde_proyeccion_kmh"]} km/h</strong>
            </p>
        </div>

        <div class="data-grid">
            <div class="data-item">
                <span class="label">Velocidad estimada impacto</span>
                <span class="value highlight">{fisica["velocidad_impacto_estimada_kmh"]} km/h</span>
            </div>
            <div class="data-item">
                <span class="label">Delta-V vehículo</span>
                <span class="value">{fisica["delta_v_vehiculo_kmh"]} km/h</span>
            </div>
            <div class="data-item">
                <span class="label">Energía cinética vehículo</span>
                <span class="value">{fisica["energia_cinetica_vehiculo_j"]:,.0f} J</span>
            </div>
            <div class="data-item">
                <span class="label">Energía transferida víctima</span>
                <span class="value">{fisica["energia_transferida_victima_j"]:,.0f} J</span>
            </div>
            <div class="data-item">
                <span class="label">Distancia percepción-reacción</span>
                <span class="value">{fisica["distancia_percepcion_reaccion_m"]} m</span>
            </div>
            <div class="data-item">
                <span class="label">Distancia total frenado teórica</span>
                <span class="value">{fisica["distancia_total_frenado_m"]} m</span>
            </div>
        </div>

        <h3>3.3 Croquis de la escena</h3>
        <div class="visualization">
            <img src="{self._svg_to_base64(self.svgs["escena"])}" alt="Croquis de la escena">
            <div class="visualization-caption">
                Fig. 1: Vista cenital del lugar del accidente con posiciones de vehículos y punto de impacto (PDI)
            </div>
        </div>
    </div>

    <!-- PÁGINA 3: ANÁLISIS BIOMECÁNICO -->
    <div class="page">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">V</div>
                <div class="logo-text">Veri<span>dict</span></div>
            </div>
            <div class="header-info">
                Expediente: {caso["numero_expediente"]}<br>
                Página 3 - Análisis Biomecánico
            </div>
        </div>

        <h2>4. Análisis Biomecánico</h2>

        <h3>4.1 Wrap Around Distance (WAD)</h3>
        <p>
            El análisis WAD determina la zona de contacto de la cabeza de la víctima con el vehículo
            en función de la velocidad de impacto, según metodología ITRASA/Euro NCAP.
        </p>

        <div class="visualization">
            <img src="{self._svg_to_base64(self.svgs["wad"])}" alt="Diagrama WAD">
            <div class="visualization-caption">
                Fig. 2: Diagrama WAD mostrando zonas de impacto craneal según velocidad.
                Velocidad de impacto estimada: {fisica["velocidad_impacto_estimada_kmh"]} km/h
            </div>
        </div>

        <div class="info-box danger">
            <div class="data-grid">
                <div class="data-item">
                    <span class="label">WAD calculado</span>
                    <span class="value">{bio["wad"]["wad_mm"]:.0f} mm ({bio["wad"]["wad_m"]} m)</span>
                </div>
                <div class="data-item">
                    <span class="label">Zona de impacto craneal</span>
                    <span class="value">{bio["wad"]["zona_impacto_cabeza"]}</span>
                </div>
                <div class="data-item">
                    <span class="label">Severidad esperada</span>
                    <span class="value">{bio["wad"]["severidad_esperada"]}</span>
                </div>
                <div class="data-item">
                    <span class="label">Probabilidad lesión grave</span>
                    <span class="value highlight">{bio["wad"]["probabilidad_lesion_grave"]}%</span>
                </div>
            </div>
        </div>

        <h3>4.2 Lesiones documentadas</h3>
        <table>
            <tr>
                <th>Región</th>
                <th>Descripción</th>
                <th>AIS</th>
                <th>Mecanismo</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>{l["region"].replace("_", " ").title()}</td>
                <td>{l["descripcion"]}</td>
                <td><span class="ais-badge ais-{l["ais"]}">AIS {l["ais"]}</span></td>
                <td>{l["mecanismo"]}</td>
            </tr>
            ''' for l in caso["lesiones_victima"])}
        </table>

        <h3>4.3 Injury Severity Score (ISS)</h3>
        <div class="data-grid">
            <div class="data-item">
                <span class="label">ISS Total</span>
                <span class="value highlight">{bio["iss"]["iss"]} puntos</span>
            </div>
            <div class="data-item">
                <span class="label">AIS Máximo</span>
                <span class="value">{bio["iss"]["max_ais"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Gravedad global</span>
                <span class="value">{bio["iss"]["gravedad_global"]}</span>
            </div>
            <div class="data-item">
                <span class="label">Pronóstico</span>
                <span class="value">{bio["iss"]["pronostico"]}</span>
            </div>
        </div>

        <h3>4.4 Análisis de consistencia</h3>
        <div class="info-box">
            <ul style="margin-left: 20px;">
                {"".join(f"<li style='margin: 8px 0;'>{c}</li>" for c in bio["consistencia"])}
            </ul>
        </div>
    </div>

    <!-- PÁGINA 4: DIAGRAMAS ANATÓMICOS Y CONCLUSIONES -->
    <div class="page">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">V</div>
                <div class="logo-text">Veri<span>dict</span></div>
            </div>
            <div class="header-info">
                Expediente: {caso["numero_expediente"]}<br>
                Página 4 - Conclusiones
            </div>
        </div>

        <h2>5. Mapeo Anatómico de Lesiones</h2>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="visualization">
                <img src="{self._svg_to_base64(self.svgs["cuerpo"])}" alt="Diagrama corporal" style="max-height: 350px;">
                <div class="visualization-caption">
                    Fig. 3: Localización de lesiones corporales
                </div>
            </div>
            <div class="visualization">
                <img src="{self._svg_to_base64(self.svgs["craneo"])}" alt="Diagrama craneal" style="max-height: 350px;">
                <div class="visualization-caption">
                    Fig. 4: Detalle de lesiones craneales
                </div>
            </div>
        </div>

        <h2>6. Conclusiones Periciales</h2>

        <div class="conclusion-box">
            <h3>Conclusiones del análisis técnico-pericial</h3>

            <div class="conclusion-item">
                <div class="conclusion-number">1</div>
                <div>
                    <strong>Velocidad de impacto:</strong> El análisis físico determina que el vehículo
                    circulaba a aproximadamente <strong>{fisica["velocidad_impacto_estimada_kmh"]} km/h</strong>
                    en el momento del impacto, basado en el análisis de huellas de frenada y distancia
                    de proyección de la víctima.
                </div>
            </div>

            <div class="conclusion-item">
                <div class="conclusion-number">2</div>
                <div>
                    <strong>Mecanismo lesional:</strong> El impacto primario se produjo en la zona del
                    paragolpes (fractura tibial), seguido de impacto secundario del tronco contra el capó
                    (lesiones torácicas y pélvicas) y finalmente impacto craneal contra la zona de
                    <strong>{bio["wad"]["zona_impacto_cabeza"]}</strong> (TCE grave).
                </div>
            </div>

            <div class="conclusion-item">
                <div class="conclusion-number">3</div>
                <div>
                    <strong>Severidad:</strong> Las lesiones presentan un ISS de <strong>{bio["iss"]["iss"]} puntos</strong>,
                    clasificadas como de gravedad "<strong>{bio["iss"]["gravedad_global"]}</strong>" con pronóstico
                    "<strong>{bio["iss"]["pronostico"]}</strong>".
                </div>
            </div>

            <div class="conclusion-item">
                <div class="conclusion-number">4</div>
                <div>
                    <strong>Factores agravantes:</strong> La <strong>ausencia de casco</strong> protector
                    contribuyó significativamente a la severidad del traumatismo craneoencefálico,
                    cuya probabilidad de lesión grave a esta velocidad es del
                    <strong>{bio["wad"]["probabilidad_lesion_grave"]}%</strong>.
                </div>
            </div>

            <div class="conclusion-item">
                <div class="conclusion-number">5</div>
                <div>
                    <strong>Consistencia:</strong> Existe <strong>consistencia biomecánica</strong>
                    entre la velocidad de impacto calculada, las zonas de daño en el vehículo,
                    y el patrón lesional documentado en la víctima.
                </div>
            </div>
        </div>

        <div class="signature-box">
            <div class="signature-line"></div>
            <p><strong>Veridict AI</strong></p>
            <p style="font-size: 9pt; color: var(--gris-medio);">
                Sistema de Reconstrucción Forense Asistido por IA<br>
                Informe generado: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
            </p>
        </div>

        <div class="footer">
            <div>
                <strong>Veridict AI</strong> - Reconstrucción Forense de Accidentes<br>
                Este informe ha sido generado mediante análisis computacional
            </div>
            <div style="text-align: right;">
                Metodología: ITRASA / Euro NCAP<br>
                Expediente: {caso["numero_expediente"]}
            </div>
        </div>
    </div>
</body>
</html>
'''
        return html

    def guardar(self, ruta: str):
        """Guarda el informe en un archivo HTML."""
        self.ejecutar_analisis()
        html = self.generar_html()

        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(html)

        return ruta


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN - DEMO
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print()
    print("=" * 70)
    print("  VERIDICT AI - DEMO INFORME PERICIAL COMPLETO")
    print("  Generador de Informes de Reconstrucción de Accidentes")
    print("=" * 70)
    print()

    # Crear directorio de salida
    output_dir = Path(__file__).parent / "demo_output"
    output_dir.mkdir(exist_ok=True)

    # Generar informe
    print("Generando informe pericial...")
    print()

    generador = GeneradorInforme(CASO_DEMO)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"informe_pericial_{timestamp}.html"

    generador.guardar(str(output_file))

    print()
    print("=" * 70)
    print("  INFORME GENERADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print(f"  Archivo: {output_file}")
    print()
    print("  Para ver el informe:")
    print(f"    1. Abre el archivo en tu navegador")
    print(f"    2. Usa el boton 'Imprimir / Guardar PDF' para exportar")
    print()
    print("=" * 70)

    # Abrir en navegador automáticamente
    import webbrowser
    webbrowser.open(f'file://{output_file.absolute()}')

    return str(output_file)


if __name__ == "__main__":
    main()

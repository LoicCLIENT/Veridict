"""
Forensic Analyst — cálculos físicos (CRASH3, Stannard Baker) + cronología.

run_physics()       → ejecuta los cálculos sin IA (pura física)
generate_timeline() → llama a Claude con los resultados para la cronología
"""

import json
import re
from typing import Any, Optional

from models import Caso, Evento, CalculoFisico, Contexto


def _parse_json(text: str) -> Any:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)


def _get_coefficients(vehiculo) -> tuple[float, float]:
    """Devuelve (coef_a, coef_b) en kPa. Auto-lookup por modelo si no están fijados."""
    if vehiculo.coef_rigidez_a > 0 and vehiculo.coef_rigidez_b > 0:
        return vehiculo.coef_rigidez_a, vehiculo.coef_rigidez_b

    if vehiculo.modelo:
        from physics.coefficients import get_vehicle_coefficients
        data = get_vehicle_coefficients(vehiculo.modelo)
        return data["coef_a"], data["coef_b"]

    return 700.0, 2400.0


def _get_friction_from_context(contexto: Optional[Contexto]) -> tuple[float, str]:
    """
    Devuelve (μ, descripción) según las condiciones meteorológicas reales.
    Prioriza datos de Open-Meteo; si no hay contexto, usa asfalto seco por defecto.
    """
    if not contexto or not contexto.meteo:
        return 0.75, "asfalto seco (por defecto)"

    estado = (contexto.meteo.estado_tiempo or "").lower()
    precip = contexto.meteo.precipitacion or 0.0

    if "hielo" in estado or "nieve" in estado or "escarcha" in estado:
        return 0.20, f"calzada helada/nevada ({estado})"
    if "nieve" in estado or precip > 5.0:
        return 0.35, f"nieve en calzada o lluvia intensa ({estado})"
    if precip > 0.5 or any(w in estado for w in ["lluvia", "llovizna", "chubascos", "tormenta"]):
        return 0.55, f"asfalto mojado ({estado})"
    if "niebla" in estado:
        return 0.65, f"asfalto seco con niebla ({estado})"

    # Si hay superficie OSM, refinar
    if contexto.via and contexto.via.superficie:
        sup = contexto.via.superficie.lower()
        if "hormigon" in sup or "hormigón" in sup:
            return 0.80, "hormigón seco"
        if "adoquin" in sup or "adoquín" in sup:
            return 0.60, "adoquín seco"
        if "grava" in sup or "gravilla" in sup:
            return 0.50, "grava seca"

    return 0.75, "asfalto seco"


class ForensicAnalyst:

    def __init__(self):
        from config import get_settings, get_claude
        self.settings = get_settings()
        self.claude = get_claude()

    async def run_physics(
        self, caso: Caso, contexto: Optional[Contexto] = None
    ) -> tuple[list[CalculoFisico], list]:
        """
        Ejecuta todos los cálculos físicos sin IA.

        Mejoras sobre la versión básica:
          • CRASH3: integración por punto (C1-C6), corrección C0, coef. restitución
          • Stannard Baker: μ ajustado por meteorología real (Open-Meteo)
          • Distancia de seguridad requerida (Art. 54.1 RGC) cuando hay huella
          • Delta-V para ambos vehículos cuando hay EBS de los dos
        """
        from physics.crash3 import calculate_ebs, calculate_delta_v
        from physics.stannard_baker import (
            calculate_pre_brake_speed,
            calculate_stopping_distance,
        )

        calculos: list[CalculoFisico] = []
        ebs_por_vehiculo: dict[str, float] = {}

        mu, mu_desc = _get_friction_from_context(contexto)

        for v in caso.vehiculos:
            coef_a, coef_b = _get_coefficients(v)
            masa = v.masa_kg or 1350

            # ── CRASH3 ──────────────────────────────────────────────────────
            if v.mediciones_C and any(c > 0 for c in v.mediciones_C):
                ebs = calculate_ebs(
                    mediciones_C=v.mediciones_C,
                    ancho_zona=v.ancho_zona_danada_cm,
                    masa=masa,
                    coef_a=coef_a,
                    coef_b=coef_b,
                    c0=0.0,   # perfil plano — perito puede ajustar si mide curvatura
                    e=0.10,   # restitución típica colisión a velocidad media-alta
                )
                ebs_por_vehiculo[v.id] = ebs
                c_avg = sum(v.mediciones_C) / 6
                calculos.append(CalculoFisico(
                    nombre=f"EBS Vehículo {v.id} — CRASH3",
                    formula="EBS = √[Σ(A·Cᵢ+B·Cᵢ²/2)/n · L · 1000 / m] / √(1−e²)",
                    valor=round(ebs, 1),
                    unidad="km/h",
                    justificacion=(
                        f"Integración por punto C1-C6 (media={c_avg:.1f} cm), "
                        f"ancho L={v.ancho_zona_danada_cm} cm, masa m={masa} kg. "
                        f"A={coef_a} kPa, B={coef_b} kPa/m ({v.modelo or 'turismo genérico'}). "
                        f"Corrección restitución e=0.10."
                    ),
                ))

            # ── Stannard Baker + distancia de seguridad ──────────────────────
            if v.longitud_frenada_m and v.longitud_frenada_m > 0:
                v_frenada = calculate_pre_brake_speed(
                    longitud_frenada=v.longitud_frenada_m,
                    coef_friccion=mu,
                )
                calculos.append(CalculoFisico(
                    nombre=f"Velocidad pre-frenada Vehículo {v.id} — Stannard Baker",
                    formula="V = √(2·μ·g·d)",
                    valor=round(v_frenada, 1),
                    unidad="km/h",
                    justificacion=(
                        f"Huella d={v.longitud_frenada_m} m, "
                        f"μ={mu:.2f} ({mu_desc})."
                    ),
                ))

                # Distancia de seguridad requerida a esa velocidad (Art. 54.1 RGC)
                dist = calculate_stopping_distance(
                    velocidad_inicial=v_frenada,
                    coef_friccion=mu,
                    tiempo_reaccion=1.5,
                )
                calculos.append(CalculoFisico(
                    nombre=f"Distancia seguridad requerida Vehículo {v.id} — Art. 54.1 RGC",
                    formula="d_seg = v·t_r + v²/(2·μ·g)",
                    valor=round(dist["distancia_total"], 1),
                    unidad="m",
                    justificacion=(
                        f"A {v_frenada:.1f} km/h con μ={mu:.2f}: "
                        f"reacción {dist['distancia_reaccion']:.1f} m + "
                        f"frenada {dist['distancia_frenada']:.1f} m = "
                        f"{dist['distancia_total']:.1f} m necesarios. "
                        f"Huella real medida: {v.longitud_frenada_m} m."
                    ),
                ))

        # ── Delta-V (requiere EBS de ambos vehículos) ────────────────────────
        vehiculos_con_ebs = [v for v in caso.vehiculos if v.id in ebs_por_vehiculo]
        if len(vehiculos_con_ebs) == 2:
            va, vb = vehiculos_con_ebs[0], vehiculos_con_ebs[1]
            masa_a = va.masa_kg or 1350
            masa_b = vb.masa_kg or 1350
            dv_a = calculate_delta_v(ebs_por_vehiculo[va.id], masa_a, masa_b)
            dv_b = calculate_delta_v(ebs_por_vehiculo[vb.id], masa_b, masa_a)
            calculos.append(CalculoFisico(
                nombre=f"Delta-V Vehículo {va.id} — cambio de velocidad en impacto",
                formula="ΔV_A = EBS_A · m_B / (m_A + m_B)",
                valor=round(dv_a, 1),
                unidad="km/h",
                justificacion=(
                    f"EBS_A={ebs_por_vehiculo[va.id]:.1f} km/h, "
                    f"m_A={masa_a} kg, m_B={masa_b} kg. "
                    f"Indica severidad biomecánica para ocupantes de {va.id}."
                ),
            ))
            calculos.append(CalculoFisico(
                nombre=f"Delta-V Vehículo {vb.id} — cambio de velocidad en impacto",
                formula="ΔV_B = EBS_B · m_A / (m_A + m_B)",
                valor=round(dv_b, 1),
                unidad="km/h",
                justificacion=(
                    f"EBS_B={ebs_por_vehiculo[vb.id]:.1f} km/h, "
                    f"m_A={masa_a} kg, m_B={masa_b} kg. "
                    f"Indica severidad biomecánica para ocupantes de {vb.id}."
                ),
            ))

        # ── Reconstrucción 2D (si hay ángulos de aproximación en ambos vehículos) ──
        vehiculos_2d = [v for v in caso.vehiculos if v.angulo_aproximacion_deg is not None and v.id in ebs_por_vehiculo]
        if len(vehiculos_2d) == 2:
            from physics.reconstruction import reconstruir_colision, analizar_huellas, inferir_hipotesis
            from physics.croquis import generar_croquis_svg

            va, vb = vehiculos_2d[0], vehiculos_2d[1]

            # Huellas de arrastre post-impacto: usar las del modelo de escena si existen,
            # con fallback a longitud_huellas_post_impacto_m del vehículo
            huellas_arrastre_a = va.longitud_huellas_post_impacto_m
            huellas_arrastre_b = vb.longitud_huellas_post_impacto_m
            if caso.escena:
                for h in caso.escena.huellas:
                    if h.vehiculo_id == va.id and h.tipo == "arrastre":
                        huellas_arrastre_a = h.longitud_m
                    if h.vehiculo_id == vb.id and h.tipo == "arrastre":
                        huellas_arrastre_b = h.longitud_m

            r = reconstruir_colision(
                masa_a=va.masa_kg or 1350,
                masa_b=vb.masa_kg or 1350,
                ebs_a_kmh=ebs_por_vehiculo[va.id],
                ebs_b_kmh=ebs_por_vehiculo[vb.id],
                angulo_pre_a=va.angulo_aproximacion_deg,
                angulo_pre_b=vb.angulo_aproximacion_deg,
                pos_final_a=va.posicion_final or (5.0, 2.0),
                pos_final_b=vb.posicion_final or (-4.0, -1.5),
                huellas_post_a_m=huellas_arrastre_a,
                huellas_post_b_m=huellas_arrastre_b,
                mu=mu,
                v_pre_a_kmh=next((c.valor for c in calculos if f"Vehículo {va.id}" in c.nombre and "pre-frenada" in c.nombre), None),
                v_pre_b_kmh=next((c.valor for c in calculos if f"Vehículo {vb.id}" in c.nombre and "pre-frenada" in c.nombre), None),
            )

            # ── Análisis de huellas en calzada ────────────────────────────────
            if caso.escena and caso.escena.huellas:
                r.evidencias_huellas = analizar_huellas(caso.escena, mu=mu)
                for ev in r.evidencias_huellas:
                    calculos.append(CalculoFisico(
                        nombre=f"Huella {ev.tipo} Vehículo {ev.vehiculo_id} — análisis cinemático",
                        formula="V_inicio = √(2·μ·g·d)",
                        valor=ev.velocidad_inicio_kmh,
                        unidad="km/h",
                        justificacion=ev.interpretacion,
                    ))

            # ── Inferencia probabilística de hipótesis ────────────────────────
            if caso.escena:
                limite_v = contexto.via.velocidad_maxima if (contexto and contexto.via and contexto.via.velocidad_maxima) else None
                r.hipotesis = inferir_hipotesis(
                    escena=caso.escena,
                    evidencias_huellas=r.evidencias_huellas,
                    v_pre_a_kmh=ebs_por_vehiculo[va.id],
                    v_pre_b_kmh=ebs_por_vehiculo[vb.id],
                    angulo_pre_a=va.angulo_aproximacion_deg,
                    angulo_pre_b=vb.angulo_aproximacion_deg,
                    limite_velocidad_kmh=limite_v,
                )
                for hip in r.hipotesis:
                    calculos.append(CalculoFisico(
                        nombre=f"Hipótesis: {hip.nombre}",
                        formula="Inferencia bayesiana sobre evidencia física",
                        valor=round(hip.probabilidad * 100, 1),
                        unidad="%",
                        justificacion=hip.conclusion,
                    ))

            calculos.append(CalculoFisico(
                nombre=f"Velocidad post-impacto Vehículo {va.id} — reconstrucción 2D",
                formula="Conservación de momento vectorial 2D + e",
                valor=r.v_post_a_kmh,
                unidad="km/h",
                justificacion=f"Ángulo salida: {r.angle_post_a_deg:.0f}°. Delta-V: {r.delta_v_a_kmh:.1f} km/h.",
            ))
            calculos.append(CalculoFisico(
                nombre=f"Velocidad post-impacto Vehículo {vb.id} — reconstrucción 2D",
                formula="Conservación de momento vectorial 2D + e",
                valor=r.v_post_b_kmh,
                unidad="km/h",
                justificacion=f"Ángulo salida: {r.angle_post_b_deg:.0f}°. Delta-V: {r.delta_v_b_kmh:.1f} km/h.",
            ))
            calculos.append(CalculoFisico(
                nombre="Coeficiente de restitución — colisión",
                formula="e = (v₂_post − v₁_post) / (v₁_pre − v₂_pre)  [componentes normales]",
                valor=r.coef_restitucion,
                unidad="adimensional",
                justificacion=f"e=0 colisión perfectamente plástica; e=1 perfectamente elástica. Rango vehicular típico: 0.05–0.35.",
            ))
            calculos.append(CalculoFisico(
                nombre="Verificación conservación de momento 2D",
                formula="|p_post| / |p_pre| − 1",
                valor=r.error_momento_pct,
                unidad="%",
                justificacion=f"Error < 15% es aceptable en peritaje. Pos. inicial A: {r.pos_inicial_a} m, B: {r.pos_inicial_b} m desde PDI.",
            ))

            # Generar croquis SVG y guardarlo para el report
            try:
                croquis_svg = generar_croquis_svg(
                    resultado=r,
                    pos_final_a=va.posicion_final or (5.0, 2.0),
                    pos_final_b=vb.posicion_final or (-4.0, -1.5),
                    angulo_pre_a=va.angulo_aproximacion_deg,
                    angulo_pre_b=vb.angulo_aproximacion_deg,
                    tipo_colision=caso.tipo_colision.value,
                    modelo_a=va.modelo or "Vehículo A",
                    modelo_b=vb.modelo or "Vehículo B",
                    escena=caso.escena,
                )
                # Guardamos en caso para que el ReportWriter lo incluya en el PDF
                if not hasattr(caso, '_croquis_svg'):
                    object.__setattr__(caso, '_croquis_svg', croquis_svg)
            except Exception as e:
                print(f"Croquis SVG error: {e}")

            if r.advertencias:
                for adv in r.advertencias:
                    print(f"[Reconstruction] {adv}")

        return calculos, []

    async def generate_timeline(
        self,
        caso: Caso,
        calculos: list[CalculoFisico],
        contexto: Optional[Contexto] = None,
    ) -> list[Evento]:
        """Genera la cronología forense llamando a Claude Sonnet."""

        calculos_txt = "\n".join(
            f"  • {c.nombre}: {c.valor} {c.unidad} ({c.justificacion})"
            for c in calculos
        ) or "  • Sin cálculos de velocidad disponibles"

        vehiculos_txt = ""
        for v in caso.vehiculos:
            vehiculos_txt += f"\n  Vehículo {v.id}: {v.modelo or 'desconocido'}, {v.masa_kg} kg"
            if v.angulo_aproximacion_deg is not None:
                vehiculos_txt += f", ángulo aproximación {v.angulo_aproximacion_deg}°"
            if v.posicion_final:
                vehiculos_txt += f", posición final ({v.posicion_final[0]:.1f}, {v.posicion_final[1]:.1f}) m desde PDI"
            if v.airbag_desplegado is not None:
                vehiculos_txt += f", airbag {'desplegado' if v.airbag_desplegado else 'NO desplegado'}"
            if v.edr_velocidad_kmh:
                vehiculos_txt += f", EDR: {v.edr_velocidad_kmh} km/h"
            if v.version_conductor:
                vehiculos_txt += f'\n    Declaración: "{v.version_conductor}"'

        escena_txt = ""
        if caso.escena:
            e = caso.escena
            if e.angulo_impacto_deg is not None:
                escena_txt += f"\n  Ángulo de impacto entre vehículos: {e.angulo_impacto_deg}°"
            if e.distancia_visibilidad_m is not None:
                escena_txt += f"\n  Distancia de visibilidad en el punto: {e.distancia_visibilidad_m} m"
            if e.estado_asfalto:
                escena_txt += f"\n  Estado del asfalto: {e.estado_asfalto}"
            if e.observaciones_perito:
                escena_txt += f"\n  Observaciones del perito: {e.observaciones_perito}"

        contexto_txt = ""
        if contexto:
            if contexto.direccion:
                contexto_txt += f"\n  Lugar: {contexto.direccion}"
            if contexto.meteo:
                m = contexto.meteo
                if m.estado_tiempo:
                    contexto_txt += f"\n  Meteorología: {m.estado_tiempo}"
                if m.visibilidad:
                    contexto_txt += f", visibilidad {m.visibilidad}"
            if contexto.via and contexto.via.velocidad_maxima:
                contexto_txt += f"\n  Límite velocidad: {contexto.via.velocidad_maxima} km/h"
            if contexto.sol and contexto.sol.deslumbramiento_posible:
                contexto_txt += "\n  ⚠ Deslumbramiento solar posible en el momento del accidente"

        prompt = f"""Eres un perito forense de accidentes de tráfico. Genera la cronología técnica del accidente.

TIPO DE COLISIÓN: {caso.tipo_colision.value}
FECHA Y HORA: {caso.fecha_accidente.strftime('%d/%m/%Y %H:%M')}
VEHÍCULOS:{vehiculos_txt}
{f'DATOS DE ESCENA (perito):{escena_txt}' if escena_txt else ''}
{f'CONTEXTO DEL LUGAR:{contexto_txt}' if contexto_txt else ''}

EVIDENCIA FÍSICA (valores calculados objetivamente):
{calculos_txt}

Genera entre 4 y 6 eventos que reconstruyan la secuencia del accidente.
— Usa los valores numéricos calculados en las descripciones (velocidades, distancias).
— El timestamp 0 es el momento del impacto; los eventos previos tienen timestamps negativos.
— Sé técnico y objetivo. No atribuyas culpa.

Responde ÚNICAMENTE con JSON válido (sin texto adicional):
[{{"timestamp": -4.0, "descripcion": "..."}}, ..., {{"timestamp": 0.0, "descripcion": "Colisión..."}}]"""

        try:
            response = await self.claude.messages.create(
                model=self.settings.model_sonnet,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            eventos_raw = _parse_json(response.content[0].text)
            return [
                Evento(timestamp=e["timestamp"], descripcion=e["descripcion"])
                for e in eventos_raw
            ]
        except Exception as e:
            print(f"Timeline error: {e}")
            return self._fallback_timeline(caso)

    def _fallback_timeline(self, caso: Caso) -> list[Evento]:
        tipo = caso.tipo_colision.value
        if tipo == "lateral":
            return [
                Evento(timestamp=-4, descripcion="Vehículo A circula por su carril"),
                Evento(timestamp=-2, descripcion="Vehículo B inicia maniobra de cambio de carril"),
                Evento(timestamp=-1, descripcion="Vehículo A detecta peligro e inicia frenada"),
                Evento(timestamp=0, descripcion="Colisión lateral"),
            ]
        if tipo == "alcance":
            return [
                Evento(timestamp=-3, descripcion="Ambos vehículos circulan en el mismo carril"),
                Evento(timestamp=-1.5, descripcion="Vehículo B reduce velocidad bruscamente"),
                Evento(timestamp=-0.7, descripcion="Vehículo A inicia frenada de emergencia"),
                Evento(timestamp=0, descripcion="Colisión por alcance trasero"),
            ]
        if tipo == "atropello":
            return [
                Evento(timestamp=-3, descripcion="Vehículo A se aproxima a la zona de cruce"),
                Evento(timestamp=-1.5, descripcion="Peatón inicia cruce por paso habilitado"),
                Evento(timestamp=-0.6, descripcion="Conductor detecta peatón e inicia frenada"),
                Evento(timestamp=0, descripcion="Impacto con peatón"),
            ]
        return [
            Evento(timestamp=-3, descripcion="Vehículos en fase de aproximación"),
            Evento(timestamp=-1, descripcion="Detección de situación de riesgo"),
            Evento(timestamp=0, descripcion="Colisión"),
        ]

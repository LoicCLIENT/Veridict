"""
Reconstrucción cinemática 2D de accidentes de tráfico.

Implementa la metodología estándar de peritos judiciales:
  1. Velocidades post-impacto por Stannard Baker inverso (huellas de arrastre)
  2. Coeficiente de restitución e = (v2_post - v1_post) / (v1_pre - v2_pre)
  3. Velocidades pre-impacto por conservación de momento vectorial 2D
  4. Posiciones iniciales por cinemática rectilínea + tiempo de reacción

Referencia: Brach & Brach, "Vehicle Accident Analysis and Reconstruction Methods", SAE 2011.
"""

import math
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import EscenaAccidente


@dataclass
class VehicleState:
    mass_kg: float
    speed_kmh: float
    angle_deg: float        # ángulo de movimiento respecto al eje X (0° = Este, 90° = Norte)

    @property
    def vx(self) -> float:
        return (self.speed_kmh / 3.6) * math.cos(math.radians(self.angle_deg))

    @property
    def vy(self) -> float:
        return (self.speed_kmh / 3.6) * math.sin(math.radians(self.angle_deg))

    @property
    def momentum_x(self) -> float:
        return self.mass_kg * self.vx

    @property
    def momentum_y(self) -> float:
        return self.mass_kg * self.vy


@dataclass
class EvidenciaHuella:
    """Interpretación física de una huella en la calzada."""
    vehiculo_id: str
    tipo: str
    longitud_m: float
    velocidad_inicio_kmh: float    # velocidad al inicio de la huella
    velocidad_fin_kmh: float       # velocidad al final (0 si para)
    curvatura: str                 # "recta" | "curva_derecha" | "curva_izquierda"
    interpretacion: str            # texto para el informe


@dataclass
class HipotesisManobra:
    """Resultado de la inferencia probabilística sobre una hipótesis de maniobra."""
    nombre: str                    # "evasión de obstáculo", "pérdida de control", etc.
    probabilidad: float            # 0.0 – 1.0
    evidencias_favor: list[str]
    evidencias_contra: list[str]
    conclusion: str                # párrafo para el informe


@dataclass
class ReconstructionResult:
    # Velocidades calculadas
    v_pre_a_kmh: float
    v_pre_b_kmh: float
    v_post_a_kmh: float
    v_post_b_kmh: float

    # Ángulos de salida post-impacto
    angle_post_a_deg: float
    angle_post_b_deg: float

    # Coeficiente de restitución
    coef_restitucion: float

    # Delta-V (cambio de velocidad en el impacto, clave para lesiones)
    delta_v_a_kmh: float
    delta_v_b_kmh: float

    # Posiciones estimadas en metros desde el PDI
    pos_inicial_a: tuple[float, float]   # (x, y) donde el conductor debió reaccionar
    pos_inicial_b: tuple[float, float]

    # Verificación de conservación de momento
    error_momento_pct: float             # < 15% = aceptable para peritaje

    # Análisis de huellas en calzada
    evidencias_huellas: list[EvidenciaHuella] = field(default_factory=list)

    # Inferencia probabilística de hipótesis
    hipotesis: list[HipotesisManobra] = field(default_factory=list)

    # Mensajes de validación
    advertencias: list[str] = field(default_factory=list)


def reconstruir_colision(
    masa_a: float,
    masa_b: float,
    ebs_a_kmh: float,           # velocidad de impacto vehículo A (CRASH3 o EDR)
    ebs_b_kmh: float,
    angulo_pre_a: float,        # ángulo de aproximación A (grados, convención cartesiana)
    angulo_pre_b: float,        # ángulo de aproximación B
    pos_final_a: tuple[float, float] = (5.0, 2.0),   # metros desde PDI
    pos_final_b: tuple[float, float] = (-4.0, -1.5),
    huellas_post_a_m: Optional[float] = None,
    huellas_post_b_m: Optional[float] = None,
    mu: float = 0.65,
    tiempo_reaccion_s: float = 1.5,     # estándar DGT / ACEA
    v_pre_a_kmh: Optional[float] = None,  # Stannard Baker pre-frenada, si disponible
    v_pre_b_kmh: Optional[float] = None,
) -> ReconstructionResult:
    """
    Reconstrucción 2D completa de una colisión entre dos vehículos.

    Metodología:
      1. Velocidad post-impacto: por huellas de arrastre (Stannard Baker)
         o estimada con e=0.15 si no hay huellas.
      2. Coeficiente de restitución: calculado si hay velocidades post;
         si no, e=0.15 (valor empírico para colisiones >40 km/h).
      3. Momento: verificación 2D vectorial pre vs post.
      4. Trayectoria previa: cinemática rectilínea uniforme desde PDI.
    """
    advertencias: list[str] = []

    # ── 1. Velocidades post-impacto ───────────────────────────────────────────
    def stannard_baker_post(huellas_m: float) -> float:
        return math.sqrt(2 * mu * 9.81 * huellas_m) * 3.6  # km/h

    if huellas_post_a_m and huellas_post_a_m > 0:
        v_post_a = stannard_baker_post(huellas_post_a_m)
    else:
        # Sin huellas: estimamos con conservación de momento (colisión plástica parcial)
        v_post_a = None
        advertencias.append("Huellas post-impacto A no disponibles — velocidad post estimada por momento.")

    if huellas_post_b_m and huellas_post_b_m > 0:
        v_post_b = stannard_baker_post(huellas_post_b_m)
    else:
        v_post_b = None
        advertencias.append("Huellas post-impacto B no disponibles — velocidad post estimada por momento.")

    # ── 2. Coeficiente de restitución ─────────────────────────────────────────
    # En colisión central (1D) e = (v_post_B - v_post_A) / (v_pre_A - v_pre_B)
    # Para colisión angular, usamos las componentes en la línea de impacto (normal al plano de contacto)
    # Línea de impacto: determinada por el ángulo relativo entre vehículos
    angulo_relativo = abs(angulo_pre_a - angulo_pre_b) % 180

    # Proyección de velocidades en la línea de impacto (normal al contacto)
    phi = math.radians(angulo_relativo / 2)   # semisuma de ángulos
    v1n_pre = ebs_a_kmh * math.cos(phi)       # componente normal vehículo A
    v2n_pre = ebs_b_kmh * math.cos(math.pi - phi)  # componente normal vehículo B (sentido opuesto)

    if v_post_a is not None and v_post_b is not None:
        v1n_post = v_post_a * math.cos(phi)
        v2n_post = v_post_b * math.cos(phi)
        closing = v1n_pre - v2n_pre
        if abs(closing) > 0.5:
            e = abs((v2n_post - v1n_post) / closing)
            e = min(max(e, 0.0), 1.0)
        else:
            e = 0.15
            advertencias.append("Velocidad de cierre muy baja — usando e=0.15 empírico.")
    else:
        # Valor empírico: e decrece con la velocidad de cierre
        # e ≈ 0.35 a 20 km/h, e ≈ 0.10 a 80 km/h (Brach 2011, Tabla 3.1)
        v_cierre = ebs_a_kmh + ebs_b_kmh
        e = max(0.05, 0.40 - 0.004 * v_cierre)
        advertencias.append(f"Coef. restitución estimado empíricamente: e={e:.2f} (v_cierre={v_cierre:.0f} km/h).")

    # ── 3. Velocidades post-impacto por conservación de momento 2D ───────────
    # Si no teníamos huellas, las calculamos ahora con momento + e
    #   m1·v1n_pre + m2·v2n_pre = m1·v1n_post' + m2·v2n_post'
    #   e = (v2n_post' - v1n_post') / (v1n_pre - v2n_pre)
    if v_post_a is None or v_post_b is None:
        closing_n = v1n_pre - v2n_pre
        # Sistema 2 ecuaciones, 2 incógnitas:
        denom = masa_a + masa_b
        v1n_post_calc = (masa_a * v1n_pre + masa_b * v2n_pre - masa_b * e * closing_n) / denom
        v2n_post_calc = (masa_a * v1n_pre + masa_b * v2n_pre + masa_a * e * closing_n) / denom
        if v_post_a is None:
            v_post_a = abs(v1n_post_calc) * 3.6 if abs(v1n_post_calc) > 0 else 0.0
            # Convertimos m/s → km/h (ya están en m/s desde las proyecciones sobre km/h... ajustar)
            # Nota: v1n_pre ya estaba en km/h, operamos consistentemente en km/h
            v1n_pre_ms = v1n_pre / 3.6
            v2n_pre_ms = v2n_pre / 3.6
            closing_ms = v1n_pre_ms - v2n_pre_ms
            v1n_post_ms = (masa_a * v1n_pre_ms + masa_b * v2n_pre_ms - masa_b * e * closing_ms) / denom
            v2n_post_ms = (masa_a * v1n_pre_ms + masa_b * v2n_pre_ms + masa_a * e * closing_ms) / denom
            v_post_a = abs(v1n_post_ms) * 3.6
            v_post_b = abs(v2n_post_ms) * 3.6

    # ── 4. Ángulos de salida post-impacto ─────────────────────────────────────
    # Las componentes tangenciales se conservan (no hay fricción lateral en el impacto puntual)
    # v_tangencial_A_post = v_tangencial_A_pre  (componente perpendicular a la línea de impacto)
    psi = math.radians(angulo_pre_a)
    vx_a_pre = (ebs_a_kmh / 3.6) * math.cos(psi)
    vy_a_pre = (ebs_a_kmh / 3.6) * math.sin(psi)

    # Componente normal y tangencial de A
    nx = math.cos(phi);  ny = math.sin(phi)
    tx = -ny;            ty = nx

    vn_a = vx_a_pre * nx + vy_a_pre * ny
    vt_a = vx_a_pre * tx + vy_a_pre * ty

    # Post impacto: normal cambia según e, tangencial se conserva
    v1n_post_ms_final = v_post_a / 3.6
    # Reconstruir vector
    vx_a_post = v1n_post_ms_final * nx + vt_a * tx
    vy_a_post = v1n_post_ms_final * ny + vt_a * ty
    angle_post_a = math.degrees(math.atan2(vy_a_post, vx_a_post)) % 360

    # Idem para B
    psi_b = math.radians(angulo_pre_b)
    vx_b_pre = (ebs_b_kmh / 3.6) * math.cos(psi_b)
    vy_b_pre = (ebs_b_kmh / 3.6) * math.sin(psi_b)
    vn_b = vx_b_pre * nx + vy_b_pre * ny
    vt_b = vx_b_pre * tx + vy_b_pre * ty
    v2n_post_ms_final = v_post_b / 3.6
    vx_b_post = v2n_post_ms_final * (-nx) + vt_b * tx
    vy_b_post = v2n_post_ms_final * (-ny) + vt_b * ty
    angle_post_b = math.degrees(math.atan2(vy_b_post, vx_b_post)) % 360

    # ── 5. Delta-V ────────────────────────────────────────────────────────────
    delta_v_a = abs(ebs_a_kmh - v_post_a)
    delta_v_b = abs(ebs_b_kmh - v_post_b)

    # ── 6. Verificación de conservación de momento ────────────────────────────
    px_pre = masa_a * (ebs_a_kmh / 3.6) * math.cos(math.radians(angulo_pre_a)) + \
             masa_b * (ebs_b_kmh / 3.6) * math.cos(math.radians(angulo_pre_b))
    py_pre = masa_a * (ebs_a_kmh / 3.6) * math.sin(math.radians(angulo_pre_a)) + \
             masa_b * (ebs_b_kmh / 3.6) * math.sin(math.radians(angulo_pre_b))
    px_post = masa_a * (v_post_a / 3.6) * math.cos(math.radians(angle_post_a)) + \
              masa_b * (v_post_b / 3.6) * math.cos(math.radians(angle_post_b))
    py_post = masa_a * (v_post_a / 3.6) * math.sin(math.radians(angle_post_a)) + \
              masa_b * (v_post_b / 3.6) * math.sin(math.radians(angle_post_b))

    mod_pre = math.sqrt(px_pre**2 + py_pre**2)
    mod_post = math.sqrt(px_post**2 + py_post**2)
    error_pct = abs(mod_post - mod_pre) / mod_pre * 100 if mod_pre > 0 else 0.0

    if error_pct > 15:
        advertencias.append(f"Error de momento {error_pct:.1f}% > 15% — revisar ángulos o velocidades.")

    # ── 7. Trayectorias previas ───────────────────────────────────────────────
    # Posición donde el conductor DEBIÓ reaccionar para evitar el accidente
    # x_inicial = x_PDI - v_pre * t_reaccion * cos(angulo)
    # Usamos velocidad pre-frenada si disponible, o EBS como aproximación
    v_pre_a = (v_pre_a_kmh or ebs_a_kmh) / 3.6    # m/s
    v_pre_b = (v_pre_b_kmh or ebs_b_kmh) / 3.6

    dist_reaccion_a = v_pre_a * tiempo_reaccion_s
    dist_reaccion_b = v_pre_b * tiempo_reaccion_s

    pos_inicial_a = (
        -dist_reaccion_a * math.cos(math.radians(angulo_pre_a)),
        -dist_reaccion_a * math.sin(math.radians(angulo_pre_a)),
    )
    pos_inicial_b = (
        -dist_reaccion_b * math.cos(math.radians(angulo_pre_b)),
        -dist_reaccion_b * math.sin(math.radians(angulo_pre_b)),
    )

    return ReconstructionResult(
        v_pre_a_kmh=round(ebs_a_kmh, 1),
        v_pre_b_kmh=round(ebs_b_kmh, 1),
        v_post_a_kmh=round(v_post_a, 1),
        v_post_b_kmh=round(v_post_b, 1),
        angle_post_a_deg=round(angle_post_a, 1),
        angle_post_b_deg=round(angle_post_b, 1),
        coef_restitucion=round(e, 3),
        delta_v_a_kmh=round(delta_v_a, 1),
        delta_v_b_kmh=round(delta_v_b, 1),
        pos_inicial_a=(round(pos_inicial_a[0], 1), round(pos_inicial_a[1], 1)),
        pos_inicial_b=(round(pos_inicial_b[0], 1), round(pos_inicial_b[1], 1)),
        error_momento_pct=round(error_pct, 1),
        advertencias=advertencias,
    )


def analizar_huellas(escena: "EscenaAccidente", mu: float = 0.65) -> list[EvidenciaHuella]:
    """
    Interpreta físicamente cada huella en la calzada.

    Para cada huella calcula:
      - Velocidad al inicio (Stannard Baker sobre longitud total)
      - Velocidad al final (0 si la huella termina sin impacto posterior, o EBS si acaba en PDI)
      - Interpretación en lenguaje pericial
    """
    resultados: list[EvidenciaHuella] = []

    for h in escena.huellas:
        # Velocidad al inicio de la huella: v = √(2·μ·g·d)
        v_inicio = math.sqrt(2 * mu * 9.81 * h.longitud_m) * 3.6  # km/h

        # Tipo de huella → interpretación
        if h.tipo == "frenada":
            v_fin = 0.0
            if h.curvatura == "recta":
                interp = (
                    f"Huella de frenada rectilínea de {h.longitud_m:.1f} m "
                    f"(vehículo {h.vehiculo_id}): neumáticos bloqueados, "
                    f"velocidad inicial estimada {v_inicio:.1f} km/h. "
                    f"Trayectoria estabilizada — sin pérdida de control lateral."
                )
            else:
                lado = "derecha" if h.curvatura == "curva_derecha" else "izquierda"
                interp = (
                    f"Huella de frenada curva hacia la {lado} de {h.longitud_m:.1f} m "
                    f"(vehículo {h.vehiculo_id}): frenada con giro simultáneo, "
                    f"velocidad inicial estimada {v_inicio:.1f} km/h. "
                    f"Indica maniobra evasiva o salida de carril durante frenada."
                )

        elif h.tipo == "derrape":
            v_fin = v_inicio * 0.6  # el derrape no detiene completamente
            lado = "derecha" if h.curvatura == "curva_derecha" else (
                "izquierda" if h.curvatura == "curva_izquierda" else "sin dirección definida"
            )
            interp = (
                f"Huella de derrape (yaw mark) hacia la {lado} de {h.longitud_m:.1f} m "
                f"(vehículo {h.vehiculo_id}): pérdida de adherencia lateral, "
                f"velocidad estimada al inicio {v_inicio:.1f} km/h. "
                f"Compatible con maniobra evasiva brusca o exceso de velocidad en curva."
            )

        elif h.tipo == "arrastre":
            v_fin = 0.0
            interp = (
                f"Huella de arrastre post-impacto de {h.longitud_m:.1f} m "
                f"(vehículo {h.vehiculo_id}): velocidad post-impacto estimada "
                f"{v_inicio:.1f} km/h. Revela dirección y magnitud del desplazamiento "
                f"tras la colisión."
            )

        elif h.tipo == "aceleracion":
            v_fin = v_inicio * 1.5
            interp = (
                f"Huella de aceleración (quemada) de {h.longitud_m:.1f} m "
                f"(vehículo {h.vehiculo_id}): aceleración brusca registrada, "
                f"incompatible con conducción prudente previa al suceso."
            )

        else:
            v_fin = 0.0
            interp = f"Huella tipo {h.tipo} de {h.longitud_m:.1f} m (vehículo {h.vehiculo_id})."

        resultados.append(EvidenciaHuella(
            vehiculo_id=h.vehiculo_id,
            tipo=h.tipo,
            longitud_m=h.longitud_m,
            velocidad_inicio_kmh=round(v_inicio, 1),
            velocidad_fin_kmh=round(v_fin, 1),
            curvatura=h.curvatura,
            interpretacion=interp,
        ))

    return resultados


def inferir_hipotesis(
    escena: "EscenaAccidente",
    evidencias_huellas: list[EvidenciaHuella],
    v_pre_a_kmh: float,
    v_pre_b_kmh: float,
    angulo_pre_a: float,
    angulo_pre_b: float,
    limite_velocidad_kmh: Optional[float] = None,
) -> list[HipotesisManobra]:
    """
    Inferencia probabilística bayesiana simplificada sobre hipótesis de maniobra.

    Evalúa cada hipótesis contando evidencias a favor y en contra,
    ponderadas por su relevancia forense.
    """
    hipotesis: list[HipotesisManobra] = []

    huellas_a = [h for h in evidencias_huellas if h.vehiculo_id == "A"]
    huellas_b = [h for h in evidencias_huellas if h.vehiculo_id == "B"]
    daños_sec = escena.daños_secundarios if escena else []

    tiene_derrape_a = any(h.tipo == "derrape" for h in huellas_a)
    tiene_derrape_b = any(h.tipo == "derrape" for h in huellas_b)
    tiene_frenada_curva_a = any(h.tipo == "frenada" and h.curvatura != "recta" for h in huellas_a)
    tiene_frenada_curva_b = any(h.tipo == "frenada" and h.curvatura != "recta" for h in huellas_b)
    tiene_daño_lateral = any(d.lado_calzada in ("izquierda", "derecha") for d in daños_sec)
    orientacion_girada_a = (
        escena.orientacion_final_a_deg is not None and
        abs(escena.orientacion_final_a_deg - angulo_pre_a) > 20
    )
    orientacion_girada_b = (
        escena.orientacion_final_b_deg is not None and
        abs(escena.orientacion_final_b_deg - angulo_pre_b) > 20
    )
    exceso_a = limite_velocidad_kmh and v_pre_a_kmh > limite_velocidad_kmh * 1.1
    exceso_b = limite_velocidad_kmh and v_pre_b_kmh > limite_velocidad_kmh * 1.1

    # ── Hipótesis 1: Maniobra evasiva ante obstáculo ────────────────────────
    h1_favor = []
    h1_contra = []

    if tiene_derrape_a or tiene_frenada_curva_a:
        h1_favor.append("Huella de derrape/frenada curva en vehículo A — giro brusco compatible con evasión")
    if tiene_daño_lateral:
        h1_favor.append("Daño en elemento lateral de la calzada — trayectoria desviada del carril original")
    if orientacion_girada_a:
        h1_favor.append(f"Vehículo A terminó girado {abs(escena.orientacion_final_a_deg - angulo_pre_a):.0f}° respecto a su dirección de marcha")
    if huellas_a and any(h.longitud_m < 5 for h in huellas_a if h.tipo == "frenada"):
        h1_favor.append("Huella de frenada corta — reacción tardía compatible con obstáculo imprevisto")

    if exceso_a:
        h1_contra.append(f"Vehículo A circulaba a {v_pre_a_kmh:.0f} km/h en zona limitada a {limite_velocidad_kmh:.0f} km/h — exceso de velocidad previo")
    if not (tiene_derrape_a or tiene_frenada_curva_a):
        h1_contra.append("Sin huellas de derrape ni frenada curva en vehículo A — trayectoria sin maniobra lateral detectada")

    prob_h1 = _calcular_probabilidad(len(h1_favor), len(h1_contra), prior=0.3)
    if h1_favor or h1_contra:
        hipotesis.append(HipotesisManobra(
            nombre="Maniobra evasiva ante obstáculo en calzada",
            probabilidad=prob_h1,
            evidencias_favor=h1_favor,
            evidencias_contra=h1_contra,
            conclusion=_conclusion_hipotesis("maniobra evasiva ante obstáculo en calzada", prob_h1, h1_favor, h1_contra),
        ))

    # ── Hipótesis 2: Pérdida de control por exceso de velocidad ─────────────
    h2_favor = []
    h2_contra = []

    if exceso_a:
        h2_favor.append(f"Velocidad A calculada ({v_pre_a_kmh:.0f} km/h) supera el límite ({limite_velocidad_kmh:.0f} km/h)")
    if tiene_derrape_a and not tiene_daño_lateral:
        h2_favor.append("Derrape sin impacto lateral — compatible con pérdida de control sin obstáculo externo")
    if orientacion_girada_a and not tiene_daño_lateral:
        h2_favor.append("Giro final sin daño lateral — el vehículo giró por inercia, no por evasión")

    if tiene_daño_lateral:
        h2_contra.append("Daño en elemento lateral indica que el vehículo sí encontró un obstáculo")
    if huellas_a and any(h.tipo == "frenada" and h.longitud_m > 10 for h in huellas_a):
        h2_contra.append("Frenada larga antes del derrape — conductor intentó frenar, no aceleró hacia la curva")

    prob_h2 = _calcular_probabilidad(len(h2_favor), len(h2_contra), prior=0.4)
    if h2_favor or h2_contra:
        hipotesis.append(HipotesisManobra(
            nombre="Pérdida de control por exceso de velocidad",
            probabilidad=prob_h2,
            evidencias_favor=h2_favor,
            evidencias_contra=h2_contra,
            conclusion=_conclusion_hipotesis("pérdida de control por exceso de velocidad", prob_h2, h2_favor, h2_contra),
        ))

    # ── Hipótesis 3: Invasión de carril contrario ────────────────────────────
    h3_favor = []
    h3_contra = []

    angulo_relativo = abs(angulo_pre_a - angulo_pre_b) % 360
    colision_frontal = angulo_relativo > 150 or angulo_relativo < 30

    if colision_frontal:
        h3_favor.append("Ángulo de impacto frontal — al menos uno de los vehículos estaba en carril contrario")
    if tiene_derrape_b and colision_frontal:
        h3_favor.append("Derrape en vehículo B antes del impacto frontal — posible corrección tardía de trayectoria")
    if exceso_b:
        h3_favor.append(f"Vehículo B circulaba a {v_pre_b_kmh:.0f} km/h — velocidad que reduce margen de reacción en caso de invasión")

    if not colision_frontal:
        h3_contra.append("Ángulo de impacto no es frontal — invasión de carril contrario menos probable")

    prob_h3 = _calcular_probabilidad(len(h3_favor), len(h3_contra), prior=0.25)
    if h3_favor or h3_contra:
        hipotesis.append(HipotesisManobra(
            nombre="Invasión de carril contrario",
            probabilidad=prob_h3,
            evidencias_favor=h3_favor,
            evidencias_contra=h3_contra,
            conclusion=_conclusion_hipotesis("invasión de carril contrario", prob_h3, h3_favor, h3_contra),
        ))

    # Ordenar por probabilidad descendente
    hipotesis.sort(key=lambda h: h.probabilidad, reverse=True)
    return hipotesis


def _calcular_probabilidad(n_favor: int, n_contra: int, prior: float = 0.5) -> float:
    """
    Actualización bayesiana simplificada.
    Cada evidencia a favor multiplica por 2.0, cada evidencia en contra por 0.4.
    """
    p = prior
    for _ in range(n_favor):
        p = min(p * 2.0, 0.95)
    for _ in range(n_contra):
        p = max(p * 0.4, 0.05)
    return round(p, 2)


def _conclusion_hipotesis(nombre: str, prob: float, favor: list, contra: list) -> str:
    if prob >= 0.70:
        nivel = "altamente compatible"
    elif prob >= 0.50:
        nivel = "compatible"
    elif prob >= 0.30:
        nivel = "posible pero no determinante"
    else:
        nivel = "poco probable"

    txt = f"La hipótesis de {nombre} es {nivel} con la evidencia física disponible (probabilidad estimada: {prob*100:.0f}%)."
    if contra:
        txt += f" Factores que la debilitan: {contra[0].lower()}."
    return txt

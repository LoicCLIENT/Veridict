import sys
sys.path.insert(0, '.')
from physics.crash3 import calculate_ebs, calculate_delta_v
from physics.stannard_baker import calculate_pre_brake_speed, calculate_stopping_distance

ebs = calculate_ebs(
    mediciones_C=[12.5,15.2,18.3,16.1,14.0,11.2],
    ancho_zona=85, masa=1350, coef_a=700, coef_b=2400
)
print(f"EBS CRASH3 (integracion por punto): {ebs} km/h")

dv = calculate_delta_v(ebs, 1350, 1400)
print(f"Delta-V A: {dv} km/h")

v_frenada = calculate_pre_brake_speed(15.0, coef_friccion=0.55)
print(f"Velocidad pre-frenada (15m, asfalto mojado mu=0.55): {v_frenada} km/h")

dist = calculate_stopping_distance(v_frenada, coef_friccion=0.55)
print(f"Distancia seguridad requerida: {dist['distancia_total']} m")
print("  - reaccion:", dist['distancia_reaccion'], "m")
print("  - frenada:", dist['distancia_frenada'], "m")

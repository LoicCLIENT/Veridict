"""
CASO ITRASA - Aulestia, Bizkaia (21/05/2020)
Reconstrucción forense completa del accidente

DATOS DEL INFORME:
- Vehículo: SEAT Ibiza 1.9 SDI, gris, 3.81m x 1.64m x 1.42m
- Bicicleta: ORBEA roja, sillín 79cm, manillar 55cm
- Víctima: Iurgi Beraza (ciclista)
- Carretera: 3.10m ancho, pendiente 9-11.6%
- Velocidad vehículo: ~50 km/h (límite 20 km/h)
- Proyección ciclista: 8.008 m
- Distancia lateral: 1.215 m
"""
import bpy
import math

print("=" * 60)
print("CASO ITRASA - Reconstrucción Forense Completa")
print("Accidente Aulestia, 21/05/2020")
print("=" * 60)

# ============ LIMPIEZA TOTAL ============
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for block in list(bpy.data.meshes) + list(bpy.data.materials) + list(bpy.data.curves):
    if hasattr(block, 'users') and block.users == 0:
        try:
            if isinstance(block, bpy.types.Mesh):
                bpy.data.meshes.remove(block)
            elif isinstance(block, bpy.types.Material):
                bpy.data.materials.remove(block)
            elif isinstance(block, bpy.types.Curve):
                bpy.data.curves.remove(block)
        except:
            pass

# ============ MATERIALES ============
def crear_material(nombre, color, metalico=0, rugosidad=0.5):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metalico
    bsdf.inputs['Roughness'].default_value = rugosidad
    return mat

# Paleta de colores
MAT_TIERRA = crear_material("Tierra", (0.78, 0.75, 0.68), 0, 0.95)
MAT_ASFALTO = crear_material("Asfalto", (0.18, 0.18, 0.18), 0, 0.9)
MAT_LINEA_BLANCA = crear_material("LineaBlanca", (0.92, 0.92, 0.92), 0, 0.4)
MAT_SEAT_GRIS = crear_material("SEAT_Gris", (0.55, 0.55, 0.58), 0.5, 0.4)
MAT_CRISTAL = crear_material("Cristal", (0.15, 0.2, 0.25), 0.1, 0.05)
MAT_RUEDA_COCHE = crear_material("RuedaCoche", (0.05, 0.05, 0.05), 0, 0.85)
MAT_LLANTA = crear_material("Llanta", (0.4, 0.4, 0.42), 0.8, 0.3)
MAT_FARO = crear_material("Faro", (0.9, 0.9, 0.85), 0, 0.1)
MAT_ORBEA_ROJO = crear_material("ORBEA_Rojo", (0.82, 0.08, 0.08), 0.6, 0.35)
MAT_RUEDA_BICI = crear_material("RuedaBici", (0.12, 0.12, 0.12), 0, 0.75)
MAT_CAMISETA_VERDE = crear_material("CamisetaVerde", (0.15, 0.58, 0.22), 0, 0.7)
MAT_PANTALON = crear_material("Pantalon", (0.1, 0.1, 0.15), 0, 0.75)
MAT_PIEL = crear_material("Piel", (0.85, 0.68, 0.52), 0, 0.65)
MAT_CASCO = crear_material("Casco", (0.08, 0.08, 0.1), 0, 0.6)
MAT_MEDICION = crear_material("Medicion", (0.01, 0.01, 0.01), 0, 0.5)
MAT_IMPACTO = crear_material("ZonaImpacto", (0.95, 0.6, 0.1), 0, 0.3)
MAT_TRAYECTORIA = crear_material("Trayectoria", (0.9, 0.2, 0.2), 0, 0.4)

# ============ ESCENARIO - Barrio Zubero ============
print("\n1. Creando escenario Barrio Zubero...")

# Terreno base
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
terreno = bpy.context.active_object
terreno.name = "Terreno"
terreno.data.materials.append(MAT_TIERRA)

# Carretera (3.10m ancho según informe)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
carretera = bpy.context.active_object
carretera.name = "Carretera_Zubero"
carretera.scale = (1.55, 22, 1)  # 3.10m ancho
carretera.data.materials.append(MAT_ASFALTO)

# Líneas de carril (discontinuas)
for y in range(-18, 19, 2):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y, 0.015))
    linea = bpy.context.active_object
    linea.name = f"LineaCarril_{y}"
    linea.scale = (0.04, 0.65, 1)
    linea.data.materials.append(MAT_LINEA_BLANCA)

# Bordes de carretera
for x in [-1.58, 1.58]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 0.012))
    borde = bpy.context.active_object
    borde.name = f"Borde_{x}"
    borde.scale = (0.06, 22, 1)
    borde.data.materials.append(MAT_LINEA_BLANCA)

# ============ SEAT IBIZA 1.9 SDI ============
print("2. Creando SEAT Ibiza 1.9 SDI (gris)...")

# Posición del coche después del impacto
SEAT_X, SEAT_Y = 0.4, 6

# Carrocería principal (3.81m x 1.64m x ~0.9m base)
bpy.ops.mesh.primitive_cube_add(size=1, location=(SEAT_X, SEAT_Y, 0.5))
carroceria = bpy.context.active_object
carroceria.name = "SEAT_Carroceria"
carroceria.scale = (0.82, 1.905, 0.38)
carroceria.data.materials.append(MAT_SEAT_GRIS)

# Cabina/techo
bpy.ops.mesh.primitive_cube_add(size=1, location=(SEAT_X, SEAT_Y + 0.15, 1.0))
cabina = bpy.context.active_object
cabina.name = "SEAT_Cabina"
cabina.scale = (0.78, 1.15, 0.38)
cabina.data.materials.append(MAT_SEAT_GRIS)

# Parabrisas (inclinado)
bpy.ops.mesh.primitive_cube_add(size=1, location=(SEAT_X, SEAT_Y - 0.75, 0.92))
parabrisas = bpy.context.active_object
parabrisas.name = "SEAT_Parabrisas"
parabrisas.scale = (0.72, 0.45, 0.02)
parabrisas.rotation_euler.x = math.radians(-25)
parabrisas.data.materials.append(MAT_CRISTAL)

# Luneta trasera
bpy.ops.mesh.primitive_cube_add(size=1, location=(SEAT_X, SEAT_Y + 1.1, 0.92))
luneta = bpy.context.active_object
luneta.name = "SEAT_Luneta"
luneta.scale = (0.68, 0.35, 0.02)
luneta.rotation_euler.x = math.radians(22)
luneta.data.materials.append(MAT_CRISTAL)

# Capó (parte frontal dañada por impacto)
bpy.ops.mesh.primitive_cube_add(size=1, location=(SEAT_X, SEAT_Y - 1.35, 0.72))
capo = bpy.context.active_object
capo.name = "SEAT_Capo"
capo.scale = (0.78, 0.55, 0.05)
capo.data.materials.append(MAT_SEAT_GRIS)

# Faros delanteros
for fx in [-0.55, 0.55]:
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(SEAT_X + fx, SEAT_Y - 1.85, 0.55))
    faro = bpy.context.active_object
    faro.name = f"SEAT_Faro_{fx}"
    faro.scale = (0.8, 0.3, 0.6)
    faro.data.materials.append(MAT_FARO)

# Ruedas (4 ruedas con llantas)
ruedas_pos = [(-0.62, -1.25), (0.62, -1.25), (-0.62, 1.35), (0.62, 1.35)]
for i, (rx, ry) in enumerate(ruedas_pos):
    # Neumático
    bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.18,
                                         location=(SEAT_X + rx, SEAT_Y + ry, 0.30))
    neumatico = bpy.context.active_object
    neumatico.name = f"SEAT_Neumatico_{i}"
    neumatico.rotation_euler.x = math.pi / 2
    neumatico.data.materials.append(MAT_RUEDA_COCHE)

    # Llanta
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.19,
                                         location=(SEAT_X + rx, SEAT_Y + ry, 0.30))
    llanta = bpy.context.active_object
    llanta.name = f"SEAT_Llanta_{i}"
    llanta.rotation_euler.x = math.pi / 2
    llanta.data.materials.append(MAT_LLANTA)

# Zona de impacto en el frontal (marca naranja)
bpy.ops.mesh.primitive_plane_add(size=0.5, location=(SEAT_X - 0.3, SEAT_Y - 1.9, 0.5))
zona_impacto = bpy.context.active_object
zona_impacto.name = "Zona_Impacto"
zona_impacto.rotation_euler.x = math.radians(90)
zona_impacto.scale = (0.8, 0.6, 1)
zona_impacto.data.materials.append(MAT_IMPACTO)

# ============ BICICLETA ORBEA ============
print("3. Creando bicicleta ORBEA (roja, caída)...")

BICI_X, BICI_Y = -1.6, 5.2

# Rueda trasera (torus)
bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.028,
                                  location=(BICI_X - 0.15, BICI_Y - 0.4, 0.22))
rueda_t = bpy.context.active_object
rueda_t.name = "ORBEA_RuedaTrasera"
rueda_t.rotation_euler = (math.radians(72), math.radians(18), 0)
rueda_t.data.materials.append(MAT_RUEDA_BICI)

# Rueda delantera (deformada por impacto)
bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.028,
                                  location=(BICI_X + 0.25, BICI_Y + 0.45, 0.28))
rueda_d = bpy.context.active_object
rueda_d.name = "ORBEA_RuedaDelantera"
rueda_d.rotation_euler = (math.radians(68), math.radians(22), math.radians(8))
rueda_d.data.materials.append(MAT_RUEDA_BICI)

# Cuadro principal (tubo diagonal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.9,
                                     location=(BICI_X + 0.05, BICI_Y, 0.35))
cuadro = bpy.context.active_object
cuadro.name = "ORBEA_Cuadro"
cuadro.rotation_euler = (math.radians(55), math.radians(15), math.radians(-18))
cuadro.data.materials.append(MAT_ORBEA_ROJO)

# Tubo horizontal superior
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.55,
                                     location=(BICI_X + 0.08, BICI_Y + 0.12, 0.48))
tubo_h = bpy.context.active_object
tubo_h.name = "ORBEA_TuboHorizontal"
tubo_h.rotation_euler = (math.radians(82), 0, math.radians(-15))
tubo_h.data.materials.append(MAT_ORBEA_ROJO)

# Horquilla delantera
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.45,
                                     location=(BICI_X + 0.28, BICI_Y + 0.5, 0.38))
horquilla = bpy.context.active_object
horquilla.name = "ORBEA_Horquilla"
horquilla.rotation_euler = (math.radians(65), math.radians(12), 0)
horquilla.data.materials.append(MAT_ORBEA_ROJO)

# Manillar (55cm ancho según informe)
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.55,
                                     location=(BICI_X + 0.35, BICI_Y + 0.58, 0.52))
manillar = bpy.context.active_object
manillar.name = "ORBEA_Manillar"
manillar.rotation_euler = (math.radians(75), math.radians(88), 0)
manillar.data.materials.append(MAT_ORBEA_ROJO)

# Sillín (79cm altura según informe - ahora caído)
bpy.ops.mesh.primitive_cube_add(size=0.12, location=(BICI_X - 0.12, BICI_Y - 0.28, 0.55))
sillin = bpy.context.active_object
sillin.name = "ORBEA_Sillin"
sillin.scale = (0.5, 1.4, 0.22)
sillin.rotation_euler = (math.radians(18), math.radians(12), 0)
sillin.data.materials.append(MAT_CASCO)

# Pedales
for px in [-0.15, 0.15]:
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(BICI_X + px, BICI_Y - 0.15, 0.22))
    pedal = bpy.context.active_object
    pedal.name = f"ORBEA_Pedal_{px}"
    pedal.scale = (1, 0.5, 0.3)
    pedal.data.materials.append(MAT_CASCO)

# ============ CICLISTA (Iurgi - proyectado 8.008m) ============
print("4. Creando ciclista Iurgi (proyectado)...")

# Posición final tras proyección de 8.008m
CIC_X, CIC_Y = -2.5, -2.8

# Torso (camiseta verde, tumbado)
bpy.ops.mesh.primitive_cube_add(size=1, location=(CIC_X, CIC_Y, 0.18))
torso = bpy.context.active_object
torso.name = "Iurgi_Torso"
torso.scale = (0.24, 0.48, 0.15)
torso.rotation_euler = (math.radians(5), math.radians(-8), math.radians(22))
torso.data.materials.append(MAT_CAMISETA_VERDE)

# Cabeza
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(CIC_X - 0.38, CIC_Y - 0.12, 0.14))
cabeza = bpy.context.active_object
cabeza.name = "Iurgi_Cabeza"
cabeza.data.materials.append(MAT_PIEL)

# Casco (dañado)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.135, location=(CIC_X - 0.38, CIC_Y - 0.12, 0.17))
casco = bpy.context.active_object
casco.name = "Iurgi_Casco"
casco.scale = (1, 1.15, 0.68)
casco.data.materials.append(MAT_CASCO)

# Brazos
for lado, angulo in [(-0.22, -35), (0.22, 40)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.52,
                                         location=(CIC_X + 0.08, CIC_Y + lado, 0.15))
    brazo = bpy.context.active_object
    brazo.name = f"Iurgi_Brazo_{lado:.0f}"
    brazo.rotation_euler = (math.radians(88), math.radians(angulo), 0)
    brazo.data.materials.append(MAT_CAMISETA_VERDE)

# Piernas
for lado, desfase in [(-0.1, 0), (0.1, 0.12)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.058, depth=0.62,
                                         location=(CIC_X + 0.55 + desfase, CIC_Y + lado, 0.1))
    pierna = bpy.context.active_object
    pierna.name = f"Iurgi_Pierna_{lado:.0f}"
    pierna.rotation_euler = (math.radians(92), math.radians(8), math.radians(-12))
    pierna.data.materials.append(MAT_PANTALON)

# Zapatillas
for lado in [-0.1, 0.1]:
    bpy.ops.mesh.primitive_cube_add(size=0.12, location=(CIC_X + 0.88, CIC_Y + lado, 0.06))
    zapato = bpy.context.active_object
    zapato.name = f"Iurgi_Zapato_{lado:.0f}"
    zapato.scale = (1.5, 0.6, 0.4)
    zapato.data.materials.append(MAT_CASCO)

# ============ TRAYECTORIA DE PROYECCIÓN ============
print("5. Creando trayectoria de proyección...")

# Línea de trayectoria (arco)
tray_curve = bpy.data.curves.new("Trayectoria", 'CURVE')
tray_curve.dimensions = '3D'
tray_curve.bevel_depth = 0.015
spline = tray_curve.splines.new('BEZIER')
spline.bezier_points.add(1)

# Punto inicio (sobre el capó)
spline.bezier_points[0].co = (BICI_X, BICI_Y, 1.2)
spline.bezier_points[0].handle_right = (BICI_X - 0.5, BICI_Y - 2, 2.5)
spline.bezier_points[0].handle_left = (BICI_X + 0.3, BICI_Y + 1, 0.8)

# Punto final (donde cayó el ciclista)
spline.bezier_points[1].co = (CIC_X, CIC_Y, 0.15)
spline.bezier_points[1].handle_left = (CIC_X + 0.5, CIC_Y + 2, 1.5)
spline.bezier_points[1].handle_right = (CIC_X - 0.3, CIC_Y - 1, 0)

trayectoria_obj = bpy.data.objects.new("Linea_Trayectoria", tray_curve)
bpy.context.collection.objects.link(trayectoria_obj)
trayectoria_obj.data.materials.append(MAT_TRAYECTORIA)

# ============ MEDICIONES FORENSES ============
print("6. Creando mediciones forenses...")

def crear_medicion_completa(p1, p2, texto, offset_txt, mostrar_flechas=True):
    """Crea línea de medición con flechas y texto"""
    # Línea
    curva = bpy.data.curves.new(f"Med_{texto}", 'CURVE')
    curva.dimensions = '3D'
    curva.bevel_depth = 0.02
    sp = curva.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (*p1, 1)
    sp.points[1].co = (*p2, 1)

    linea = bpy.data.objects.new(f"Linea_{texto}", curva)
    bpy.context.collection.objects.link(linea)
    linea.data.materials.append(MAT_MEDICION)

    if mostrar_flechas:
        # Calcular ángulo
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        angulo = math.atan2(dy, dx)

        # Flechas en extremos
        for punto, rotacion in [(p1, math.pi), (p2, 0)]:
            bpy.ops.mesh.primitive_cone_add(radius1=0.085, depth=0.16, location=punto)
            flecha = bpy.context.active_object
            flecha.name = f"Flecha_{texto}_{rotacion:.0f}"
            flecha.rotation_euler = (0, math.pi/2, angulo + rotacion)
            flecha.data.materials.append(MAT_MEDICION)

    # Texto
    pos_txt = ((p1[0]+p2[0])/2 + offset_txt[0],
               (p1[1]+p2[1])/2 + offset_txt[1],
               max(p1[2], p2[2]) + offset_txt[2])
    bpy.ops.object.text_add(location=pos_txt)
    txt = bpy.context.active_object
    txt.name = f"Texto_{texto}"
    txt.data.body = texto
    txt.data.size = 0.38
    txt.data.align_x = 'CENTER'
    txt.rotation_euler = (math.pi/2, 0, 0)
    txt.data.materials.append(MAT_MEDICION)

# Distancia de proyección: 8.008 m
crear_medicion_completa(
    p1=(BICI_X, BICI_Y, 0.12),
    p2=(CIC_X, CIC_Y, 0.12),
    texto="8.008 m",
    offset_txt=(1.8, 0, 0.45)
)

# Distancia lateral: 1.215 m
crear_medicion_completa(
    p1=(SEAT_X, SEAT_Y - 1.5, 0.12),
    p2=(BICI_X, BICI_Y, 0.12),
    texto="1.215 m",
    offset_txt=(0, 0.9, 0.45)
)

# Etiqueta de velocidad
bpy.ops.object.text_add(location=(SEAT_X + 2, SEAT_Y, 1.8))
txt_vel = bpy.context.active_object
txt_vel.name = "Texto_Velocidad"
txt_vel.data.body = "~50 km/h"
txt_vel.data.size = 0.32
txt_vel.data.align_x = 'CENTER'
txt_vel.rotation_euler = (math.pi/2, 0, 0)
txt_vel.data.materials.append(MAT_IMPACTO)

# ============ ILUMINACIÓN ============
print("7. Configurando iluminación...")

# Sol principal
bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
sol = bpy.context.active_object
sol.name = "Sol_Principal"
sol.data.energy = 5
sol.data.angle = math.radians(10)
sol.rotation_euler = (math.radians(48), 0, math.radians(32))

# Luz de relleno
bpy.ops.object.light_add(type='AREA', location=(-10, 10, 15))
relleno = bpy.context.active_object
relleno.name = "Luz_Relleno"
relleno.data.energy = 300
relleno.data.size = 10

# Cielo
world = bpy.data.worlds.new("Cielo_Aulestia")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs['Color'].default_value = (0.68, 0.78, 0.88, 1)
bg.inputs['Strength'].default_value = 0.9

# ============ CÁMARAS ============
print("8. Configurando cámaras...")

# Cenital (vista técnica ortográfica)
bpy.ops.object.camera_add(location=(0, 1.5, 25))
cam_cenital = bpy.context.active_object
cam_cenital.name = "Cam_Cenital"
cam_cenital.data.type = 'ORTHO'
cam_cenital.data.ortho_scale = 22

# Perspectiva 3D (estilo Virtual Crash)
bpy.ops.object.camera_add(location=(14, -16, 9))
cam_3d = bpy.context.active_object
cam_3d.name = "Cam_3D"
cam_3d.rotation_euler = (math.radians(62), 0, math.radians(42))
cam_3d.data.lens = 28

# Frontal (vista del conductor)
bpy.ops.object.camera_add(location=(6, -16, 4.5))
cam_frontal = bpy.context.active_object
cam_frontal.name = "Cam_Frontal"
cam_frontal.rotation_euler = (math.radians(78), 0, math.radians(20))
cam_frontal.data.lens = 40

# Lateral (vista del impacto)
bpy.ops.object.camera_add(location=(-12, 4, 5))
cam_lateral = bpy.context.active_object
cam_lateral.name = "Cam_Lateral"
cam_lateral.rotation_euler = (math.radians(75), 0, math.radians(-90))
cam_lateral.data.lens = 35

bpy.context.scene.camera = cam_cenital

# Configuración de render
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("\n" + "=" * 60)
print("ESCENA ITRASA COMPLETA")
print("-" * 60)
print("Vehículo: SEAT Ibiza 1.9 SDI (gris)")
print("Bicicleta: ORBEA (roja)")
print("Víctima: Iurgi Beraza (camiseta verde)")
print("Proyección: 8.008 m")
print("Distancia lateral: 1.215 m")
print("Velocidad estimada: ~50 km/h")
print("=" * 60)

"""
Escena LIMPIA - Solo geometría primitiva, sin GLTF
Caso ITRASA: SEAT Ibiza vs Ciclista
"""
import bpy
import math

print("=" * 60)
print("ESCENA LIMPIA - Geometría Simple")
print("=" * 60)

# ============ LIMPIAR ============
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for c in list(bpy.data.curves):
    bpy.data.curves.remove(c)

# ============ MATERIALES ============
def mat(name, color, metallic=0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

# Materiales
MAT_SUELO = mat("Suelo", (0.82, 0.80, 0.76), 0, 0.9)
MAT_ASFALTO = mat("Asfalto", (0.22, 0.22, 0.22), 0, 0.85)
MAT_LINEA = mat("LineaBlanca", (0.95, 0.95, 0.95), 0, 0.3)
MAT_COCHE = mat("CocheGris", (0.5, 0.5, 0.55), 0.6, 0.35)
MAT_CRISTAL = mat("Cristal", (0.2, 0.25, 0.3), 0, 0.1)
MAT_RUEDA = mat("Rueda", (0.08, 0.08, 0.08), 0, 0.8)
MAT_BICI = mat("BiciRoja", (0.85, 0.12, 0.12), 0.7, 0.3)
MAT_CAMISETA = mat("CamisetaVerde", (0.18, 0.65, 0.28), 0, 0.7)
MAT_PANTALON = mat("Pantalon", (0.12, 0.12, 0.18), 0, 0.7)
MAT_PIEL = mat("Piel", (0.88, 0.72, 0.58), 0, 0.6)
MAT_MEDIDA = mat("Medida", (0.02, 0.02, 0.02), 0, 0.4)

# ============ ESCENARIO ============
print("1. Escenario...")

# Suelo
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
bpy.context.active_object.name = "Suelo"
bpy.context.active_object.data.materials.append(MAT_SUELO)

# Carretera (3.1m ancho)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.005))
road = bpy.context.active_object
road.name = "Carretera"
road.scale = (1.55, 18, 1)
road.data.materials.append(MAT_ASFALTO)

# Líneas de carril
for y in range(-15, 16, 2):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y, 0.01))
    line = bpy.context.active_object
    line.name = f"Linea_{y}"
    line.scale = (0.04, 0.7, 1)
    line.data.materials.append(MAT_LINEA)

# ============ COCHE (SEAT Ibiza) ============
print("2. SEAT Ibiza gris...")

# Dimensiones: 3.81m largo, 1.64m ancho, 1.42m alto
CAR_X, CAR_Y, CAR_Z = 0.3, 5, 0

# Carrocería inferior
bpy.ops.mesh.primitive_cube_add(size=1, location=(CAR_X, CAR_Y, 0.45))
body = bpy.context.active_object
body.name = "Coche_Carroceria"
body.scale = (0.82, 1.9, 0.35)
body.data.materials.append(MAT_COCHE)

# Cabina
bpy.ops.mesh.primitive_cube_add(size=1, location=(CAR_X, CAR_Y + 0.2, 0.95))
cabin = bpy.context.active_object
cabin.name = "Coche_Cabina"
cabin.scale = (0.75, 1.1, 0.35)
cabin.data.materials.append(MAT_COCHE)

# Cristales (ventanas)
bpy.ops.mesh.primitive_cube_add(size=1, location=(CAR_X, CAR_Y + 0.2, 0.95))
glass = bpy.context.active_object
glass.name = "Coche_Cristal"
glass.scale = (0.72, 1.05, 0.30)
glass.data.materials.append(MAT_CRISTAL)

# Ruedas
wheel_pos = [(-0.55, -1.3), (0.55, -1.3), (-0.55, 1.3), (0.55, 1.3)]
for i, (wx, wy) in enumerate(wheel_pos):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.18,
                                         location=(CAR_X + wx, CAR_Y + wy, 0.28))
    wheel = bpy.context.active_object
    wheel.name = f"Coche_Rueda_{i}"
    wheel.rotation_euler.x = math.pi / 2
    wheel.data.materials.append(MAT_RUEDA)

# ============ BICICLETA (ORBEA) ============
print("3. Bicicleta ORBEA roja (caída)...")

BICI_X, BICI_Y, BICI_Z = -1.8, 4.5, 0.25

# Rueda trasera
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.025,
                                  location=(BICI_X, BICI_Y - 0.45, BICI_Z))
w1 = bpy.context.active_object
w1.name = "Bici_RuedaTrasera"
w1.rotation_euler = (math.radians(75), math.radians(15), 0)
w1.data.materials.append(MAT_BICI)

# Rueda delantera
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.025,
                                  location=(BICI_X + 0.3, BICI_Y + 0.5, BICI_Z + 0.1))
w2 = bpy.context.active_object
w2.name = "Bici_RuedaDelantera"
w2.rotation_euler = (math.radians(70), math.radians(20), math.radians(10))
w2.data.materials.append(MAT_BICI)

# Cuadro diagonal
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.85,
                                     location=(BICI_X + 0.15, BICI_Y, BICI_Z + 0.2))
frame = bpy.context.active_object
frame.name = "Bici_Cuadro"
frame.rotation_euler = (math.radians(60), math.radians(12), math.radians(-20))
frame.data.materials.append(MAT_BICI)

# Tubo horizontal
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.5,
                                     location=(BICI_X + 0.1, BICI_Y + 0.1, BICI_Z + 0.4))
tube = bpy.context.active_object
tube.name = "Bici_TuboHoriz"
tube.rotation_euler = (math.radians(85), 0, math.radians(-15))
tube.data.materials.append(MAT_BICI)

# Manillar
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.45,
                                     location=(BICI_X + 0.35, BICI_Y + 0.55, BICI_Z + 0.35))
handlebar = bpy.context.active_object
handlebar.name = "Bici_Manillar"
handlebar.rotation_euler = (math.radians(80), math.radians(90), 0)
handlebar.data.materials.append(MAT_BICI)

# Sillín
bpy.ops.mesh.primitive_cube_add(size=0.12, location=(BICI_X - 0.1, BICI_Y - 0.3, BICI_Z + 0.45))
seat = bpy.context.active_object
seat.name = "Bici_Sillin"
seat.scale = (0.6, 1.5, 0.25)
seat.rotation_euler = (math.radians(15), math.radians(10), 0)
seat.data.materials.append(MAT_RUEDA)

# ============ CICLISTA (proyectado 8m) ============
print("4. Ciclista con camiseta verde...")

CIC_X, CIC_Y, CIC_Z = -2.8, -3.5, 0.12

# Torso (tumbado)
bpy.ops.mesh.primitive_cube_add(size=1, location=(CIC_X, CIC_Y, CIC_Z + 0.15))
torso = bpy.context.active_object
torso.name = "Ciclista_Torso"
torso.scale = (0.22, 0.45, 0.14)
torso.rotation_euler = (math.radians(8), math.radians(-5), math.radians(25))
torso.data.materials.append(MAT_CAMISETA)

# Cabeza
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(CIC_X - 0.35, CIC_Y - 0.15, CIC_Z + 0.12))
head = bpy.context.active_object
head.name = "Ciclista_Cabeza"
head.data.materials.append(MAT_PIEL)

# Casco
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(CIC_X - 0.35, CIC_Y - 0.15, CIC_Z + 0.15))
helmet = bpy.context.active_object
helmet.name = "Ciclista_Casco"
helmet.scale = (1, 1.1, 0.7)
helmet.data.materials.append(MAT_RUEDA)

# Brazos
for side, angle in [(-0.18, -30), (0.18, 30)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.45,
                                         location=(CIC_X + 0.1, CIC_Y + side, CIC_Z + 0.12))
    arm = bpy.context.active_object
    arm.name = f"Ciclista_Brazo_{side}"
    arm.rotation_euler = (math.radians(85), math.radians(angle), 0)
    arm.data.materials.append(MAT_CAMISETA)

# Piernas
for side, offset in [(-0.08, 0), (0.08, 0.15)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.55,
                                         location=(CIC_X + 0.45 + offset, CIC_Y + side, CIC_Z + 0.08))
    leg = bpy.context.active_object
    leg.name = f"Ciclista_Pierna_{side}"
    leg.rotation_euler = (math.radians(88), math.radians(5), math.radians(-15))
    leg.data.materials.append(MAT_PANTALON)

# ============ MEDICIONES ============
print("5. Líneas de medición...")

def crear_medicion(p1, p2, texto, offset_texto):
    # Línea
    curve = bpy.data.curves.new(f"Curva_{texto}", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.022
    sp = curve.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (*p1, 1)
    sp.points[1].co = (*p2, 1)
    obj = bpy.data.objects.new(f"Linea_{texto}", curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(MAT_MEDIDA)

    # Flechas
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    for pt, flip in [(p1, math.pi), (p2, 0)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.09, depth=0.18, location=pt)
        arr = bpy.context.active_object
        arr.name = f"Flecha_{texto}_{flip:.0f}"
        arr.rotation_euler = (0, math.pi/2, angle + flip)
        arr.data.materials.append(MAT_MEDIDA)

    # Texto
    mid = ((p1[0]+p2[0])/2 + offset_texto[0],
           (p1[1]+p2[1])/2 + offset_texto[1],
           p1[2] + offset_texto[2])
    bpy.ops.object.text_add(location=mid)
    txt = bpy.context.active_object
    txt.name = f"Texto_{texto}"
    txt.data.body = texto
    txt.data.size = 0.42
    txt.data.align_x = 'CENTER'
    txt.rotation_euler = (math.pi/2, 0, 0)
    txt.data.materials.append(MAT_MEDIDA)

# Proyección: bici -> ciclista (8.008m)
crear_medicion(
    p1=(BICI_X, BICI_Y, 0.15),
    p2=(CIC_X, CIC_Y, 0.15),
    texto="8.008 m",
    offset_texto=(1.5, 0, 0.5)
)

# Lateral: coche -> bici (1.215m)
crear_medicion(
    p1=(CAR_X, CAR_Y, 0.15),
    p2=(BICI_X, BICI_Y, 0.15),
    texto="1.215 m",
    offset_texto=(0, 0.8, 0.5)
)

# ============ ILUMINACIÓN ============
print("6. Iluminación...")

bpy.ops.object.light_add(type='SUN', location=(8, -8, 18))
sun = bpy.context.active_object
sun.name = "Sol"
sun.data.energy = 4.5
sun.data.angle = math.radians(12)
sun.rotation_euler = (math.radians(50), 0, math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-8, 8, 12))
fill = bpy.context.active_object
fill.name = "Relleno"
fill.data.energy = 250
fill.data.size = 8

# Cielo
world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs['Color'].default_value = (0.72, 0.80, 0.90, 1)
bg.inputs['Strength'].default_value = 0.85

# ============ CÁMARAS ============
print("7. Cámaras...")

# Cenital ortográfica
bpy.ops.object.camera_add(location=(0, 1, 22))
cam_top = bpy.context.active_object
cam_top.name = "Cam_Cenital"
cam_top.data.type = 'ORTHO'
cam_top.data.ortho_scale = 20

# Perspectiva 3D
bpy.ops.object.camera_add(location=(12, -14, 8))
cam_3d = bpy.context.active_object
cam_3d.name = "Cam_3D"
cam_3d.rotation_euler = (math.radians(65), 0, math.radians(42))
cam_3d.data.lens = 32

# Frontal
bpy.ops.object.camera_add(location=(5, -14, 4))
cam_front = bpy.context.active_object
cam_front.name = "Cam_Frontal"
cam_front.rotation_euler = (math.radians(78), 0, math.radians(18))
cam_front.data.lens = 45

bpy.context.scene.camera = cam_top

# Config render
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("\n" + "=" * 60)
print("ESCENA LIMPIA CREADA")
print("- Coche SEAT Ibiza gris")
print("- Bicicleta ORBEA roja caída")
print("- Ciclista verde proyectado")
print("- Mediciones 8.008m y 1.215m")
print("=" * 60)

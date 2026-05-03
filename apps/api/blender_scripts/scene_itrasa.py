"""
Escena ITRASA - Caso Aulestia (Iurgi Beraza)
Reconstrucción forense profesional estilo Virtual Crash 5.0

Datos del informe:
- SEAT Ibiza: 3.81m largo, 1.64m ancho, gris
- ORBEA bicicleta: roja
- Ciclista: camiseta verde
- Carretera: 3.10m ancho
- Medidas: 8.008m proyección, 1.215m lateral
- Velocidad vehículo: ~50 km/h
"""
import bpy
import math
import os

MODELS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\models\extracted"

# ============= LIMPIEZA =============
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes) + list(bpy.data.materials) + list(bpy.data.curves):
        if block.users == 0:
            if isinstance(block, bpy.types.Mesh):
                bpy.data.meshes.remove(block)
            elif isinstance(block, bpy.types.Material):
                bpy.data.materials.remove(block)
            elif isinstance(block, bpy.types.Curve):
                bpy.data.curves.remove(block)

# ============= MATERIALES =============
def mat_color(name, color, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

# ============= ESCENARIO =============
def create_ground():
    """Suelo gris claro (tierra/cemento)"""
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01))
    obj = bpy.context.active_object
    obj.name = "Suelo"
    obj.data.materials.append(mat_color("Mat_Suelo", (0.75, 0.73, 0.70), 0.9))

def create_road():
    """Carretera de 3.10m de ancho según informe"""
    # Asfalto principal
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Carretera"
    road.scale = (1.55, 15, 1)  # 3.10m ancho
    road.data.materials.append(mat_color("Mat_Asfalto", (0.25, 0.25, 0.25), 0.85))

    # Línea central discontinua
    for i in range(-12, 13, 2):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, i, 0.005))
        line = bpy.context.active_object
        line.name = f"Linea_{i}"
        line.scale = (0.05, 0.6, 1)
        line.data.materials.append(mat_color(f"Blanco_{i}", (0.95, 0.95, 0.95), 0.3))

    # Bordes de carretera
    for x in [-1.55, 1.55]:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 0.003))
        edge = bpy.context.active_object
        edge.name = f"Borde_{x}"
        edge.scale = (0.08, 15, 1)
        edge.data.materials.append(mat_color(f"BordeBl_{x}", (0.9, 0.9, 0.9), 0.4))

# ============= VEHÍCULOS (SIMPLIFICADOS SI GLTF FALLA) =============
def create_simple_car(name, loc, rot_z, color):
    """Coche simplificado tipo SEAT Ibiza: 3.81m x 1.64m x 1.4m"""
    # Carrocería
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    body = bpy.context.active_object
    body.name = name
    body.scale = (0.82, 1.9, 0.55)  # 1.64m ancho, 3.8m largo, 1.1m alto (mitad)
    body.location.z = 0.55
    body.rotation_euler.z = math.radians(rot_z)
    body.data.materials.append(mat_color(f"Mat_{name}", color, 0.3))

    # Cabina (parte superior)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 1.1))
    cabin = bpy.context.active_object
    cabin.name = f"{name}_Cabina"
    cabin.scale = (0.7, 1.2, 0.4)
    cabin.rotation_euler.z = math.radians(rot_z)
    cabin.data.materials.append(mat_color(f"Mat_{name}_Cab", color, 0.3))
    cabin.parent = body

    # Ruedas
    wheel_mat = mat_color(f"Rueda_{name}", (0.1, 0.1, 0.1), 0.8)
    positions = [(-0.6, -1.2, 0.25), (0.6, -1.2, 0.25), (-0.6, 1.2, 0.25), (0.6, 1.2, 0.25)]
    for i, (wx, wy, wz) in enumerate(positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.18, location=(loc[0]+wx, loc[1]+wy, wz))
        wheel = bpy.context.active_object
        wheel.name = f"{name}_Rueda_{i}"
        wheel.rotation_euler = (math.pi/2, 0, math.radians(rot_z))
        wheel.data.materials.append(wheel_mat)
        wheel.parent = body

    return body

def create_simple_bicycle(name, loc, rot, color):
    """Bicicleta simplificada"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    parent = bpy.context.active_object
    parent.name = name
    parent.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))

    mat = mat_color(f"Mat_{name}", color, 0.4)

    # Cuadro (tubo principal)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.9, location=(0, 0, 0.45))
    frame = bpy.context.active_object
    frame.rotation_euler.x = math.radians(70)
    frame.data.materials.append(mat)
    frame.parent = parent

    # Rueda trasera
    bpy.ops.mesh.primitive_torus_add(major_radius=0.33, minor_radius=0.025, location=(0, -0.4, 0.33))
    wheel1 = bpy.context.active_object
    wheel1.rotation_euler.x = math.pi/2
    wheel1.data.materials.append(mat_color("Rueda_Bici1", (0.15, 0.15, 0.15), 0.7))
    wheel1.parent = parent

    # Rueda delantera
    bpy.ops.mesh.primitive_torus_add(major_radius=0.33, minor_radius=0.025, location=(0, 0.5, 0.33))
    wheel2 = bpy.context.active_object
    wheel2.rotation_euler.x = math.pi/2
    wheel2.data.materials.append(mat_color("Rueda_Bici2", (0.15, 0.15, 0.15), 0.7))
    wheel2.parent = parent

    # Manillar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.55, location=(0, 0.45, 0.85))
    handlebar = bpy.context.active_object
    handlebar.rotation_euler.y = math.pi/2
    handlebar.data.materials.append(mat)
    handlebar.parent = parent

    # Sillín
    bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0, -0.3, 0.85))
    seat = bpy.context.active_object
    seat.scale = (0.8, 1.5, 0.3)
    seat.data.materials.append(mat_color("Sillin", (0.1, 0.1, 0.1), 0.6))
    seat.parent = parent

    return parent

def create_simple_person(name, loc, rot, shirt_color):
    """Persona simplificada (ciclista)"""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    parent = bpy.context.active_object
    parent.name = name
    parent.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))

    # Torso
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.85))
    torso = bpy.context.active_object
    torso.name = f"{name}_Torso"
    torso.scale = (0.22, 0.15, 0.3)
    torso.data.materials.append(mat_color("Camiseta", shirt_color, 0.6))
    torso.parent = parent

    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, 1.25))
    head = bpy.context.active_object
    head.name = f"{name}_Cabeza"
    head.data.materials.append(mat_color("Piel", (0.85, 0.7, 0.55), 0.5))
    head.parent = parent

    # Piernas
    leg_mat = mat_color("Pantalon", (0.15, 0.15, 0.2), 0.7)
    for x in [-0.08, 0.08]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.5, location=(x, 0, 0.35))
        leg = bpy.context.active_object
        leg.data.materials.append(leg_mat)
        leg.parent = parent

    # Brazos
    arm_mat = mat_color("Brazos", shirt_color, 0.6)
    for x in [-0.28, 0.28]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.35, location=(x, 0, 0.85))
        arm = bpy.context.active_object
        arm.rotation_euler.y = math.radians(15 if x > 0 else -15)
        arm.data.materials.append(arm_mat)
        arm.parent = parent

    return parent

# ============= IMPORTAR MODELOS GLTF =============
def import_gltf_model(folder, name, loc, rot, scale):
    """Intenta importar modelo GLTF, si falla usa geometría simple"""
    filepath = os.path.join(MODELS_DIR, folder, "scene.gltf")

    if not os.path.exists(filepath):
        print(f"WARN: No existe {filepath}")
        return None

    try:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=filepath)
        new_objs = list(set(bpy.data.objects) - before)

        if not new_objs:
            return None

        # Crear parent
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
        parent = bpy.context.active_object
        parent.name = name
        parent.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
        parent.scale = scale

        for obj in new_objs:
            obj.parent = parent

        print(f"OK: Importado {name} ({len(new_objs)} objetos)")
        return parent

    except Exception as e:
        print(f"ERROR importando {folder}: {e}")
        return None

# ============= MEDICIONES FORENSES =============
def create_measurement(p1, p2, text, offset=(0, 0, 0.5)):
    """Línea de medición con flechas y texto"""
    # Línea
    curve = bpy.data.curves.new(f"Medida_{text}", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.02
    spline = curve.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (*p1, 1)
    spline.points[1].co = (*p2, 1)

    line_obj = bpy.data.objects.new(f"Linea_{text}", curve)
    bpy.context.collection.objects.link(line_obj)

    line_mat = mat_color(f"Negro_{text}", (0.02, 0.02, 0.02), 0.3)
    line_obj.data.materials.append(line_mat)

    # Flechas en los extremos
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)

    for pt, flip in [(p1, math.pi), (p2, 0)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.2, location=pt)
        arrow = bpy.context.active_object
        arrow.name = f"Flecha_{text}_{flip}"
        arrow.rotation_euler = (0, math.pi/2, angle + flip)
        arrow.data.materials.append(line_mat)

    # Texto con medida
    mid = ((p1[0]+p2[0])/2 + offset[0], (p1[1]+p2[1])/2 + offset[1], max(p1[2], p2[2]) + offset[2])
    bpy.ops.object.text_add(location=mid)
    txt = bpy.context.active_object
    txt.name = f"Texto_{text}"
    txt.data.body = text
    txt.data.size = 0.45
    txt.data.align_x = 'CENTER'
    txt.rotation_euler = (math.pi/2, 0, 0)

    txt_mat = mat_color(f"TxtMat_{text}", (0.05, 0.05, 0.05), 0.4)
    txt.data.materials.append(txt_mat)

# ============= CÁMARAS =============
def setup_cameras():
    """Configura 3 cámaras: cenital, perspectiva, frontal"""
    cameras = []

    # Cenital (ortográfica - vista técnica)
    bpy.ops.object.camera_add(location=(0, 2, 18))
    cam_top = bpy.context.active_object
    cam_top.name = "Cam_Cenital"
    cam_top.data.type = 'ORTHO'
    cam_top.data.ortho_scale = 22
    cam_top.rotation_euler = (0, 0, 0)
    cameras.append(cam_top)

    # Perspectiva 3D (estilo Virtual Crash)
    bpy.ops.object.camera_add(location=(10, -12, 6))
    cam_3d = bpy.context.active_object
    cam_3d.name = "Cam_3D"
    cam_3d.rotation_euler = (math.radians(70), 0, math.radians(40))
    cam_3d.data.lens = 35
    cameras.append(cam_3d)

    # Frontal (vista del conductor)
    bpy.ops.object.camera_add(location=(3, -10, 3))
    cam_front = bpy.context.active_object
    cam_front.name = "Cam_Frontal"
    cam_front.rotation_euler = (math.radians(80), 0, math.radians(15))
    cam_front.data.lens = 50
    cameras.append(cam_front)

    return cameras

# ============= ILUMINACIÓN =============
def setup_lighting():
    """Iluminación suave tipo estudio forense"""
    # Sol principal
    bpy.ops.object.light_add(type='SUN', location=(8, -8, 15))
    sun = bpy.context.active_object
    sun.name = "Sol"
    sun.data.energy = 3.5
    sun.data.angle = math.radians(15)
    sun.rotation_euler = (math.radians(55), 0, math.radians(35))

    # Luz de relleno
    bpy.ops.object.light_add(type='AREA', location=(-6, 6, 10))
    fill = bpy.context.active_object
    fill.name = "Relleno"
    fill.data.energy = 150
    fill.data.size = 6

    # Fondo/cielo
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.7, 0.78, 0.88, 1)  # Cielo claro
        bg.inputs['Strength'].default_value = 0.8

# ============= CREAR ESCENA COMPLETA =============
print("="*60)
print("ESCENA ITRASA - Caso Aulestia")
print("="*60)

clear_scene()

print("\n1. Creando escenario...")
create_ground()
create_road()

print("\n2. Posicionando vehículos...")

# Intentar importar modelos GLTF, si falla usar simplificados
USE_SIMPLE = True  # Cambiar a False para intentar GLTF

if USE_SIMPLE:
    # SEAT Ibiza gris - posición de impacto
    # Según informe: vehículo circulando hacia el norte, impacta ciclista
    coche = create_simple_car(
        "SEAT_Ibiza",
        loc=(0.5, 4, 0),
        rot_z=180,  # Mirando hacia sur (acaba de impactar)
        color=(0.45, 0.45, 0.48)  # Gris
    )

    # Bicicleta ORBEA roja - caída tras impacto
    bici = create_simple_bicycle(
        "ORBEA",
        loc=(-1.2, 3.5, 0.1),
        rot=(0, 25, 75),  # Caída lateral
        color=(0.8, 0.1, 0.1)  # Roja
    )

    # Ciclista - proyectado 8.008m según informe
    # Posición final tras proyección
    ciclista = create_simple_person(
        "Ciclista_Iurgi",
        loc=(-2, -4, 0.1),
        rot=(85, 0, 20),  # Tumbado en el suelo
        shirt_color=(0.2, 0.6, 0.25)  # Verde
    )
else:
    # Usar modelos GLTF
    coche = import_gltf_model("coche", "SEAT_Ibiza", (0.5, 4, 0), (0, 0, 180), (0.016, 0.016, 0.016))
    bici = import_gltf_model("bicicleta", "ORBEA", (-1.2, 3.5, 0.1), (0, 25, 75), (1.0, 1.0, 1.0))
    ciclista = import_gltf_model("humano", "Ciclista", (-2, -4, 0.1), (85, 0, 20), (0.9, 0.9, 0.9))

print("\n3. Creando mediciones forenses...")

# Medida de proyección: 8.008 m (desde punto de impacto hasta posición final ciclista)
create_measurement(
    p1=(-1.2, 3.5, 0.15),
    p2=(-2, -4, 0.15),
    text="8.008 m",
    offset=(1.8, 0, 0.6)
)

# Medida lateral: 1.215 m (distancia lateral vehículo-bicicleta)
create_measurement(
    p1=(0.5, 4, 0.15),
    p2=(-1.2, 3.5, 0.15),
    text="1.215 m",
    offset=(0, 1.0, 0.6)
)

print("\n4. Configurando iluminación...")
setup_lighting()

print("\n5. Configurando cámaras...")
cameras = setup_cameras()
bpy.context.scene.camera = cameras[0]  # Cenital por defecto

# Configuración de render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

print("\n" + "="*60)
print("ESCENA LISTA - Caso Aulestia (Iurgi Beraza)")
print("- SEAT Ibiza gris en posición de impacto")
print("- Bicicleta ORBEA roja caída")
print("- Ciclista proyectado 8.008m")
print("- Mediciones forenses incluidas")
print("="*60)

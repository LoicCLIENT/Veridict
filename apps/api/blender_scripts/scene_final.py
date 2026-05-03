"""
Escena de accidente FINAL - estilo referencia exacto
"""
import bpy
import math
import os

RENDERS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"
MODELS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\models\extracted"

def clear_all():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def create_ground():
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.01))
    ground = bpy.context.active_object
    ground.name = "Suelo"
    mat = bpy.data.materials.new(name="Mat_Suelo")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.85, 0.85, 0.83, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.95
    ground.data.materials.append(mat)

def create_road():
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Carretera"
    road.scale = (5, 25, 1)
    mat = bpy.data.materials.new(name="Mat_Asfalto")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.28, 0.28, 0.28, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.85
    road.data.materials.append(mat)

    # Líneas centrales
    for i in range(-20, 21, 3):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, i, 0.005))
        line = bpy.context.active_object
        line.scale = (0.06, 0.8, 1)
        mat_w = bpy.data.materials.new(name=f"Blanco_{i}")
        mat_w.use_nodes = True
        mat_w.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1)
        line.data.materials.append(mat_w)

def import_model(folder, name, loc, rot, scl):
    filepath = os.path.join(MODELS_DIR, folder, "scene.gltf")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath}")
        return None

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    new_objs = list(set(bpy.data.objects) - before)

    if not new_objs:
        return None

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    parent = bpy.context.active_object
    parent.name = name
    parent.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
    parent.scale = scl

    for obj in new_objs:
        obj.parent = parent

    print(f"OK: {name}")
    return parent

def create_measure(p1, p2, text, offset=(0, 0, 0.6)):
    # Línea negra
    curve = bpy.data.curves.new(f"L_{text}", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.025
    sp = curve.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (*p1, 1)
    sp.points[1].co = (*p2, 1)
    obj = bpy.data.objects.new(f"Linea_{text}", curve)
    bpy.context.collection.objects.link(obj)

    mat = bpy.data.materials.new(f"Negro_{text}")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    obj.data.materials.append(mat)

    # Flechas
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    for pt, flip in [(p1, math.pi), (p2, 0)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.25, location=pt)
        arr = bpy.context.active_object
        arr.rotation_euler = (0, math.pi/2, angle + flip)
        arr.data.materials.append(mat)

    # Texto
    mid = ((p1[0]+p2[0])/2 + offset[0], (p1[1]+p2[1])/2 + offset[1], p1[2] + offset[2])
    bpy.ops.object.text_add(location=mid)
    txt = bpy.context.active_object
    txt.data.body = text
    txt.data.size = 0.55
    txt.data.align_x = 'CENTER'
    txt.rotation_euler = (math.pi/2, 0, 0)
    mat_t = bpy.data.materials.new(f"T_{text}")
    mat_t.use_nodes = True
    mat_t.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)
    txt.data.materials.append(mat_t)

def setup_scene():
    # Sol suave
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 4
    sun.data.angle = math.radians(12)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Relleno
    bpy.ops.object.light_add(type='AREA', location=(-8, 8, 12))
    fill = bpy.context.active_object
    fill.data.energy = 200
    fill.data.size = 8

    # Cielo claro
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.72, 0.8, 0.9, 1)
        bg.inputs['Strength'].default_value = 0.9

    # Cámara cenital
    bpy.ops.object.camera_add(location=(0, 3, 20))
    cam1 = bpy.context.active_object
    cam1.name = "Cam_Top"
    cam1.data.type = 'ORTHO'
    cam1.data.ortho_scale = 20

    # Cámara 3D
    bpy.ops.object.camera_add(location=(12, -16, 7))
    cam2 = bpy.context.active_object
    cam2.name = "Cam_3D"
    cam2.rotation_euler = (math.radians(72), 0, math.radians(38))

    # Cámara frontal (como referencia 4)
    bpy.ops.object.camera_add(location=(5, -14, 4))
    cam3 = bpy.context.active_object
    cam3.name = "Cam_Front"
    cam3.rotation_euler = (math.radians(82), 0, math.radians(18))

    return cam1

# ========== CREAR ESCENA ==========
print("="*60)
print("ESCENA FINAL - ESTILO REFERENCIA")
print("="*60)

clear_all()
create_ground()
create_road()

print("\nImportando modelos...")

# COCHE - posición de impacto
coche = import_model(
    "coche", "Coche",
    loc=(1.2, 6, 0),
    rot=(0, 0, 180),  # Mirando hacia sur
    scl=(0.018, 0.018, 0.018)
)

# BICICLETA - al lado del frontal del coche, caída
bici = import_model(
    "bicicleta", "Bicicleta",
    loc=(-1.5, 5.5, 0.15),
    rot=(0, 35, 85),  # Caída de lado
    scl=(1.2, 1.2, 1.2)  # Escala normal - este modelo parece más pequeño
)

# CICLISTA - proyectado hacia adelante, en el suelo
ciclista = import_model(
    "humano", "Ciclista",
    loc=(-2.5, -2, 0.1),
    rot=(90, 0, 30),  # Tumbado en el suelo
    scl=(1.0, 1.0, 1.0)
)

# Mediciones
print("\nCreando mediciones...")

# Distancia proyección: desde bici hasta ciclista
create_measure(
    p1=(-1.5, 5.5, 0.1),
    p2=(-2.5, -2, 0.1),
    text="8.008 m",
    offset=(2.0, 0, 0.8)
)

# Distancia lateral: desde coche hasta bici
create_measure(
    p1=(1.2, 6, 0.1),
    p2=(-1.5, 5.5, 0.1),
    text="1.215 m",
    offset=(0, 1.2, 0.8)
)

print("\nConfigurando escena...")
cam = setup_scene()
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

print("\nESCENA LISTA")

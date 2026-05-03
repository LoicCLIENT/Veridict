"""
Escena de accidente - versión corregida
Basada en las imágenes de referencia
"""
import bpy
import math
import os

RENDERS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"
MODELS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\models\extracted"

def clear_all():
    """Limpiar escena completa"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def create_ground():
    """Suelo gris claro"""
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.01))
    ground = bpy.context.active_object
    ground.name = "Suelo"

    mat = bpy.data.materials.new(name="Mat_Suelo")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.82, 0.82, 0.80, 1)
    bsdf.inputs['Roughness'].default_value = 0.95
    ground.data.materials.append(mat)

def create_road():
    """Carretera gris oscuro estilo referencia"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Carretera"
    road.scale = (5, 25, 1)

    mat = bpy.data.materials.new(name="Mat_Asfalto")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1)
    bsdf.inputs['Roughness'].default_value = 0.85
    road.data.materials.append(mat)

    # Línea central
    for i in range(-20, 21, 3):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, i, 0.005))
        line = bpy.context.active_object
        line.name = f"Linea_{i}"
        line.scale = (0.06, 0.8, 1)

        mat_w = bpy.data.materials.new(name=f"Blanco_{i}")
        mat_w.use_nodes = True
        mat_w.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1)
        line.data.materials.append(mat_w)

def import_gltf_simple(folder_name, obj_name, loc, rot, scl):
    """Importar GLTF de forma simple"""
    filepath = os.path.join(MODELS_DIR, folder_name, "scene.gltf")

    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} no existe")
        return None

    # Guardar objetos actuales
    before = set(bpy.data.objects)

    # Importar
    bpy.ops.import_scene.gltf(filepath=filepath)

    # Encontrar nuevos objetos
    after = set(bpy.data.objects)
    new_objs = list(after - before)

    if not new_objs:
        print(f"ERROR: No se importó nada de {folder_name}")
        return None

    # Crear empty padre
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    parent = bpy.context.active_object
    parent.name = obj_name
    parent.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
    parent.scale = scl

    # Emparentar
    for obj in new_objs:
        obj.parent = parent

    print(f"OK: {obj_name} ({len(new_objs)} objetos)")
    return parent

def create_measure(p1, p2, text, text_offset=(0, 0, 0.5)):
    """Crear línea de medición negra"""
    # Línea
    curve = bpy.data.curves.new(f"Curva_{text}", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.02

    sp = curve.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (*p1, 1)
    sp.points[1].co = (*p2, 1)

    obj = bpy.data.objects.new(f"Linea_{text}", curve)
    bpy.context.collection.objects.link(obj)

    # Material negro
    mat = bpy.data.materials.new(f"Negro_{text}")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
    obj.data.materials.append(mat)

    # Flechas
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)

    for pt, flip in [(p1, math.pi), (p2, 0)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.2, location=pt)
        arr = bpy.context.active_object
        arr.rotation_euler = (0, math.pi/2, angle + flip)
        arr.data.materials.append(mat)

    # Texto
    mid = ((p1[0]+p2[0])/2 + text_offset[0], (p1[1]+p2[1])/2 + text_offset[1], p1[2] + text_offset[2])
    bpy.ops.object.text_add(location=mid)
    txt = bpy.context.active_object
    txt.data.body = text
    txt.data.size = 0.5
    txt.data.align_x = 'CENTER'
    txt.rotation_euler = (math.pi/2, 0, 0)

    mat_t = bpy.data.materials.new(f"TextoMat_{text}")
    mat_t.use_nodes = True
    mat_t.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)
    txt.data.materials.append(mat_t)

def setup_scene():
    """Configurar iluminación y cámaras"""
    # Sol
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 4
    sun.data.angle = math.radians(10)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Relleno
    bpy.ops.object.light_add(type='AREA', location=(-8, 8, 12))
    fill = bpy.context.active_object
    fill.data.energy = 250
    fill.data.size = 8

    # Cielo
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.7, 0.78, 0.88, 1)
        bg.inputs['Strength'].default_value = 0.8

    # Cámara cenital
    bpy.ops.object.camera_add(location=(0, 2, 22))
    cam1 = bpy.context.active_object
    cam1.name = "Cam_Top"
    cam1.rotation_euler = (0, 0, 0)
    cam1.data.type = 'ORTHO'
    cam1.data.ortho_scale = 22

    # Cámara 3D perspectiva
    bpy.ops.object.camera_add(location=(12, -18, 8))
    cam2 = bpy.context.active_object
    cam2.name = "Cam_Persp"
    cam2.rotation_euler = (math.radians(70), 0, math.radians(35))

    # Cámara frontal
    bpy.ops.object.camera_add(location=(6, -16, 4))
    cam3 = bpy.context.active_object
    cam3.name = "Cam_Front"
    cam3.rotation_euler = (math.radians(80), 0, math.radians(20))

    return cam1, cam2, cam3

# ============ EJECUTAR ============
print("="*60)
print("CREANDO ESCENA ESTILO REFERENCIA")
print("="*60)

clear_all()
create_ground()
create_road()

print("\nImportando modelos...")

# El coche viene del modelo BYD - probamos diferentes rotaciones
coche = import_gltf_simple(
    "coche", "Coche",
    loc=(1.5, 6, 0),
    rot=(0, 0, 180),  # Mirando hacia -Y
    scl=(0.015, 0.015, 0.015)  # Escala pequeña - los modelos GLTF suelen ser grandes
)

# Bicicleta
bici = import_gltf_simple(
    "bicicleta", "Bicicleta",
    loc=(-0.8, 5, 0.1),
    rot=(0, 0, 100),  # Girada tras impacto
    scl=(0.01, 0.01, 0.01)
)

# Humano/Ciclista
humano = import_gltf_simple(
    "humano", "Ciclista",
    loc=(-2, -2, 0.05),
    rot=(0, 0, 60),  # En el suelo
    scl=(1.0, 1.0, 1.0)
)

print("\nCreando mediciones...")
create_measure((1.5, 6, 0.1), (-2, -2, 0.1), "8.008 m", text_offset=(2.5, 0, 0.8))
create_measure((1.5, 6, 0.1), (-0.8, 5, 0.1), "1.215 m", text_offset=(0, 1.5, 0.8))

print("\nConfigurando escena...")
cam1, cam2, cam3 = setup_scene()
bpy.context.scene.camera = cam1

# Render config
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

print("\n" + "="*60)
print("ESCENA LISTA")
print("="*60)

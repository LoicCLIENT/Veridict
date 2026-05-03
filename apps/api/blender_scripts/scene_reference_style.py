"""
Escena de accidente estilo referencia profesional
- Carretera gris sobre suelo blanco/gris claro
- Líneas de medición negras con flechas
- Vista cenital técnica
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

    # Limpiar datos huérfanos
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)

def create_ground():
    """Suelo blanco/gris claro con grid sutil"""
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.02))
    ground = bpy.context.active_object
    ground.name = "Suelo"

    mat = bpy.data.materials.new(name="Mat_Suelo")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.85, 0.85, 0.85, 1)  # Gris muy claro
    bsdf.inputs['Roughness'].default_value = 0.9
    ground.data.materials.append(mat)
    return ground

def create_road():
    """Carretera gris oscuro, recta"""
    # Carretera principal - más larga en Y (dirección del coche)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Carretera"
    road.scale = (6, 30, 1)  # 12m ancho x 60m largo

    mat = bpy.data.materials.new(name="Mat_Asfalto")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.25, 0.25, 0.25, 1)  # Gris oscuro
    bsdf.inputs['Roughness'].default_value = 0.85
    road.data.materials.append(mat)

    # Línea central discontinua
    for i in range(-25, 26, 4):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, i, 0.005))
        line = bpy.context.active_object
        line.name = f"LineaCentro_{i}"
        line.scale = (0.08, 1.2, 1)

        mat_white = bpy.data.materials.new(name=f"Mat_Linea_{i}")
        mat_white.use_nodes = True
        bsdf = mat_white.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1)
        line.data.materials.append(mat_white)

    return road

def import_model(filepath, name, location, rotation_deg, scale):
    """Importar modelo GLTF"""
    if not os.path.exists(filepath):
        print(f"ERROR: No existe {filepath}")
        return None

    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = bpy.context.selected_objects

    if imported:
        # Crear empty padre
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        parent = bpy.context.active_object
        parent.name = name
        parent.rotation_euler = (
            math.radians(rotation_deg[0]),
            math.radians(rotation_deg[1]),
            math.radians(rotation_deg[2])
        )
        parent.scale = scale

        for obj in imported:
            obj.parent = parent
            obj.location = (0, 0, 0)

        print(f"OK: {name} importado")
        return parent
    return None

def create_measurement_line(start, end, label_text, offset_label=(0, 0, 0)):
    """Crear línea de medición estilo referencia - negra con flechas"""

    # Línea principal negra
    curve = bpy.data.curves.new(name=f"Linea_{label_text}", type='CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.025

    spline = curve.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (start[0], start[1], start[2], 1)
    spline.points[1].co = (end[0], end[1], end[2], 1)

    line_obj = bpy.data.objects.new(f"Medicion_{label_text}", curve)
    bpy.context.collection.objects.link(line_obj)

    # Material negro
    mat_black = bpy.data.materials.new(name=f"Mat_Linea_{label_text}")
    mat_black.use_nodes = True
    bsdf = mat_black.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
    line_obj.data.materials.append(mat_black)

    # Flechas en los extremos
    for pos, rot_z in [(start, 0), (end, math.pi)]:
        # Calcular dirección de la flecha
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)

        bpy.ops.mesh.primitive_cone_add(
            radius1=0.12,
            depth=0.25,
            location=(pos[0], pos[1], pos[2])
        )
        arrow = bpy.context.active_object
        arrow.name = f"Flecha_{label_text}_{pos[0]:.1f}"

        if pos == start:
            arrow.rotation_euler = (0, math.pi/2, angle + math.pi)
        else:
            arrow.rotation_euler = (0, math.pi/2, angle)

        arrow.data.materials.append(mat_black)

    # Texto de medición
    mid_x = (start[0] + end[0]) / 2 + offset_label[0]
    mid_y = (start[1] + end[1]) / 2 + offset_label[1]
    mid_z = max(start[2], end[2]) + 0.5 + offset_label[2]

    bpy.ops.object.text_add(location=(mid_x, mid_y, mid_z))
    text_obj = bpy.context.active_object
    text_obj.data.body = label_text
    text_obj.name = f"Texto_{label_text}"
    text_obj.data.size = 0.6
    text_obj.data.align_x = 'CENTER'
    text_obj.rotation_euler = (math.pi/2, 0, 0)

    # Material negro para texto
    mat_text = bpy.data.materials.new(name=f"Mat_Texto_{label_text}")
    mat_text.use_nodes = True
    bsdf = mat_text.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)
    text_obj.data.materials.append(mat_text)

def setup_lighting():
    """Iluminación suave tipo estudio"""
    # Luz principal (sol suave)
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    sun = bpy.context.active_object
    sun.name = "Sol"
    sun.data.energy = 3
    sun.data.angle = math.radians(15)  # Sombras suaves
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Luz de relleno
    bpy.ops.object.light_add(type='AREA', location=(-10, 10, 15))
    fill = bpy.context.active_object
    fill.name = "Relleno"
    fill.data.energy = 200
    fill.data.size = 10

    # Cielo claro
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.75, 0.82, 0.92, 1)  # Azul cielo claro
        bg.inputs['Strength'].default_value = 1.0

def setup_cameras():
    """Cámaras para diferentes vistas"""
    # Vista cenital (plano técnico) - la más importante
    bpy.ops.object.camera_add(location=(0, 5, 25))
    cam_top = bpy.context.active_object
    cam_top.name = "Cam_Cenital"
    cam_top.rotation_euler = (0, 0, 0)
    cam_top.data.type = 'ORTHO'
    cam_top.data.ortho_scale = 25

    # Vista perspectiva 3D
    bpy.ops.object.camera_add(location=(15, -15, 12))
    cam_3d = bpy.context.active_object
    cam_3d.name = "Cam_3D"
    cam_3d.rotation_euler = (math.radians(60), 0, math.radians(135))

    # Vista frontal (como la referencia 4)
    bpy.ops.object.camera_add(location=(8, -20, 5))
    cam_front = bpy.context.active_object
    cam_front.name = "Cam_Frontal"
    cam_front.rotation_euler = (math.radians(78), 0, math.radians(20))

    return cam_top, cam_3d, cam_front

# ==================== CREAR ESCENA ====================
print("="*60)
print("CREANDO ESCENA ESTILO REFERENCIA")
print("="*60)

clear_all()

# Escenario base
print("\n1. Creando escenario...")
create_ground()
create_road()

# Importar modelos
print("\n2. Importando modelos...")

# COCHE - Orientado hacia +Y (norte), en posición de impacto
coche = import_model(
    filepath=os.path.join(MODELS_DIR, "coche", "scene.gltf"),
    name="Coche_SEAT",
    location=(1.2, 5, 0),  # Ligeramente a la derecha, avanzando
    rotation_deg=(-90, 0, 180),  # Mirando hacia -Y (sur, hacia nosotros)
    scale=(1.8, 1.8, 1.8)
)

# BICICLETA - En el lateral del coche, caída
bici = import_model(
    filepath=os.path.join(MODELS_DIR, "bicicleta", "scene.gltf"),
    name="Bicicleta",
    location=(-1, 4.5, 0.1),  # Al lado del coche
    rotation_deg=(-90, 25, 90),  # Caída hacia un lado
    scale=(1.3, 1.3, 1.3)
)

# CICLISTA - Proyectado delante del coche
ciclista = import_model(
    filepath=os.path.join(MODELS_DIR, "humano", "scene.gltf"),
    name="Ciclista",
    location=(-2.5, -3, 0.05),  # Proyectado hacia adelante
    rotation_deg=(-90, 0, 45),  # En el suelo
    scale=(1.0, 1.0, 1.0)
)

# Crear líneas de medición estilo referencia
print("\n3. Añadiendo mediciones...")

# Distancia de proyección del ciclista (8.008 m en referencia)
create_measurement_line(
    start=(-1, 4.5, 0.1),  # Desde la bici
    end=(-2.5, -3, 0.1),   # Hasta el ciclista
    label_text="8.008 m",
    offset_label=(2, 0, 0)
)

# Distancia lateral (1.215 m en referencia)
create_measurement_line(
    start=(1.2, 5, 0.1),   # Desde el coche
    end=(-1, 4.5, 0.1),    # Hasta la bici
    label_text="1.215 m",
    offset_label=(0, 1.5, 0)
)

# Iluminación y cámaras
print("\n4. Configurando iluminación y cámaras...")
setup_lighting()
cam_top, cam_3d, cam_front = setup_cameras()

# Configurar render
print("\n5. Configurando render...")
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False

# Activar cámara cenital por defecto
scene.camera = cam_top

os.makedirs(RENDERS_DIR, exist_ok=True)

print("\n" + "="*60)
print("ESCENA CREADA - ESTILO REFERENCIA")
print("="*60)
print("\nElementos:")
print(f"  - Coche: {coche.name if coche else 'ERROR'}")
print(f"  - Bicicleta: {bici.name if bici else 'ERROR'}")
print(f"  - Ciclista: {ciclista.name if ciclista else 'ERROR'}")
print("\nCámaras disponibles:")
print("  - Cam_Cenital (vista técnica)")
print("  - Cam_3D (perspectiva)")
print("  - Cam_Frontal (vista frontal)")

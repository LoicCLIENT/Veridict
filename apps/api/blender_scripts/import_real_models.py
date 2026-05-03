"""
Importar modelos reales de Sketchfab y crear escena de accidente
"""

import bpy
import math
import os

# Rutas de los modelos
MODELS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\models\extracted"
RENDERS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"

def clear_scene():
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

def create_road(length=50, width=12):
    """Crear carretera realista"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.01))
    road = bpy.context.active_object
    road.name = "Carretera"
    road.scale = (length, width, 1)

    # Material asfalto
    mat = bpy.data.materials.new(name="Asfalto")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    road.data.materials.append(mat)

    # Líneas de carril
    for i in range(-20, 21, 4):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(i, 0, 0.001))
        line = bpy.context.active_object
        line.name = f"LineaCarril_{i}"
        line.scale = (1.5, 0.08, 1)

        mat_white = bpy.data.materials.new(name=f"Blanco_{i}")
        mat_white.use_nodes = True
        bsdf = mat_white.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.9, 1)
        line.data.materials.append(mat_white)

    return road

def import_gltf(filepath, name, location=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    """Importar modelo GLTF y posicionar"""
    print(f"Importando {name} desde {filepath}...")

    # Importar GLTF
    bpy.ops.import_scene.gltf(filepath=filepath)

    # Obtener objetos importados
    imported_objects = bpy.context.selected_objects

    if imported_objects:
        # Crear empty como padre para agrupar
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        parent = bpy.context.active_object
        parent.name = name
        parent.rotation_euler = (math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]))
        parent.scale = scale

        # Emparentar todos los objetos importados
        for obj in imported_objects:
            obj.select_set(True)
            obj.parent = parent
            # Resetear transformación local
            obj.location = (0, 0, 0)

        print(f"  -> {len(imported_objects)} objetos importados para {name}")
        return parent
    else:
        print(f"  -> ERROR: No se importaron objetos para {name}")
        return None

def create_measurement(start, end, label, color=(1, 0.3, 0, 1)):
    """Crear línea de medición con flecha y etiqueta"""
    # Línea
    curve_data = bpy.data.curves.new(name=f"Medicion_{label}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.03

    spline = curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (*start, 1)
    spline.points[1].co = (*end, 1)

    curve_obj = bpy.data.objects.new(f"Linea_{label}", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Material naranja brillante
    mat = bpy.data.materials.new(name=f"Mat_{label}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = 2.0
    curve_obj.data.materials.append(mat)

    # Texto
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, start[2] + 0.5)
    bpy.ops.object.text_add(location=mid)
    text = bpy.context.active_object
    text.data.body = label
    text.name = f"Texto_{label}"
    text.scale = (0.4, 0.4, 0.4)
    text.rotation_euler = (math.pi/2, 0, 0)

    # Material texto
    mat_text = bpy.data.materials.new(name=f"MatTexto_{label}")
    mat_text.use_nodes = True
    bsdf = mat_text.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    text.data.materials.append(mat_text)

def setup_lighting():
    """Iluminación profesional"""
    # Sol principal
    bpy.ops.object.light_add(type='SUN', location=(15, -15, 25))
    sun = bpy.context.active_object
    sun.name = "Sol"
    sun.data.energy = 5
    sun.data.angle = math.radians(1)
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

    # Luz de relleno
    bpy.ops.object.light_add(type='AREA', location=(-10, 10, 15))
    fill = bpy.context.active_object
    fill.name = "LuzRelleno"
    fill.data.energy = 800
    fill.data.size = 10

    # Configurar mundo/cielo
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.6, 0.7, 0.85, 1)
        bg.inputs['Strength'].default_value = 1.0

def setup_cameras():
    """Configurar cámaras para diferentes vistas"""
    cameras = []

    # Vista cenital (plano técnico)
    bpy.ops.object.camera_add(location=(0, 0, 30))
    cam_top = bpy.context.active_object
    cam_top.name = "Camara_Cenital"
    cam_top.data.type = 'ORTHO'
    cam_top.data.ortho_scale = 40
    cameras.append(cam_top)

    # Vista perspectiva 3D
    bpy.ops.object.camera_add(location=(20, -20, 12))
    cam_persp = bpy.context.active_object
    cam_persp.name = "Camara_3D"
    cam_persp.rotation_euler = (math.radians(65), 0, math.radians(45))
    cameras.append(cam_persp)

    # Vista lateral
    bpy.ops.object.camera_add(location=(25, 0, 5))
    cam_side = bpy.context.active_object
    cam_side.name = "Camara_Lateral"
    cam_side.rotation_euler = (math.radians(80), 0, math.radians(90))
    cameras.append(cam_side)

    return cameras

def render_scene(camera_name, output_name):
    """Renderizar desde una cámara específica"""
    scene = bpy.context.scene

    camera = bpy.data.objects.get(camera_name)
    if camera:
        scene.camera = camera
        scene.render.filepath = os.path.join(RENDERS_DIR, output_name)
        bpy.ops.render.render(write_still=True)
        print(f"Renderizado: {output_name}")

# ========== CREAR ESCENA DE ACCIDENTE ==========

print("="*60)
print("CREANDO ESCENA DE ACCIDENTE CON MODELOS REALES")
print("="*60)

# Limpiar
clear_scene()

# Crear carretera
print("\n1. Creando carretera...")
create_road()

# Importar modelos
print("\n2. Importando modelos...")

# Coche (punto de impacto)
coche = import_gltf(
    filepath=os.path.join(MODELS_DIR, "coche", "scene.gltf"),
    name="Coche_BYD",
    location=(5, -0.5, 0),
    rotation=(-90, 0, -15),  # Rotación para orientar correctamente
    scale=(1.2, 1.2, 1.2)
)

# Moto (en trayectoria de colisión)
moto = import_gltf(
    filepath=os.path.join(MODELS_DIR, "moto", "scene.gltf"),
    name="Moto",
    location=(-8, 2, 0),
    rotation=(-90, 0, 45),
    scale=(0.8, 0.8, 0.8)
)

# Bicicleta (caída tras impacto)
bici = import_gltf(
    filepath=os.path.join(MODELS_DIR, "bicicleta", "scene.gltf"),
    name="Bicicleta",
    location=(-3, 3, 0.2),
    rotation=(-90, 35, 60),  # Inclinada como si hubiera caído
    scale=(1.0, 1.0, 1.0)
)

# Humano/Ciclista (posición de caída)
humano = import_gltf(
    filepath=os.path.join(MODELS_DIR, "humano", "scene.gltf"),
    name="Ciclista",
    location=(-1, 4, 0.1),
    rotation=(-90, 0, 30),
    scale=(1.0, 1.0, 1.0)
)

# Crear mediciones forenses
print("\n3. Añadiendo mediciones forenses...")

create_measurement(
    start=(-15, -2, 0.05),
    end=(5, -2, 0.05),
    label="20.5 m (distancia frenada)",
    color=(1, 0.5, 0, 1)
)

create_measurement(
    start=(5, -0.5, 0.05),
    end=(-3, 3, 0.05),
    label="8.9 m (trayectoria impacto)",
    color=(1, 0.2, 0.2, 1)
)

create_measurement(
    start=(-3, 3, 0.05),
    end=(-1, 4, 0.05),
    label="2.2 m (proyección víctima)",
    color=(0.2, 0.6, 1, 1)
)

# Iluminación y cámaras
print("\n4. Configurando iluminación y cámaras...")
setup_lighting()
cameras = setup_cameras()

# Configurar render
print("\n5. Configurando render...")
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Crear directorio de renders
os.makedirs(RENDERS_DIR, exist_ok=True)

# Renderizar todas las vistas
print("\n6. Renderizando vistas...")
scene.camera = bpy.data.objects.get("Camara_3D")

print("\n" + "="*60)
print("ESCENA CREADA EXITOSAMENTE")
print("="*60)
print(f"\nModelos importados:")
print(f"  - Coche: {coche.name if coche else 'ERROR'}")
print(f"  - Moto: {moto.name if moto else 'ERROR'}")
print(f"  - Bicicleta: {bici.name if bici else 'ERROR'}")
print(f"  - Ciclista: {humano.name if humano else 'ERROR'}")
print(f"\nCámaras disponibles:")
for cam in cameras:
    print(f"  - {cam.name}")
print(f"\nPara renderizar, usa: Render > Render Image (F12)")

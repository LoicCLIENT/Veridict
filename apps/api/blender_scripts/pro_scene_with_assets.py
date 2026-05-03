"""
Escena profesional usando modelos de Sketchfab/asset libraries
Para usar con Blender MCP que tiene integración con Sketchfab

Este script crea la escena base y deja placeholders donde
el usuario puede arrastrar modelos desde las librerías de assets
"""

import bpy
import math
import os

def clear_scene():
    """Limpiar escena"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_road_professional(length=40, width=10):
    """Crear carretera con marcas viales"""
    # Superficie principal
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Road_Surface"
    road.scale = (length, width, 1)

    # Material asfalto realista
    mat = bpy.data.materials.new(name="Asphalt_Pro")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Specular IOR Level'].default_value = 0.2

    road.data.materials.append(mat)

    # Líneas de carril (centro - discontinua)
    for i in range(-15, 16, 3):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(i, 0, 0.01))
        line = bpy.context.active_object
        line.name = f"CenterLine_{i}"
        line.scale = (1.0, 0.1, 1)

        mat_white = bpy.data.materials.new(name=f"WhiteLine_{i}")
        mat_white.use_nodes = True
        bsdf = mat_white.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.9, 1)
        bsdf.inputs['Roughness'].default_value = 0.7
        line.data.materials.append(mat_white)

    return road

def create_placeholder_car(location, name, color=(0.6, 0.6, 0.65, 1)):
    """
    Crear placeholder de coche - REEMPLAZAR con modelo de Sketchfab

    Para reemplazar:
    1. Usar Blender MCP > Use assets from Sketchfab
    2. Buscar: "sedan car low poly free"
    3. Arrastrar al placeholder
    4. Escalar y posicionar
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    body = bpy.context.active_object
    body.name = f"{name}_PLACEHOLDER"
    body.scale = (2.2, 0.9, 0.5)
    body.location.z = 0.5

    # Cabina
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0] - 0.3, location[1], 0.95))
    cabin = bpy.context.active_object
    cabin.name = f"{name}_Cabin_PLACEHOLDER"
    cabin.scale = (1.0, 0.8, 0.4)

    mat = bpy.data.materials.new(name=f"{name}_Paint")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.25
    body.data.materials.append(mat)
    cabin.data.materials.append(mat)

    # Añadir texto indicador
    bpy.ops.object.text_add(location=(location[0], location[1], 2))
    text = bpy.context.active_object
    text.data.body = f"← {name}\nReemplazar con\nmodelo Sketchfab"
    text.scale = (0.2, 0.2, 0.2)
    text.rotation_euler = (math.pi/2, 0, 0)

    return body

def create_placeholder_bicycle(location, name="Bicycle"):
    """
    Placeholder de bicicleta - REEMPLAZAR con modelo de Sketchfab

    Buscar: "bicycle low poly free"
    """
    # Representación simple
    bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.03, location=(location[0]-0.5, location[1], 0.35))
    wheel1 = bpy.context.active_object
    wheel1.name = f"{name}_Wheel1_PLACEHOLDER"
    wheel1.rotation_euler = (math.pi/2, 0, 0)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.03, location=(location[0]+0.5, location[1], 0.35))
    wheel2 = bpy.context.active_object
    wheel2.name = f"{name}_Wheel2_PLACEHOLDER"
    wheel2.rotation_euler = (math.pi/2, 0, 0)

    mat_red = bpy.data.materials.new(name="BikeRed")
    mat_red.use_nodes = True
    bsdf = mat_red.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)
    bsdf.inputs['Metallic'].default_value = 0.6
    wheel1.data.materials.append(mat_red)
    wheel2.data.materials.append(mat_red)

    return wheel1

def create_placeholder_human(location, name="Person"):
    """
    Placeholder de persona - REEMPLAZAR con modelo de Sketchfab

    Buscar: "human figure low poly" o "pedestrian"
    """
    # Cuerpo simplificado
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.7, location=(location[0], location[1], 0.75))
    torso = bpy.context.active_object
    torso.name = f"{name}_Torso_PLACEHOLDER"

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(location[0], location[1], 1.35))
    head = bpy.context.active_object
    head.name = f"{name}_Head_PLACEHOLDER"

    mat_green = bpy.data.materials.new(name="PersonGreen")
    mat_green.use_nodes = True
    bsdf = mat_green.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.2, 1)
    torso.data.materials.append(mat_green)

    mat_skin = bpy.data.materials.new(name="PersonSkin")
    mat_skin.use_nodes = True
    bsdf = mat_skin.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.5, 1)
    head.data.materials.append(mat_skin)

    return torso

def create_measurement_marker(start, end, label, color=(1, 0.3, 0, 1)):
    """Marcador de medición profesional"""
    # Línea principal
    curve_data = bpy.data.curves.new(name=f"Measure_{label}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.02

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)
    polyline.points[0].co = (start[0], start[1], start[2], 1)
    polyline.points[1].co = (end[0], end[1], end[2], 1)

    curve_obj = bpy.data.objects.new(f"MeasureLine_{label}", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    mat = bpy.data.materials.new(name=f"MeasureMat_{label}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = 0.5
    curve_obj.data.materials.append(mat)

    # Texto de medida
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, max(start[2], end[2]) + 0.3)
    bpy.ops.object.text_add(location=mid)
    text_obj = bpy.context.active_object
    text_obj.data.body = label
    text_obj.name = f"MeasureText_{label}"
    text_obj.scale = (0.25, 0.25, 0.25)
    text_obj.rotation_euler = (math.pi/2, 0, 0)

    # Flechas en extremos
    for pos, rot in [(start, 0), (end, math.pi)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.15, location=pos)
        arrow = bpy.context.active_object
        arrow.rotation_euler = (0, math.pi/2, rot)
        arrow.data.materials.append(mat)

    return curve_obj

def setup_professional_lighting():
    """Iluminación de estudio profesional"""
    # HDRI o luz ambiental
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.7, 0.75, 0.85, 1)
        bg.inputs['Strength'].default_value = 0.8

    # Sol principal
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    sun = bpy.context.active_object
    sun.name = "Sun_Main"
    sun.data.energy = 4
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))

    # Luz de relleno suave
    bpy.ops.object.light_add(type='AREA', location=(-8, 8, 12))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 300
    fill.data.size = 8

def setup_cameras():
    """Configurar cámaras para renders"""
    # Vista cenital (plano técnico)
    bpy.ops.object.camera_add(location=(0, 0, 25))
    cam_top = bpy.context.active_object
    cam_top.name = "Camera_TopView"
    cam_top.data.type = 'ORTHO'
    cam_top.data.ortho_scale = 30

    # Vista 3D perspectiva
    bpy.ops.object.camera_add(location=(15, -15, 10))
    cam_persp = bpy.context.active_object
    cam_persp.name = "Camera_3D"
    cam_persp.rotation_euler = (math.radians(65), 0, math.radians(45))

    # Vista lateral
    bpy.ops.object.camera_add(location=(0, -20, 3))
    cam_side = bpy.context.active_object
    cam_side.name = "Camera_Side"
    cam_side.rotation_euler = (math.radians(85), 0, 0)

    return cam_top, cam_persp, cam_side

# ========== CREAR ESCENA PROFESIONAL ==========

print("="*50)
print("CREANDO ESCENA PROFESIONAL")
print("="*50)

clear_scene()

# Elementos de escena
create_road_professional(length=35, width=8)

# Vehículos (PLACEHOLDERS - reemplazar con modelos Sketchfab)
create_placeholder_car(
    location=(3, -1, 0),
    name="VehiculoA_SEAT",
    color=(0.55, 0.55, 0.58, 1)  # Gris plata
)

# Bicicleta
create_placeholder_bicycle(location=(-3, 1.5, 0), name="Bicicleta")

# Ciclista
create_placeholder_human(location=(-2, 1, 0), name="Ciclista")

# Mediciones forenses
create_measurement_marker(
    start=(-10, 3, 0.05),
    end=(3, 3, 0.05),
    label="13.2 m (distancia frenada)",
    color=(1, 0.5, 0, 1)
)

create_measurement_marker(
    start=(3, -1, 0.05),
    end=(-3, 1.5, 0.05),
    label="6.7 m (trayectoria impacto)",
    color=(1, 0.2, 0.2, 1)
)

create_measurement_marker(
    start=(-3, 1.5, 0.05),
    end=(-5, 4, 0.05),
    label="3.2 m (proyección ciclista)",
    color=(0.2, 0.6, 1, 1)
)

# Iluminación y cámaras
setup_professional_lighting()
cam_top, cam_persp, cam_side = setup_cameras()

# Activar cámara perspectiva
bpy.context.scene.camera = cam_persp

print("")
print("ESCENA CREADA CON PLACEHOLDERS")
print("")
print("Para mejorar la escena:")
print("1. Panel Blender MCP > 'Use assets from Sketchfab'")
print("2. Buscar modelos:")
print("   - 'sedan car free' para vehículos")
print("   - 'bicycle low poly' para bicicleta")
print("   - 'human figure' para personas")
print("3. Arrastrar modelos sobre los placeholders")
print("4. Eliminar placeholders después de posicionar")
print("")
print("="*50)

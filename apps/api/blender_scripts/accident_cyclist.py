"""
Blender script para crear escena de atropello a ciclista
Ejecutar desde Blender o via MCP
"""

import bpy
import math

def clear_scene():
    """Limpiar escena actual"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_road(length=30, width=7):
    """Crear carretera"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    road = bpy.context.active_object
    road.name = "Road"
    road.scale = (length, width, 1)

    # Material asfalto
    mat = bpy.data.materials.new(name="Asphalt")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1)
    bsdf.inputs['Roughness'].default_value = 0.8
    road.data.materials.append(mat)

    return road

def create_car(location=(0, 0, 0), rotation=0, name="Car"):
    """Crear modelo simplificado de coche"""
    # Cuerpo principal
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    body = bpy.context.active_object
    body.name = f"{name}_Body"
    body.scale = (2.2, 0.9, 0.6)
    body.location.z = 0.5

    # Cabina
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0] - 0.3, location[1], location[2] + 1.0))
    cabin = bpy.context.active_object
    cabin.name = f"{name}_Cabin"
    cabin.scale = (1.2, 0.85, 0.5)

    # Material coche (gris plateado como en las imágenes)
    mat = bpy.data.materials.new(name=f"{name}_Paint")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.3
    body.data.materials.append(mat)
    cabin.data.materials.append(mat)

    # Ruedas
    wheel_positions = [
        (location[0] + 0.8, location[1] + 0.5, 0.2),
        (location[0] + 0.8, location[1] - 0.5, 0.2),
        (location[0] - 0.8, location[1] + 0.5, 0.2),
        (location[0] - 0.8, location[1] - 0.5, 0.2),
    ]

    for i, pos in enumerate(wheel_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.15, location=pos)
        wheel = bpy.context.active_object
        wheel.name = f"{name}_Wheel_{i}"
        wheel.rotation_euler = (math.pi/2, 0, 0)

        # Material rueda
        mat_wheel = bpy.data.materials.new(name=f"Wheel_{i}")
        mat_wheel.use_nodes = True
        bsdf = mat_wheel.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
        wheel.data.materials.append(mat_wheel)

    # Agrupar todo
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.select_set(True)

    # Rotar todo el coche
    if rotation != 0:
        bpy.ops.transform.rotate(value=math.radians(rotation), orient_axis='Z')

    return body

def create_bicycle(location=(0, 0, 0), name="Bicycle"):
    """Crear bicicleta simplificada"""
    # Rueda trasera
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.35, minor_radius=0.02,
        location=(location[0] - 0.5, location[1], 0.35)
    )
    wheel_back = bpy.context.active_object
    wheel_back.name = f"{name}_WheelBack"
    wheel_back.rotation_euler = (math.pi/2, 0, 0)

    # Rueda delantera
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.35, minor_radius=0.02,
        location=(location[0] + 0.5, location[1], 0.35)
    )
    wheel_front = bpy.context.active_object
    wheel_front.name = f"{name}_WheelFront"
    wheel_front.rotation_euler = (math.pi/2, 0, 0)

    # Cuadro (simplificado como cilindros)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.02, depth=1.0,
        location=(location[0], location[1], 0.5)
    )
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    frame.rotation_euler = (0, math.pi/4, 0)

    # Material rojo (como en las imágenes de referencia)
    mat = bpy.data.materials.new(name="BikeRed")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)
    bsdf.inputs['Metallic'].default_value = 0.5
    wheel_back.data.materials.append(mat)
    wheel_front.data.materials.append(mat)
    frame.data.materials.append(mat)

    return wheel_back

def create_cyclist(location=(0, 0, 0), pose="riding", name="Cyclist"):
    """Crear ciclista simplificado (maniquí)"""
    # Torso
    bpy.ops.mesh.primitive_cube_add(size=0.4, location=(location[0], location[1], location[2] + 0.9))
    torso = bpy.context.active_object
    torso.name = f"{name}_Torso"
    torso.scale = (0.5, 0.3, 0.7)

    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0], location[1], location[2] + 1.4))
    head = bpy.context.active_object
    head.name = f"{name}_Head"

    # Piernas
    for side, y_offset in [("L", 0.1), ("R", -0.1)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.06, depth=0.5,
            location=(location[0], location[1] + y_offset, location[2] + 0.4)
        )
        leg = bpy.context.active_object
        leg.name = f"{name}_Leg{side}"
        if pose == "riding":
            leg.rotation_euler = (math.pi/6, 0, 0)

    # Material verde (como en las imágenes)
    mat_green = bpy.data.materials.new(name="CyclistGreen")
    mat_green.use_nodes = True
    bsdf = mat_green.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.2, 0.7, 0.2, 1)
    torso.data.materials.append(mat_green)

    # Material piel
    mat_skin = bpy.data.materials.new(name="Skin")
    mat_skin.use_nodes = True
    bsdf = mat_skin.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.5, 1)
    head.data.materials.append(mat_skin)

    return torso

def create_measurement_line(start, end, label=""):
    """Crear línea de medición con texto"""
    # Crear curva para la línea
    curve_data = bpy.data.curves.new(name=f"Measurement_{label}", type='CURVE')
    curve_data.dimensions = '3D'

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)
    polyline.points[0].co = (start[0], start[1], start[2], 1)
    polyline.points[1].co = (end[0], end[1], end[2], 1)

    curve_obj = bpy.data.objects.new(f"Line_{label}", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Material negro para la línea
    mat = bpy.data.materials.new(name=f"LineMat_{label}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
    curve_obj.data.materials.append(mat)

    # Añadir texto con la medida
    if label:
        mid_point = ((start[0] + end[0])/2, (start[1] + end[1])/2, (start[2] + end[2])/2 + 0.5)
        bpy.ops.object.text_add(location=mid_point)
        text_obj = bpy.context.active_object
        text_obj.data.body = label
        text_obj.scale = (0.3, 0.3, 0.3)

    return curve_obj

def setup_camera_top_view():
    """Configurar cámara vista cenital"""
    bpy.ops.object.camera_add(location=(0, 0, 20))
    camera = bpy.context.active_object
    camera.name = "Camera_TopView"
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 25
    bpy.context.scene.camera = camera
    return camera

def setup_camera_perspective():
    """Configurar cámara perspectiva"""
    bpy.ops.object.camera_add(location=(12, -12, 8))
    camera = bpy.context.active_object
    camera.name = "Camera_Perspective"
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    return camera

def setup_lighting():
    """Configurar iluminación tipo estudio"""
    # Sol principal
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(45), math.radians(30), 0)

    # Luz de relleno
    bpy.ops.object.light_add(type='AREA', location=(-5, 5, 10))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 500
    fill.data.size = 5

def setup_world_background():
    """Configurar fondo del mundo (cielo claro)"""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.8, 0.85, 0.9, 1)
        bg_node.inputs['Strength'].default_value = 1.0

def create_accident_scene_cyclist():
    """Crear escena completa de atropello a ciclista"""
    print("Creando escena de atropello a ciclista...")

    # Limpiar
    clear_scene()

    # Crear elementos
    create_road(length=20, width=5)

    # Coche (posición de impacto)
    create_car(location=(0, 0, 0), rotation=0, name="SEAT")

    # Bicicleta caída
    create_bicycle(location=(-2, 0.8, 0), name="Bicycle")

    # Ciclista en posición de impacto
    create_cyclist(location=(-1, 0.5, 0), pose="riding", name="Cyclist")

    # Mediciones (como en las imágenes de referencia)
    create_measurement_line(
        start=(-8, 2, 0.1),
        end=(0, 2, 0.1),
        label="8.008 m"
    )
    create_measurement_line(
        start=(0, 0, 0.1),
        end=(0, 1.2, 0.1),
        label="1.215 m"
    )

    # Iluminación y cámaras
    setup_lighting()
    setup_world_background()
    setup_camera_top_view()
    cam_persp = setup_camera_perspective()

    # Activar cámara perspectiva
    bpy.context.scene.camera = cam_persp

    # Configurar render
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    print("Escena creada exitosamente!")
    return True

# Ejecutar si se llama directamente
if __name__ == "__main__":
    create_accident_scene_cyclist()

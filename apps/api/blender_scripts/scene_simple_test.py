"""
Test simple - objetos grandes y visibles para verificar que funciona
"""
import bpy
import math

print("="*50)
print("TEST SIMPLE - Verificando creación de objetos")
print("="*50)

# 1. Limpiar escena
print("\n1. Limpiando escena...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Crear suelo gris claro
print("2. Creando suelo...")
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
suelo = bpy.context.active_object
suelo.name = "Suelo"
mat_suelo = bpy.data.materials.new("Mat_Suelo")
mat_suelo.use_nodes = True
mat_suelo.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.78, 0.75, 1)
suelo.data.materials.append(mat_suelo)

# 3. Crear carretera
print("3. Creando carretera...")
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
carretera = bpy.context.active_object
carretera.name = "Carretera"
carretera.scale = (1.5, 12, 1)
mat_asfalto = bpy.data.materials.new("Mat_Asfalto")
mat_asfalto.use_nodes = True
mat_asfalto.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1)
carretera.data.materials.append(mat_asfalto)

# 4. COCHE - Cubo grande gris (SEAT Ibiza)
print("4. Creando coche (SEAT Ibiza)...")
bpy.ops.mesh.primitive_cube_add(size=2, location=(0.5, 3, 0.7))
coche = bpy.context.active_object
coche.name = "SEAT_Ibiza"
coche.scale = (0.8, 1.8, 0.6)  # ~1.6m ancho, 3.6m largo, 1.2m alto
coche.rotation_euler.z = math.radians(180)
mat_coche = bpy.data.materials.new("Mat_Coche")
mat_coche.use_nodes = True
mat_coche.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.5, 0.55, 1)
mat_coche.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0.6
coche.data.materials.append(mat_coche)

# Ruedas del coche
print("   - Añadiendo ruedas...")
mat_rueda = bpy.data.materials.new("Mat_Rueda")
mat_rueda.use_nodes = True
mat_rueda.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)

for i, (wx, wy) in enumerate([(-0.7, -1.5), (0.7, -1.5), (-0.7, 1.5), (0.7, 1.5)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.15,
                                         location=(0.5+wx, 3+wy, 0.3))
    rueda = bpy.context.active_object
    rueda.name = f"Rueda_Coche_{i}"
    rueda.rotation_euler.x = math.pi/2
    rueda.data.materials.append(mat_rueda)

# 5. BICICLETA - Roja, caída
print("5. Creando bicicleta (ORBEA)...")
bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.03,
                                  location=(-1.5, 2.5, 0.35))
rueda_bici1 = bpy.context.active_object
rueda_bici1.name = "Bici_Rueda1"
rueda_bici1.rotation_euler.x = math.pi/2
rueda_bici1.rotation_euler.z = math.radians(30)

bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.03,
                                  location=(-1.0, 3.3, 0.35))
rueda_bici2 = bpy.context.active_object
rueda_bici2.name = "Bici_Rueda2"
rueda_bici2.rotation_euler.x = math.pi/2
rueda_bici2.rotation_euler.z = math.radians(30)

# Cuadro de la bici (tubo)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.2,
                                     location=(-1.25, 2.9, 0.5))
cuadro = bpy.context.active_object
cuadro.name = "Bici_Cuadro"
cuadro.rotation_euler = (math.radians(70), math.radians(15), math.radians(30))

# Material rojo para bici
mat_bici = bpy.data.materials.new("Mat_Bici")
mat_bici.use_nodes = True
mat_bici.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)
mat_bici.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0.7
rueda_bici1.data.materials.append(mat_bici)
rueda_bici2.data.materials.append(mat_bici)
cuadro.data.materials.append(mat_bici)

# 6. CICLISTA - Proyectado
print("6. Creando ciclista...")
# Torso
bpy.ops.mesh.primitive_cube_add(size=0.4, location=(-2.5, -3, 0.2))
torso = bpy.context.active_object
torso.name = "Ciclista_Torso"
torso.scale = (1, 0.6, 1.2)
torso.rotation_euler = (math.radians(85), 0, math.radians(20))
mat_camiseta = bpy.data.materials.new("Mat_Camiseta")
mat_camiseta.use_nodes = True
mat_camiseta.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.7, 0.3, 1)  # Verde
torso.data.materials.append(mat_camiseta)

# Cabeza
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-2.3, -3.3, 0.15))
cabeza = bpy.context.active_object
cabeza.name = "Ciclista_Cabeza"
mat_piel = bpy.data.materials.new("Mat_Piel")
mat_piel.use_nodes = True
mat_piel.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.9, 0.75, 0.6, 1)
cabeza.data.materials.append(mat_piel)

# Piernas
mat_pantalon = bpy.data.materials.new("Mat_Pantalon")
mat_pantalon.use_nodes = True
mat_pantalon.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.15, 0.2, 1)
for x in [-0.1, 0.1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.5,
                                         location=(-2.7+x, -2.6, 0.15))
    pierna = bpy.context.active_object
    pierna.name = f"Ciclista_Pierna_{x}"
    pierna.rotation_euler = (math.radians(85), 0, 0)
    pierna.data.materials.append(mat_pantalon)

# 7. MEDICIONES
print("7. Creando líneas de medición...")

# Medición 8.008m (proyección)
curve1 = bpy.data.curves.new("Medida_8m", 'CURVE')
curve1.dimensions = '3D'
curve1.bevel_depth = 0.025
sp1 = curve1.splines.new('POLY')
sp1.points.add(1)
sp1.points[0].co = (-1.5, 2.5, 0.2, 1)
sp1.points[1].co = (-2.5, -3, 0.2, 1)
linea1 = bpy.data.objects.new("Linea_8m", curve1)
bpy.context.collection.objects.link(linea1)
mat_linea = bpy.data.materials.new("Mat_Linea")
mat_linea.use_nodes = True
mat_linea.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
linea1.data.materials.append(mat_linea)

# Texto 8.008m
bpy.ops.object.text_add(location=(-0.5, 0, 1))
txt1 = bpy.context.active_object
txt1.name = "Texto_8m"
txt1.data.body = "8.008 m"
txt1.data.size = 0.5
txt1.data.align_x = 'CENTER'
txt1.rotation_euler = (math.pi/2, 0, 0)
mat_texto = bpy.data.materials.new("Mat_Texto")
mat_texto.use_nodes = True
mat_texto.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
txt1.data.materials.append(mat_texto)

# Medición 1.215m (lateral)
curve2 = bpy.data.curves.new("Medida_1m", 'CURVE')
curve2.dimensions = '3D'
curve2.bevel_depth = 0.025
sp2 = curve2.splines.new('POLY')
sp2.points.add(1)
sp2.points[0].co = (0.5, 3, 0.2, 1)
sp2.points[1].co = (-1.5, 2.5, 0.2, 1)
linea2 = bpy.data.objects.new("Linea_1m", curve2)
bpy.context.collection.objects.link(linea2)
linea2.data.materials.append(mat_linea)

# Texto 1.215m
bpy.ops.object.text_add(location=(-0.5, 4, 1))
txt2 = bpy.context.active_object
txt2.name = "Texto_1m"
txt2.data.body = "1.215 m"
txt2.data.size = 0.4
txt2.data.align_x = 'CENTER'
txt2.rotation_euler = (math.pi/2, 0, 0)
txt2.data.materials.append(mat_texto)

# 8. ILUMINACIÓN
print("8. Configurando iluminación...")
bpy.ops.object.light_add(type='SUN', location=(5, -5, 15))
sol = bpy.context.active_object
sol.name = "Sol"
sol.data.energy = 4
sol.rotation_euler = (math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-5, 5, 10))
relleno = bpy.context.active_object
relleno.name = "Relleno"
relleno.data.energy = 200
relleno.data.size = 5

# Fondo
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.75, 0.82, 0.9, 1)
    bg.inputs['Strength'].default_value = 0.8

# 9. CÁMARAS
print("9. Configurando cámaras...")

# Cenital
bpy.ops.object.camera_add(location=(0, 0, 18))
cam_top = bpy.context.active_object
cam_top.name = "Cam_Cenital"
cam_top.data.type = 'ORTHO'
cam_top.data.ortho_scale = 18

# Perspectiva
bpy.ops.object.camera_add(location=(10, -10, 6))
cam_3d = bpy.context.active_object
cam_3d.name = "Cam_3D"
cam_3d.rotation_euler = (math.radians(70), 0, math.radians(45))

# Frontal
bpy.ops.object.camera_add(location=(4, -12, 3))
cam_front = bpy.context.active_object
cam_front.name = "Cam_Frontal"
cam_front.rotation_euler = (math.radians(82), 0, math.radians(18))

# Cámara por defecto
bpy.context.scene.camera = cam_top

# Configuración render
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Contar objetos creados
objetos = [o for o in bpy.data.objects if o.type in ['MESH', 'CURVE', 'FONT', 'CAMERA', 'LIGHT']]
print(f"\n{'='*50}")
print(f"ESCENA CREADA CON {len(objetos)} OBJETOS:")
for o in objetos[:15]:
    print(f"  - {o.name} ({o.type})")
if len(objetos) > 15:
    print(f"  ... y {len(objetos)-15} más")
print("="*50)

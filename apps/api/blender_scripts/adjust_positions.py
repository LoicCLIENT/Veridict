"""
Ajustar posiciones de los modelos para una escena de accidente realista
Escenario: Coche atropella a ciclista en intersección
"""
import bpy
import math

def get_model(name_contains):
    """Buscar modelo por nombre parcial"""
    for obj in bpy.data.objects:
        if name_contains.lower() in obj.name.lower():
            return obj
    return None

def set_transform(obj, location, rotation_deg, scale):
    """Establecer transformación completa"""
    if obj:
        obj.location = location
        obj.rotation_euler = (
            math.radians(rotation_deg[0]),
            math.radians(rotation_deg[1]),
            math.radians(rotation_deg[2])
        )
        obj.scale = scale
        print(f"  {obj.name}: pos={location}, rot={rotation_deg}")
        return True
    return False

print("="*60)
print("AJUSTANDO POSICIONES DE MODELOS")
print("="*60)

# Buscar modelos importados
coche = get_model("Coche") or get_model("BYD") or get_model("car")
moto = get_model("Moto") or get_model("scooter") or get_model("motorcycle")
bici = get_model("Bici") or get_model("bicycle")
humano = get_model("Ciclista") or get_model("human") or get_model("male") or get_model("figure")

print("\nModelos encontrados:")
print(f"  Coche: {coche.name if coche else 'NO ENCONTRADO'}")
print(f"  Moto: {moto.name if moto else 'NO ENCONTRADO'}")
print(f"  Bicicleta: {bici.name if bici else 'NO ENCONTRADO'}")
print(f"  Humano: {humano.name if humano else 'NO ENCONTRADO'}")

print("\nReposicionando para escena de accidente...")

# ============================================
# ESCENARIO: Atropello de ciclista
# El coche venía por el carril derecho
# El ciclista cruzaba la carretera
# Impacto en el lateral del coche
# ============================================

# COCHE - Posición post-frenada, ligeramente girado por el impacto
# Orientado hacia +X (adelante), girado 10° por impacto
set_transform(
    coche,
    location=(4.0, -1.5, 0),      # Posición final tras frenada
    rotation_deg=(-90, 0, -10),   # -90 en X para GLTF, -10 giro por impacto
    scale=(1.5, 1.5, 1.5)         # Escala apropiada
)

# BICICLETA - Caída tras impacto, en el suelo
# Posición a 5m del coche, inclinada como si hubiera caído
set_transform(
    bici,
    location=(-2.0, 2.5, 0.1),    # Desplazada por impacto
    rotation_deg=(-90, 45, 75),   # Caída en el suelo
    scale=(1.2, 1.2, 1.2)
)

# CICLISTA/HUMANO - Proyectado tras impacto
# Posición más alejada que la bici (proyección)
set_transform(
    humano,
    location=(-4.0, 4.0, 0.05),   # Proyectado más lejos
    rotation_deg=(-90, 0, 120),   # Posición de caída
    scale=(1.0, 1.0, 1.0)
)

# MOTO - Vehículo testigo detenido
# Posición apartada, como si hubiera parado al ver el accidente
set_transform(
    moto,
    location=(-12.0, -3.0, 0),    # Detenida atrás
    rotation_deg=(-90, 0, 15),    # Orientada hacia la escena
    scale=(1.0, 1.0, 1.0)
)

# Actualizar mediciones forenses
print("\nActualizando líneas de medición...")

# Buscar y eliminar mediciones antiguas
old_measurements = [obj for obj in bpy.data.objects if "Medicion" in obj.name or "Linea_" in obj.name or "Texto_" in obj.name]
for obj in old_measurements:
    bpy.data.objects.remove(obj, do_unlink=True)

# Crear nuevas mediciones
def create_measurement(start, end, label, color=(1, 0.3, 0, 1)):
    """Crear línea de medición"""
    # Curva
    curve_data = bpy.data.curves.new(name=f"Medicion_{label[:10]}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.04

    spline = curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (*start, 1)
    spline.points[1].co = (*end, 1)

    curve_obj = bpy.data.objects.new(f"Linea_{label[:10]}", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Material emisivo
    mat = bpy.data.materials.new(name=f"Mat_{label[:10]}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = 3.0
    curve_obj.data.materials.append(mat)

    # Texto
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, start[2] + 0.8)
    bpy.ops.object.text_add(location=mid)
    text = bpy.context.active_object
    text.data.body = label
    text.name = f"Texto_{label[:10]}"
    text.scale = (0.5, 0.5, 0.5)
    text.rotation_euler = (math.pi/2, 0, 0)

    # Material texto blanco
    mat_text = bpy.data.materials.new(name=f"MatTxt_{label[:10]}")
    mat_text.use_nodes = True
    bsdf_t = mat_text.node_tree.nodes["Principled BSDF"]
    bsdf_t.inputs['Base Color'].default_value = (1, 1, 1, 1)
    text.data.materials.append(mat_text)

# Distancia de frenada (marcas en asfalto hasta el coche)
create_measurement(
    start=(-15.0, -1.5, 0.05),
    end=(4.0, -1.5, 0.05),
    label="19.0 m - Frenada",
    color=(1, 0.5, 0, 1)  # Naranja
)

# Trayectoria de impacto (coche a bicicleta)
create_measurement(
    start=(4.0, -1.5, 0.05),
    end=(-2.0, 2.5, 0.05),
    label="7.2 m - Impacto",
    color=(1, 0.15, 0.15, 1)  # Rojo
)

# Proyección del ciclista (bici a humano)
create_measurement(
    start=(-2.0, 2.5, 0.05),
    end=(-4.0, 4.0, 0.05),
    label="2.5 m - Proyeccion",
    color=(0.2, 0.5, 1, 1)  # Azul
)

# Ajustar cámaras para mejor encuadre
print("\nAjustando cámaras...")

cam_cenital = bpy.data.objects.get("Camara_Cenital")
if cam_cenital:
    cam_cenital.location = (-2, 0, 28)
    cam_cenital.data.ortho_scale = 35

cam_3d = bpy.data.objects.get("Camara_3D")
if cam_3d:
    cam_3d.location = (18, -18, 12)
    cam_3d.rotation_euler = (math.radians(60), 0, math.radians(45))

cam_lateral = bpy.data.objects.get("Camara_Lateral")
if cam_lateral:
    cam_lateral.location = (0, -22, 6)
    cam_lateral.rotation_euler = (math.radians(75), 0, 0)

print("\n" + "="*60)
print("POSICIONES AJUSTADAS")
print("="*60)
print("\nEscenario: Atropello de ciclista")
print("  - Coche: Pos final tras frenada de 19m")
print("  - Bicicleta: Caída a 7.2m del punto de impacto")
print("  - Ciclista: Proyectado 2.5m desde la bicicleta")
print("  - Moto: Testigo detenido")
print("\nPresiona F12 en Blender para renderizar")

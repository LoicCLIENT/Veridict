"""
Ejecutar escena ITRASA completa y renderizar todas las vistas
"""
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from send_to_blender import send_to_blender

renders_dir = os.path.join(script_dir, "renders")
os.makedirs(renders_dir, exist_ok=True)

print("=" * 60)
print("CASO ITRASA - Renderizado Completo")
print("=" * 60)

# 1. Crear escena
print("\n[1/2] Creando escena forense...")
with open(os.path.join(script_dir, "scene_itrasa_full.py"), "r", encoding="utf-8") as f:
    script = f.read()

result = send_to_blender(script, timeout=120.0)
print("Escena creada")

# 2. Renderizar todas las vistas
print("\n[2/2] Renderizando 4 vistas...")
render_script = f'''
import bpy
import os

RENDERS = r"{renders_dir}"
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

vistas = [
    ("Cam_Cenital", "itrasa_cenital.png"),
    ("Cam_3D", "itrasa_3d.png"),
    ("Cam_Frontal", "itrasa_frontal.png"),
    ("Cam_Lateral", "itrasa_lateral.png")
]

for nombre_cam, archivo in vistas:
    cam = bpy.data.objects.get(nombre_cam)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS, archivo)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{archivo}}")
    else:
        print(f"ERROR: {{nombre_cam}} no encontrada")

print("Renderizado completo")
'''

result = send_to_blender(render_script, timeout=300.0)
print("Renderizado completado")

# 3. Verificar
print("\n" + "=" * 60)
print("RENDERS GENERADOS:")
print("=" * 60)
for f in sorted(os.listdir(renders_dir)):
    if f.startswith("itrasa_"):
        path = os.path.join(renders_dir, f)
        size = os.path.getsize(path) // 1024
        print(f"  [{size:4d} KB] {f}")

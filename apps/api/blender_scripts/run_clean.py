"""
Ejecutar escena limpia y renderizar
"""
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from send_to_blender import send_to_blender

renders_dir = os.path.join(script_dir, "renders")
os.makedirs(renders_dir, exist_ok=True)

print("=" * 60)
print("ESCENA LIMPIA - Sin modelos GLTF")
print("=" * 60)

# 1. Crear escena
print("\n[1/2] Creando escena...")
with open(os.path.join(script_dir, "scene_clean.py"), "r", encoding="utf-8") as f:
    script = f.read()

result = send_to_blender(script, timeout=90.0)
print("Escena creada")

# 2. Renderizar
print("\n[2/2] Renderizando 3 vistas...")
render_script = f'''
import bpy
import os

RENDERS = r"{renders_dir}"
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

cams = [
    ("Cam_Cenital", "clean_cenital.png"),
    ("Cam_3D", "clean_3d.png"),
    ("Cam_Frontal", "clean_frontal.png")
]

for name, file in cams:
    cam = bpy.data.objects.get(name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS, file)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{file}}")

print("Listo")
'''

result = send_to_blender(render_script, timeout=180.0)
print("Renderizado completado")

# Verificar
print("\nArchivos generados:")
for f in sorted(os.listdir(renders_dir)):
    if f.startswith("clean_"):
        size = os.path.getsize(os.path.join(renders_dir, f)) // 1024
        print(f"  - {f} ({size} KB)")

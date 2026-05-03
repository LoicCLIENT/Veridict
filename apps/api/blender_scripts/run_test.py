"""
Test de escena simple
"""
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from send_to_blender import send_to_blender

renders_dir = os.path.join(script_dir, "renders")
os.makedirs(renders_dir, exist_ok=True)

print("="*60)
print("TEST DE ESCENA SIMPLE")
print("="*60)

# 1. Crear escena
print("\n[1] Creando escena de prueba...")
with open(os.path.join(script_dir, "scene_simple_test.py"), "r", encoding="utf-8") as f:
    script = f.read()

result = send_to_blender(script, timeout=60.0)
print(f"Resultado: {result}")

# 2. Renderizar
print("\n[2] Renderizando...")
render_script = f'''
import bpy
import os

RENDERS = r"{renders_dir}"

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

for name, file in [("Cam_Cenital", "test_cenital.png"), ("Cam_3D", "test_3d.png"), ("Cam_Frontal", "test_frontal.png")]:
    cam = bpy.data.objects.get(name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS, file)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{file}}")
    else:
        print(f"ERROR: {{name}} no encontrada")

# Listar todos los objetos para verificar
print("\\nOBJETOS EN ESCENA:")
for obj in bpy.data.objects:
    print(f"  - {{obj.name}} ({{obj.type}})")
'''

result = send_to_blender(render_script, timeout=120.0)
print(f"Resultado: {result}")

# 3. Verificar
print("\n[3] Verificando renders...")
for f in os.listdir(renders_dir):
    if f.startswith("test_"):
        path = os.path.join(renders_dir, f)
        size = os.path.getsize(path) / 1024
        print(f"  ✓ {f}: {size:.0f} KB")

print("\nHecho!")

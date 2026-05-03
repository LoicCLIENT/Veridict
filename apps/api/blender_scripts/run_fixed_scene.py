"""
Ejecutar escena corregida
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    renders_dir = os.path.join(script_dir, "renders")

    # Crear escena
    print("="*60)
    print("Creando escena corregida...")
    print("="*60)

    with open(os.path.join(script_dir, "scene_fixed.py"), "r", encoding="utf-8") as f:
        script = f.read()

    send_to_blender(script, timeout=120.0)

    # Renderizar
    print("\nRenderizando...")

    render_script = f'''
import bpy
import os

RENDERS_DIR = r"{renders_dir}"
os.makedirs(RENDERS_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

cams = [("Cam_Top", "final_cenital.png"), ("Cam_Persp", "final_3d.png"), ("Cam_Front", "final_frontal.png")]

for name, file in cams:
    cam = bpy.data.objects.get(name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, file)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{file}}")
'''

    send_to_blender(render_script, timeout=180.0)

    # Verificar
    files = [f for f in os.listdir(renders_dir) if f.startswith("final_")]
    print(f"\nRenders: {files}")

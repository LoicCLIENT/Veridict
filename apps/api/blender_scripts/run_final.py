"""
Ejecutar escena final y renderizar
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    renders_dir = os.path.join(script_dir, "renders")

    print("="*60)
    print("ESCENA FINAL - ESTILO REFERENCIA")
    print("="*60)

    # Crear escena
    print("\n1. Creando escena...")
    with open(os.path.join(script_dir, "scene_final.py"), "r", encoding="utf-8") as f:
        send_to_blender(f.read(), timeout=120.0)

    # Renderizar
    print("\n2. Renderizando 3 vistas...")
    render_script = f'''
import bpy
import os

RENDERS = r"{renders_dir}"
os.makedirs(RENDERS, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

for name, file in [("Cam_Top", "vista_cenital.png"), ("Cam_3D", "vista_3d.png"), ("Cam_Front", "vista_frontal.png")]:
    cam = bpy.data.objects.get(name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS, file)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{file}}")
'''
    send_to_blender(render_script, timeout=180.0)

    # Verificar
    files = [f for f in os.listdir(renders_dir) if f.startswith("vista_")]
    print(f"\n3. Renders completados: {files}")
    for f in files:
        size = os.path.getsize(os.path.join(renders_dir, f)) / 1024
        print(f"   - {f}: {size:.0f} KB")

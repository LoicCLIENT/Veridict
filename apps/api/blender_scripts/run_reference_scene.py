"""
Crear escena estilo referencia y renderizar
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    renders_dir = os.path.join(script_dir, "renders")

    # Paso 1: Crear escena
    print("="*60)
    print("PASO 1: Creando escena estilo referencia...")
    print("="*60)

    scene_path = os.path.join(script_dir, "scene_reference_style.py")
    with open(scene_path, "r", encoding="utf-8") as f:
        scene_script = f.read()

    result = send_to_blender(scene_script, timeout=120.0)
    print("Escena creada.\n")

    # Paso 2: Renderizar múltiples vistas
    print("="*60)
    print("PASO 2: Renderizando vistas...")
    print("="*60)

    render_script = f'''
import bpy
import os

RENDERS_DIR = r"{renders_dir}"
os.makedirs(RENDERS_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Renderizar cada cámara
cameras = [
    ("Cam_Cenital", "ref_cenital.png"),
    ("Cam_3D", "ref_3d.png"),
    ("Cam_Frontal", "ref_frontal.png")
]

for cam_name, filename in cameras:
    cam = bpy.data.objects.get(cam_name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, filename)
        bpy.ops.render.render(write_still=True)
        print(f"Renderizado: {{filename}}")
    else:
        print(f"Camara no encontrada: {{cam_name}}")

print("RENDERS COMPLETADOS")
'''

    result = send_to_blender(render_script, timeout=180.0)

    # Verificar archivos
    if os.path.exists(renders_dir):
        files = [f for f in os.listdir(renders_dir) if f.startswith("ref_")]
        print(f"\n¡COMPLETADO! Renders: {files}")
        for f in files:
            path = os.path.join(renders_dir, f)
            size = os.path.getsize(path) / 1024
            print(f"  - {f}: {size:.0f} KB")

"""
Ejecutar escena ITRASA y renderizar todas las vistas
"""
import os
import sys

# Añadir directorio al path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from send_to_blender import send_to_blender

def main():
    renders_dir = os.path.join(script_dir, "renders")
    os.makedirs(renders_dir, exist_ok=True)

    print("="*60)
    print("RENDERIZADO CASO ITRASA - Aulestia")
    print("="*60)

    # 1. Crear escena
    print("\n[1/2] Creando escena forense...")
    scene_path = os.path.join(script_dir, "scene_itrasa.py")

    with open(scene_path, "r", encoding="utf-8") as f:
        scene_script = f.read()

    result = send_to_blender(scene_script, timeout=120.0)
    print(result.get("message", "Escena creada"))

    # 2. Renderizar vistas
    print("\n[2/2] Renderizando vistas...")

    render_script = f'''
import bpy
import os

RENDERS_DIR = r"{renders_dir}"
os.makedirs(RENDERS_DIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Configuración EEVEE para mejor calidad
eevee = scene.eevee
eevee.use_soft_shadows = True
eevee.shadow_cube_size = '2048'
eevee.shadow_cascade_size = '2048'

# Lista de cámaras y archivos
renders = [
    ("Cam_Cenital", "itrasa_cenital.png"),
    ("Cam_3D", "itrasa_3d.png"),
    ("Cam_Frontal", "itrasa_frontal.png")
]

for cam_name, filename in renders:
    cam = bpy.data.objects.get(cam_name)
    if cam:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, filename)
        bpy.ops.render.render(write_still=True)
        print(f"OK: {{filename}}")
    else:
        print(f"WARN: Cámara {{cam_name}} no encontrada")

print("Renderizado completado")
'''

    result = send_to_blender(render_script, timeout=180.0)
    print(result.get("message", "Renderizado completado"))

    # 3. Verificar resultados
    print("\n" + "="*60)
    print("RESULTADOS:")
    print("="*60)

    for f in os.listdir(renders_dir):
        if f.startswith("itrasa_"):
            path = os.path.join(renders_dir, f)
            size_kb = os.path.getsize(path) / 1024
            print(f"  ✓ {f}: {size_kb:.0f} KB")

    print("\nRenders guardados en:", renders_dir)

if __name__ == "__main__":
    main()

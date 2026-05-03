"""
Renderizar la escena con modelos reales desde múltiples ángulos
"""
import bpy
import os

RENDERS_DIR = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"

# Asegurar directorio existe
os.makedirs(RENDERS_DIR, exist_ok=True)

# Configurar render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# Renderizar desde cada cámara
cameras = ["Camara_Cenital", "Camara_3D", "Camara_Lateral"]
output_names = ["accidente_cenital.png", "accidente_3d.png", "accidente_lateral.png"]

for cam_name, output_name in zip(cameras, output_names):
    camera = bpy.data.objects.get(cam_name)
    if camera:
        scene.camera = camera
        scene.render.filepath = os.path.join(RENDERS_DIR, output_name)
        print(f"Renderizando: {output_name}...")
        bpy.ops.render.render(write_still=True)
        print(f"  -> Completado: {output_name}")
    else:
        print(f"  -> Cámara {cam_name} no encontrada")

print("\n" + "="*50)
print("RENDERS COMPLETADOS")
print("="*50)
print(f"Archivos en: {RENDERS_DIR}")

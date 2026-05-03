"""
Render rápido de escena de accidente - usando EEVEE para velocidad
"""

import bpy
import os

# Configurar render EEVEE (mucho más rápido)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'  # Blender 5.x usa BLENDER_EEVEE

# Resolución más baja para preview
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Formato de salida
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'

# Directorio de salida
output_dir = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"

# Crear directorio si no existe
os.makedirs(output_dir, exist_ok=True)

# Renderizar vista cenital
camera_top = bpy.data.objects.get("Camera_TopView")
if camera_top:
    scene.camera = camera_top
    scene.render.filepath = os.path.join(output_dir, "cenital.png")
    bpy.ops.render.render(write_still=True)
    print("Vista cenital renderizada")

# Renderizar vista perspectiva
camera_persp = bpy.data.objects.get("Camera_Perspective")
if camera_persp:
    scene.camera = camera_persp
    scene.render.filepath = os.path.join(output_dir, "perspectiva.png")
    bpy.ops.render.render(write_still=True)
    print("Vista perspectiva renderizada")

print(f"Renders guardados en: {output_dir}")

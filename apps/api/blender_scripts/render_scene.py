"""
Render de escena de accidente desde múltiples ángulos
"""

import bpy
import os

def setup_render_settings():
    """Configurar ajustes de render"""
    scene = bpy.context.scene

    # Usar Cycles para mejor calidad
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

    # Resolución
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    # Formato de salida
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

def render_from_camera(camera_name: str, output_path: str):
    """Renderizar desde una cámara específica"""
    scene = bpy.context.scene

    # Buscar cámara
    camera = bpy.data.objects.get(camera_name)
    if camera:
        scene.camera = camera
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        print(f"Renderizado: {output_path}")
        return True
    else:
        print(f"Cámara no encontrada: {camera_name}")
        return False

def render_all_views(output_dir: str):
    """Renderizar todas las vistas"""

    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)

    setup_render_settings()

    # Renderizar vista cenital
    render_from_camera(
        "Camera_TopView",
        os.path.join(output_dir, "vista_cenital.png")
    )

    # Renderizar vista perspectiva
    render_from_camera(
        "Camera_Perspective",
        os.path.join(output_dir, "vista_perspectiva.png")
    )

    print(f"Renders completados en: {output_dir}")

if __name__ == "__main__":
    # Directorio de salida
    output_dir = r"C:\Users\hypex\Desktop\HACKATHON JAVI BAP\Veridict\apps\api\blender_scripts\renders"
    render_all_views(output_dir)

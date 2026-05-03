"""
Ejecutar render rápido en Blender
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    # Leer el script de render rápido
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "quick_render.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    # Enviar a Blender con timeout largo (2 minutos)
    print("Iniciando renders EEVEE en Blender...")
    print("(Esto puede tomar 30-60 segundos)")
    result = send_to_blender(script, timeout=120.0)
    print(f"Resultado: {result}")

    # Verificar si los archivos fueron creados
    renders_dir = os.path.join(script_dir, "renders")
    if os.path.exists(renders_dir):
        files = os.listdir(renders_dir)
        print(f"Archivos en renders/: {files}")

"""
Ejecutar render en Blender
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    # Leer el script de render
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "render_scene.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    # Enviar a Blender
    print("Iniciando renders en Blender...")
    print("(Esto puede tomar unos segundos)")
    result = send_to_blender(script)
    print(f"Resultado: {result}")

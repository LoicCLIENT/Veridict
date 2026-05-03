"""
Crear escena profesional con placeholders para assets
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "pro_scene_with_assets.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    print("Creando escena profesional con placeholders...")
    result = send_to_blender(script, timeout=60.0)
    print(f"Resultado: {result}")

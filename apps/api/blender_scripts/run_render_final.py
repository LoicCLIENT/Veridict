"""
Ejecutar render de la escena final
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "render_final_scene.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    print("="*50)
    print("RENDERIZANDO ESCENA CON MODELOS REALES")
    print("="*50)
    print("\nVistas a renderizar:")
    print("  - Vista cenital (plano técnico)")
    print("  - Vista 3D perspectiva")
    print("  - Vista lateral")
    print("\nEnviando a Blender (puede tomar 1-2 minutos)...")

    result = send_to_blender(script, timeout=180.0)

    if result.get('status') == 'success':
        print("\n¡RENDERS COMPLETADOS!")
        renders_dir = os.path.join(script_dir, "renders")
        if os.path.exists(renders_dir):
            files = [f for f in os.listdir(renders_dir) if f.startswith("accidente_")]
            print(f"\nArchivos creados: {files}")
    else:
        print(f"\nError: {result}")

"""
Ajustar posiciones y renderizar escena final
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Paso 1: Ajustar posiciones
    print("="*50)
    print("PASO 1: Ajustando posiciones de modelos...")
    print("="*50)

    adjust_path = os.path.join(script_dir, "adjust_positions.py")
    with open(adjust_path, "r", encoding="utf-8") as f:
        adjust_script = f.read()

    result = send_to_blender(adjust_script, timeout=60.0)
    print("Posiciones ajustadas.\n")

    # Paso 2: Renderizar
    print("="*50)
    print("PASO 2: Renderizando 3 vistas...")
    print("="*50)

    render_path = os.path.join(script_dir, "render_final_scene.py")
    with open(render_path, "r", encoding="utf-8") as f:
        render_script = f.read()

    result = send_to_blender(render_script, timeout=180.0)

    # Verificar renders
    renders_dir = os.path.join(script_dir, "renders")
    if os.path.exists(renders_dir):
        files = [f for f in os.listdir(renders_dir) if f.startswith("accidente_")]
        print(f"\n¡COMPLETADO! Renders creados: {files}")
        for f in files:
            path = os.path.join(renders_dir, f)
            size = os.path.getsize(path) / 1024
            print(f"  - {f}: {size:.0f} KB")

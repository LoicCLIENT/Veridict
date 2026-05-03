"""
Ejecutar creación de escena y render completo
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "create_and_render.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    print("Enviando script combinado a Blender...")
    print("Creará escena de accidente + renderizará 2 vistas")
    print("(Puede tomar 1-2 minutos)")

    result = send_to_blender(script, timeout=180.0)
    print(f"Resultado: {result}")

    # Verificar archivos
    renders_dir = os.path.join(script_dir, "renders")
    if os.path.exists(renders_dir):
        files = os.listdir(renders_dir)
        if files:
            print(f"Archivos creados: {files}")
        else:
            print("Directorio renders/ vacío")

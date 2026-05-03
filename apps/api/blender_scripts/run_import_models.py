"""
Ejecutar importación de modelos reales en Blender
"""
import os
from send_to_blender import send_to_blender

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "import_real_models.py")

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    print("="*50)
    print("IMPORTANDO MODELOS REALES A BLENDER")
    print("="*50)
    print("\nModelos a importar:")
    print("  - Coche BYD Seal 2024")
    print("  - Moto")
    print("  - Bicicleta Low Poly")
    print("  - Humano Rigged")
    print("\nEnviando a Blender...")

    result = send_to_blender(script, timeout=120.0)

    if result.get('status') == 'success':
        print("\n¡ÉXITO! Escena creada en Blender")
        print("\nPróximos pasos:")
        print("  1. Revisa la escena en Blender")
        print("  2. Ajusta posiciones si es necesario")
        print("  3. Presiona F12 para renderizar")
    else:
        print(f"\nError: {result}")

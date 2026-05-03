"""
Enviar script a Blender via socket TCP
"""
import socket
import json

def send_to_blender(code: str, host: str = "localhost", port: int = 9876, timeout: float = 60.0) -> dict:
    """Enviar código Python a Blender via socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Configurable timeout
        sock.connect((host, port))

        # Formato del comando para el addon
        command = {
            "type": "execute_code",
            "params": {
                "code": code
            }
        }

        message = json.dumps(command) + "\n"
        sock.sendall(message.encode('utf-8'))

        # Recibir respuesta con timeout
        response = b""
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"\n" in chunk:
                    break
        except socket.timeout:
            print("Timeout esperando respuesta (esto es normal)")

        sock.close()

        if response:
            return json.loads(response.decode('utf-8'))
        return {"status": "no_response"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import os
    # Leer el script de accidente (usar path absoluto)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "accident_cyclist.py")
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    # Enviar a Blender
    print("Enviando script a Blender...")
    result = send_to_blender(script)
    print(f"Resultado: {result}")

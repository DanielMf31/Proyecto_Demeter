import socket
import json
import sys
from pydantic import BaseModel

# --- 1. Definir el Modelo (Mismo contrato que el servidor) ---
class MensajeChat(BaseModel):
    usuario: str
    texto: str
    prioridad: int = 1

def run_pydantic_client(usuario, texto):
    port = 9000
    print(f"🍌 Nano Banana Client: Conectando a {port}...")
    
    try:
        # 1. Crear Objeto Pydantic
        mi_mensaje = MensajeChat(usuario=usuario, texto=texto, prioridad=5)
        print(f"🤖 Objeto Python creado: {mi_mensaje}")
        
        # 2. Serializar a JSON (Aplanar)
        json_a_enviar = mi_mensaje.model_dump_json()
        print(f"📦 Serializado a JSON: '{json_a_enviar}'")
        
        # 3. Enviar
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', port))
        client.send(json_a_enviar.encode('utf-8'))
        
        # 4. Respuesta
        data = client.recv(1024)
        print(f"📥 Respuesta: {data.decode('utf-8')}")
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    u = "Daniel"
    t = "Hola desde Pydantic"
    if len(sys.argv) > 2:
        u = sys.argv[1]
        t = " ".join(sys.argv[2:])
        
    run_pydantic_client(u, t)

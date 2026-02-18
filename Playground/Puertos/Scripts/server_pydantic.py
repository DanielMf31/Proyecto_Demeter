import socket
import json
from pydantic import BaseModel, ValidationError

# --- 1. Definir el Modelo (El Contrato) ---
class MensajeChat(BaseModel):
    usuario: str
    texto: str
    prioridad: int = 1  # Opcional, por defecto 1

def start_pydantic_server(port=9000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    
    print(f"🍌 Nano Banana Pydantic Server: Escuchando en {port}...")

    while True:
        try:
            client, addr = server_socket.accept()
            print(f"\n📞 Conexión de: {addr}")
            
            data = client.recv(1024)
            if not data:
                break
                
            raw_json = data.decode('utf-8')
            print(f"📥 Datos Crudos recibidos: '{raw_json}'")
            
            # --- 2. Validación con Pydantic ---
            try:
                # Intentamos inflar el JSON a un objeto Python
                mensaje_obj = MensajeChat.model_validate_json(raw_json)
                
                print("✅ ¡Validación Exitosa!")
                print(f"   -> Usuario: {mensaje_obj.usuario}")
                print(f"   -> Texto: {mensaje_obj.texto}")
                print(f"   -> Prioridad: {mensaje_obj.prioridad}")
                
                respuesta = {"status": "OK", "msg": f"Hola {mensaje_obj.usuario}, recibido."}
                
            except ValidationError as e:
                print("❌ ¡Error de Validación! El cliente envió basura.")
                print(e)
                respuesta = {"status": "ERROR", "msg": "Tus datos no cumplen el contrato."}
            except Exception as e:
                print(f"❌ Error JSON: {e}")
                respuesta = {"status": "ERROR", "msg": "Eso no era ni JSON."}

            # Enviar respuesta como JSON
            client.send(json.dumps(respuesta).encode('utf-8'))
            client.close()
            
        except KeyboardInterrupt:
            print("\n🍌 Servidor apagado.")
            break

    server_socket.close()

if __name__ == "__main__":
    start_pydantic_server()

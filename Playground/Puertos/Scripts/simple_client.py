import socket
import sys

def run_client(port, message="Hola Servidor"):
    print(f"🍌 Nano Banana Client: Buscando el edificio 127.0.0.1, puerta {port}...")
    
    try:
        # 1. Crear Socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Connect (Llamar al timbre)
        client_socket.connect(('127.0.0.1', port))
        print("✅ ¡Conexión establecida! Alguien abrió la puerta.")
        
        # 3. Send (Hablar)
        print(f"📤 Enviando: '{message}'")
        client_socket.send(message.encode('utf-8'))
        
        # 4. Receive (Escuchar respuesta)
        data = client_socket.recv(1024)
        print(f"📥 Respuesta del Servidor: '{data.decode('utf-8')}'")
        
        # 5. Close (Irse)
        client_socket.close()
        print("🔴 Conexión cerrada.")
        
    except ConnectionRefusedError:
        print(f"❌ Nadie responde en el puerto {port}. ¿Está el servidor encendido?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Uso: python simple_client.py <PUERTO> [MENSAJE]")
        print("Ejemplo: python simple_client.py 8888 'Hola Banana'")
        sys.exit(1)
        
    puerto = int(sys.argv[1])
    msg = "Hola desde el Cliente!"
    if len(sys.argv) > 2:
        msg = " ".join(sys.argv[2:])
        
    run_client(puerto, msg)

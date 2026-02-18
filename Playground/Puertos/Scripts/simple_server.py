import socket
import sys

def start_server(port=8888):
    # 1. Crear el Socket (Teléfono)
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Bind (Reservar la habitación con el Recepcionista/Kernel)
    # '0.0.0.0' significa escucharlo TODO (Local y Externo si hubiera)
    # '127.0.0.1' significa SOLO local
    host = '127.0.0.1'
    try:
        server_socket.bind((host, port))
        print(f"🍌 Nano Banana Server: Habitación {port} reservada en {host}.")
    except OSError as e:
        print(f"❌ Error: La habitación {port} está ocupada. ¿Ya hay otro servidor corriendo?")
        return

    # 3. Listen (Ponerse a esperar la llamada)
    server_socket.listen(1)
    print("👂 Escuchando... (Esperando llamada)")

    while True:
        try:
            # 4. Accept (Descolgar el teléfono)
            # Esto BLOQUEA el programa hasta que alguien llame
            client_socket, addr = server_socket.accept()
            print(f"\n📞 ¡LLAMADA ENTRANTE! De: {addr}")
            
            # 5. Receive (Escuchar lo que dicen)
            data = client_socket.recv(1024) # Leer hasta 1024 bytes
            mensaje = data.decode('utf-8')
            print(f"📩 Mensaje recibido: '{mensaje}'")
            
            # 6. Send (Responder)
            respuesta = f"Hola amigo. Recibí tu mensaje: {mensaje}"
            client_socket.send(respuesta.encode('utf-8'))
            print("📤 Respuesta enviada.")
            
            # 7. Close (Colgar esta llamada)
            client_socket.close()
            print("🔴 Llamada finalizada. Volviendo a escuchar...")
            
        except KeyboardInterrupt:
            print("\n🍌 Nano Banana se va a dormir. ¡Adiós!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

    server_socket.close()

if __name__ == "__main__":
    puerto = 8888
    if len(sys.argv) > 1:
        puerto = int(sys.argv[1])
    start_server(puerto)

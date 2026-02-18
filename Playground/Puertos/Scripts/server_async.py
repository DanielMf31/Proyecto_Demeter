import asyncio
import sys

async def handle_client(reader, writer):
    """
    Esta función se ejecuta de forma INDEPENDIENTE para cada cliente.
    Es como si clonáramos al recepcionista para cada llamada.
    """
    addr = writer.get_extra_info('peername')
    print(f"\n✨ Nuevo Cliente Conectado: {addr}")

    try:
        while True:
            # 1. READ (Esperar datos)
            # 'await' significa: "Nano Banana, vete a hacer otras cosas 
            # mientras llegan los datos. Avísame cuando lleguen".
            data = await reader.read(100)
            
            if not data:
                print(f"👋 Cliente {addr} se desconectó.")
                break

            message = data.decode().strip()
            print(f"📩 [{addr[1]}] Dice: {message}")

            # 2. PROCESS (Simular trabajo)
            # Imagina que guardamos en base de datos
            response = f"ECO: {message}"
            
            # 3. WRITE (Responder)
            writer.write(response.encode())
            await writer.drain() # Asegurar que se envía todo

    except Exception as e:
        print(f"❌ Error con {addr}: {e}")
    finally:
        writer.close()

async def main():
    port = 8888
    # start_server es la magia. Crea el socket y el bucle.
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', port
    )

    addr = server.sockets[0].getsockname()
    print(f"🍌 Nano Banana Async Server corriendo en {addr}")
    print("   -> ¡Puede atender a miles de clientes a la vez!")

    # Mantener el servidor vivo para siempre
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        # Arrancamos el Bucle de Eventos (Event Loop)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🍌 Servidor detenido.")

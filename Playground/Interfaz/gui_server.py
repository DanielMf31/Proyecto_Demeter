import asyncio
import json

async def handle_gui_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"\n🖥️  [GUI Server] Nueva conexión desde: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            
            message = data.decode().strip()
            print(f"📥 [RX] Recibido: {message}")
            
            # Intentar parsear JSON
            try:
                command = json.loads(message)
                action = command.get("action", "UNKNOWN")
                print(f"⚙️  [ACCION] Ejecutando: {action}")
                
                # Simular respuesta
                response = {"status": "OK", "msg": f"Comando '{action}' recibido correctamente."}
                writer.write(json.dumps(response).encode())
                await writer.drain()
                print(f"📤 [TX] Respondido OK.")
                
            except json.JSONDecodeError:
                print("❌ Error: No es JSON válido.")

    except Exception as e:
        print(f"❌ Error conexión: {e}")
    finally:
        print(f"👋 Cliente {addr} desconectado.")
        writer.close()

async def main():
    server = await asyncio.start_server(handle_gui_client, '127.0.0.1', 8080)
    print("🍌 Nano Banana GUI Server (Port 8080) LISTO.")
    print("   -> Esperando clics de botones...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApagando GUI Server.")

import asyncio
import sys
import random

async def run_repeater_client(client_id):
    uri = '127.0.0.1'
    port = 8888
    
    print(f"🤖 Cliente {client_id}: Intentando conectar a {port}...")
    
    try:
        reader, writer = await asyncio.open_connection(uri, port)
        print(f"✅ Cliente {client_id}: Conectado. Enviando mensajes periódicos.")
        
        counter = 1
        while True:
            # 1. Generar Mensaje
            msg = f"Mensaje #{counter} de Cliente {client_id}"
            print(f"📤 [{client_id}] Enviando: {msg}")
            
            writer.write(msg.encode())
            await writer.drain()
            
            # 2. Leer Respuesta
            data = await reader.read(100)
            print(f"📥 [{client_id}] Recibido: {data.decode().strip()}")
            
            counter += 1
            
            # 3. Esperar un tiempo aleatorio (para desincronizar clientes)
            wait_time = random.uniform(2.0, 5.0)
            print(f"⏳ [{client_id}] Durmiendo {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
            
    except ConnectionRefusedError:
        print(f"❌ No se pudo conectar. ¿Está 'server_async.py' corriendo?")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("Fin.")

if __name__ == "__main__":
    cid = "A"
    if len(sys.argv) > 1:
        cid = sys.argv[1]
    
    try:
        asyncio.run(run_repeater_client(cid))
    except KeyboardInterrupt:
        print("\n👋 Cliente detenido.")

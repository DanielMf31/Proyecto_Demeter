import asyncio
import json
from protocol_schema import GpioCommand, ActionResponse

async def run_demeter_client():
    uri = '127.0.0.1'
    port = 9999
    
    print(f"🖥️  [TUI Mock] Conectando al Backend en {port}...")
    
    try:
        reader, writer = await asyncio.open_connection(uri, port)
        print("✅ Conectado.")

        # --- Escenario de Prueba ---
        
        # 1. Crear el Comando (Objeto Python)
        mi_comando = GpioCommand(pin=2, action="TOGGLE")
        print(f"🤖 [CLIENT] Generando Comando: {mi_comando}")

        # 2. Serializar (A JSON)
        json_payload = mi_comando.model_dump_json()
        print(f"📦 [CLIENT] Serializado: {json_payload}")

        # 3. Enviar
        writer.write(json_payload.encode())
        await writer.drain()

        # 4. Esperar Respuesta
        data = await reader.read(1024)
        if data:
            response_json = data.decode()
            print(f"📥 [CLIENT] Respuesta Cruda: {response_json}")
            
            # 5. Deserializar Respuesta (Validar que el server no miente)
            try:
                respuesta_obj = ActionResponse.model_validate_json(response_json)
                state_icon = "🟢" if respuesta_obj.pin_state else "🔴"
                print(f"✅ [CLIENT] Respuesta Validada: {respuesta_obj.message} | Estado: {state_icon}")
            except Exception as e:
                print("❌ El servidor envió basura.")

        print("Cerrando conexión.")
        writer.close()
        await writer.wait_closed()

    except ConnectionRefusedError:
        print("❌ No se encuentra el servidor. Ejecuta 'server_demeter_mock.py' primero.")

if __name__ == "__main__":
    asyncio.run(run_demeter_client())

import asyncio
import json
from pydantic import ValidationError
from protocol_schema import GpioCommand, ActionResponse

# Simulación del Estado del Hardware (en memoria)
gpio_state = {} 

async def handle_demeter_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"\n🌱 [Demeter Mock] Conexión de TUI Simulada: {addr}")

    try:
        while True:
            # 1. Leer Datos (JSON String)
            data = await reader.read(1024)
            if not data:
                break
            
            raw_json = data.decode().strip()
            print(f"📥 [RX] Raw: {raw_json}")

            try:
                # 2. Deserializar y Validar (El Contrato)
                cmd = GpioCommand.model_validate_json(raw_json)
                
                # 3. Lógica de Negocio (Simular Hardware)
                print(f"⚙️  [LOGIC] Procesando comando GPIO en Pin {cmd.pin}...")
                
                # Simular cambio de estado
                current = gpio_state.get(cmd.pin, False)
                
                if cmd.action == "ON":
                    new_state = True
                elif cmd.action == "OFF":
                    new_state = False
                else: # TOGGLE
                    new_state = not current
                
                gpio_state[cmd.pin] = new_state
                print(f"💡 [HARDWARE] Pin {cmd.pin} ahora es {'ENCENDIDO' if new_state else 'APAGADO'}")

                # 4. Crear Respuesta (Response Object)
                response = ActionResponse(
                    status="OK",
                    message=f"Pin {cmd.pin} cambiado a {cmd.action}",
                    pin_state=new_state
                )

            except ValidationError as e:
                print(f"❌ [ERROR] Validación fallida:\n{e}")
                response = ActionResponse(status="ERROR", message="JSON Invalido o Esquema Incorrecto")
            except Exception as e:
                print(f"❌ [ERROR] {e}")
                response = ActionResponse(status="ERROR", message=str(e))

            # 5. Serializar Respuesta y Enviar
            response_json = response.model_dump_json()
            writer.write(response_json.encode())
            await writer.drain()
            print(f"📤 [TX] Enviado: {response_json}")

    except Exception as e:
        print(f"Error de conexión: {e}")
    finally:
        writer.close()

async def main():
    server = await asyncio.start_server(handle_demeter_client, '127.0.0.1', 9999)
    print("🍌 Nano Banana Demeter Mock (Port 9999) LISTO.")
    print("   -> Esperando comandos GPIO...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApagando Mock Server.")

# 2. Núcleo Asíncrono y Manejo de Eventos

El corazón del sistema es `DemeterService`, una aplicación basada en `asyncio` que permite la concurrencia real de E/S. Esto significa que el sistema puede estar recibiendo datos de telemetría por UART mientras simultáneamente atiende peticiones de la GUI, sin bloquearse.

## 2.1 Bucle de Eventos (Event Loop)

El servicio inicia dos tareas asíncronas principales:

1.  **Servidor TCP (`handle_tcp_client`):** Escucha conexiones entrantes de clientes (GUI). Por cada cliente, se crea una corutina dedicada que lee sus peticiones JSON.
2.  **Lectura UART (`_read_loop` en `AsyncUartTransport`):** Una tarea de fondo que lee continuamente del puerto serial. Cuando llegan bytes, invoca un *callback* en el hilo principal del loop.

## 2.2 Procesamiento de Protocolo

El flujo de datos desde el hardware es el siguiente:

1.  **Recepción (`on_uart_data`):** Los bytes crudos se añaden a un `rx_buffer`.
2.  **Parseo (`process_buffer`):**
    *   El servicio busca el byte de inicio `SYNC (0xFE)`.
    *   Verifica si hay suficientes datos para la longitud indicada.
    *   Extrae la trama y verifica el CRC usando `DemeterProtocolV2`.
3.  **Despacho (`handle_protocol_command`):**
    *   Si es `DATA_REPORT`: Se convierte a JSON y se emite a todos los clientes TCP conectados ("Broadcast").
    *   Si es `ACK/NACK`: Se loguea para depuración.

## 2.3 Sistema de Eventos (Broadcasting)

El backend implementa un patrón **Publish-Subscribe** simple sobre TCP.

*   Cualquier cliente conectado (GUI) se añade automáticamente al conjunto `self.clients`.
*   Cuando ocurre un evento relevante (ej. llega temperatura de un sensor), el servicio invoca `broadcast_event`.
*   Este método serializa el modelo Pydantic a JSON y lo escribe en el stream de salida de *todos* los sockets conectados.

### Código Relevante (`async_service.py`)

```python
def broadcast_event(self, model):
    """Envía modelo Pydantic como JSON a todos los clientes TCP."""
    json_str = model.model_dump_json()
    data = json_str.encode()
    
    for writer in list(self.clients):
        try:
            writer.write(data) # Non-blocking write
        except Exception:
            self.clients.discard(writer)
```

## 2.4 Modo Mock

El sistema soporta un `MOCK_MODE` (activado por variable de entorno `DEMETER_MOCK=True` o flag `--mock`).
En este modo:
*   No se intenta abrir el puerto Serial.
*   Las acciones GPIO se simulan en memoria (`mock_gpio_state`).
*   Las peticiones de sensores devuelven respuestas simuladas inmediatas.
*   Esto permite desarrollar y probar la GUI sin tener el hardware conectado.

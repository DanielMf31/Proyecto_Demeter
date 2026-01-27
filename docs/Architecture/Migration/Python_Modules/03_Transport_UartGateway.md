# Documentación del Módulo: `uart_gateway.py`

**Ubicación:** `Python/src/transport/uart_gateway.py`

## Propósito
Gestiona la comunicación asíncrona con el hardware. Aísla la complejidad de los puertos serie (`/dev/tty...`) del resto de la aplicación.

## Clases Principales

### `class UartGateway(threading.Thread)`

Hereda de `Thread`, lo que significa que su método `run()` se ejecuta en paralelo al resto del programa.

#### Conceptos Clave
1.  **Thread Safety (Seguridad de Hilos):**
    *   Python (y Tkinter) no permite que dos hilos toquen la pantalla a la vez.
    *   Este módulo usa una `queue.Queue` para recibir órdenes de la UI. Las colas en Python son "Thread Safe" (seguras) por diseño.

2.  **Bucle de Ejecución (`run`)**
    *   Es un `while True` que hace dos cosas muy rápido:
        1.  **Tx (Transmitir):** Mira si hay algo en la cola. Si hay, lo envía por Serial.
        2.  **Rx (Recibir):** Mira si hay bytes en el buffer Serial. Si hay, busca el byte `0xFE` (Sync) y trata de reconstruir un mensaje.

#### Métodos Clave
*   **`send_frame(bytes)`**: No envía nada. Solo pone el mensaje en la cola ("Buzón"). El hilo lo recogerá milisegundos después.
*   **`set_callback(func)`**: Permite a la UI decirle: *"Cuando recibas un mensaje válido, llama a esta función"*.

## Dependencias
*   Requiere `pyserial`.
*   Usa `ProtocolV2` para validar lo que recibe (CRC check).

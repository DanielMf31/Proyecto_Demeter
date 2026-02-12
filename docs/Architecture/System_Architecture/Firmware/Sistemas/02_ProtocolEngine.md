# ProtocolEngine (Procesador)

## Descripción
El **ProtocolEngine** es el núcleo de la lógica de comunicación del Firmware. Implementa las reglas del **Protocolo Demeter V2**, encargándose de la serialización, deserialización y despacho de comandos.

## Ubicación
*   **Header**: `C++/include/core/ProtocolEngine.h`
*   **Source**: `C++/src/core/ProtocolEngine.cpp`

## Funciones Principales

### 1. Gestión de Transporte
Recibe una estrategia de comunicación (`ICommunicationStrategy*`) en su constructor (e.g., `EspNowStrategy`, `UartStrategy` o `GatewayStrategy`). Usa esta estrategia para enviar los frames binarios.

### 2. Parsing (Deserialización)
Procesa buffers de bytes entrantes, valida:
*   Byte de Sincronismo (`0xFE`).
*   Longitud y estructura.
*   Checksum/CRC (si implementado en V2).
*   Target ID (si el mensaje es para este nodo).

### 3. Callbacks y Eventos
Expone un sistema de hooks para que la aplicación (Main) reaccione a eventos:
*   `onSetGpio(...)`: Cuando llega una orden de actuar.
*   `onPingRecv(...)`: Cuando llega un Ping.
*   `onDataReportRecv(...)`: Cuando llega un dato de sensor (útil en Gateway).

### 4. Generación de Mensajes (Serialización)
Métodos helper para construir y enviar tramas:
*   `sendPing(uint8_t target)`
*   `sendTempHumReport(...)`
*   `sendPinReport(...)`
*   `sendAck(...)`

## Flujo de Trabajo
1.  `engine.update()` se llama en el bucle principal.
2.  Lee datos de la estrategia de transporte.
3.  Si hay un frame válido, invoca el callback correspondiente.
4.  Si es un PING, responde con ACK automáticamente.

# Documentación Técnica: ProtocolEngine (V2)

## 1. Visión General
El `ProtocolEngine` es el núcleo de la lógica de comunicación del sistema Demeter. Su función es **interpretar** el flujo de bytes crudos que provienen de la capa de transporte (`IComms`) y transformarlos en acciones concretas del sistema (Comandos), así como generar respuestas (ACK/NACK) hacia el controlador maestro.

Es agnóstico del medio de transporte: funciona igual sobre UART, LoRa o WiFi, siempre que se le pase una implementación válida de `IComms`.

## 2. Características Principales
*   **Validación de Integridad:** Implementa verificación CRC-8 para asegurar que los datos no se han corrompido.
*   **Sincronización:** Detecta automáticamente el inicio de tramas válidas mediante el byte de sincronización (`0xFE`).
*   **Sistema de Callbacks:** Utiliza `std::function` para notificar a las capas superiores cuando llega un comando válido, desacoplando el parseo de la ejecución.
*   **Respuestas Automáticas:** Gestiona automáticamente el handshake (ACK) para comandos como `PING`.

## 3. Estructura de la Trama (Wire Format)
| Byte | Nombre | Descripción |
| :--- | :--- | :--- |
| 0 | **SYNC** | `0xFE` - Inicio de trama. |
| 1 | **LEN** | Longitud del Payload (N). |
| 2 | **FLAGS** | Reservado para flags de control. |
| 3 | **SRC** | ID del emisor. |
| 4 | **DST** | ID del receptor (Target). |
| 5 | **CMD** | ID del Comando (ver tabla). |
| 6..N | **PAYLOAD** | Datos variables del comando. |
| N+1 | **CRC** | Suma de comprobación (Header[1:] + Payload). |

### Comandos Soportados
*   **PING (`0x01`):** Verificación de conectividad. Responde con ACK.
*   **ACK (`0x02`):** Confirmación positiva.
*   **NACK (`0x03`):** Confirmación negativa / Error.
*   **SET_GPIO (`0x10`):** Control Digital (ON/OFF) de pines.
*   **SET_PWM (`0x11`):** Control Anológico (PWM) de pines.
*   **EXEC_SEQUENCE (`0x30`):** Ejecución de secuencias preprogramadas.
    *   **Payload Estructura:**
        *   `[COUNT]` (1 Byte): Número de pasos.
        *   `[STEP_1]` ... `[STEP_N]` (8 Bytes cada uno).
        *   **Estructura del Paso (8 Bytes):**
            *   `[TGT_ID]` (1): Reservado (Target).
            *   `[CMD_ID]` (1): Reservado (Tipo de Acción).
            *   `[PIN]` (1): GPIO Pin.
            *   `[VAL]` (1): Valor (0/1).
            *   `[DELAY]` (4): Tiempo en ms (Little Endian).

## 4. Referencia de API

### Configuración (Callbacks)
Para reaccionar a los comandos, se deben registrar funciones (lambdas o punteros a función):

*   **`onSetGpio(GpioCallback cb)`**: Se invoca al recibir un comando `SET_GPIO`.
    *   Entrega un `struct SetGpioCmd { pin, value, flags }`.
*   **`onSetPwm(PwmCallback cb)`**: Se invoca al recibir un comando `SET_PWM`.
    *   Entrega un `struct SetPwmCmd { pin, value }`.
*   **`onExecSequence(SequenceCallback cb)`**: Se invoca al recibir `EXEC_SEQUENCE`.

### Ciclo de Vida
*   **`void update()`**: Debe llamarse periódicamente en el `loop()` principal. Lee datos del transporte, busca tramas completas y despacha los callbacks.

### Métodos Internos (Output)
*   **`sendAck(uint8_t targetId)`**: Envía una trama ACK al ID especificado.
*   **`sendFrame(...)`**: Construye y envía una trama binaria calculando el CRC automáticamente.

## 5. Ejemplo de Flujo
1.  **Transporte** recibe bytes `[FE 03 00 0A 01 10 04 01 00 23]`.
2.  **ProtocolEngine::update()** lee los bytes.
3.  **ProtocolEngine** detecta `SYNC`, valida `LEN` y calcula `CRC`.
4.  Si CRC es válido, identifica `CMD = 0x10 (SET_GPIO)`.
5.  Parsea el Payload: `Pin=4`, `Val=1`.
6.  Ejecuta `_onGpioCommand({4, true, 0})`.

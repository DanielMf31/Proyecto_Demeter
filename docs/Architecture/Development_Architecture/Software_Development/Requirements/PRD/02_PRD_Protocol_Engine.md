# PRD 02: Motor de Protocolo (Protocol Engine)

## 1. Introducción
El `ProtocolEngine` es el componente encargado de interpretar los bytes crudos recibidos desde la capa de transporte (`IComms`) y convertirlos en comandos estructurados (`InternalTypes`) que el sistema pueda ejecutar. También es responsable de generar respuestas (ACK/NACK).

## 2. Requisitos Funcionales

### 2.1. Estructura de Trama (Frame)
El motor debe validar tramas con el sigiente formato:
`[SYNC 0xFE] [LEN] [FLAGS] [SRC] [DST] [CMD] [PAYLOAD...] [CRC]`

*   **SYNC:** Byte de sincronización `0xFE`.
*   **LEN:** Longitud del PAYLOAD (N bytes). Si N=0, la trama tiene 7 bytes en total.
*   **CRC:** Suma simple (Modulo 256) de todos los bytes desde `LEN` hasta el final del Payload.

### 2.2. Comandos Soportados
El motor debe ser capaz de parsear y despachar los siguientes comandos:

1.  **PING (0x01):**
    *   Payload: 0 bytes.
    *   Acción: Responder con `ACK`.

2.  **SET_GPIO (0x10):**
    *   Payload: 3 bytes (`[PIN] [VAL] [FLAGS]`).
    *   Acción: Invocar `GpioCallback`.

3.  **SET_PWM (0x11):**
    *   Payload: 3 bytes (`[PIN] [VAL_L] [VAL_H]`). (Little Endian uint16).
    *   Acción: Invocar `PwmCallback`.

4.  **EXEC_SEQUENCE (0x30):**
    *   Payload: Variable (Definido en V2).
    *   Acción: Invocar `SequenceCallback`.

### 2.3. Callbacks
La clase debe exponer métodos para registrar callbacks para cada comando soportado:
*   `onSetGpio(cb)`
*   `onSetPwm(cb)`
*   `onExecSequence(cb)`
*   `onPing(cb)` (Opcional, si el sistema requiere logica adicional).

## 3. Criterios de Validación
1.  **Descarte de Ruido:** Bytes que no empiecen con `0xFE` deben ser ignorados hasta encontrar un Sync válido.
2.  **Validación CRC:** Si el CRC calculado no coincide con el recibido, descarte silencioso (o conteo de error).
3.  **Longitud Insuficiente:** Si `available()` < Frame esperado, esperar más bytes.

## 4. Diseño Técnico (`InternalTypes.h`)
Es necesario agregar las estructuras faltantes en `InternalTypes.h`:
```cpp
struct SetPwmCmd { ... }; // Ya existe
struct ExecSequenceCmd { ... }; // Definir estructura básica si se va a implementar full
```

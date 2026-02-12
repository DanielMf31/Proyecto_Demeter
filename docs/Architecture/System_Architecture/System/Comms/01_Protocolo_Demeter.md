# Especificación de Diseño: Protocolo Demeter V2.2
**Versión del Estándar:** 2.2
**Fecha de Revisión:** 10 Febrero 2026
**Implementación de Referencia:** `C++/src/core/ProtocolEngine.cpp`

## 1. Visión General
El protocolo Demeter V2 es un estándar de comunicación binario, orientado a tramas (Frame-oriented), diseñado para redes IoT híbridas (UART, ESP-NOW, LoRa).

### Características Clave
*   **Binario Puro:** No se usa JSON ni ASCII.
*   **Endianness:** **Little Endian (<)** para todos los campos numéricos multibyte.
*   **Integridad:** Checksum CRC-8 (Suma % 256).

---

## 2. Estructura de la Trama (Frame Layers)

| Offset | Campo | Tipo | Tamaño | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `SYNC` | `uint8` | 1 Byte | **0xFE** (254). Byte mágico de inicio. |
| **1** | `LEN` | `uint8` | 1 Byte | Longitud del **PAYLOAD**. |
| **2** | `FLAGS` | `uint8` | 1 Byte | Bits de control (0x01=ACK_REQ). |
| **3** | `SRC` | `uint8` | 1 Byte | ID del nodo origen. |
| **4** | `DST` | `uint8` | 1 Byte | ID del nodo destino. |
| **5** | `CMD` | `uint8` | 1 Byte | Identificador de la Operación. |
| **6** | `PAYLOAD`| `bytes` | Variable | Datos específicos del comando. |
| **6+N**| `CRC` | `uint8` | 1 Byte | Checksum `(Sum(Bytes[1]..Bytes[End]) % 256)`. |

---

## 3. Catálogo de Comandos (Command Set)

### 3.1 Comandos de Sistema y Red

#### `CMD_PING` (0x01)
*   **Descripción:** `Keep-alive`.
*   **Payload:** 0 Bytes.

#### `CMD_ACK` (0x02)
*   **Descripción:** Confirmación positiva.
*   **Payload:** 0 Bytes.

#### `CMD_NACK` (0x03)
*   **Descripción:** Error en recepción/ejecución.
*   **Payload:** 0 Bytes (En implementación actual, v2.1 definía ErrorCode pero código envía vacío).

#### `CMD_ROUTE_ADD` (0x0A)
*   **Descripción:** Registra ruta estática (Gateway -> Nodo).
*   **Payload:** 7 Bytes.
    *   `[0]`: `Target_ID` (uint8).
    *   `[1..6]`: `MAC_Address` (6 bytes).

### 3.2 Comandos de Sensores (Telemetry)

#### `CMD_DATA_REPORT` (0x0B)
*   **Descripción:** Reporte de telemetría (Temp/Hum).
*   **Payload:** 4 Bytes.
    *   `[0..1]`: `Temperature` (int16 LE) - Escalado x100 (ej. 2550 = 25.50°C).
    *   `[2..3]`: `Humidity` (int16 LE) - Escalado x100.

#### `CMD_GET_SENSORS` (0x20)
*   **Descripción:** Solicita un `CMD_DATA_REPORT` inmediato.
*   **Payload:** 0 Bytes.

### 3.3 Comandos de Actuación

#### `CMD_SET_GPIO` (0x10)
*   **Descripción:** Control digital.
*   **Payload:** 3 Bytes.
    *   `[0]`: `PIN` (uint8).
    *   `[1]`: `VAL` (uint8) - (1=HIGH, 0=LOW).
    *   `[2]`: `FLAGS` (uint8) - Opcional.

#### `CMD_SET_PWM` (0x11)
*   **Descripción:** Control analógico (PWM).
*   **Payload:** 3 Bytes.
    *   `[0]`: `PIN` (uint8).
    *   `[1..2]`: `VALUE` (uint16 LE) - Duty Cycle.

### 3.4 Comandos de Secuencia

#### `CMD_EXEC_SEQUENCE` (0x30)
*   **Descripción:** Ejecuta una lista de pasos temporizados.
*   **Payload:** `1 + (N * 8)` bytes.
    *   `[0]`: `COUNT` (uint8) - Número de pasos.
    *   `[1..8]`: **Paso 1**.
    
**Estructura de Paso (8 Bytes):**
*   `[0]`: `RESERVED` (Ignorado en V2.2 implementation).
*   `[1]`: `RESERVED` (Ignorado en V2.2 implementation).
*   `[2]`: `PIN` (uint8).
*   `[3]`: `VAL` (uint8).
*   `[4..7]`: `DELAY` (uint32 LE) - Tiempo a esperar **después** del paso (ms).

# Especificación de Diseño: Protocolo Demeter V2
**Versión del Estándar:** 2.1
**Fecha de Revisión:** 31 Enero 2026
**Implementación de Referencia:** `proyecto_demeter.protocols.protocol_v2.DemeterProtocolV2`

## 1. Visión General
El protocolo Demeter V2 es un estándar de comunicación binario, orientado a tramas (Frame-oriented), diseñado para redes IoT híbridas (UART, ESP-NOW, LoRa). Prioriza la eficiencia en el uso del ancho de banda y la integridad de los datos sobre la legibilidad humana.

### Características Clave
*   **Binario Puro:** No se usa JSON ni ASCII para la transmisión.
*   **Endianness:** **Little Endian (<)** para todos los campos numéricos multibyte.
*   **Alineación:** Packed (1 byte alignment). Sin padding.
*   **Integridad:** Checksum CRC-8 simple (Suma % 256) en esta versión MVP.

---

## 2. Estructura de la Trama (Frame Layers)

Cada mensaje enviado o recibido en la red debe cumplir rigurosamente con este formato.

| Offset | Campo | Tipo | Tamaño | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `SYNC` | `uint8` | 1 Byte | **0xFE** (254). Byte mágico de inicio. |
| **1** | `LEN` | `uint8` | 1 Byte | Longitud del **PAYLOAD** (0 - 255). No cuenta Header ni CRC. |
| **2** | `FLAGS` | `uint8` | 1 Byte | Bits de control (Ver 2.1). |
| **3** | `SRC` | `uint8` | 1 Byte | ID del nodo origen (0=Master, 1=Gateway). |
| **4** | `DST` | `uint8` | 1 Byte | ID del nodo destino. |
| **5** | `CMD` | `uint8` | 1 Byte | Identificador de la Operación (Ver 3.0). |
| **6** | `PAYLOAD`| `bytes` | Variable | Datos específicos del comando. |
| **6+N**| `CRC` | `uint8` | 1 Byte | Checksum de validación. |

### 2.1 Flags (Bits de Control)
*   **Bit 0 (0x01):** `ACK_REQ` - Si es 1, el receptor debe responder con un `CMD_ACK` o `CMD_NACK`.
*   **Bit 1 (0x02):** `RESERVED` - Uso futuro (ej. Mensaje Encriptado).
*   **Bit 2-7:** Reservados.

### 2.2 Algoritmo CRC
El CRC se calcula sobre el rango `[LEN ... Ultimo Byte de Payload]`.
**NO** se incluye el byte `SYNC` en el cálculo.
*Fórmula:* `CRC = Sum(Bytes[1] hasta Bytes[End]) % 256`

---

## 3. Catálogo de Comandos (Command Set)

### 3.1 Comandos de Sistema (0x00 - 0x0F)

#### `CMD_PING` (0x01)
*   **Descripción:** Verifica si un nodo está vivo y alcanzable.
*   **Payload:** 0 Bytes.
*   **Respuesta Esperada:** `CMD_ACK`.

#### `CMD_ACK` (0x02)
*   **Descripción:** Confirmación positiva de operación.
*   **Payload:** 0 Bytes.

#### `CMD_NACK` (0x03)
*   **Descripción:** Error en la recepción o ejecución.
*   **Payload:** 1 Byte (`ErrorCode`).
    *   `0x01`: CRC Error.
    *   `0x02`: Comando Desconocido.
    *   `0x03`: Recurso Ocupado.

#### `CMD_ROUTE_ADD` (0x0A)
*   **Descripción:** Enseña al Gateway una ruta MAC estática.
*   **Payload:** 7 Bytes.
    *   `[0]`: `Target_Node_ID` (uint8).
    *   `[1..6]`: `MAC_Address` (6 bytes).
*   **Uso:** Al arrancar el sistema Python, envía esto al Gateway para cada nodo del `inventory.json`.

---

### 3.2 Comandos de Actuación (0x10 - 0x1F)

#### `CMD_SET_GPIO` (0x10)
*   **Descripción:** Cambia el estado digital de un pin.
*   **Payload:** 3 Bytes.
    *   `[0]`: `PIN` (uint8) - Número de GPIO físico.
    *   `[1]`: `CTX` (uint8) - Valor (1=HIGH, 0=LOW).
    *   `[2]`: `FLAGS` (uint8) - (0=Normal, 1=Invertir lógica, etc).

#### `CMD_SET_PWM` (0x11)
*   **Descripción:** Establece un valor analógico (PWM) para motores o luces.
*   **Payload:** 3 Bytes.
    *   `[0]`: `PIN` (uint8).
    *   `[1..2]`: `VALUE` (uint16 LE) - Duty Cycle (0-65535).

---

### 3.3 Comandos de Flujo (0x30 - 0x3F)

#### `CMD_EXEC_SEQUENCE` (0x30)
*   **Descripción:** Ejecuta una lista de pasos cronometrados en el nodo destino. Permite automatización sin intervención constante del Master.
*   **Payload:** Variable (`1 + (N * 8)` bytes).
    *   `[0]`: `COUNT` (uint8) - Número de pasos.
    *   `[1..8]`: **Paso 1** (Ver Estructura de Paso).
    *   `[9..16]`: **Paso 2**...
    
**Estructura de un Paso (Sequence Step - 8 Bytes):**
*   `[0]`: `TARGET_ID` (uint8) - A quién va dirigido (útil si el Gateway orquesta a varios).
*   `[1]`: `CMD` (uint8) - Sub-comando (ej. `0x10` para GPIO).
*   `[2]`: `PIN` (uint8).
*   `[3]`: `VAL` (uint8).
*   `[4..7]`: `DELAY` (uint32 LE) - Tiempo a esperar **después** de ejecutar, en milisegundos.

---

## 4. Ejemplos de Tramas (Forensics)

### Ejemplo 1: Encender "Bomba Norte" (ID 10, Pin 4)
*   **Intención:** Master (0) -> Nodo (10). CMD 0x10. Pin 4. HIGH.
*   **Trama Hex:**
    ```
    FE 03 01 00 0A 10 04 01 00 23
    ```
    *   `FE`: Sync
    *   `03`: Len Payload (3 bytes)
    *   `01`: Flags (ACK Req)
    *   `00`: Src (Master)
    *   `0A`: Dst (10)
    *   `10`: Cmd (Set GPIO)
    *   `04 01 00`: Payload (Pin 4, Val 1, Flags 0)
    *   `23`: CRC (Calculado sobre `03 01 00 0A 10 04 01 00`)

### Ejemplo 2: Registrar Ruta en Gateway
*   **Intención:** Master (0) -> Gateway (1). ID 10 tiene MAC `AA:BB:CC:DD:EE:FF`.
*   **Trama Hex:**
    ```
    FE 07 01 00 01 0A 0A AA BB CC DD EE FF CRC
    ```
    *   `0A`: Cmd Route Add
    *   `0A`: Target ID (10)
    *   `AA..FF`: MAC Address

---

## 5. Notas para Desarrolladores

1.  **Validación de Entrada:**
    *   Cualquier trama que no empiece por `0xFE` debe ser descartada hasta encontrar el siguiente `0xFE`.
    *   Si el CRC no coincide, **JAMÁS** ejecutar la acción. Responder `NACK_CRC`.
    
2.  **Buffers:**
    *   El tamaño máximo de trama teórica es ~262 bytes. Se recomienda un buffer de recepción de al menos **300 bytes**.

3.  **Timeouts:**
    *   En UART: Timeout de byte a byte recomendado: 10ms.
    *   En Transacción: Esperar respuesta (ACK) máximo 200ms por UART, 2000ms por LoRa.

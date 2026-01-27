# Estándar de Comunicación: Protocolo Demeter V2

**Versión:** 2.1 (Final)
**Tipo:** Binario / Endianness Little-Endian
**Soporte:** UART, LoRa, ESP-NOW

## 1. Estructura de Trama (Frame Anatomy)

Todos los mensajes, sin excepción, siguen esta estructura estricta. El tamaño mínimo de un paquete válido es de **7 Bytes** (Header + CRC).

| Offset | Byte | Nombre | Descripción |
| :--- | :--- | :--- | :--- |
| 0 | `0xFE` | **SYNC** | Byte de Sincronización. Inicio de Trama. |
| 1 | `0xNN` | **LEN** | Longitud del **Payload** (Datos). No incluye Header. |
| 2 | `0xNN` | **FLAGS** | `Bit 0`: ACK_REQ (1=Responder, 0=Fuego y Olvida). |
| 3 | `0xNN` | **SRC** | ID del Emisor. `0`=Master, `1`=Gateway. |
| 4 | `0xNN` | **DST** | ID del Receptor. `10-254`=Nodos. |
| 5 | `0xNN` | **CMD** | ID del Comando (Ver Sección 2). |
| 6...N | `...` | **DATA** | Payload variable (0 a 240 bytes). |
| N+1 | `CRC` | **CRC** | Checksum simple `(Sum(Bytes 1..N) % 256)`. |

---

## 2. Catálogo de Comandos (Command Set)

### 2.1 Control del Sistema (0x00 - 0x0F)
| Hex | Nombre | Payload | Uso |
| :--- | :--- | :--- | :--- |
| **0x01** | `PING` | 0 Bytes | Verificar conexión. |
| **0x02** | `ACK` | 0 Bytes | Confirmación positiva ("Recibido OK"). |
| **0x03** | `NACK` | 1 Byte (ErrCode) | Error ("CRC incorrecto", "Cola llena"). |
| **0x0A** | `ROUTE_ADD`| 7 Bytes `[ID][MAC(6)]` | Enseñar una ruta MAC al Gateway. |

### 2.2 Actuación (0x10 - 0x1F)
| Hex | Nombre | Payload | Uso |
| :--- | :--- | :--- | :--- |
| **0x10** | `SET_GPIO` | 3 Bytes `[PIN][VAL][FLAGS]` | Activar Relé/LED. |
| **0x11** | `SET_PWM` | 3 Bytes `[PIN][VAL_L][VAL_H]` | Motor/Luz regulable (0-65535). |

### 2.3 Sensores (0x20 - 0x2F)
| Hex | Nombre | Payload | Uso |
| :--- | :--- | :--- | :--- |
| **0x20** | `GET_SENSORS` | 0 Bytes | Pedir estado completo. |
| **0x22** | `REPORT_BATCH`| Variable | Respuesta masiva comprimida. |

### 2.4 Secuencias (0x30 - 0x3F)
| Hex | Nombre | Payload | Uso |
| :--- | :--- | :--- | :--- |
| **0x30** | `EXEC_SEQ` | `[Count] + [Steps...]` | Ejecutar lista de tareas con retardos. |

---

## 3. Ejemplos de Flujo (Byte-Level Trace)

### Caso 1: Encender Luz (ID 10, Pin 4)
*   **Intención:** Master pide a Nodo 10 poner GPIO 4 en HIGH.
*   **Header:**
    *   `FE`: Sync
    *   `03`: Len (3 bytes de payload: Pin+Val+Flag)
    *   `01`: Flags (Pide ACK)
    *   `00`: Src (Master)
    *   `0A`: Dst (10)
    *   `10`: Cmd (Set GPIO)
*   **Payload:**
    *   `04`: Pin 4
    *   `01`: Val 1 (High)
    *   `00`: Flags extra
*   **CRC:** `03+01+00+0A+10 + 04+01+00 = 0x23`
*   **Trama Final:** `FE 03 01 00 0A 10 04 01 00 23`

### Caso 2: Riego Secuencial (Batch)
*   **Intención:** Encender Bomba (ID 15) 5 seg, luego esperar.
*   **Cmd:** `EXEC_SEQ (0x30)`
*   **Payload:**
    *   `01`: Count (1 paso)
    *   **Paso 1:**
        *   `0F`: ID 15
        *   `10`: Cmd Set GPIO
        *   `04`: Pin 4
        *   `01`: Val 1
        *   `88 13 00 00`: Delay 5000ms (Little Endian)
*   **Trama Final:** `FE 09 01 00 01 30  01 0F 10 04 01 88 13 00 00  CRC`

---

## 4. Notas de Implementación

1.  **Endianness:** Todo es **Little Endian**.
    *   Correcto: `5000` -> `0x88 0x13`.
    *   Incorrecto: `5000` -> `0x13 0x88`.
2.  **Alineación:** No hay `padding` entre bytes. En C++, usar `#pragma pack(1)`.
3.  **Timeouts:** El Master debe esperar 500ms por un ACK antes de reintentar. Máximo 3 intentos.

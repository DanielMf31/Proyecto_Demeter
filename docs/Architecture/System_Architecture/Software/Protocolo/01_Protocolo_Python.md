# Protocolo y Transporte

## 1. Transporte (`async_uart.py`)
Maneja la capa física de comunicación serie.
*   Usa `pyserial-asyncio`.
*   Lee bytes en chunks y los pasa al buffer del `async_service` para su reconstrucción.

## 2. Protocolo Demeter V2 (`protocol_v2.py`)
Implementación de la lógica binaria de comunicación.

### Estructura de Trama
`[SYNC(0xFE)] [LEN] [FLAGS] [SRC] [DST] [CMD_ID] [...PAYLOAD...] [CRC]`

### Comandos Soportados (Python)
Definidos en `protocol_schemas.py` usando Pydantic para validación interna y `struct` para serialización binaria.

*   **Control**: `PING`, `ACK`, `NACK`.
*   **Actuación**: `SET_GPIO`, `SET_PWM`.
*   **Secuencias**: `EXEC_SEQUENCE` (Lista de pasos temporizados).
*   **Reportes**: `TEMP_HUM_REPORT`, `PIN_REPORT`, `SYSTEM_REPORT`.

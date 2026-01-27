# Documentación del Módulo: `protocol_v2.py`

**Ubicación:** `Python/src/core/protocol_v2.py`

## Propósito
Este archivo es la **definición oficial** del protocolo binario Demeter V2 en Python. Su única responsabilidad es convertir datos de alto nivel (números, listas) en cadenas de bytes (`bytes`) listas para enviar, y viceversa.

## Clases Principales

### `class DemeterProtocolV2`

#### Constantes (Command IDs)
Define el diccionario de operaciones permitidas.
*   `CMD_SET_GPIO (0x10)`: Actuación digital.
*   `CMD_EXEC_SEQUENCE (0x30)`: Ejecución de listas de tareas.

#### Métodos Clave

1.  **`create_set_gpio(target_id, pin, value) -> bytes`**
    *   **Input:** ID del nodo (ej. 10), Pin (ej. 4), Valor (1/0).
    *   **Proceso:** Empaqueta usando `struct.pack('<BBB', ...)` para asegurar Little Endian. Añade Header y CRC.
    *   **Output:** Trama completa (ej. `b'\xFE\x05...'`).

2.  **`create_sequence(steps) -> bytes`**
    *   **Complejidad:** Alta.
    *   **Proceso:** Itera una lista de diccionarios. Por cada paso, genera un sub-bloque de 8 bytes. Concadena todos los pasos y los mete en el Payload.
    *   **Uso:** Permite enviar programas complejos de una sola vez.

3.  **`_calculate_crc(data) -> int`**
    *   Implementa la validación de integridad. Actualmente suma simple `% 256` (Checksum), fácil de depurar.

## Conceptos Clave
*   **Struct Packing:** Uso de la librería `struct` para garantizar que un entero de 4 bytes en Python (`int`) se convierta exactamente en 4 bytes en C++ (`uint32_t`).
*   **Stateless:** Esta clase no guarda estado (salvo un contador de secuencia opcional). No sabe si el puerto está abierto o cerrado.

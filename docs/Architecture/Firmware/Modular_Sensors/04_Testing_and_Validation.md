# Pruebas y Validación: Sistema de Sensores Modulares

Este documento detalla la estrategia de pruebas implementada para verificar la nueva arquitectura modular de sensores, incluyendo pruebas unitarias de los drivers y pruebas de integración del nodo completo.

## 1. Estrategia de Pruebas

Se ha optado por un enfoque **Hybrid Mock/Real**, donde el mismo código de producción puede ejecutarse en dos modos:
1.  **Modo Real:** Interactúa con el hardware físico (ESP32, GPIO, UART).
2.  **Modo Mock:** Simula el hardware, generando datos predecibles para validación algorítmica.

Esto permite ejecutar pruebas unitarias (`unittest`) en el entorno `native` (PC local) sin necesidad de flashear un microcontrolador cada vez.

### Entorno de Pruebas
*   **Framework:** Unity (integrado en PlatformIO).
*   **Entorno:** `env:native` (Linux/Windows).
*   **Archivo de Test:** `C++/test/test_modular_sensors/test_modular_sensors.cpp`.

## 2. Pruebas Unitarias Implementadas

### 2.1 Sensor DHT22 (Mock)
*   **Objetivo:** Verificar inicialización y rango de lecturas simuladas.
*   **Comportamiento Mock:**
    *   Temperatura: Onda senoidal base 25°C ± 5°C.
    *   Humedad: Onda cosenoidal base 50% ± 10%.
*   **Validación:**
    ```cpp
    TEST_ASSERT_FLOAT_WITHIN(3.0f, 25.0f, data.value1); // Temp ~ 25
    TEST_ASSERT_FLOAT_WITHIN(6.0f, 50.0f, data.value2); // Hum ~ 50
    ```

### 2.2 Sensor DS18B20 (Mock)
*   **Objetivo:** Verificar lectura de temperatura aislada.
*   **Comportamiento Mock:**
    *   Temperatura: Aleatorio entre 18°C y 22°C.
    *   Humedad: Siempre 0.
*   **Validación:**
    ```cpp
    TEST_ASSERT_FLOAT_WITHIN(3.0f, 20.0f, data.value1);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, data.value2);
    ```

### 2.3 Sensor Humedad Suelo Capacitivo (Mock)
*   **Objetivo:** Verificar mapeo porcentual.
*   **Comportamiento Mock:**
    *   Humedad: Aleatorio 0-100%.
*   **Validación:**
    ```cpp
    TEST_ASSERT_GREATER_OR_EQUAL(0.0f, data.value1);
    TEST_ASSERT_LESS_OR_EQUAL(100.0f, data.value1);
    ```

## 3. Pruebas de Integración (Nodo -> Protocolo)

Verifica que el `Node` orqueste correctamente la lectura de sensores y la transmisión de datos a través del `ProtocolEngine`.

### Flujo de Prueba
1.  Se instancia un `Node` con ID 2.
2.  Se registra un `DHTSensor` (Mock).
3.  Se inyecta una estrategia de comunicación simulada (`MockComms`) al motor de protocolo.
4.  Se dispara la transmisión de un reporte de datos (`DATA_REPORT`).
5.  Se captura la trama binaria resultante en `MockComms` y se decodifica.

### Validación de Trama (Ejemplo)

Para una lectura simulada de **25.5°C** y **60.2% HR**:

*   **Valores RAW (Int16 x100):**
    *   Temp: `2550` -> `0x09F6`
    *   Hum: `6020` -> `0x1784`
*   **Trama Generada (Little Endian):**
    ```
    [SYNC] [LEN] [FLAGS] [SRC] [DST] [CMD] [PL_0] [PL_1] [PL_2] [PL_3] [CRC]
     FE     04    00      01    01    14    F6     09     84     17     XX
    ```
    *   `CMD 0x14`: `DATA_REPORT`
    *   `PL_0, PL_1`: `F6 09` -> `0x09F6` -> 2550 -> **25.50**
    *   `PL_2, PL_3`: `84 17` -> `0x1784` -> 6020 -> **60.20**

Esta prueba asegura que no solo el sensor funciona, sino que el dato llega íntegro y en el formato correcto hasta la capa de transporte, listo para ser enviado por ESP-NOW o LoRa.

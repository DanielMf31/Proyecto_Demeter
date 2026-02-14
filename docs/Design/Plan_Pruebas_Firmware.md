# Plan de Pruebas de Firmware - Proyecto Demeter

Este documento define la estrategia de pruebas para el firmware de los nodos (Sensor, Actuador, Gateway) del proyecto Demeter. El objetivo es asegurar la fiabilidad, robustez y mantenibilidad del código mediante pruebas escalonadas.

## 1. Niveles de Pruebas

Seguiremos una pirámide de pruebas estándar adaptada a sistemas embebidos:

1.  **Unitarias (Native):** Pruebas de lógica pura en PC (Host). Simulan hardware y comunicación. Son rápidas y aisladas.
2.  **Integración (Hardware/HIL):** Pruebas en hardware real (ESP32) pero controladas (ej. inyección de mensajes de prueba).
3.  **Sistema (End-to-End):** Pruebas del flujo completo (Sensor -> Gateway -> Backend/Actuador) en escenario real.

---

## 2. Estrategia por Componente

### 2.1. Librerías Core (`src/core`)

Estas librerías son compartidas y críticas. Deben tener **100% de cobertura lógica** en pruebas unitarias.

| Componente | Qué Testear | Método |
| :--- | :--- | :--- |
| **ProtocolEngine** | - Parsing correcto de tramas (Header, CRC, Payload).<br>- Rechazo de CRCs inválidos.<br>- Dispatch a callbacks correctos (`onSetGpio`, etc.).<br>- Generación de tramas (serialización). | **Unitario (Native)**<br>Crear mocks de `IComms` para inyectar bytes y verificar salidas. |
| **SystemContext** | - Inicialización de subsistemas.<br>- Gestión de errores globales. | **Unitario/Integración** |

### 2.2. Nodo Sensor (`Node_Sensor`)

Responsable de leer datos y enviarlos periódicamente o bajo demanda.

| Prueba | Descripción | Verificación |
| :--- | :--- | :--- |
| **Inicialización** | Verificar que `begin()` configures los sensores y callbacks del Engine. | Unitario (Mock Engine) |
| **Lectura de Sensores** | Simular lectura de datos (Temp/Hum/Humedad Suelo). | Unitario (Mock SensorManager) |
| **Reporte Periódico** | Verificar que tras `REPORT_INTERVAL` se envía un mensaje `TEMP_HUM_REPORT`. | Unitario (Mock Time & Comms) |
| **Deep Sleep** | Verificar que el nodo entra en suspensión tras reportar (si está habilitado). | Revisión de Código / Log Serial en HW |
| **Comando GET_SENSORS** | Enviar comando `GET_SENSORS` y verificar respuesta inmediata. | Integración (Gateway -> Sensor) |

### 2.3. Nodo Actuador (`Node_Actuador`)

Responsable de ejecutar acciones físicas (relés, motores) y dar feedback.

| Prueba | Descripción | Verificación |
| :--- | :--- | :--- |
| **Recepción SET_GPIO** | Enviar trama `SET_GPIO` válida. Verificar cambio de estado en Pin. | **Unitario (Mock GPIO)** & Integración |
| **Feedback (ACK)** | Verificar que tras ejecutar, envía `PIN_REPORT` o `ACK` al origen. | Unitario (Mock Comms) |
| **Timeouts/Seguridad** | (Futuro) Si se activa un motor, ¿se apaga solo tras X tiempo si se pierde conexión? | Unitario |
| **Indicación Visual** | Verificar LED RGB (Azul=Rx, Verde=High, Rojo=Low). | **Manual (Visual)** |
| **Filtrado de IDs** | Enviar mensaje destinado a Otro ID. Verificar que LO IGNORA. | Unitario |

### 2.4. Nodo Gateway (`Node_Gateway`)

Puente entre la red ESP-NOW y el mundo exterior (UART/WiFi/LoRa).

| Prueba | Descripción | Verificación |
| :--- | :--- | :--- |
| **Enrutamiento** | Verificar tabla de rutas (ID <-> MAC). `registerRoute`. | Unitario |
| **Bridge UART -> ESP-NOW** | Inyectar bytes por UART simulada, verificar envío ESP-NOW. | Integración |
| **Bridge ESP-NOW -> UART** | Inyectar trama ESP-NOW, verificar salida UART (formato correcto). | Integración |
| **Modos de Operación** | Verificar cambio entre IDLE, LISTEN, y RELAY mediante comandos Seriales. | Sistema (Manual) |

---

## 3. Buenas Prácticas de Implementación

### 3.1. Inyección de Dependencias (DI)
Para hacer el código testearble, **NUNCA** instancies clases de hardware (`GpioController`, `SensorManager`) directamente en el constructor de la clase lógica (`Node_XX`) usando `new`.
*   **Mal:** `Node_Sensor() { _sensor = new DHTSensor(); }` -> Imposible testear sin sensor real.
*   **Bien:** `Node_Sensor(ISensor* sensor)` -> Permite pasar un `MockSensor` en los tests.

### 3.2. Mocks vs Fakes
*   Usa **Mocks** (clases simuladas) en `test/mocks/` para aislar la lógica.
*   Ejemplo: `MockGpioController` guarda el estado del pin en un `map<int, bool>` en lugar de escribir en registros físicos.

### 3.3. Entornos de PlatformIO (`platformio.ini`)
*   `[env:native]`: Para tests lógicos rápidos en PC. Usa flag `-D NATIVE_ENV`.
*   `[env:sensor]`, `[env:actuador]`: Para compilación real.
*   `[env:sensor_node_3]`: Entornos de "Disfrace" para debuggear hardware cruzado.

### 3.4. Continuous Integration
Ejecutar `pio test -e native` antes de cada commit importante. Si los tests nativos fallan, **NO SUBIR** código.

---

## 4. Plan de Ejecución Inmediata

1.  **Refactorizar Nodos:** Ya iniciado. Asegurar que `Node_Sensor` y `Node_Gateway` también usen DI como se hizo con `Node_Actuador`.
2.  **Completar Tests Nativos:**
    *   `test_native_actuator`: Cubrir SetGPIO, Feedback, Ignorar Mensajes Ajenos.
    *   `test_native_sensor`: Cubrir Reporte Periódico (simulando tiempo).
    *   `test_native_engine`: Cubrir todos los comandos (Ping, Ack, Sequence).
3.  **Validación en Hardware:**
    *   Usar el modo "Spam" del Gateway ('t' command) para validar recepción física en Actuador.
    *   Validar rango y estabilidad de ESP-NOW.

---
**Autor:** Antigravity (IA Assistant) & Daniel
**Fecha:** 12/02/2026

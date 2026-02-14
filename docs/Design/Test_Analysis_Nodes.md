# Análisis Detallado de Pruebas: Nodos (Lógica de Aplicación)

**Archivos Analizados:** `src/core/Node_Sensor.cpp`, `src/core/Node_Actuator.cpp`, `src/core/Node_Gateway.cpp`
**Responsabilidad:** Lógica de negocio, orquestación de hardware, máquinas de estado y temporización.

## 1. Análisis de Riesgos

La capa de "Nodo" une el Protocolo con el Hardware.
*   **Bloqueos:** Bucles infinitos esperando hardware (ej. sensor desconectado).
*   **Fugas de Memoria:** Creación/Destrucción incorrecta de objetos (`SystemContext`, `SensorManager`) en el ciclo de vida.
*   **Timing:** Reportes que no se envían a tiempo o problemas con el Sleep Mode.
*   **Estado Inconsistente:** Actuadores que quedan encendidos tras perder conexión.

---

## 2. Recomendación de Pruebas (Test Suite)

Se recomienda implementar los siguientes tests unitarios en el entorno `native` (`test/test_native_nodes/`).

### Componente: Node_Sensor

| ID | Nombre del Test | Descripción Detallada | Por qué es necesario |
| :--- | :--- | :--- | :--- |
| **NS01** | `test_init_registers_callbacks` | Verificar que al llamar `begin()`, el nodo se suscribe a `onGetSensorsRecv` en el `ProtocolEngine`. | Sin esto, el nodo es "sordo" a peticiones manuales. |
| **NS02** | `test_periodic_report_trigger` | Configurar intervalo a 100ms. Simular avance de tiempo (mock millis). Verificar llamada a `engine->sendTempHumReport`. | Es la función core del sensor. Debe ser puntual. |
| **NS03** | `test_manual_read_request` | Simular recepción de `GET_SENSORS`. Verificar envío inmediato de datos sin esperar al timer. | Validad la interactividad bajo demanda. |
| **NS04** | `test_sensor_read_failure` | Simular que `SensorManager` devuelve lista vacía o error. Verificar que NO se envían tramas basura. | Robustez ante fallos de hardware (cable suelto). |

### Componente: Node_Actuator

| ID | Nombre del Test | Descripción Detallada | Por qué es necesario |
| :--- | :--- | :--- | :--- |
| **NA01** | `test_gpio_command_execution` | Inyectar comando `SET_GPIO(PIN=4, VAL=1)`. Verificar que `mockGpio->digitalRead(4) == 1`. | Valida que la orden lógica se convierte en señal eléctrica. |
| **NA02** | `test_feedback_generation` | Tras ejecutar el comando anterior, verificar que el nodo envía automáticamente un `PIN_REPORT` de vuelta. | El usuario necesita saber si la luz realmente se encendió. |
| **NA03** | `test_invalid_pin_protection` | Intentar actuar sobre un Pin reservado o inexistente (si aplica lógica de validación). | Seguridad del dispositivo. |
| **NA04** | `test_state_recovery` | (Futuro) Verificar comportamiento tras reinicio. ¿Recupera estado anterior o inicia apagado? | Definición de comportamiento seguro. |

### Componente: Node_Gateway

| ID | Nombre del Test | Descripción Detallada | Por qué es necesario |
| :--- | :--- | :--- | :--- |
| **NG01** | `test_route_registration` | Simular comando `ROUTE_ADD`. Verificar que la MAC se guarda en la tabla interna del `EspNowStrategy` (o su mock). | Sin rutas, el Gateway no sabe a dónde enviar los ACKs. |
| **NG02** | `test_uart_to_espnow_bridge` | Inyectar bytes por Serial (Mock). Verificar que se empaquetan y salen por `EspNow`. | Funcionalidad principal del Gateway como puente. |
| **NG03** | `test_mode_switching` | Cambiar modo a `MODE_IDLE`. Verificar que tramas entrantes NO se imprimen por Serial. | Control de flujo y depuración. |

---

## 3. Técnicas de Testing Recomendadas

### 3.1. Dependency Injection (DI)
Como vimos en `Node_Actuator`, la clave es **inyectar los controladores**.
*   **Sensor:** Inyectar `MockSensorManager` que devuelva valores fijos (`25.0C`).
*   **Actuador:** Inyectar `MockGpioController` que registre escrituras en un mapa.
*   **Gateway:** Inyectar `MockSerial` y `MockEspNow`.

### 3.2. Mocking de Tiempo
Para probar `NS02` (Periodicidad), no uses `delay()`. Crea una interfaz `ITimeProvider` o, en tests nativos, sobreescribe `millis()` mediante weak linkage o defines, para "avanzar el reloj".
*   `mock_millis_set(1000); node.update(); // Debe enviar`
*   `mock_millis_set(1050); node.update(); // No debe enviar`

### 3.3. Verificación de Estado
No solo verifiques la salida. Verifica el estado interno si es posible (ej. `_lastReportTime` cambió) o los efectos secundarios en los Mocks.

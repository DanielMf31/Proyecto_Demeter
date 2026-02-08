# Documentación Técnica: UartStrategy

## 1. Visión General
`UartStrategy` es la implementación concreta de la interfaz `IComms` para la comunicación serie (UART) en el ESP32. Su propósito principal es abstraer el hardware subyacente (`HardwareSerial` en Arduino/ESP32) permitiendo que el resto del sistema envíe y reciba bytes sin conocer los detalles físicos.

Esta clase sigue el patrón de diseño **Strategy**, permitiendo cambiar el medio de comunicación (por ejemplo a LoRa o ESP-NOW) sin modificar la lógica del negocio.

## 2. Características Principales
*   **Abstracción de Hardware:** Oculta la complejidad de `HardwareSerial`.
*   **Inyección de Dependencias:** Recibe los pines RX/TX y el BaudRate en el constructor, permitiendo configuración dinámica y facilitando el testing.
*   **Mockeable:** Gracias a la interfaz `IComms`, se puede sustituir por un `MockComms` en los tests unitarios nativos.
*   **Bufferización:** Implementa lectura de bloques de bytes un `std::vector` para facilitar el procesamiento.

## 3. Referencia de API

### Constructor
```cpp
UartStrategy(HardwareSerial* serial, uint32_t baudRate, int8_t rxPin, int8_t txPin);
```
*   **serial:** Puntero a la instancia de `HardwareSerial` (ej. `&Serial2`).
*   **baudRate:** Velocidad de comunicación (ej. `115200`).
*   **rxPin:** Pin GPIO para recepción (RX).
*   **txPin:** Pin GPIO para transmisión (TX).

### Métodos (Implementación IComms)

#### `void begin()`
Inicializa el puerto serie con la configuración proporcionada.
*   En ESP32: Llama internamente a `_serial->begin(_baudRate, SERIAL_8N1, _rxPin, _txPin)`.
*   En Native/Test: Simula la inicialización.

#### `void send(const uint8_t* data, size_t length)`
Envía un array de bytes por el puerto serie.
*   **data:** Puntero a los datos.
*   **length:** Cantidad de bytes a enviar.

#### `bool available()`
Verifica si hay datos esperando en el buffer de recepción del hardware.
*   **Retorna:** `true` si hay bytes disponibles, `false` en caso contrario.

#### `std::vector<uint8_t> read()`
Lee **todos** los bytes disponibles actualmente en el buffer y los devuelve en un vector.
*   **Retorna:** `std::vector<uint8_t>` con los datos leídos. Si no hay datos, retorna un vector vacío.

## 4. Ejemplo de Uso
```cpp
#include "communications/UartStrategy.h"

// Instanciación (ESP32)
UartStrategy uart(&Serial2, 115200, 16, 17);

void setup() {
    uart.begin(); // Configura pines 16(RX) y 17(TX) a 115200 baudios
}

void loop() {
    if (uart.available()) {
        auto data = uart.read();
        // Procesar data...
    }
}
```

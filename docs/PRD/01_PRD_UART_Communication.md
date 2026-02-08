# PRD 01: Módulo de Comunicación UART

## 1. Introducción
Este módulo es responsable de la transmisión y recepción de datos a través del puerto serie hardware del ESP32. Debe implementar la interfaz común `IComms`.

## 2. Requisitos Funcionales

### 2.1. Interfaz IComms
La clase concreta `UartStrategy` debe heredar de `IComms` y cumplir su contrato:
*   `void begin()`: Inicialización del hardware.
*   `void send(data, len)`: Envío de bytes.
*   `bool available()`: Verificación de datos entrantes.
*   `vector<uint8_t> read()`: Lectura de datos.

### 2.2. Configuración de Hardware
A diferencia de la implementación anterior, `UartStrategy` debe ser **autónoma** en su configuración.
*   **Pines:** Debe recibir los pines `RX` y `TX` en su constructor.
*   **BaudRate:** Debe recibir la velocidad en su constructor.
*   **Inicialización:** El método `begin()` debe llamar a `SerialX.begin(baud, config, rx, tx)` internamente. No se permite configuración externa en el `main.cpp`.

## 3. Diseño Técnico

### 3.1. Clase UartStrategy
```cpp
class UartStrategy : public IComms {
private:
    HardwareSerial* _serial;
    uint32_t _baudRate;
    int8_t _rxPin;
    int8_t _txPin;

public:
    UartStrategy(HardwareSerial* serial, uint32_t baud, int8_t rxPin, int8_t txPin);
    void begin() override; // Llama a _serial->begin(_baud, SERIAL_8N1, _rxPin, _txPin);
    // ... rest of IComms
};
```

### 3.2. Dependencias
*   `HardwareSerial` (Arduino Core).
*   `IComms` (Interface).

## 4. Criterios de Aceptación/Tests
1.  **Test de Inicialización:** Verificar que `begin()` configura los pines correctos (Mockear HardwareSerial).
2.  **Test de Envío:** Verificar que `send` escribe en el registro del puerto serie mockeado.
3.  **Test de Recepción:** Verificar que `read` devuelve los datos disponibles en el buffer mockeado.

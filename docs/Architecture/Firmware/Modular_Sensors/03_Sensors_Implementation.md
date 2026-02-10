# Guía de Implementación: Sensores Modulares Demeter

Esta guía detalla el proceso para agregar nuevos sensores al sistema y cómo manejar la dualidad **Mock vs Real**.

## 1. Estructura de Archivos

Cada sensor debe tener su par de archivos `.h` y `.cpp` en las siguientes rutas:

*   **Header:** `C++/include/hardware/sensors/MySensor.h`
*   **Implementation:** `C++/src/hardware/sensors/MySensor.cpp`

## 2. Patrón de Diseño: Mock & Real

Para facilitar el desarrollo sin hardware y las pruebas unitarias, cada clase de sensor debe ser capaz de comportarse como un **Mock** (datos simulados) o **Real** (driver de hardware), controlado por el constructor o flags de compilación.

### Enfoque Recomendado: Constructor Flag

```cpp
class MySensor : public Demeter::ISensor {
private:
    uint8_t _pin;
    bool _isMock; // Controla el modo

public:
    MySensor(uint8_t pin, bool isMock = false); 
    
    bool init() override {
        if (_isMock) return true;
        // Real logic: pinMode, Wire.begin...
    }

    bool read(SensorReading& out) override {
        if (_isMock) {
            out.value1 = random(20, 30);
            return true;
        }
        // Real logic: sensor.readTemperature()
    }
};
```

## 3. Pasos para Agregar un Sensor

1.  **Heredar de `ISensor`**: Implementar `init()`, `read()`, y `getName()`.
2.  **Definir Dependencias**: Si requiere una librería externa (ej. `Adafruit DHT`), agregarla a `platformio.ini` bajo `lib_deps`.
3.  **Implementar Lógica Dual**:
    *   **Mock:** Generar datos deterministas o aleatorios coherentes.
    *   **Real:** Llamar al hardware. Manejar fallos (ej. timeout, checksum) retornando `false` o `isValid = false`.
4.  **Registrar en Nodo**:
    *   En `main_node.cpp`, instanciar el sensor.
    *   Llamar a `node.registerSensor(&mySensor)`.

## 4. Sensores Implementados (Planned)

| Sensor | Clase | Librería PlatformIO |
| :--- | :--- | :--- |
| **DHT22** | `DHTSensor` | `adafruit/DHT sensor library` |
| **DS18B20** | `DS18B20Sensor` | `paulstoffregen/OneWire`, `milesburton/DallasTemperature` |
| **Capacitive Soil** | `SoilMoistureSensor` | N/A (AnalogRead) |

## 5. Pruebas

Para probar sin hardware:
1.  Instanciar con `isMock = true`.
2.  Verificar logs seriales.
3.  Verificar que los datos llegan al Gateway.

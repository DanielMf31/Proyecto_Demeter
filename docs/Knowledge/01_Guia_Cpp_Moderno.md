# Guía de C++ Moderno y Arquitectura Strategy
**Objetivo:** Entender la sintaxis y conceptos del código de comunicaciones implementado.

## 1. El Concepto: Polimorfismo y Strategy Pattern

En Python, gracias al "Duck Typing", no te importa el tipo de una variable mientras tenga el método que buscas.
En C++, el tipado es estricto. Para lograr flexibilidad, usamos **Herencia y Polimorfismo**.

### ¿Qué es `IComms`? (La Interface)
Es un **Contrato**. Dice: *"Cualquier cosa que quiera ser una radio, debe tener estos métodos"*.

```cpp
// IComms.h
class IComms {
public:
    // "virtual ... = 0" significa que este método NO tiene código aquí.
    // Es OBLIGATORIO que los hijos lo implementen.
    virtual void send(const uint8_t* data, size_t length) = 0; 
};
```
*   **`virtual`**: Palabra clave mágica. Le dice al compilador: *"No decidas qué función llamar ahora. Decídelo cuando el programa esté corriendo, dependiendo de si el objeto real es un UartStrategy o un LoraStrategy"*.
*   **`= 0`**: Esto hace que la función sea **Virtual Pura**. Convierte a la clase en **Abstracta** (no puedes hacer `new IComms()`, solo puedes instanciar sus hijos).

---

## 2. La Implementación: `UartStrategy`

Esta clase **firma el contrato**. Se compromete a rellenar el código que falta.

```cpp
// UartStrategy.h
// ": public IComms" significa HERENCIA. UartStrategy ES UN IComms.
class UartStrategy : public IComms { 
public:
    // "override" es como un seguro. Si te equivocas en el nombre (ej. "sent" en vez de "send"),
    // el compilador te da error. Confirma que estás sobrescribiendo al padre.
    void send(const uint8_t* data, size_t length) override;
};
```

### Sintaxis Explicada (UartStrategy.cpp)

#### Constructor y Lista de Inicialización
```cpp
// C++ Clásico
UartStrategy::UartStrategy(HardwareSerial* serial, uint32_t baud) {
    _serial = serial;
    _baudRate = baud;
}

// C++ Moderno (Lo que usé)
UartStrategy::UartStrategy(HardwareSerial* serial, uint32_t baud) 
    : _serial(serial), _baudRate(baud) {} // <-- Lista de Inicialización
```
La lista de inicialización (`: _var(val)`) es más eficiente porque asigna el valor *mientras se crea* la variable, en lugar de crearla vacía y luego asignarle valor dentro de las llaves.

#### Punteros (`*`) vs Referencias
Utilicé `HardwareSerial* serial` (Puntero).
*   **Puntero (`*`)**: Es una dirección de memoria (ej. `0x00FF`). Puede ser `nullptr` (nulo, vacío).
*   **Flecha (`->`)**: Se usa para acceder a métodos de un puntero.
    *   `_serial->begin(...)` es lo mismo que `(*_serial).begin(...)`.

#### Preprocesador (`#ifdef`)
```cpp
#ifdef ARDUINO
    #include <Arduino.h>
#else
    // Mock para PC
#endif
```
Esto es "Metaprogramación". Antes de compilar, el preprocesador mira esto.
*   Si estás en ESP32, PlatformIO define `ARDUINO`. Se incluye la librería real.
*   Si estás en PC (Tests), `ARDUINO` no existe. Se usa el código falso (Mock) para que no falle al no encontrar `Serial`.

---

## 3. ¿Por qué hacerlo así? (La Ventaja Real)

Imagina que mañana compras un módulo LoRa.
Solo creas `LoraStrategy.h/cpp` copiando a UartStrategy pero cambiando `Serial.write` por `LoRa.send`.

Tu código principal (el `ProtocolEngine` que haremos luego) se verá así:

```cpp
// Tu Engine NO sabe qué radio usa. Solo ve un puntero a IComms.
class ProtocolEngine {
    IComms* _radio; 
public:
    void enviarMensaje() {
        // AQUÍ ESTÁ LA MAGIA DEL POLIMORFISMO
        // Si _radio apunta a Uart, envía por cable.
        // Si _radio apunta a LoRa, envía por aire.
        // El código es idéntico.
        _radio->send(bafer, len); 
    }
};
```

Esto separa responsabilidades. El Engine piensa en **Protocolos**, la Strategy piensa en **Electricidad/Cables**.

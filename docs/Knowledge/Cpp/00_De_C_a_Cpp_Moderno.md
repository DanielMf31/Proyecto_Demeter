# C++ para Programadores de C: El Salto Conceptual

**Objetivo:** Explicar C++ aprovechando tu sólido conocimiento de C. No te enseñaré bucles ni ifs (ya los sabes). Te enseñaré **dónde se guarda la memoria** y **quién es el dueño**.

## 1. Structs con Vitaminas (Clases)

En C, un `struct` es solo una bolsa de datos.
```c
// C
struct Motor {
    int pin;
    int velocidad;
};
void init_motor(struct Motor* m, int p) { m->pin = p; m->velocidad = 0; }
```

En C++, el `struct` cobra vida y protege sus datos. Le llamamos `class`.

```cpp
// C++
class Motor {
private: // NADIE de fuera puede tocar esto. Seguridad.
    int _pin;
    int _velocidad;

public: // Esta es tu API
    // Constructor: Reemplaza a tu función init_motor
    Motor(int pin) : _pin(pin), _velocidad(0) { }

    void acelerar() { _velocidad++; } // 'this' está implícito
};
```

**La diferencia clave:** En C, cualquiera puede hacer `m->velocidad = 99999` y romper tu lógica. En C++, el compilador lo prohíbe.

## 2. Punteros (`*`) vs Referencias (`&`)

En C amas los punteros. En C++ intentamos evitarlos, pero en Embedded son necesarios.
Sin embargo, inventamos las **Referencias** para no volvernos locos con `*` y `->`.

### Referencia = Un Alias (Apodo)
Una referencia es **un puntero que no puede ser NULL y se usa sin asteriscos**.

```cpp
void resetearMotor(Motor* m) { // Estilo C
    if (m) m->velocidad = 0;   // Riesgo de NULL, sintaxis fea ->
}

void resetearMotor(Motor& m) { // Estilo C++
    m.velocidad = 0;           // Sintaxis de punto (.), como si fuera valor
    // IMPOSIBLE que m sea NULL (el compilador no deja pasar null)
}
```
**Regla de Oro:**
*   ¿El objeto puede no existir (NULL)? Usa Puntero (`Motor*`).
*   ¿El objeto SIEMPRE tiene que existir? Usa Referencia (`Motor&`).

## 3. Interfaces (El viejo `void*` pero seguro)

En C, para hacer código genérico usabas `void*` y reza para castearlo bien.
En C++ usamos **Clases Abstractas** (Interfaces).

```cpp
// El Contrato (Header file)
class IComunicaciones {
public:
    virtual void enviar(char byte) = 0; // = 0 significa "No tengo código, tú impleméntalo"
};

// La Implementación (Source file)
class Uart : public IComunicaciones {
public:
    void enviar(char byte) override { 
        // Lógica real de hardware
    }
};
```

**¿Por qué es brutal?**
Tu código principal (`SystemContext`) recibe un `IComunicaciones*`.
No sabe si es UART, WiFi o un Simulador en PC. Solo sabe que puede llamar a `->enviar()`.
Esto nos permite **cambiar el hardware sin tocar el código lógico**.

## 4. RAII (Resource Acquisition Is Initialization)
El nombre asusta, pero la idea es simple:
*   En C: `malloc()` -> USAR -> `free()` (Si se te olvida free, memory leak).
*   En C++: El **Constructor** pide memoria, el **Destructor** la libera.
*   Ocurre AUTOMÁTICAMENTE cuando la variable sale de ámbito (`}`).

## Práctica Sugerida
Ve a `C++/include/core/InternalTypes.h`. Es un archivo estilo C (structs simples).
Luego mira `ProtocolEngine.h`. Es estilo C++ (Clase, private, métodos).
¿Ves la diferencia entre "Datos Tontos" y "Objetos Inteligentes"?

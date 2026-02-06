# Test de Comprensión: Arquitectura C++ y Strategy Pattern

**Instrucciones:** Intenta responder estas preguntas mentalmente o en un papel antes de ver las soluciones al final.

## Nivel 1: Conceptos Básicos (Lo que has resumido)

1.  **La Interfaz:** Si olvido escribir `virtual void send(...) = 0;` en `IComms.h` y solo escribo `void send(...) = 0;` (sin `virtual`), ¿qué problema tendría el `ProtocolEngine` al intentar enviar un mensaje usando `IComms*`?
2.  **Polimorfismo:** En `ProtocolEngine`, tendremos una variable `IComms* radio`. Si asignamos `radio = new UartStrategy(...)`, ¿cómo sabe el programa en tiempo de ejecución que debe llamar al `send` de Uart y no al de una supuesta `LoraStrategy`?
3.  **Inyección de Dependencia:** En `UartStrategy`, recibimos `HardwareSerial*` en el constructor. ¿Por qué pedimos un **puntero** (`*`) y no el objeto por valor (`HardwareSerial serial`)? ¿Qué pasaría con la conexión Serial real si pasáramos una copia?

## Nivel 2: Profundizando en el Código

4.  **Mocks y Preprocesador:**
    En `UartStrategy.h` tenemos:
    ```cpp
    #ifdef ARDUINO
       #include <Arduino.h>
    #else
       class HardwareSerial { ... };
    #endif
    ```
    Si compilas en modo `env:transmisor` (ESP32), ¿el compilador "ve" la clase `HardwareSerial` falsa que definimos en el `else`? ¿O esa parte del código "desaparece" antes de compilar?

5.  **Pure Virtual Functions:**
    ¿Es posible crear una instancia directa de `IComms`? Ejemplo: `IComms miRadio;`. ¿Por qué sí o por qué no?

6.  **Memoria y Vectores:**
    En el método `read()`, devolvemos `std::vector<uint8_t>`.
    ```cpp
    std::vector<uint8_t> read() {
        std::vector<uint8_t> buffer;
        buffer.push_back(0xFE);
        return buffer;
    }
    ```
    Cuando esa función termina (`return buffer`), la variable local `buffer` se destruye. ¿Cómo es posible que quien llamó a la función reciba los datos si la variable local ha muerto? (Pista: Semántica de Movimiento / Copia de retorno).

---

## Soluciones Explicadas

**1. Sin `virtual`, no hay Polimorfismo:**
Si quitas `virtual`, el compilador hará "Static Binding".
Si tienes `IComms* radio = new UartStrategy()`, y llamas a `radio->send()`, el programa llamará al `send` de `IComms` (que no existe o está vacío) en lugar del de `UartStrategy`. **`virtual` es lo que activa la búsqueda dinámica** de la función correcta.

**2. V-Table (Tabla Virtual):**
Internamente, C++ crea una tabla oculta de punteros a funciones para cada clase con métodos virtuales. Cuando llamas a `radio->send()`, el programa no salta directo a una dirección de memoria fija; consulta la "Matrícula" del objeto (V-Table) para ver cuál es la dirección real de `send` para ese tipo de objeto específico.

**3. ¿Por qué Punteros? (La Copia es el Enemigo):**
Si pasas `HardwareSerial serial` (por valor), C++ crea una **COPIA EXACTA** del objeto.
En el mundo físico, no puedes "clonar" el puerto USB de tu ordenador. Copiar un objeto que representa hardware suele romper la conexión o es imposible/prohibido. Usamos punteros (o referencias) para decir "Usa ESTE puerto serial que ya existe", no "Crea uno nuevo igual".

**4. El Preprocesador es una Tijera:**
El código del `#else` **DESAPARECE**. Literalmente. Antes de que el compilador vea el código, el preprocesador corta y borra el texto que no cumple la condición. Para el compilador ESP32, esa clase Mock nunca existió.

**5. Clases Abstractas:**
No. **Imposible.** Como `IComms` tiene métodos marcados con `= 0` (Puros), es una "Clase Abstracta". Es un plano incompleto. El compilador te prohíbe instanciar algo que no está terminado. Solo puedes instanciar a sus hijos que hayan completado ("implementado") esos métodos.

**6. Return by Value:**
C++ moderno es listo. Al hacer `return buffer`, ocurre una de dos cosas:
1.  **Copia:** Se crea un nuevo vector fuera y se copian los datos (lento).
2.  **Move (RVO - Return Value Optimization):** El compilador se da cuenta de que `buffer` va a morir, así que en lugar de copiar, simplemente le "regala" las tripas (el puntero interno a los datos) a la variable que recibe el resultado. Es casi instantáneo.

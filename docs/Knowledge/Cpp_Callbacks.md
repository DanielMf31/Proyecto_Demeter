# Conceptos C++: Callbacks, std::function y Lambdas

En el proyecto Demeter, el `ProtocolEngine` necesita notificar a otras partes del sistema (como el `GpioController` o el `SystemContext`) cuando ocurre un evento importante, por ejemplo, cuando llega un comando válido para encender un LED.

Para lograr esto sin que el `ProtocolEngine` dependa directamente de esas clases (desacoplamiento), utilizamos un patrón de diseño basado en **Callbacks**.

## 1. ¿Qué es un Callback?

Un callback es una función (o un bloque de código ejecutable) que se pasa como argumento a otra función para que sea ejecutada ("llamada de vuelta") en un momento posterior, generalmente cuando ocurre un evento.

En el contexto de Demeter:

* **Evento:** Llega un comando `SET_GPIO` válido por UART.
* **Callback:** Una función que sabe cómo activar el pin físico en el ESP32.

## 2. Implementación Moderna en C++ (`std::function`)

Antiguamente en C se usaban punteros a función (`void (*func)(int)`), que son difíciles de leer y limitados (no pueden capturar contexto).

C++11 introdujo `std::function`, una envoltura genérica que puede almacenar cualquier cosa "invocable":

* Funciones normales.
* Lambda expressions (funciones anónimas).
* Objetos función (Functors).
* Métodos de clase (con `std::bind`).

### Definición en `ProtocolEngine.h`

```cpp
// Definimos un alias para facilitar la lectura
using GpioCallback = std::function<void(const Demeter::SetGpioCmd&)>;

// Variable miembro para guardar el callback
GpioCallback _onGpioCommand;

// Método para que quien use la clase registre su callback
void onSetGpio(GpioCallback cb) {
    _onGpioCommand = cb;
}
```

## 3. Lambdas: Funciones Anónimas

Las Lambdas son la forma más potente y concisa de definir callbacks en C++. Permiten escribir la función en el mismo lugar donde se registra, y además pueden "capturar" variables del entorno.

Sintaxis: `[capturas](argumentos) { cuerpo }`

### Ejemplo en `SystemContext.cpp`

```cpp
// Le decimos al motor: "Cuando recibas un comando GPIO, ejecuta este código"
_engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
  
    // [this] significa que dentro de esta función podemos acceder a
    // los métodos y variables de ESTA instancia de SystemContext.
  
    if (_mode == ExecutionMode::IMMEDIATE) {
        // Ejecutar ya
        this->_executor.setGpio(cmd);
    } else {
        // Guardar para después
        this->queueCommand(cmd);
    }
});
```

## 4. ¿Por qué usar este enfoque?

1. **Desacoplamiento:** `ProtocolEngine` no necesita incluir `GpioController.h`. Solo sabe que debe llamar a "una función" con ciertos parámetros.
2. **Flexibilidad:** Podríamos cambiar la implementación del callback para que en lugar de encender un LED, imprima por pantalla, sin tocar ni una línea del `ProtocolEngine`.
3. **Testabilidad:** En los tests unitarios, registramos lambdas sencillas que solo cambian un booleano `wasCalled = true`, facilitando la verificación sin necesidad de hardware real.

---

**Resumen:** Los Callbacks permiten que el módulo de bajo nivel (`ProtocolEngine`) notifique al de alto nivel (`SystemContext`) sin crear dependencias circulares ni código espagueti.

## 5. Anatomía de `std::function` (El Contrato Riguroso)

Has preguntado por esta línea críptica:

```cpp
using GpioCallback = std::function<void(const Demeter::SetGpioCmd&)>;
```

Esto no es una "tarjeta de visita", es un **CONTRATO DE ADUANA**.

### 1. El Molde (`std::function`)

 es una caja universal. Puede guardar cualquier cosa que se pueda ejecutar (función normal, lambda. etc).
Pero esa caja tiene una forma específica.

### 2. La Firma (`<void(const Demeter::SetGpioCmd&)>`)

Aquí definimos la forma exacta de la clavija.

* **`void`**: El valor de retorno. Significa "No devuelvas nada".
* **`(...)`**: Lo que va dentro de los paréntesis son los **Argumentos Obligatorios**.
* **`const Demeter::SetGpioCmd&`**: El tipo de dato exacto.

**¿Qué significa esto?**
El  está diciendo:

> *"Yo solo acepto guardar funciones que reciban EXACTAMENTE una estructura SetGpioCmd. Si intentas pasarme una función que pide un  o un , daré error de compilación."*

Esto garantiza que cuando  dispare el evento, **tiene la certeza absoluta** de que la función al otro lado sabrá qué hacer con los datos recibidos.

## 6. El Misterio del Ámbito (`[this]`)

Cuando escribimos esto en :

```cpp
_engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
    this->handleGpioCommand(cmd);
});
```

### El Problema del "Ámbito Local"

Una función normal en C++ es tonta. No sabe nada de lo que hay fuera de sus llaves .
Si  es un método de  necesita saber **sobre qué instancia** de SystemContext ejecutarse (¿la instancia A o la B?).

### La Solución: Captura Lambda (`[this]`)

* **`[]`**: Crea una función anónima nueva.
* **`[this]`**: "Oye función anónima, llévate una copia de mi puntero `this` en tu mochila".

Cuando la Lambda se ejecuta (horas después, cuando llega el comando), abre su mochila, saca el puntero `this`, y dice: "Ah, tengo que llamar a `handleGpioCommand` de ESTE objeto concreto".

## 7. Desmitificando la Magia: Lo que ve el Compilador

Preguntas cómo "salta" de un lado a otro y cómo funciona la memoria. La respuesta es sorprendente: **Las Lambdas NO existen**. Son un truco sintáctico.

Cuando escribes esto:
```cpp
_engine.onSetGpio([this](auto cmd) { 
    this->handleGpioCommand(cmd); 
});
```

El compilador **reescribe tu código** y genera una clase oculta (Functor) automáticamente. Es algo parecido a esto:

### El Código Secreto Generado
```cpp
// 1. El compilador crea una clase con un nombre aleatorio
class Lambda_Generada_XYZ {
public:
    // VARIABLE OCULTA: Aquí se guarda lo que pusiste en [this]
    SystemContext* puntero_guardado; 

    // CONSTRUCTOR: Para guardar el puntero cuando se crea la lambda
    Lambda_Generada_XYZ(SystemContext* p) : puntero_guardado(p) {}

    // LA FUNCIÓN: Esto es lo que pusiste entre { }
    void operator()(const Demeter::SetGpioCmd& cmd) {
        // Usa el puntero guardado para saber a QUIÉN llamar
        puntero_guardado->handleGpioCommand(cmd);
    }
};
```

### El Flujo de Memoria Real
1.  **SETUP ():**
    *   C++ crea una instancia de .
    *   Guarda tu  (la dirección de memoria  donde está tu ) dentro de la variable  de esa lambda.
    *   Ese objeto lambda se guarda dentro de .

2.  **EJECUCIÓN ():**
    *   El engine tiene el objeto lambda guardado.
    *   Llama a su función .
    *   Dentro de esa función, el código usa  (que vale ) para saltar a la memoria del  y ejecutar la función.

### Conclusión
No es magia. Es un **Objeto**.
*   El **CÓDIGO** (instrucciones) está en una dirección de memoria fija (Flash).
*   El **CONTEXTO** (el puntero ) está guardado como una variable dentro del objeto Lambda en la RAM.
*    es solo el envase que transporta ese objeto.

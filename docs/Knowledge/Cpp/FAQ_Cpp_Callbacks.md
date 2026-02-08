# FAQ: Callbacks y Lambdas en C++ (Proyecto Demeter)

Este documento responde a las dudas comunes sobre cómo fluyen los datos y se ejecutan las órdenes en nuestro sistema usando Callbacks.

## 1. ¿Quién ejecuta realmente el código del GpioController?
**Pregunta:** *¿El ProtocolEngine se encarga de ejecutar las funciones del GpioController directamente?*

**Respuesta:** No directamente. El `ProtocolEngine` es "ciego". No sabe que existe un `GpioController`.
1.  El `ProtocolEngine` solo sabe que tiene guardada una **función anónima** (el callback) que debe llamar cuando recibe un comando válido.
2.  Cuando llama a esa función, se ejecuta el código que definimos dentro de ella (normalmente en el `main.cpp` o `SystemContext.cpp`).
3.  Es ese código intermedio el que finalmente llama a `gpioController.setGpio(...)`.

Es como un **interruptor de luz**: El mecanismo del interruptor (ProtocolEngine) no sabe si enciende una bombilla o un ventilador (GpioController). Solo cierra el circuito (llama al callback).

## 2. Flujo Completo: Desde el Byte hasta el LED
**Pregunta:** *¿Cuál es el recorrido exacto de una trama?*

Supongamos que llega la trama para encender el PIN 4.

1.  **Recepción (Hardware):** El módulo UART del ESP32 recibe los bytes y los guarda en su buffer interno.
2.  **Lectura (Polling):** En el `loop()`, llamamos a `systemCtx.loop()`, que llama a `engine.update()`.
3.  **Extracción:** `ProtocolEngine` saca los bytes del buffer y detecta la trama válida (Sync, Length, CRC OK).
4.  **Disparo (Trigger):** El `ProtocolEngine` ve que el comando es `SET_GPIO` e invoca a `_onGpioCommand(cmd)`.
5.  **Ejecución del Callback (Lambda):**
    *   Se ejecuta el código que definimos en `SystemContext`:
    ```cpp
    _engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
        // Estamos AQUÍ.
        // El ProtocolEngine nos ha "pasado la pelota".
        
        if (modo == INTERACTIVE_QUEUE) {
            queue.push_back(cmd); // Guardar para luego
        } else {
            _executor.setGpio(cmd); // EJECUTAR AHORA
        }
    });
    ```
6.  **Acción Física:** `_executor.setGpio` (GpioController) hace `digitalWrite(4, HIGH)`.

## 3. Simultaneidad y Tiempos
**Pregunta:** *¿Se ejecuta al mismo tiempo que otra cosa?*

**Respuesta:** En nuestra arquitectura actual (Single Threaded / Arduino Loop estándar): **NO**.
*   Todo ocurre secuencialmente en el hilo principal.
*   Cuando `engine.update()` llama al callback, **el sistema se "detiene" en ese callback** hasta que termina.
*   Si tu callback tarda 1 segundo (ej. un `delay(1000)`), el `ProtocolEngine` no seguirá leyendo bytes ni haciendo nada más durante ese segundo.
*   Por eso los callbacks deben ser **rápidos** (solo cambiar un pin o guardar en una variable).

## 4. ¿Por qué usamos Lambdas?
**Pregunta:** *¿Qué son esas cosas con corchetes `[]` y para qué sirven?*

Una **Lambda** es una función que se escribe "al vuelo".

**Sin Lambdas (Estilo C antiguo):**
Tendrías que crear una función suelta fuera de la clase:
```cpp
void funcionSuelta(Cmd cmd) {
    // Problema: ¿Cómo accedo a 'gpioController' si es una variable de otra clase?
    // Necesitaria que gpioController fuera global :(
}
```

**Con Lambdas (C++ Moderno):**
```cpp
[this](Cmd cmd) { 
    // Los corchetes [this] son la "Captura".
    // Permiten que esta función anónima tenga acceso a las variables
    // de la clase donde se escribe (SystemContext).
    this->_executor.setGpio(cmd); 
}
```
**Utilidad:** Nos permiten "pegar" lógica de una clase (`SystemContext`) dentro de otra (`ProtocolEngine`) sin que la segunda tenga que conocer a la primera.

## 5. Resumen Visual
```
[Main Loop]
    |
    +-> engine.update()
          |
          +-> (Hay Trama Válida?) -> SÍ
                |
                +-> LLAMAR Callback (std::function)
                      |
                      |  <-- Salta al código definido en SystemContext
                      |
                      +-> Lambda: [this] { _executor.setGpio() }
                            |
                            +-> GpioController::setGpio()
                                  |
                                  +-> digitalWrite() -> LED ENCENDIDO
```

## 6. Rastreo de Código: El Camino del SET_GPIO

Aquí tienes el código real que se ejecuta en cada paso cuando llega un comando `SET_GPIO`.

### Paso A: Definición del Comando (`InternalTypes.h`)
Primero, definimos qué datos componen la orden.
```cpp
namespace Demeter {
    struct SetGpioCmd {
        uint8_t pin;   // Qué pin (ej. 4)
        bool value;    // Encendido (true) o Apagado (false)
        uint8_t flags; // Opciones extra
    };
}
```

### Paso B: El Interruptor (`ProtocolEngine`)
El motor de protocolo recibe los bytes, rellena la estructura anterior y llama al callback (si existe).
```cpp
// ProtocolEngine.cpp
if (hdr->cmd_id == (uint8_t)Demeter::CommandType::SET_GPIO) {
    if (_onGpioCommand) { // ¿Hay alguien escuchando?
        Demeter::SetGpioCmd cmd;
        // ... (Rellenar cmd con los bytes recibidos) ...
        
        _onGpioCommand(cmd); // <--- ¡DISPARO!
    }
}
```

### Paso C: La Conexión (`SystemContext.cpp`)
Aquí es donde decidimos qué hacer con ese disparo. Usamos una Lambda para conectar el evento con nuestro sistema.
```cpp
void SystemContext::setup() {
    // ...
    // Le decimos al motor: "Cuando recibas GPIO, llama a mi función handleGpioCommand"
    _engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
        this->handleGpioCommand(cmd);
    });
}

void SystemContext::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_execMode == ExecutionMode::IMMEDIATE) {
        _executor.execute(cmd); // Ejecutar YA
    } else {
        _commandQueue.push_back(cmd); // Guardar para luego
    }
}
```

### Paso D: La Acción Real (`GpioController.cpp`)
Finalmente, el controlador de hardware hace el trabajo sucio.
```cpp
void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Seguridad (No tocar pines prohibidos)
    if (cmd.pin == 0 || cmd.pin == 1) return;

    // 2. Configurar y Actuar
    pinMode(cmd.pin, OUTPUT);
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
}
```

---

## 7. Preguntas de Auto-Evaluación

Para saber si has entendido el sistema de Callbacks, intenta responder estas preguntas (y verifica con el código):

1.  **¿Qué pasaría si en  olvidamos llamar a ?**
    *   *Pista:* Mira la línea  en .

2.  **¿Dónde tendrías que tocar código si quisieras que al recibir un  también se imprimiera un mensaje por Serial?**
    *   *Pista:* ¿Hace falta modificar ? ¿O solo la Lambda en ?

3.  **¿Por qué  recibe  (referencia) en lugar de simplemente  (copia)?**
    *   *Pista:* Eficiencia. ¿Qué pasa si la estructura fuera muy grande?

4.  **Si  es , ¿cuándo se llama a ?**
    *   *Pista:* Mira el método .

## 8. Deep Dive: Anatomía de una Trama (Header y parseFrame)

Has preguntado por el "Header misterioso" y cómo convertimos bytes mágicos en objetos C++. Aquí está la explicación detallada.

### El Header: Mapa del Tesoro (`ProtocolEngine.h`)
El Header no es más que una "plantilla" que ponemos sobre los bytes para leerlos ordenadamente.

```cpp
#pragma pack(push, 1) // Importante: Sin huecos entre bytes
struct Header {
    uint8_t sync;    // 0: El "Hola" (0xFE)
    uint8_t length;  // 1: Cuánto datos vienen después
    uint8_t flags;   // 2: Opciones
    uint8_t src_id;  // 3: Quién lo envía
    uint8_t dst_id;  // 4: Para quién es
    uint8_t cmd_id;  // 5: QUÉ hay que hacer (SET_GPIO, PING...)
};
#pragma pack(pop)
```

### El Truco de Magia: `reinterpret_cast`
Cuando llegan datos, llegan como un array de `uint8_t` (bytes crudos). ¿Cómo sabe C++ que el byte 5 es el `cmd_id`?

Usamos **Reinterpret Cast**: Le decimos al compilador "Confía en mí, trata este puntero de bytes como si fuera un puntero a una estructura Header".

```cpp
// Supongamos que frame = { 0xFE, 0x03, 0x00, 0x0A, 0x01, 0x10, ... }
const Header* hdr = reinterpret_cast<const Header*>(frame.data());

// Ahora podemos acceder así:
uint8_t comando = hdr->cmd_id; // C++ va automáticamente a la posición 5
```

### Paso a Paso en `parseFrame`

1.  **Tamaño Mínimo:** ¿Tenemos al menos 7 bytes (Header + CRC)? Si no, ni miramos.
2.  **Cast:** Ponemos la "plantilla" Header sobre los datos.
3.  **Sync:** ¿El primer byte es `0xFE`? Si no, es ruido. Descartar.
4.  **Longitud:** Leemos . Verificamos si realmente han llegado esos N bytes de payload.
5.  **CRC (Matemáticas):**
    *   Sumamos todos los bytes desde  hasta el final del payload.
    *   Comparamos esa suma con el último byte de la trama (el CRC recibido).
    *   Si no coinciden -> ¡CORRUPCIÓN! Alguien habló encima del cable. Ignorar.
6.  **Despacho (Switch/If):**
    *   Si todo está bien, miramos `hdr->cmd_id`.
    *   Si es `SET_GPIO`, sacamos los bytes del Payload y los metemos en la struct `SetGpioCmd`.
    *   Llamamos al callback.

### Resumen Gráfico
```text
Trama en memoria (Bytes):
[ FE ][ 03 ][ 00 ][ 0A ][ 01 ][ 10 ][ 04 01 00 ][ 13 ]
  ^     ^                       ^
  |     |                       |
  |     +--- hdr->length        +--- hdr->cmd_id (SET_GPIO)
  |
  +--- hdr->sync
```

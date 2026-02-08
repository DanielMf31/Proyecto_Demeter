# Arquitectura del Sistema Demeter (Firmware)

Este documento describe cómo interactúan todas las piezas del firmware para convertir un mensaje serial en una acción física.

## 1. Diagrama de Bloques (Conceptual)

```mermaid
graph TD
    Host[Host (Python/PC)] -->|Bytes por UART| UART[UartStrategy]
    UART -->|Buffer Crudo| Protocol[ProtocolEngine]
    Protocol -->|Comando Struct| System[SystemContext]
    System -->|Orden Ejecutiva| GPIO[GpioController]
    GPIO -->|Voltaje| Hardware[LEDs/Motores]
```

## 2. Componentes Principales

### A. Capa de Transporte (`UartStrategy`)
*   **Responsabilidad:** Mover bytes de un lado a otro.
*   **Función:** "Soy el cartero. No leo las cartas, solo las entrego".
*   **Abstracción:** Usa `Serial2` (HardwareSerial) pero podría ser WiFi o LoRa.

### B. Capa de Protocolo (`ProtocolEngine`)
*   **Responsabilidad:** Entender el idioma (Protocolo Demeter V2).
*   **Función:** "Soy el traductor. Recibo garabatos y los convierto en frases con sentido".
*   **Acciones:**
    1.  Busca el inicio (`0xFE`).
    2.  Valida la integridad (CRC).
    3.  Avisa al jefe (`SystemContext`) usando el Teléfono Rojo (Callbacks).

### C. Capa de Orquestación (`SystemContext`)
*   **Responsabilidad:** Tomar decisiones de negocio.
*   **Función:** "Soy el Jefe de Planta. Decido SI se hace, CUÁNDO se hace y QUIÉN lo hace".
*   **Lógica:**
    *   ¿Estamos en modo *Inmediato*? -> Ejecutar ya.
    *   ¿Estamos en modo *Cola*? -> Guardar para luego.
    *   ¿Hay error de emergencia? -> Ignorar todo.

### D. Capa de Hardware (`GpioController`)
*   **Responsabilidad:** Mover electrones.
*   **Función:** "Soy el operario. Si me dicen 'Enciende el 4', yo subo la palanca del 4".
*   **Abstracción:** Usa `digitalWrite`, `ledcWrite` (PWM).

## 3. Flujo de Vida de un Comando (`SET_GPIO`)

1.  **Llegada:** `UartStrategy` llena su buffer con `[FE 03 ... 10 04 01 ... CRC]`.
2.  **Detección:** `ProtocolEngine::update()` ve los bytes y confirma que el CRC es válido.
3.  **Despacho:** `ProtocolEngine` identifica `CMD 0x10` (GPIO) y llama al Callback registrado.
4.  **Decisión:** `SystemContext` recibe el callback. Verifica que no hay errores y decide ejecutarlo.
5.  **Acción:** `SystemContext` llama a `GpioController::execute()`.
6.  **Física:** `GpioController` llama a `digitalWrite(4, HIGH)`. **¡La luz se enciende!**

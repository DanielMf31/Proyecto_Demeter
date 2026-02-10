# 1. Visión General del Sistema (System Overview)

El firmware del Proyecto Demeter está construido bajo una arquitectura modular y desacoplada, siguiendo principios de **Clean Architecture** y **Strategy Pattern**. El objetivo principal es separar la lógica de negocio (Protocolo y Orquestación) de los detalles de implementación (Hardware, Comunicación, WiFi).

## Arquitectura de Alto Nivel

El sistema se divide en tres capas principales:

1.  **Capa de Hardware (Drivers & Strategies)**
    *   Maneja la interacción directa con el hardware (GPIO, UART, WiFi/ESP-NOW).
    *   Implementa interfaces abstractas para que el núcleo no dependa del hardware específico.
2.  **Capa de Protocolo (Protocol Engine)**
    *   Responsable de serializar y deserializar tramas binarias.
    *   Valida integridad (CRC) y estructura.
    *   Agnóstica del medio de transporte (funciona igual sobre UART, LoRa o ESP-NOW).
3.  **Capa de Sistema (System Context)**
    *   Orquestador central.
    *   Gestiona el estado del dispositivo (IDLE, PROCESSING, ERROR).
    *   Maneja la cola de comandos y el secuenciador.
    *   Vincula los eventos del Protocolo con las acciones del Hardware.

### Diagrama de Flujo de Datos

```mermaid
graph TD
    Hardware[Hardware (UART/ESP-NOW)] -->|Bytes| Strategy[IComms Strategy]
    Strategy -->|Buffer| Protocol[Protocol Engine]
    Protocol -->|Event Object| Context[System Context]
    Context -->|Command| GPIO[Gpio Controller]
    GPIO -->|Signal| Pins[Physical Pins]
    
    Context -->|Reply/Ack| Protocol
    Protocol -->|Frame| Strategy
    Strategy -->|Bytes| Hardware
```

## Principios de Diseño

*   **Inyección de Dependencias:** El `SystemContext` y `ProtocolEngine` reciben sus dependencias (Estrategias, Controladores) en el constructor. Esto facilita el testing unitario y la simulación.
*   **Event-Driven:** El `ProtocolEngine` no ejecuta acciones directamente; dispara *callbacks* que el `SystemContext` escucha.
*   **Non-Blocking:** Todo el sistema está diseñado para funcionar en un `loop()` no bloqueante, utilizando máquinas de estados para procesos largos (como secuencias).

## Estructura de Directorios

*   `src/core`: Contiene la lógica pura (Agnóstica de plataforma en su mayoría).
    *   `ProtocolEngine`: Parser del protocolo.
    *   `SystemContext`: Máquina de estados y orquestador.
*   `src/communications`: Implementación de estrategias de comunicación.
    *   `UartStrategy`: Comunicación Serial.
    *   `EspNowStrategy`: Comunicación inalámbrica mesh.
    *   `GatewayStrategy`: Composite que une UART y ESP-NOW.
*   `src/boot`: (Opcional) Inicialización y configuración.

## Puntos de Entrada

El firmware soporta múltiples roles compilables desde el mismo código base, definidos por el archivo `main_*.cpp` que se incluya:

*   **Gateway (`main_gateway.cpp`):** Actúa como puente entre el Host (Python/UART) y la Red de Nodos (ESP-NOW).
*   **Nodo (`main_node.cpp`):** Dispositivo final que ejecuta órdenes y reporta sensores.
*   **Simulador (`main_simulator.cpp`):** Para pruebas en PC (si se abstrae Arduino).

---
**Siguiente:** Ver [Módulos Principales](02_Core_Modules.md) para detalle de clases.

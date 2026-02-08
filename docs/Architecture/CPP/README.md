# Arquitectura Firmware C++ (ESP32)

Este directorio documenta los módulos principales del firmware del ESP32 Receptor, basado en la arquitectura de **Inyección de Dependencias** y **Patrón Estrategia**.

## Módulos Principales

### 1. Core (`src/core/`)
*   **[ProtocolEngine](02_ProtocolEngine.md):** Motor de parseo y validación de tramas binarias. Implementa la lógica de deserialización, CRC y despacho de comandos.
*   **SystemContext:** Orquestador principal del sistema. Maneja la máquina de estados y la cola de comandos (Modo Interactivo vs Inmediato).
*   **GpioController:** Abstracción de Hardware (HAL) para el control de pines físicos. Aísla la lógica de negocio de la API de Arduino.
*   **InternalTypes:** Definiciones de datos internas desacopladas del protocolo de red.

### 2. Comunicaciones (`src/communications/`)
*   **[UartStrategy](01_UartStrategy.md):** Implementación concreta de `IComms` para puerto Serial. Maneja la transmisión TX/RX.
*   **IComms:** Interfaz abstracta que define el contrato de comunicación (Send/Receive/Available), permitiendo mockear el hardware para tests nativos.

## Flujo de Datos

1.  **Entrada:** `UartStrategy` recibe bytes por UART.
2.  **Proceso:** `ProtocolEngine` reconstruye la trama, valida CRC y extrae el payload.
3.  **Lógica:** `SystemContext` decide si ejecutar inmediatamente o encolar.
4.  **Hardware:** `GpioController` ejecuta la acción física sobre el pin.

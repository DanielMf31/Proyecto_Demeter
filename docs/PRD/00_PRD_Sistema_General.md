# PRD 00: Sistema de Control Demeter (General)

## 1. Introducción
El sistema "Demeter" tiene como objetivo controlar actuadores (bombas, ventiladores) mediante un microcontrolador ESP32, el cual recibe comandos desde una Raspberry Pi (u otro host) a través de un protocolo de comunicación robusto.

## 2. Objetivos del Sistema
*   **Recepción de Comandos:** El ESP32 debe ser capaz de recibir tramas de datos binarios.
*   **Decodificación:** El sistema debe validar (CRC) y decodificar las tramas según el Protocolo V2.
*   **Ejecución:** Una vez decodificado, el sistema debe actuar sobre el Hardware (GPIO).
*   **Modularidad:** La capa de comunicación debe ser intercambiable (UART, LoRa, ESP-NOW) sin afectar la lógica de negocio.

## 3. Arquitectura de Alto Nivel
1.  **Host (RPi/PC):** Genera y envía comandos.
2.  **Medio de Transporte (UART):** Canal físico.
3.  **Firmware (ESP32):**
    *   **Transport Layer (IComms):** Abstracción del hardware de comunicación.
    *   **Protocol Engine:** Intérprete de bytes a objetos comando.
    *   **System Context:** Orquestador de estados y modos (Inmediato/Cola).
    *   **GPIO Controller:** Driver de bajo nivel para los pines.

## 4. Flujo de Datos
`[Host] -> (Bytes) -> [UART Strategy] -> (Vector<uint8_t>) -> [Protocol Engine] -> (Command Struct) -> [System Context] -> [GPIO Controller] -> [Hardware]`

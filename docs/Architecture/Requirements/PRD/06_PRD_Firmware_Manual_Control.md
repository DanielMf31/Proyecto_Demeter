# PRD: Control Manual de Firmware (USB/Serial)

## 1. Introducción
El sistema de **Control Manual** permite a un desarrollador o técnico interactuar directamente con el ESP32 a través del puerto Serial USB (UART0), sin necesidad de pasar por el Protocolo Demeter V2 ni la Raspberry Pi.

## 2. Objetivos
*   **Depuración:** Probar el hardware (GPIOs) independientemente del protocolo.
*   **Configuración:** Cambiar modos de operación en tiempo de ejecución.
*   **Emergencia:** Controlar actuadores si falla la red principal.

## 3. Especificación de Interfaz (CLI)

El menú se presenta por el puerto Serial a 115200 baudios.

### 3.1 Comandos de Teclado
| Tecla | Acción | Descripción |
| :--- | :--- | :--- |
| **`1` - `4`** | Toggle GPIO | Invierte el estado de los pines 4, 5, 6, 7 respectivamente. |
| **`I`** | Modo Inmediato | Cambia `SystemContext` a modo `IMMEDIATE`. |
| **`R`** | Modo Recepción | Cambia `SystemContext` a modo `INTERACTIVE_QUEUE`. |
| **`E`** | Ejecutar Cola | Dispara la ejecución de todos los comandos pendientes en la cola. |
| **`C`** | Limpiar Cola | Borra todos los comandos pendientes. |

## 4. Flujo de Implementación (`main_receptor.cpp`)

1.  **Lectura:** En `loop()`, se verifica `Serial.available()`.
2.  **Parsing:** Se lee el carácter y se convierte a mayúscula.
3.  **Acción Local:**
    *   Si es `1-4`: Se actualiza un array local `pinStates` para llevar el control del toggle (ON/OFF).
    *   Se crea un `Demeter::SetGpioCmd` sintético.
4.  **Inyección:** Se llama a `systemCtx.injectCommand(cmd)`.
    *   Esto hace que el sistema crea que el comando vino por la red, respetando la lógica de Estados y Modos (Cola vs Inmediato).

## 5. Ejemplo de Sesión
```text
=== DEMETER RECEPTOR V2 (MVP GPIO) ===
 [1-4] Toggle PIN 4-7
 [I] Mode: IMMEDIATE
...

>> MANUAL: PIN 4 -> ON    (Usuario pulsó '1')
>> MANUAL: PIN 5 -> ON    (Usuario pulsó '2')
>> MODE: QUEUE            (Usuario pulsó 'R')
>> MANUAL: PIN 4 -> OFF   (Usuario pulsó '1' -> Encolado)
>> EXECUTING QUEUE...     (Usuario pulsó 'E' -> Se apaga Pin 4)
```

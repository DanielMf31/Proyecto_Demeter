# Sistema Ejecutor (`GpioController`)

## Descripción
El **GpioController** es la abstracción del Firmware encargada de la manipulación directa del hardware (pines GPIO). Desacopla la lógica de protocolo de la implementación física.

## Ubicación
*   **Header**: `C++/include/core/GpioController.h`
*   **Source**: `C++/src/core/GpioController.cpp`

## Responsabilidades
1.  **Mapeo de Pines**: Traduce IDs de pines lógicos o índices a pines físicos del microcontrolador.
2.  **Ejecución Segura**: Aplica `digitalWrite`, `analogRead` o configuraciones `pinMode`.
3.  **Estado**: Mantiene (opcionalmente) el estado conocido de las salidas.

## Integración
Es utilizado príncipalmente por `SystemContext` para ejecutar los comandos `SET_GPIO` recibidos a través del Protocolo.

```cpp
// Ejemplo de uso
gpioController.setPin(4, HIGH);
```

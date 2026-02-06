# Simulación End-to-End (E2E)

**Estado:** Implementado y Funcionando ✅
**Script Principal:** `Python/scripts/e2e_simulation.py`

## Arquitectura

El sistema simula la conexión física UART usando tuberías (Pipes) del Sistema Operativo.

1.  **Python (Transmisor):** Genera tramas binarias validas usando `Pydantic` y `struct`.
2.  **C++ (Receptor):** Ejecutable nativo (`.pio/build/simulator/program`) que lee de `STDIN`.
3.  **Verificación:** Python captura el `STDOUT` de C++ para confirmar que el `GpioController` "encendió" los pines virtuales.

## Cómo Ejecutar

Desde la raíz del proyecto:

```bash
# 1. Asegúrate de tener el entorno virtual activo (o las deps instaladas)
# 2. Ejecuta el runner (él se encarga de compilar C++)
PYTHONPATH=Python/python/src Python/python/venv/bin/python Python/scripts/e2e_simulation.py
```

## Resultado Esperado

Deberías ver algo como:

```text
=== DEMETER E2E SIMULATION RUNNER ===
[1/4] Compiling Native Simulator...
[2/4] Compilation Success. Starting Simulator Process...
[3/4] Simulator Running. Injecting Commands...
 -> Sending: Set GPIO 4=HIGH (fe03010001100401001a)
 -> Sending: Set GPIO 5=LOW (fe03010001100500001a)
[4/4] Verifying Output...

--- SIMULATOR STDOUT ---
[GPIO] PIN 4 -> 1
[GPIO] PIN 5 -> 0

------------------------
✅ SUCCESS: GPIO 4 turned HIGH
✅ SUCCESS: GPIO 5 turned LOW

🎉 E2E SIMULATION PASSED!
```

## Detalles Técnicos
*   **main_simulator.cpp:** Usa `ioctl` para lectura no bloqueante de `STDIN`.
*   **GpioController.cpp:** Tiene un mock `#ifndef ARDUINO` que imprime logs parseables.

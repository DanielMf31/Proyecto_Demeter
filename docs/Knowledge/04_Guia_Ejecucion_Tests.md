# Guía de Ejecución de Tests y QA

Este documento explica cómo verificar la integridad del sistema Demeter V2.

## 1. Niveles de Testing

| Nivel | Herramienta | Objetivo | Comando Rápido |
| :--- | :--- | :--- | :--- |
| **Unitario (Python)** | `pytest` | Verificar lógica de negocio y Modelos Pydantic. | `pytest Python/python/tests` |
| **Unitario (C++)** | `pio test` | Verificar clases aisladas (`UartStrategy`). | `pio test -e native` |
| **Integración (C++)** | `pio test` | Verificar flujo `Bytes -> Motor -> GPIO`. | `pio test -e native` |
| **E2E (Simulado)** | `Python Script` | Verificar Backend -> Firmware Comunicacion. | `python Python/scripts/e2e_simulation.py` |

---

## 2. Prerrequisitos

 Asegúrate de estar en la raíz del proyecto.

### Python Environment
```bash
# Activar entorno virtual
source Python/python/venv/bin/activate
# Instalar dependencias
pip install -r Python/python/requirements.txt
```

### C++ Environment
Tener PlatformIO instalado (`pip install platformio` o extensión VSCode).

---

## 3. Ejecución Detallada

### A. Tests de Python (Backend)
Verifican que los modelos Pydantic serialicen/deserialicen correctamente.

```bash
# Ejecutar todos los tests
PYTHONPATH=Python/python/src pytest Python/python/tests -v
```

### B. Tests de C++ (Firmware)
Se ejecutan en tu PC (Nativo) usando Mocks.

```bash
# Ejecutar Suite Completa
pio test -e native
```

### C. Simulación End-to-End (La Joya de la Corona 👑)
Esta prueba compila el firmware C++ en un ejecutable especial que lee de `STDIN` y escribe a `STDOUT`. El script de Python lanza este ejecutable y le "habla" como si fuera el chip ESP32 real.

**Flujo:**
1.  Python crea comando `SetGpio(pin=4, val=1)`.
2.  Python envía bytes `FE 03...` al proceso C++.
3.  C++ procesa y hace `cout << "[GPIO] PIN 4 -> 1"`.
4.  Python lee la respuesta y valida.

**Comando:**
```bash
PYTHONPATH=Python/python/src python Python/scripts/e2e_simulation.py
```

## 4. Solución de Problemas Comunes

*   **Error: `ModuleNotFoundError: No module named 'proyecto_demeter'`**
    *   Falta configurar el PYTHONPATH. Usa: `export PYTHONPATH=$PYTHONPATH:$(pwd)/Python/python/src`
*   **Error: `pio command not found`**
    *   No tienes PlatformIO en el PATH. Intenta `/home/tu_usuario/.platformio/penv/bin/pio`.

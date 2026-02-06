# Guía de Ejecución de Tests (QA)

Este documento explica cómo ejecutar las baterías de pruebas para garantizar que el sistema funciona antes de desplegar.

## 1. Tests de Firmware C++ (PlatformIO)

El Firmware tiene dos tipos de tests:
1.  **Nativos (En tu PC):** Prueban la lógica (Protocolo, Clases) sin necesitar el hardware. Son rápidos.
2.  **Embebidos (En ESP32):** Prueban que el código funciona en el chip real. (Aún no implementados).

### Cómo ejecutar Tests Nativos
Requisito: Tener `pio` instalado (o usar el virtualenv de PlatformIO).

```bash
# Desde la carpeta raíz del proyecto C++
cd C++

# Ejecutar TODOS los tests nativos
/home/danielmf31/.platformio/penv/bin/pio test -e native

# Ejecutar con salida detallada (Verbose)
/home/danielmf31/.platformio/penv/bin/pio test -e native -v
```

Si ves `[PASSED]`, la lógica de tu código es correcta.

---

## 2. Tests de Backend Python

Python usa `unittest` y una estructura de paquete estándar.

### Preparación
Asegúrate de que estás en el entorno virtual o con las dependencias instaladas.
```bash
# Desde la raíz del proyecto (Proyecto_Demeter)
source python/venv/bin/activate  # Si usas venv
pip install -r proyecto_demeter/python/requirements.txt
```

### Ejecución
```bash
# Navegar a la carpeta del paquete
cd proyecto_demeter

# Ejecutar TODOS los tests (descubrimiento automático)
python3 -m unittest discover python/tests

# Ejecutar un test específico (ej. Protocolo V2)
python3 -m unittest python/tests/test_protocol_v2.py
```

### Tests Importantes
*   `test_protocol_v2.py`: Verifica que los bytes se generan igual que en el estándar.
*   `test_device_manager.py`: Verifica que `inventory.json` carga bien.
*   `test_integration_mock.py`: Simula una comunicación completa sin hardware real.

# Estrategia de Testing - Python

**Framework:** `pytest`
**Directorio:** `Python/tests/`

## Visión General
La estrategia de pruebas del proyecto Demeter se centra en **Pruebas Unitarias Aisladas** para la lógica de negocio y drivers, utilizando *Mocking* para simular el hardware (UART) que no está presente durante el desarrollo o CI/CD.

## Estructura de Tests

### 1. Protocolo (`test_protocol_engine.py`)
Valida la máquina de estados sin necesitar un ESP32 real.
*   **Qué se prueba:** Transiciones de estado (101->102->Data), Configuración de paquetes, Verificación de Eco.
*   **Técnica:** Se inyecta un `MockUART` en el motor. Simulamos respuestas del ESP32 (`mock_uart.receive.side_effect = [...]`) y verificamos que el motor responda correctamente (`mock_uart.send.assert_called_with(...)`).

### 2. Hardware Abstraction (`test_uart_service.py`)
Valida que el driver serial se comporte correctamente ante la librería `pyserial`.
*   **Qué se prueba:** Conexión exitosa/fallida, codificación de strings a bytes, manejo de `UnicodeDecodeError`.
*   **Técnica:** Se usa `@patch('serial.Serial')` para interceptar la creación del puerto real.

### 3. Infraestructura (`test_logger.py`)
Valida que el sistema de soporte funcione.
*   **Qué se prueba:** Creación de carpetas de logs, generación de archivos de sesión.

## Ejecución de Pruebas

Para ejecutar la suite completa, utilizamos el script de entorno virtual creado por `setup_deployment.sh`:

```bash
# Desde la raíz del proyecto
export PYTHONPATH=$PYTHONPATH:Python
Python/venv/bin/python -m pytest Python/tests/
```

## Cobertura
El objetivo actual es cubrir el 100% de los "Happy Paths" (flujo normal) y los casos de error más comunes (Timeout, Desconexión, Checksum error).

| Componente | Tipo de Test | Dependencias Externas |
| :--- | :--- | :--- |
| `protocol_engine.py` | Unitario (Lógica) | Mockeadas |
| `uart_service.py` | Unitario (Driver) | Mockeadas (`pyserial`) |
| `gui_controller.py` | Manual (Integration) | Requiere Display/X11 |

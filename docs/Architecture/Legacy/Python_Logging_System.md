# Arquitectura de Logging - Python

**Módulo:** `utils/logger.py`
**Configuración:** `config/config.py`

## Visión General
El sistema de logging de Demeter está diseñado para garantizar la trazabilidad completa de cada sesión de uso. A diferencia de un log rotativo tradicional, utilizamos un enfoque **basado en sesiones**, donde cada ejecución del programa genera un archivo de auditoría único e inmutable.

## Estructura de Archivos
```text
Python/
└── logs/
    └── sessions/
        ├── session_20240126_203000.log  <-- Sesión 1
        ├── session_20240126_214512.log  <-- Sesión 2 (Actual)
        └── ...
```

## Componentes

### 1. Singleton `SystemLogger`
La clase `SystemLogger` en `utils/logger.py` actúa como un Singleton. Esto asegura que la configuración (handlers, formatos) se aplique una única vez al inicio de la aplicación en `main.py`.

### 2. Canales de Salida (Handlers)
El sistema divide la información en dos canales con diferente granularidad:

| Canal | Destino | Nivel Mínimo | Formato | Objetivo |
| :--- | :--- | :--- | :--- | :--- |
| **Consola** | `stdout` | **INFO** | Simplificado | Feedback inmediato al operador. |
| **Archivo** | `logs/sessions/*.log` | **DEBUG** | Detallado | Auditoría forense y depuración profunda. |

### 3. Loggers Nombrados
No usamos el logger raíz directamente. Cada módulo instancia su propio logger para facilitar el filtrado:
*   `Demeter.GUI`: Eventos de usuario (Clicks, cambios de pantalla).
*   `Demeter.UART`: Tráfico de bytes crudos (TX/RX).
*   `Demeter.Protocol`: Lógica de estados y validación.

## Uso en Código

Para instrumentar una nueva clase, simplemente instanciamos el logger con el nombre adecuado:

```python
import logging
logger = logging.getLogger('Demeter.MiModulo')

def mi_funcion():
    logger.info("Inicio de operación")
    try:
        # ...
    except Exception as e:
        logger.error(f"Fallo crítico: {e}", exc_info=True)
```

## Formato de Log
El formato estandarizado para los archivos es:
`HORA | NIVEL | MODULO | MENSAJE`

Ejemplo real:
```text
20:30:05 | INFO     | Demeter.GUI     | ACTION: START_SEQUENCE | PARAMS: {'count': 5}
20:30:05 | INFO     | Demeter.Protocol| Iniciando Handshake (Enviando 101)...
20:30:05 | DEBUG    | Demeter.UART    | TX >> 31 30 31 0A | '101'
```

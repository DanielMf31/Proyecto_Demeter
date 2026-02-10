# Mock Transport Modes

El sistema de transporte simulado (`MockTransport`) ha sido refactorizado para soportar múltiples comportamientos mediante el **Patrón Estrategia**. Esto permite probar distintas partes del sistema sin necesidad de hardware real.

## Modos Disponibles

La configuración se realiza a través de la variable de entorno `DEMETER_MOCK_MODE` o en `provider.py`.

### 1. SENSORS (Aspiradora de Datos)
- **Comportamiento**: Simula nodos de sensores que envían reportes periódicos (`DataReport`).
- **Uso**: Ideal para probar la ingesta de datos, base de datos y visualización en el GUI.
- **Interacción**: Ignora comandos enviados por el servidor (no actúa).

### 2. ACTUATOR (Reactivo)
- **Comportamiento**: Simula un nodo actuador (ID 3) que responde a comandos.
- **Uso**: Ideal para probar la lógica de control, `SET_GPIO`, secuencias y confirmaciones (`ACK`).
- **Interacción**:
    - Responde a `PING` con `ACK`.
    - Responde a `SET_GPIO` con `DataReport` indicando el nuevo estado.

### 3. MIXED (Híbrido)
- **Comportamiento**: Combina ambas estrategias anteriores.
- **Uso**: Pruebas de integración completa y concurrencia.
- **Detalle**: Ejecuta el bucle de sensores en segundo plano mientras espera comandos para el actuador.

## Configuración

Para activar el modo Mock y seleccionar el tipo:

**En `.env`:**
```ini
DEMETER_MOCK=True
DEMETER_MOCK_MODE=MIXED  # Opciones: SENSORS, ACTUATOR, MIXED
```

**Ejecución Manual:**
```bash
# Modo Actuador
DEMETER_MOCK=True DEMETER_MOCK_MODE=ACTUATOR python3 Python/main_async.py

# Modo Sensores
DEMETER_MOCK=True DEMETER_MOCK_MODE=SENSORS python3 Python/main_async.py
```

## Cambios Recientes (Refactorización)

- **Arquitectura**: Se migró de una clase monolítica a una arquitectura basada en estrategias (`SensorStrategy`, `ActuatorStrategy`, `MixedStrategy`).
- **Logs**: Se han eliminado todos los emojis de los logs para asegurar compatibilidad y limpieza en consolas de producción o CI/CD.
- **Settings**: Se unificó la carga de configuración utilizando `pydantic-settings` en `provider.py`.

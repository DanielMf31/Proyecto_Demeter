# Documentación del Módulo: `device_manager.py`

**Ubicación:** `Python/src/core/device_manager.py`

## Propósito
Actúa como la **Base de Datos en Memoria** del sistema. Carga el archivo `inventory.json` y ofrece métodos para consultar la configuración tanto de dispositivos individuales como del sistema global.

## Clases Principales

### `class DeviceManager`

#### Atributos
*   `self.devices`: Diccionario de dispositivos.
*   `self.global_config`: Configuración del sistema (Puertos, UI).

#### Métodos Clave

1.  **`load_inventory()`**
    *   Lee el JSON. Si falla, carga una configuración por defecto segura (Safe Mode) para que el programa no crashee.
    *   **Refactor:** Ahora también carga la sección `"config"` para eliminar hardcoding.

2.  **`get_config(key)`**
    *   Método universal para obtener ajustes.
    *   Ejemplo: `mgr.get_config("baud_rate")` devuelve `115200`.

3.  **`get_all_routes()`**
    *   **Crítico para V2:** Extrae todas las direcciones MAC del JSON y las devuelve en formato binario.
    *   La UI usa esto para enviar la tabla de enrutamiento al Gateway al arrancar.

## Archivo de Configuración (`inventory.json`)
El archivo JSON ahora tiene 3 secciones:
1.  `"config"`: Ajustes de la App (Puerto, Título).
2.  `"system"`: IDs reservados (Master, Gateway).
3.  `"devices"`: Lista de nodos físicos.

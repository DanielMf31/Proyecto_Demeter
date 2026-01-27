# Documentación del Módulo: `main_window.py`

**Ubicación:** `Python/src/ui/main_window.py`

## Propósito
Interfaz Gráfica de Usuario (GUI) basada en Tkinter. Su objetivo es ser "Dumb" (Tonta): no contiene lógica de negocio, solo muestra lo que hay en el `DeviceManager` y pasa comandos al `Gateway`.

## Clases Principales

### `class MainWindow(tk.Tk)`

#### Conceptos Clave
1.  **Factory Pattern (Generación Dinámica):**
    *   No hay botones fijos ("BtnBomba").
    *   El constructor itera sobre `device_manager.devices`. Por cada entrada, instancia un `Frame` con botones ON/OFF.
    *   Esto permite añadir 50 dispositivos al JSON y la UI se adapta sola (Layout Grid automático).

2.  **Config Driven UI:**
    *   El título de la ventana y su tamaño (`geometry`) se leen del JSON de configuración, no están escritos en el código.

#### Interacción con otros Módulos
*   **Al pulsar ON:**
    1.  Llama a `protocol.create_set_gpio(ID, PIN, 1)`.
    2.  Pasa el resultado a `gateway.send_frame()`.
*   **Al pulsar "Connect":**
    1.  Inicia el `Gateway`.
    2.  Dispara la **Sincronización de Rutas** (`sync_routes`), que envía todas las MACs al hardware.

#### Eventos
*   Usa `gateway.set_callback` para recibir logs del hardware y pintarlos en la consola (o en pantalla en futuras versiones).

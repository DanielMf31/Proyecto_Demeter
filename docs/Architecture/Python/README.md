# Arquitectura Backend Python (Raspberry Pi)

Este directorio documenta la estructura del software que corre en el Host (Raspberry Pi/PC).

## Módulos Principales

### 1. Interfaz de Usuario (UI)
*   **`mvp_gui.py`:** Punto de entrada de la aplicación gráfica MVP.
*   **`ui/main_window.py`:** Implementación de la ventana principal en Tkinter. Maneja eventos de usuario y actualización optimista de la UI.

### 2. Lógica de Protocolo (`protocols/`)
*   **`protocol_v2.py`:** Implementación del Estándar Demeter V2. Serializa objetos Pydantic a bytes y viceversa.
*   **`schemas_protocol.py`:** Definición de modelos de datos (Comandos) usando Pydantic.

### 3. Transporte (`transport/`)
*   **`uart.py`:** Implementación del driver serial. Corre en un hilo separado para no bloquear la UI.
*   **`interface.py`:** Interfaz base `TransportStrategy` para permitir futuros transportes (WiFi/MQTT).

## Flujo de Ejecución (MVP)

1.  **Usuario** presiona un botón en `MainWindow`.
2.  **App** actualiza el color del botón (UI Optimista).
3.  **Protocolo** serializa el comando `SetGpio` a bytes.
4.  **Transporte** envía los bytes por `/dev/serial0`.
5.  **Listener** (Hilo UART) escucha respuestas (ACKs) y las loguea.

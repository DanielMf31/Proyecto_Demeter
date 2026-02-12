# Interfaz Gráfica (`gui_app.py` / `gui_main_ctk.py`)

La interfaz de usuario permite el control y monitoreo del sistema Demeter desde un entorno de escritorio.

## 1. Tecnologías
*   **Framework**: `customtkinter` (Modern UI para Tkinter).
*   **Comunicación**: Sockets TCP Asyncio (Cliente).
*   **Patrón**: MVVM (Model-View-ViewModel) en la versión profesional (`gui_main_ctk.py`).

## 2. Arquitectura (Versión Profesional)

### ViewModel (`DemeterViewModel`)
*   Desacopla la lógica de red de la vista.
*   Mantiene el estado de la conexión y las colas de mensajes.
*   Expone métodos asíncronos (`send_command`, `send_ping`) que la UI invoca de forma segura (thread-safe).

### Vistas (`views.py`)
Componentes modulares de la UI:
*   **Sidebar**: Estado de conexión y navegación.
*   **ControlPanel**: Botones para GPIO y Actuadores.
*   **SequencePlanner**: Interfaz para crear listas de pasos (secuencias) visualmente.
*   **LogConsole**: Visualizador de logs en tiempo real.

## 3. Características Clave

### Control de Actuadores
*   **Ventana (Nodo 3)**:
    *   Botones Abrir/Cerrar que envían `SET_GPIO` (Pin 2).
    *   Indicador de estado visual (Rojo/Verde) basado en `PinReport`.
    *   Indicador de batería basado en `SystemReport` o `DataReport` (según versión).

### Feedback en Tiempo Real
La GUI escucha pasivamente eventos del servidor:
*   `TempHumReport` -> Actualiza gráficas o logs.
*   `SystemReport` -> Actualiza voltaje de batería.

## 4. Ejecución
*   **Prototipo**: `python Python/src/proyecto_demeter/ui/gui_app.py`
*   **Pro**: `python Python/main_gui.py`

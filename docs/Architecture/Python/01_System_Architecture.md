# 1. Arquitectura del Sistema Python (System Architecture)

El backend de Python (`proyecto_demeter`) está diseñado como un servicio asíncrono robusto que actúa como puente entre la interfaz de usuario (GUI/CLI) y el hardware físico (Red de Nodos).

## Visión General

La arquitectura sigue un modelo **Cliente-Servidor Asíncrono** desacoplado:

1.  **Servicio Core (`DemeterService`):** Proceso demonio que maneja la conexión UART y el estado del protocolo.
2.  **Capa de Transporte:** Abstracción sobre `asyncio` para comunicaciones seriales no bloqueantes.
3.  **Interfaz IPC (TCP Socket):** Permite que múltiples clientes (GUI, TUI, Scripts) envíen comandos y reciban eventos en tiempo real.

### Diagrama de Componentes

```mermaid
graph TD
    User[Usuario (GUI/CLI)] -->|JSON/TCP| Server[Demeter Async Service]
    Server -->|Bytes/UART| Transport[Async UART Transport]
    Transport -->|Serial| Gateway[Hardware Gateway ESP32]
    
    Gateway -->|ESP-NOW| Node1[Nodo Riego]
    Gateway -->|ESP-NOW| Node2[Nodo Sensor]

    subgraph "Python Backend"
        Server
        Transport
        Protocol[Protocol Engine V2]
    end
```

## Estructura del Proyecto

El código fuente se encuentra en `Python/src/proyecto_demeter` y se organiza de la siguiente manera:

*   **`core/`**: Lógica central del servicio.
    *   `async_service.py`: Clase principal `DemeterService`. Maneja el bucle de eventos, servidor TCP y buffer UART.
*   **`transport/`**: Adaptadores de entrada/salida.
    *   `async_uart.py`: Wrapper de `serial_asyncio`.
*   **`protocols/`**: Implementación del estándar de comunicación.
    *   `protocol_v2.py`: Serializador/Deserializador binario.
*   **`shared/`**: Modelos de datos compartidos.
    *   `schemas.py`: Modelos Pydantic (`GpioCommand`, `DataReport`).
*   **`ui/`**: Interfaces de usuario (GUI CustomTkinter).

## Puntos de Entrada

### 1. Backend Service (`main_async.py`)
Es el punto de entrada principal para el servicio.
*   **Responsabilidad:** Iniciar el proceso de fondo, configurar logging, manejar señales de terminación (`SIGINT`, `SIGTERM`) y asegurar que el puerto del socket esté libre.
*   **Ejecución:** Usa `subprocess` para lanzar `async_service.py` en un entorno aislado y robusto.

### 2. GUI Pro (`main_gui.py`)
Lanzador de la interfaz gráfica profesional.
*   **Responsabilidad:** Configurar variables de entorno (`HOST`, `PORT`), lanzar la ventana de Login y posteriormente la aplicación principal (`DemeterApp`).

---
**Siguiente:** Ver [Núcleo Asíncrono y Eventos](02_Async_Core_&_Events.md) para detalles de implementación.

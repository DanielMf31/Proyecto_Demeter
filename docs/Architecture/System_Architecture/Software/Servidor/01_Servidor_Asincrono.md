# Servidor Asincrónico (`async_service.py`)

El **Servidor** es el núcleo de la lógica de negocio en la Raspberry Pi. Escrito en Python con `asyncio`, orquesta la comunicación entre el Hardware (UART/Mock), la Persistencia (SQLite) y los Clientes (GUI).

## 1. Responsabilidades

*   **Gestión de Hardware**: Inicializa y maneja la conexión UART con el Gateway.
*   **Servidor TCP**: Expone un socket en el puerto `8888` para permitir que múltiples clientes (GUI, CLI) envíen comandos y reciban datos en tiempo real.
*   **Persistencia**: Guarda automáticamente todos los reportes de sensores en la base de datos SQLite.
*   **Logging**: Mantiene un registro detallado de operaciones para depuración.

## 2. Componentes Principales

### `DemeterService`
Clase principal que inicializa los subsistemas:
1.  **Transporte**: `AsyncUartTransport` (Hardware Real) o `MockTransport` (Simulación).
2.  **Protocolo**: Instancia de `DemeterProtocolV2` para parseo de tramas binarias.
3.  **Gestor de Datos**: `DatabaseManager` para inserciones asíncronas.

### Flujo de Datos
1.  **Entrada UART**: `on_uart_data` recibe bytes -> `process_buffer` busca tramas `0xFE` -> `protocol.parse_frame`.
2.  **Procesamiento**:
    *   Si es `TempHumReport`: Se guarda en DB y se hace broadcast a clientes TCP.
    *   Si es `PinReport`: Se hace broadcast para actualizar UI.
3.  **Entrada TCP (Comandos)**:
    *   Recibe JSON (`GPIO_CMD`, `PING_CMD`).
    *   Valida con Pydantic (`GpioCommand`).
    *   Serializa a binario y envía al Gateway vía UART.

## 3. Configuración
Se alimenta de `config/provider.py` (variables de entorno o `.env`):
*   `DEMETER_PORT`: Puerto Serial (e.g., `/dev/ttyUSB0`).
*   `DEMETER_MOCK`: `True`/`False`.
*   `DEMETER_MOCK_MODE`: `SENSORS`, `ACTUATOR`, `MIXED`.

## 4. Ejecución
Archivo de entrada: `Python/main_async.py` (Wrapper que configura logs y lanza el servicio).

# Manual Técnico: Backend Python (Demeter V2)

**Estado:** Activo
**Versión Protocolo:** 2.1
**Ubicación:** `proyecto_demeter/python/`

## 1. Visión General
El Backend Python actúa como el cerebro de alto nivel del sistema Demeter. Se ejecuta en Raspberry Pi (u otro Linux).
Responsabilidades:
1.  **Orquestación:** Carga secuencias y decide cuándo ejecutarlas.
2.  **Abstracción:** Oculta la complejidad del protocolo binario tras la clase `DeviceManager`.
3.  **Interfaz:** Provee API para la UI (Tkinter) o Servicios Web.

## 2. Estructura del Código

### 2.1 Módulos Principales (`src/proyecto_demeter/protocols/`)
*   **`device_manager.py`:** 
    *   Carga `config/inventory.json`.
    *   Mapea Nombres ("Bomba Norte") a IDs (10) y MACs.
    *   *Singleton* que centraliza el conocimiento del sistema.
*   **`protocol_v2.py`:**
    *   Motor de serialización.
    *   Convierte Objetos Pydantic (`SetGpio`) a Bytes (`b'\xFE...'`).
    *   Valida CRC.
*   **`uart_gateway.py`:**
    *   Maneja el hilo de comunicación serial (`/dev/ttyACM0`).
    *   Cola de mensajes thread-safe.

### 2.2 Modelos de Datos (`schemas_protocol.py`)
Usamos **Pydantic** para validar todo antes de enviarlo.
*   `DemeterCommand`: Clase base.
*   `SetGpio`, `SetPwm`, `ExecSequence`: Comandos específicos.

## 3. Configuración (`config/inventory.json`)
El sistema no tiene hardcode. Todo está aquí:
```json
{
    "system": { "gateway_id": 1 },
    "nodes": [
        { "id": 10, "name": "Bomba Norte", "mac": "AA:BB:CC..." }
    ]
}
```

## 4. Flujo de Trabajo Típico
1.  Usuario pulsa botón en UI.
2.  UI llama a `DeviceManager.get_node_id("Bomba Norte")`.
3.  UI crea `cmd = SetGpio(target=10, pin=4, val=1)`.
4.  UI pasa `cmd` al `UartGateway`.
5.  Gateway serializa (`protocol.serialize(cmd)`) y envía bytes.
6.  Hilo de lectura recibe `ACK`, decodifica y notifica a la UI.

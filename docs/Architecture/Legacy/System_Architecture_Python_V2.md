# Arquitectura del Sistema Python V2 (Demeter)

**Estado:** Activa (En desarrollo)
**Versión Protocolo:** 2.1 (Binario)
**Framework UI:** Tkinter
**Concurrencia:** Threading + Queue

## 1. Visión General
El sistema Demeter V2 abandona el modelo de scripts monolíticos de la V1 para adoptar una arquitectura de **Micro-Kernel Modular**. El objetivo es la robustez, la testabilidad y la separación estricta de responsabilidades.

### Diagrama de Paquetes
```text
Python/
├── config/              # Configuración (NO CÓDIGO)
│   └── inventory.json   # Base de datos de dispositivos y ajustes globales
├── src/                 # Código Fuente (Paquetes)
│   ├── core/            # Lógica Pura (Sin UI, Sin Hardware)
│   │   ├── __init__.py
│   │   ├── device_manager.py
│   │   └── protocol_v2.py
│   ├── transport/       # Abstracción de Hardware
│   │   ├── __init__.py
│   │   └── uart_gateway.py
│   ├── ui/              # Interfaz Gráfica
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── legacy/          # Código V1 (Archivado)
└── main.py              # Entry Point
```

## 2. Componentes Clave

### A. Core (`src.core`)
*   **`DeviceManager`:** Es la "Autoridad de la Verdad". Carga `inventory.json` y resuelve nombres como "Bomba Norte" a tuplas `(NodeID=10, Pin=4)`. También provee la configuración global (Puertos, Baudrates).
*   **`DemeterProtocolV2`:** Implementación pura del estándar binario. No tiene efectos secundarios.
    *   **Input:** Comandos abstractos.
    *   **Output:** `bytes` con Header + CRC.

### B. Transport (`src.transport`)
*   **`UartGateway`:** Implementa el patrón **Producer-Consumer**.
    *   Corre en un `Thread` separado (Daemon).
    *   Consume `bytes` de una `Queue` (Cola) thread-safe.
    *   Escribe en el puerto Serial físico.
    *   Lee del puerto Serial y decodifica tramas `0xFE` (Sync).

### C. UI (`src.ui`)
*   **`MainWindow`:** Interfaz "declarativa". No contiene lógica de botones hardcodeada. Lee el inventario al inicio y genera los controles necesarios dinámicamente.

## 3. Análisis de Trama (Binary forensics)

Análisis real de una trama capturada en simulación (`simulate_workflow.py`):

`FE 21 01 00 01 30 04 0A 10 04 01 D0 07 00 00 ...`

| Byte(s) | Valor | Significado |
| :--- | :--- | :--- |
| **0** | `FE` | **SYNC:** Inicio de trama. |
| **1** | `21` | **LEN:** 33 bytes de payload. |
| **2** | `01` | **FLAGS:** ACK Request. |
| **3** | `00` | **SRC:** Master. |
| **4** | `01` | **DST:** Gateway. |
| **5** | `30` | **CMD:** `EXEC_SEQUENCE`. |
| **6** | `04` | **COUNT:** 4 pasos en la lista. |
| **7..14**| `0A...` | **PASO 1:** Encender Bomba (ID 10) por 2000ms. |

Esta capacidad de empaquetar secuencias complejas en un solo envío atómico es la mayor ventaja de V2 sobre V1.

## 4. Estrategia Legacy
El código de la versión anterior se ha movido a `src/legacy/` y `tests/legacy/`.
*   **Motivo:** Referencia histórica y rollback de emergencia.
*   **Estado:** Deprecado. No se mantiene activamente.

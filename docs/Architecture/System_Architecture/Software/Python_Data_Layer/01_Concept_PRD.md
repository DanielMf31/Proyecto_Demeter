# Product Requirement Document (PRD): Python Data Layer

| Atributo | Valor |
| :--- | :--- |
| **Título** | Capa de Persistencia y Logging de Datos de Sensores |
| **Estado** | Borrador |
| **Autor** | Agent (Antigravity) |
| **Fecha** | 10-Feb-2026 |

## 1. Introducción

El sistema actual transmite datos desde el Node al Gateway y este al Backend Python, pero los datos son efímeros; se envían a la GUI y se pierden. Se requiere un sistema robusto para persistir estos datos con fines de monitoreo histórico, análisis y visualización (ej. Grafana).

## 2. Objetivos

1.  **Persistencia Estructurada:** Almacenar todas las mediciones de sensores en una base de datos relacional ligera (SQLite).
2.  **Logging Redundante:** Generar archivos de log planos (`sensors.log`) específicos para mediciones, separados del log del sistema.
3.  **Visualización:** Estructurar la base de datos para facilitar su consulta por herramientas como Grafana.
4.  **No Bloqueante:** La escritura en disco/DB no debe bloquear el bucle de eventos principal (Async IO).

## 3. Requerimientos Funcionales

### 3.1 Base de Datos (`DatabaseManager`)
*   **Motor:** SQLite3 (archivo local `demeter_data.db`).
*   **Esquema:** Tabla `sensor_readings` con columnas:
    *   `id` (PK, Auto Increment)
    *   `timestamp` (DATETIME, ISO8601 o Epoch con microsegundos)
    *   `node_id` (INTEGER)
    *   `sensor_type` (TEXT, ej. "DHT22", "DS18B20") - *Nota: El protocolo actual no envía tipo, solo valores. Se inferirá o se añadirá metadata.* -> Para MVP V2, usaremos `measurement_type` (Temperatura, Humedad).
    *   `temperature` (REAL, Nullable)
    *   `humidity` (REAL, Nullable)
*   **Consultas:** Capacidad de recuperar promedio, min, max por rango de fechas.

### 3.2 Logging (`SensorLogger`)
*   **Archivo:** `logs/sensors.log` (Rotación diaria o por tamaño).
*   **Formato:** CSV o JSON Lines para fácil parseo.
    *   `TIMESTAMP, NODE_ID, TEMP, HUM`

### 3.3 Integración
*   El `DemeterService` debe interceptar los eventos `DATA_REPORT` y pasarlos al Data Layer de forma asíncrona ("Fire and Forget" o `await` rápido).

## 4. Requerimientos No Funcionales

*   **Performance:** Operaciones DB optimizadas (uso de transacciones o batch insert si la frecuencia es alta).
*   **Concurrencia:** Uso de `aiosqlite` o ejecución en `ThreadPoolExecutor` para no bloquear `asyncio` loop.
*   **Robustez:** Manejo de errores de disco/DB sin crashear el servicio principal.

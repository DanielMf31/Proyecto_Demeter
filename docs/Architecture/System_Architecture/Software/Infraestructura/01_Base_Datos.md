# Infraestructura de Datos

## 1. Base de Datos (`database.py`)
El sistema utiliza **SQLite** para un almacenamiento ligero y sin servidor, ideal para Raspberry Pi.

*   **Librería**: `aiosqlite` (Acceso asíncrono para no bloquear el bucle principal).
*   **Ubicación**: `Python/data/demeter_data.db`.

### Esquema
Tabla principal `sensor_readings`:
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Identificador único auto-incremental. |
| `timestamp` | DATETIME | Fecha/Hora UTC de registro. |
| `node_id` | INTEGER | ID del nodo origen (e.g., 2, 10, 11). |
| `temperature` | REAL | Valor de temperatura en °C. |
| `humidity` | REAL | Valor de humedad relativa en %. |

### Índices
Se crean índices en `timestamp` y `node_id` para acelerar consultas de históricos y gráficas.

## 2. Sistema de Logs
Además de la consola, el sistema puede rotar logs en archivo para auditoría a largo plazo.
Configurado en `async_service.py` mediante el módulo `logging` estándar de Python.

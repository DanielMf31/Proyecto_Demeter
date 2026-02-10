# Gestión de Datos y Mantenimiento

Este manual describe cómo administrar, respaldar y consultar los datos generados por el sistema Proyecto Demeter.

## 1. Ubicación de los Datos

El sistema almacena la información en dos ubicaciones principales dentro del directorio del proyecto (o directorio de despliegue):

| Tipo de Dato | Ubicación Relativa | Archivo Principal | Descripción |
| :--- | :--- | :--- | :--- |
| **Base de Datos** | `Python/data/` | `demeter_data.db` | Archivo SQLite con histórico de mediciones. |
| **Logs de Sensores** | `Python/logs/` | `sensors.log` | Registro CSV de mediciones (rotativo). |
| **Logs del Sistema** | `Python/logs/` | *variable* | Logs de depuración del servicio (si configurado). |

## 2. Base de Datos (SQLite)

### 2.1 Acceso Directo
Puede acceder a la base de datos utilizando cualquier cliente compatible con SQLite (DBeaver, DB Browser for SQLite) o mediante la línea de comandos:

```bash
cd Python/data
sqlite3 demeter_data.db
```

### 2.2 Consultas Útiles
Una vez dentro de la consola `sqlite3`:

**Ver últimas 10 mediciones:**
```sql
SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;
```

**Estadísticas de hoy por nodo:**
```sql
SELECT node_id, AVG(temperature), AVG(humidity) 
FROM sensor_readings 
WHERE date(timestamp) = date('now') 
GROUP BY node_id;
```

### 2.3 Mantenimiento (VACUUM)
SQLite es un archivo único. Con el tiempo, si se borran datos, el archivo puede fragmentarse. Se recomienda ejecutar mensualmente:
```sql
VACUUM;
```

## 3. Logs de Sensores

El archivo `sensors.log` rota automáticamente cuando alcanza los **10 MB**.
*   Se mantienen hasta 5 versiones antiguas (`sensors.log.1`, `...`).
*   Formato CSV compatible con Excel/LibreOffice Calc.

**Ejemplo de contenido:**
```csv
2026-02-10 15:30:01,123,25.50,60.20
2026-02-10 15:30:05,124,26.10,58.50
```

## 4. Respaldos (Backups)

Para evitar pérdida de datos históricos, se recomienda configurar una tarea programada (`cron`) que copie el archivo `.db` a una ubicación segura.

**Ejemplo de script de backup:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
cp /opt/demeter/Python/data/demeter_data.db /backup/demeter_data_$DATE.db
gzip /backup/demeter_data_$DATE.db
```

> **Nota:** SQLite permite copiar el archivo incluso mientras está en uso, aunque para una integridad perfecta se recomienda usar el comando `.backup` de la CLI de sqlite3.

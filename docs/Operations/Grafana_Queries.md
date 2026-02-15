# 📊 Queries de Grafana para Proyecto Demeter

Aquí tienes las consultas SQL exactas para visualizar los datos en Grafana usando el plugin de **SQLite**.

### Tabla de Datos: `sensor_readings`
Columnas: `timestamp`, `node_id`, `temperature`, `humidity`.

---

## 1. Monitorizar Temperatura (Gráfico A)
Usa esta query para crear un gráfico de línea (Time Series) de la temperatura.

**Panel Settings:**
*   **Data Source:** Demeter SQLite
*   **Format:** Time Series

```sql
SELECT 
  timestamp, 
  temperature 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```
*(Nota: Cambia `node_id = 2` si tu sensor tiene otro ID. El Nodo 2 es el Sensor Ambiental por defecto).*

---

## 2. Monitorizar Humedad (Gráfico B)
Grafana necesita que la columna de tiempo se llame `time` y esté en formato Unix Epoch (segundos).

**Query para Temperatura:**
```sql
SELECT 
  strftime('%s', timestamp) as time,
  temperature 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

**Query para Humedad:**
```sql
SELECT 
  strftime('%s', timestamp) as time,
  humidity 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

**Query Combinada:**
```sql
SELECT 
  strftime('%s', timestamp) as time,
  temperature,
  humidity
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

---

## 5. Debug: Ver Datos en Crudo (Tabla)
Si no ves gráficos, usa esta query y cambia la visualización a **"Table"** para ver si Grafana está leyendo *algo*.

```sql
SELECT 
  timestamp, 
  node_id,
  temperature,
  humidity
FROM sensor_readings
ORDER BY timestamp DESC
LIMIT 10
```
*(Si esto muestra datos pero el gráfico no, el problema es el formato de fecha).*

---

## 4. Estadísticas (Stat Panel)
Para ver el valor actual (último recibido) en grande.

**Temperatura Actual:**
```sql
SELECT 
  temperature 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp DESC 
LIMIT 1
```

**Humedad Actual:**
```sql
SELECT 
  humidity 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp DESC 
LIMIT 1
```

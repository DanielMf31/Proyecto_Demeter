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
Usa esta query para crear un gráfico de línea (Time Series) de la humedad.

**Panel Settings:**
*   **Data Source:** Demeter SQLite
*   **Format:** Time Series

```sql
SELECT 
  timestamp, 
  humidity 
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```

---

## 3. Monitorizar Temperatura + Humedad (Combinado)
Si quieres ver ambos en el mismo gráfico.

```sql
SELECT 
  timestamp, 
  temperature,
  humidity
FROM sensor_readings 
WHERE node_id = 2 
ORDER BY timestamp ASC
```
*(En la pestaña "Overrides" del panel a la derecha, puedes asignar ejes Y diferentes si las escalas son muy distintas).*

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

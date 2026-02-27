# 📊 Guía de Monitorización: PostgreSQL y Redis (TUI)

Esta guía contiene los comandos esenciales para supervisar el estado del sistema Demeter directamente desde la terminal del servidor usando herramientas de interfaz de texto (TUI).

---

## 🐘 PostgreSQL (con `pgcli`)

`pgcli` es un cliente avanzado para Postgres con auto-completado y colores.

### 1. Conexión
```bash
# Desde el host (si tienes pgcli instalado)
pgcli -h localhost -p 5432 -U postgres -d demeter_db

# Si prefieres usar el "psql" estándar dentro del contenedor:
docker exec -it demeter-db psql -U postgres -d demeter_db
```
*(Contraseña por defecto: `password`)*

### 2. Comandos de Inspección Rápidos (Comandos `\`)
* `\dt`: Listar todas las tablas creadas.
* `\d nombre_tabla`: Ver la estructura (columnas) de una tabla específica.
* `\x auto`: Activa el modo expandido (ideal para ver filas con muchas columnas).
* `\watch X`: Repite la última consulta cada X segundos (¡Modo monitor!).

### 3. Consultas de Monitorización Útiles

#### Ver Telemetría en Tiempo Real
Ideal para ver si los sensores de temperatura/humedad están reportando.
```sql
SELECT * FROM telemetry_th ORDER BY timestamp DESC LIMIT 10;
\watch 1
```

#### Histórico de Pines (Bombas/Válvulas)
Ver los últimos cambios de estado confirmados por el hardware.
```sql
SELECT * FROM pin_history ORDER BY timestamp DESC LIMIT 5;
```

#### Log de Actividad (Pulsaciones de botones)
Ver las acciones manuales del usuario (procesadas por lotes).
```sql
SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 10;
```

#### Estadísticas Rápidas
```sql
-- ¿Cuántos reportes tenemos hoy?
SELECT node_id, COUNT(*) 
FROM telemetry_th 
WHERE timestamp > CURRENT_DATE 
GROUP BY node_id;
```

---

## 🏎️ Redis (Pub/Sub y Caché)

Útil para ver el flujo de mensajes entre el Backend y la Raspberry.

### 1. Monitorizar Comandos (Pub/Sub)
Para ver los comandos JSON en el momento exacto en que se envían:
```bash
docker exec -it demeter-redis redis-cli SUBSCRIBE demeter:commands
```

### 2. Ver Eventos del Sistema
```bash
docker exec -it demeter-redis redis-cli SUBSCRIBE iot_events
```

### 3. Inspeccionar el Caché de Estados (60s)
Para ver si un pin está en el caché temporal de 60 segundos:
```bash
# Ver el valor (ON/OFF)
docker exec -it demeter-redis redis-cli GET demeter:cache:device:4

# Ver cuánto tiempo le queda de vida al caché
docker exec -it demeter-redis redis-cli TTL demeter:cache:device:4
```

### 4. Modo Monitor (Todo lo que pasa en Redis)
```bash
docker exec -it demeter-redis redis-cli MONITOR
```

---

## 🛠️ Otros comandos de soporte

### Ver logs del Backend
Si algo falla en las inserciones de la base de datos:
```bash
docker logs demeter-backend --tail 50 -f
```

### Reiniciar Stack de Base de Datos
```bash
docker-compose -f docker-compose.server.yml restart db redis backend
```

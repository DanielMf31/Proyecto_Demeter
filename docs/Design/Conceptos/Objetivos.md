# Guía Práctica: PostgreSQL + Redis en Docker

> **Contenedores reales del proyecto:**
> - PostgreSQL → `demeter-db` · base de datos: `demeter_db` · user: `postgres` · pass: `postgres_local_pass`
> - Redis → `demeter-redis` · DB 0 = caché general · DB 1 = cola RQ de workers

---

## 1. PostgreSQL (`demeter-db`)

### 1.1 Entrar a psql dentro del contenedor
```bash
docker exec -it demeter-db psql -U postgres -d demeter_db
```
> Ya estás dentro. Verás el prompt `demeter_db=#`

### 1.2 Ver todas las tablas
```sql
\dt                    -- tablas del schema public
\dt *.*                -- todas las tablas de todos los schemas
\d+ nombre_tabla       -- descripción detallada de una tabla (columnas, índices, FK)
```

### 1.3 Ver columnas de una tabla específica
```sql
\d plantas
\d mediciones
\d experimentos
```

### 1.4 Consultas básicas
```sql
-- Ver todas las plantas
SELECT id, name, especie_variedad, estado_vital, node_id FROM plantas;

-- Ver las últimas 20 mediciones
SELECT * FROM mediciones ORDER BY timestamp DESC LIMIT 20;

-- Ver experimentos con sus plantas
SELECT e.name AS experimento, p.name AS planta
FROM experimentos e
JOIN experimento_planta ep ON e.id = ep.experimento_id
JOIN plantas p ON ep.planta_id = p.id;
```

### 1.5 Ver actualizaciones en tiempo real (modo watch)
Abre **dos terminales**:

**Terminal 1 — Suscribirse a cambios:**
```sql
-- Dentro de psql
LISTEN demeter_updates;
-- Queda escuchando. Cada NOTIFY que llegue aparecerá aquí.
```

**Terminal 2 — Insertar datos de prueba en bucle:**
```bash
# Script que inserta 1 medición cada 3 segundos
watch -n 3 'docker exec demeter-db psql -U postgres -d demeter_db \
  -c "INSERT INTO mediciones (node_id, temperatura, humedad, timestamp) \
      VALUES (1, round((random()*10+20)::numeric,1), round((random()*20+60)::numeric,1), NOW()); \
      NOTIFY demeter_updates, '"'"'nueva_medicion'"'"';"'
```

O con un bucle bash más limpio:
```bash
while true; do
  docker exec demeter-db psql -U postgres -d demeter_db -c \
    "INSERT INTO mediciones (node_id, temperatura, humedad, timestamp)
     VALUES (1, round((random()*10+20)::numeric,1),
                round((random()*20+60)::numeric,1), NOW());"
  sleep 3
done
```

### 1.6 JOINs detallados
```sql
-- Mediciones de las plantas de un experimento específico (id=1)
SELECT
    p.name        AS planta,
    p.node_id,
    m.temperatura,
    m.humedad,
    m.timestamp
FROM mediciones m
JOIN plantas p ON p.node_id = m.node_id
JOIN experimento_planta ep ON ep.planta_id = p.id
WHERE ep.experimento_id = 1
ORDER BY m.timestamp DESC
LIMIT 50;

-- Estadísticas por planta (media, mín, máx)
SELECT
    p.name,
    COUNT(*) AS n,
    ROUND(AVG(m.temperatura)::numeric, 2) AS avg_temp,
    ROUND(MIN(m.temperatura)::numeric, 2) AS min_temp,
    ROUND(MAX(m.temperatura)::numeric, 2) AS max_temp
FROM mediciones m
JOIN plantas p ON p.node_id = m.node_id
GROUP BY p.name
ORDER BY avg_temp DESC;
```

**Atajos útiles de psql:**
```
\timing    → muestra tiempo de cada query
\x         → activa modo vertical (cada columna en su propia línea, ideal para filas anchas)
\q         → salir
\?         → ayuda completa de comandos \ 
\l         → listar bases de datos
```

---

## 2. Redis (`demeter-redis`)

### 2.1 Entrar a redis-cli
```bash
docker exec -it demeter-redis redis-cli
```
> Prompt: `127.0.0.1:6379>`

### 2.2 Operaciones principales

#### Strings (caché simple)
```redis
SET mi_clave "hola mundo"     -- guardar
GET mi_clave                   -- leer
TTL mi_clave                   -- cuántos segundos le quedan (-1 = sin expiración)
EXPIRE mi_clave 300            -- poner expiración de 5 min
DEL mi_clave                   -- borrar
```

#### Hashes (objetos)
```redis
HSET planta:1 name "Tomate-01" vpd_kpa 0.87 node_id 11
HGET planta:1 name
HGETALL planta:1               -- ver todos los campos del hash
HKEYS planta:1                 -- solo los nombres de los campos
```

#### Lists (cola FIFO)
```redis
RPUSH cola_tareas "tarea_a" "tarea_b"
LPOP cola_tareas               -- sacar el primero (worker consume así)
LRANGE cola_tareas 0 -1        -- ver toda la lista
LLEN cola_tareas               -- longitud
```

#### Sets y Sorted Sets
```redis
SADD alertas "nodo_3" "nodo_7"
SMEMBERS alertas
ZADD ranking 0.87 "nodo_1" 1.2 "nodo_3"   -- sorted set con score (VPD por ej.)
ZRANGE ranking 0 -1 WITHSCORES
```

### 2.3 Ver la estructura ACTUAL del proyecto en Redis
```bash
# Ver todas las claves (¡cuidado en producción con millones de claves!)
docker exec -it demeter-redis redis-cli KEYS "*"

# Buscar claves por patrón
docker exec -it demeter-redis redis-cli KEYS "demeter:plant_telemetry:*"
docker exec -it demeter-redis redis-cli KEYS "rq:*"

# Ver el tipo de una clave
docker exec -it demeter-redis redis-cli TYPE demeter:plant_telemetry:1

# Ver info del servidor (memoria, conexiones, versión)
docker exec -it demeter-redis redis-cli INFO server
docker exec -it demeter-redis redis-cli INFO memory

# Stats en tiempo real (refresco cada segundo)
docker exec -it demeter-redis redis-cli --stat
```

**Ver la telemetría cacheada de una planta:**
```bash
# JSON almacenado como String
docker exec demeter-redis redis-cli GET "demeter:plant_telemetry:1" | python3 -m json.tool

# Si es un Hash:
docker exec demeter-redis redis-cli HGETALL "demeter:plant_telemetry:1"
```

### 2.4 Pub/Sub — suscribirse a un canal en tiempo real
**Terminal 1 — Suscriptor:**
```bash
docker exec -it demeter-redis redis-cli SUBSCRIBE demeter_alerts
# Queda escuchando. Cada mensaje publicado aparece aquí.
```

**Terminal 2 — Publicar un mensaje de prueba:**
```bash
docker exec demeter-redis redis-cli PUBLISH demeter_alerts '{"node": 3, "vpd": 1.8, "alert": "stress"}'
```

Suscribirse a todos los canales del proyecto:
```bash
docker exec -it demeter-redis redis-cli PSUBSCRIBE "demeter_*"
# PSUBSCRIBE → suscripción con patrón wildcard
```

### 2.5 Ver la cola RQ (Redis Queue)
El proyecto usa la DB 1 para las colas de workers (`RQ_REDIS_URL=redis://...6379/1`):
```bash
# Cambiar a DB 1
docker exec -it demeter-redis redis-cli -n 1

# Ver las colas que existen
KEYS "rq:queue:*"

# Ver cuántos jobs hay en cola
LLEN rq:queue:demeter_tasks

# Ver los jobs pendientes (IDs)
LRANGE rq:queue:demeter_tasks 0 -1

# Ver el contenido de un job específico
HGETALL rq:job:<JOB_ID>
```

Levantar un worker en tiempo real y ver qué procesa:
```bash
docker exec -it demeter-math-worker bash -c \
  "rq worker demeter_tasks --url redis://demeter-redis:6379/1 --with-scheduler"
```

### 2.6 Entender el sistema de colas RQ

El flujo es:
```
API (Productor)
  └─► RPUSH rq:queue:demeter_tasks  ← mete el job
          │
          ▼
   demeter-math-worker (Consumidor)
          └─► LPOP rq:queue:demeter_tasks ← coge el job
          └─► Ejecuta la función Python
          └─► Guarda resultado en rq:job:<id>:result
```

Ver el resultado de un job completado:
```bash
docker exec demeter-redis redis-cli -n 1 HGETALL "rq:job:<ID>"
```

### 2.7 ¿Existe una UI visual para Redis?

Sí. Puedes levantar **Redis Commander** sin instalación:
```bash
docker run --rm -it \
  --network demeter-net \
  -p 8081:8081 \
  rediscommander/redis-commander \
  --redis-host demeter-redis

# Abrir en: http://localhost:8081
```

O instalar `redis-insight` (GUI oficial de Redis):
```bash
# Apunta a localhost:6379 mapeando el puerto primero:
docker run -d --name demeter-redis-tmp \
  --network demeter-net \
  -p 6380:6379 \
  redis:alpine redis-server --port 6379

# Luego conecta RedisInsight a localhost:6380
# Descarga: https://redis.io/insight/
```

---

## Resumen de Comandos de Entrada Rápida

```bash
# PostgreSQL
docker exec -it demeter-db psql -U postgres -d demeter_db

# Redis DB0 (caché general)
docker exec -it demeter-redis redis-cli

# Redis DB1 (cola workers)
docker exec -it demeter-redis redis-cli -n 1

# Stats Redis en vivo
docker exec -it demeter-redis redis-cli --stat

# Monitor Redis (TODOS los comandos en tiempo real)
docker exec -it demeter-redis redis-cli MONITOR
```
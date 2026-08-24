# Análisis del Backend Demeter — Guía de Dominio Completa

## Estructura de Directorios

```
Software/Servidor/Backend/
├── app.py                          # Entry point FastAPI + lifespan
├── Core/
│   ├── config.py                   # Proxy a Common/configuration.py
│   ├── database.py                 # AsyncEngine + SessionLocal + Base
│   ├── auth.py                     # JWT + bcrypt + OAuth2
│   ├── redis.py                    # RedisManager singleton
│   ├── startup.py                  # create_default_admin()
│   └── logger.py                   # Logging config
├── BD/
│   ├── models.py                   # SQLAlchemy ORM (12 tablas)
│   ├── schemas.py                  # Pydantic validation
│   ├── init_db.py                  # Creación de tablas (deshabilitado, Alembic)
│   └── seed_data.py                # Datos de prueba (20 plantas, 6 meses)
├── API/routers/
│   ├── auth_router.py              # /api/auth (login, register, me)
│   ├── command_router.py           # POST /api/command
│   ├── system_router.py            # /api/system (health check)
│   ├── discovery_router.py         # GET /api/devices
│   ├── lims_router.py              # /api/lims (plantas, experimentos, sensor-map)
│   ├── analysis_router.py          # /api/analysis (jobs RQ)
│   ├── export_router.py            # /api/export (ETL + zip)
│   ├── history_router.py           # /api/history (telemetría por nodo)
│   ├── sdk_router.py               # /api/sdk (acceso por API key)
│   └── ws_router.py                # WebSocket /ws/{client_id}
├── WS_Manager/
│   ├── manager.py                  # ConnectionRegistry (dict client_id→WS)
│   └── dispatcher.py               # Redis listener + gateway message handler
├── Worker/
│   └── tasks.py                    # Pipeline ETL (extract→transform→load)
├── Secuenciador/
│   └── main.py                     # APScheduler (sync horaria, demo, ETL nocturno)
├── Analisis_datos/
│   └── calculos_agronomicos.py     # VPD, punto de rocío, entalpía, etc.
├── alembic/                        # 3 migraciones
└── tests/                          # pytest
```

---

## Flujo de Datos Principal

```
Frontend → POST /api/command → Redis pub/sub "demeter:commands"
    → start_redis_listener() → registry.send("raspberry_gateway", cmd)
    → RPi WS client → UART → ESP32 → ESP-NOW → Nodo destino

Telemetría inversa:
Nodo → ESP-NOW → Gateway ESP32 → UART → RPi → WebSocket
    → handle_gateway_message() → INSERT DB + cache Redis + broadcast frontends
```

---

## Servicios Docker

| Servicio       | Rol                                                        |
| -------------- | ---------------------------------------------------------- |
| **api**        | FastAPI (uvicorn, puerto 8000) — endpoints REST + WS       |
| **math-worker**| RQ worker — consume cola `demeter_tasks` (export, análisis)|
| **sequencer**  | APScheduler — cronjobs periódicos                          |
| **db**         | PostgreSQL 15 — almacenamiento persistente                 |
| **redis**      | Cache + pub/sub + cola activity logs + cola RQ             |

---

## 40 Preguntas de Dominio con Respuestas

---

### Nivel 1: Arquitectura General

#### 1. ¿Cuál es el entry point del backend y qué hace el lifespan context manager?

El entry point es `app.py`. La función `create_application()` crea la instancia FastAPI y `lifespan()` es un `@asynccontextmanager` que gestiona el ciclo de vida:

**Startup:**
1. Espera 2s para warmup de PostgreSQL
2. Crea usuario admin por defecto via `create_default_admin()`
3. Siembra datos de prueba via `seed_historical_data()`
4. Conecta a Redis via `redis_manager.connect()`
5. Lanza 2 background tasks: `start_redis_listener()` y `start_activity_batch_flusher()`

**Shutdown:**
- Cierra la conexión Redis con `redis_manager.close()`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.sleep(2)  # warmup PostgreSQL
    async with AsyncSessionLocal() as session:
        await create_default_admin(session)
        await seed_historical_data(session)
    await redis_manager.connect()
    asyncio.create_task(start_redis_listener())
    asyncio.create_task(start_activity_batch_flusher())
    yield
    await redis_manager.close()
```

---

#### 2. ¿Qué 5 servicios Docker componen el backend y cuál es el rol de cada uno?

| Servicio       | Rol                                                               |
| -------------- | ----------------------------------------------------------------- |
| **api**        | FastAPI (uvicorn, puerto 8000) — endpoints REST + WebSocket       |
| **math-worker**| RQ worker — consume jobs de la cola `demeter_tasks`               |
| **sequencer**  | APScheduler — cronjobs (sync caché, demo data, ETL nocturno)     |
| **db**         | PostgreSQL 15 — almacenamiento persistente                        |
| **redis**      | Cache + pub/sub + cola de activity logs + cola RQ                 |

---

#### 3. ¿Cómo se organiza el código en módulos? Nombra los 7 directorios principales y su responsabilidad.

| Directorio        | Responsabilidad                                                   |
| ----------------- | ----------------------------------------------------------------- |
| `Core/`           | Infraestructura: config, database engine, auth JWT, Redis, logger |
| `BD/`             | ORM models, Pydantic schemas, init_db, seed_data                  |
| `API/routers/`    | 10 routers FastAPI (endpoints HTTP + WS)                          |
| `WS_Manager/`     | ConnectionRegistry (dict de WebSockets) + dispatcher de mensajes  |
| `Worker/`         | Pipeline ETL (extract→transform→load) para exportaciones          |
| `Secuenciador/`   | APScheduler daemon con 3 jobs programados                         |
| `Analisis_datos/` | Cálculos agronómicos (VPD, GDD, ET₀, etc.)                       |

---

#### 4. ¿Qué patrón usa FastAPI para inyectar la sesión de base de datos en los endpoints?

**Dependency Injection** con `Depends(get_db)`. La función `get_db()` en `Core/database.py` es un generador asíncrono que yield una `AsyncSession` y la cierra automáticamente al terminar el request:

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# En un endpoint:
async def endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model))
```

---

#### 5. ¿Por qué el backend usa `asyncpg` y no `psycopg2`? ¿Qué ventaja da?

Porque FastAPI es asíncrono (`async/await`). `asyncpg` es un driver **nativo asíncrono** para PostgreSQL que no bloquea el event loop, permitiendo manejar miles de conexiones concurrentes en un solo thread. `psycopg2` es síncrono y **bloquearía el event loop** en cada query, anulando la ventaja de FastAPI.

La URL de conexión refleja esto: `postgresql+asyncpg://...`

---

### Nivel 2: Base de Datos

#### 6. ¿Cuántas tablas hay y cuáles son las de telemetría? ¿Qué diferencia hay entre `TelemetryAmbient` y `TelemetrySoil`?

Hay **12 tablas** en total. Las de telemetría son:

| Tabla               | Contenido                                | Clave de indexación |
| ------------------- | ---------------------------------------- | ------------------- |
| `telemetry_ambient` | Temperatura y humedad del **aire**       | `node_id`           |
| `telemetry_soil`    | Temperatura y humedad del **suelo**      | `plant_id` (FK)     |
| `pin_history`       | Historial ON/OFF de relés (GPIO)         | `node_id`           |
| `system_history`    | Salud del gateway (modo, batería mV)     | `node_id`           |

**Diferencia clave:** `TelemetryAmbient` se indexa por `node_id` (sensor físico) — representa una medición ambiental genérica. `TelemetrySoil` se indexa por `plant_id` (planta lógica, resuelto via `PlantSensorMap`) — vincula la lectura directamente a una planta específica.

---

#### 7. ¿Qué es `PlantSensorMap` y qué problema resuelve?

Es una tabla que mapea `(node_id, sensor_slot)` → `plant_id`. Resuelve el **acoplamiento frágil** entre firmware y DB: sin ella, los IDs del firmware tendrían que coincidir exactamente con los IDs de plantas en la DB.

```python
class PlantSensorMap(Base):
    __tablename__ = "plant_sensor_map"
    id        = Column(Integer, primary_key=True)
    node_id   = Column(Integer, nullable=False, index=True)
    sensor_slot = Column(Integer, nullable=False)
    plant_id  = Column(Integer, ForeignKey("plants.id"), nullable=False)

    __table_args__ = (
        Index('uq_node_slot', 'node_id', 'sensor_slot', unique=True),
    )
```

El constraint único `(node_id, sensor_slot)` evita mapeos duplicados. El servidor es el **Source of Truth** — el firmware solo reporta datos crudos.

---

#### 8. ¿Cómo funciona la relación muchos-a-muchos entre `Plant` y `Experiment`?

Via la tabla puente `ExperimentoPlantaLink` con **clave primaria compuesta** `(experiment_id, plant_id)`:

```python
class ExperimentoPlantaLink(Base):
    __tablename__ = "experimento_planta_link"
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), primary_key=True)
    plant_id      = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True)
    linked_at     = Column(DateTime, default=datetime.utcnow)
```

SQLAlchemy usa `secondary="experimento_planta_link"` en ambos lados:
- `Experiment.plants = relationship("Plant", secondary=..., back_populates="experiments")`
- `Plant.experiments = relationship("Experiment", secondary=..., back_populates="plants")`

Ambas FK tienen `ondelete="CASCADE"` — si se borra una planta o experimento, los links se eliminan automáticamente.

---

#### 9. ¿Qué tipo de columna usa `metadata_cientifica` en `Plant` y por qué?

```python
metadata_cientifica = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default={})
```

Usa **JSONB** (en PostgreSQL). Permite almacenar atributos científicos dinámicos (variedad, sustrato, CE target, pH, ubicación) sin alterar el esquema relacional. JSONB soporta **indexación GIN** y consultas sobre campos internos (`metadata_cientifica->>'variedad'`), a diferencia de JSON plano que se almacena como texto sin indexar.

Ejemplo de contenido:
```json
{
  "variedad": "Cherry",
  "sustrato": "Fibra de coco",
  "ce_target_ds_m": 2.5,
  "ph_target": 6.2,
  "location": "Módulo A - Fila 1"
}
```

---

#### 10. ¿Qué hace `seed_data.py` al arrancar y cuántos registros genera aproximadamente?

Se ejecuta en el startup del app. Genera:

| Dato                   | Cantidad                                           |
| ---------------------- | -------------------------------------------------- |
| Plantas                | 20 (4 especies × 5 variedades)                     |
| Experimentos           | 3 ("Estrés Salino", "Lumínico", "Control General") |
| Telemetría ambiental   | ~86,400 registros (20 plantas × 180 días × 24h)    |
| Sensor maps            | 20 (1 por planta, slot 0)                           |
| Links planta-experimento | ~24 (~8 plantas por experimento)                  |

Pasos clave:
1. Limpia datos previos (DELETE plantas, experimentos, telemetría)
2. **Resetea secuencias:** `ALTER SEQUENCE plants_id_seq RESTART WITH 1` (IDs siempre 1-20)
3. Genera telemetría con **ciclo diurno sinusoidal** + ruido gaussiano via NumPy
4. Cachea todo en Redis: `demeter:plant_telemetry:{id}` y `demeter:raw_data:experimento_{id}`

---

#### 11. ¿Cómo se manejan las migraciones? Nombra las 3 migraciones de Alembic y qué hace cada una.

| Migración                                    | Qué hace                                                              |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `eb2b85ec72b6` — Initial LIMS Architecture   | Crea tablas base: users, devices, plants, experiments, activity_log, sequences, sequence_steps, telemetry_th, pin_history, system_history |
| `a1b2c3d4e5f6` — Rename Telemetry + Add Soil | Renombra `telemetry_th` → `telemetry_ambient`, añade `telemetry_soil` |
| `c3f4a5b6d7e8` — Add Plant Sensor Map        | Añade tabla `plant_sensor_map` con constraint único `(node_id, sensor_slot)` |

Se ejecutan con:
```bash
make dev-migrate    # Docker dev
make migrate        # Staging
```

Alembic usa `env.py` configurado con el async engine de SQLAlchemy y `Base.metadata` de `BD.models`.

---

### Nivel 3: WebSocket y Dispatcher

#### 12. ¿Qué es el `ConnectionRegistry` y cómo diferencia entre el gateway (RPi) y los frontends?

Es un **singleton** en `WS_Manager/manager.py` que mantiene un `Dict[str, WebSocket]` en memoria:

```python
class ConnectionRegistry:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}
```

La Raspberry se conecta con `client_id="raspberry_gateway"` (constante `GATEWAY_ID`). Los frontends usan cualquier otro ID.

Métodos clave:
- `send(client_id, payload)` — envía JSON a un cliente específico
- `broadcast_except(GATEWAY_ID, data)` — envía telemetría a **todos los frontends sin hacer eco** a la Raspberry
- `is_connected(GATEWAY_ID)` — comprueba si el gateway está online

---

#### 13. Explica el flujo completo cuando un usuario pulsa "Encender bomba" hasta que el ESP32 la enciende.

```
1.  Frontend: POST /api/command
    Body: {"type": "set_gpio", "target_id": 2, "pin": 4, "value": 1}
         │
2.  command_router.py: valida con TypeAdapter(AnyDemeterCommand)
    Publica en Redis canal "demeter:commands"
    Devuelve HTTP 202 ACCEPTED (fire-and-forget)
         │
3.  start_redis_listener() (background task):
    Recibe mensaje del canal Redis
    Valida de nuevo con Pydantic
    Comprueba: registry.is_connected("raspberry_gateway")
         │
4.  registry.send("raspberry_gateway", cmd_dict) → WebSocket JSON
         │
5.  RPi edge_server.py: recibe JSON, serializa a protocolo binario V2
    Frame: [0xFE][LEN][FLAGS][SRC=1][DST=2][CMD=0x10][pin=4,val=1][CRC]
         │
6.  UART → ESP32 Gateway
         │
7.  Gateway reenvía por ESP-NOW al nodo destino (target_id=2)
         │
8.  Nodo ejecuta SET_GPIO(pin=4, value=1) → relé ON
    Devuelve ACK
         │
9.  ACK viaja de vuelta:
    ESP-NOW → Gateway → UART → RPi → WebSocket
         │
10. handle_gateway_message({"type": "ack", ...})
    broadcast_except(GATEWAY_ID) → todos los frontends reciben confirmación
```

---

#### 14. ¿Qué hace `handle_gateway_message()` cuando recibe un `temp_hum_report`?

4 pasos secuenciales:

1. **Parse:** Instancia `TempHumReport(**data)` con Pydantic (valida campos)
2. **DB Persist:** Crea `TelemetryAmbient(node_id, air_temperature, air_humidity, timestamp=utcnow())` y hace `session.commit()`
3. **Redis Cache:** `redis_manager.save_telemetry(node_id, data)` con TTL 60s para acceso real-time
4. **Broadcast:** `registry.broadcast_except(GATEWAY_ID, report.model_dump())` — envía a todos los frontends conectados sin eco a la Raspberry

---

#### 15. ¿Qué es `start_activity_batch_flusher()` y por qué no se hace un INSERT por cada evento?

Es un background task que cada **1 segundo** extrae hasta 100 eventos de la lista Redis `demeter:activity:batch` y los inserta en batch en `ActivityLog`:

```python
async def start_activity_batch_flusher():
    while True:
        batch = await redis_manager.pop_activity_batch(100)
        if batch:
            async with AsyncSessionLocal() as session:
                for event in batch:
                    session.add(ActivityLog(...))
                await session.commit()
        await asyncio.sleep(1)
```

**¿Por qué batching?**
- Reduce presión de escritura en PostgreSQL (1 transacción con N inserts vs N transacciones)
- No bloquea el dispatcher (`command_router` solo hace `lpush` a Redis, que es O(1))
- Mejor rendimiento bajo carga alta de comandos

---

#### 16. ¿Qué pasa si el Raspberry Pi está desconectado y se envía un comando?

1. `command_router` publica igualmente en Redis y devuelve `{"status": "gateway_offline"}`
2. En `start_redis_listener()`, al ver `not registry.is_connected(GATEWAY_ID)`, hace broadcast a los frontends:

```json
{
  "type": "dispatcher_status",
  "status": "gateway_offline",
  "message": "Comando 'set_gpio' descartado: la Raspberry no está conectada."
}
```

**El comando se pierde** — no hay cola de reintentos ni persistencia de comandos pendientes.

---

### Nivel 4: Redis

#### 17. ¿Para qué usa el backend Redis? Nombra al menos 4 usos distintos.

| Uso                    | Key pattern                              | Detalle                                |
| ---------------------- | ---------------------------------------- | -------------------------------------- |
| 1. Pub/Sub comandos    | canal `demeter:commands`                 | Despacho Frontend → Raspberry          |
| 2. Cache telemetría    | `sensor:{id}:telemetry` (TTL 60s)       | Última lectura real-time               |
| 3. Cache estado        | `device:{id}:state` (persistente)        | Último ON/OFF conocido                 |
| 4. Cola batching       | lista `demeter:activity:batch`           | Activity logs pendientes               |
| 5. Cache discovery     | `demeter:discovery:config`               | Topología de dispositivos              |
| 6. Cache seed 6 meses  | `demeter:plant_telemetry:{id}`           | Telemetría histórica por planta        |
| 7. Cache datos ETL     | `demeter:calculated_data:experimento_{id}` | Resultados procesados (TTL 30 días)  |
| 8. Cola RQ             | DB 1 — cola `demeter_tasks`              | Jobs de exportación/análisis           |

---

#### 18. ¿Qué diferencia hay entre Redis DB 0 y DB 1?

| DB   | URL                      | Uso                                           |
| ---- | ------------------------ | --------------------------------------------- |
| DB 0 | `redis://redis:6379/0`   | Cache, pub/sub, batching — usado por la API   |
| DB 1 | `redis://redis:6379/1`   | Cola RQ `demeter_tasks` — usado por math-worker |

Separar DBs evita colisiones de keys entre la aplicación principal y el sistema de colas RQ.

---

#### 19. ¿Qué pasa si Redis no está disponible al arrancar?

`RedisManager.connect()` captura la excepción y setea `self.redis = None` (no hace raise):

```python
async def connect(self):
    try:
        self.redis = redis.from_url(settings.REDIS_URL, ...)
        await self.redis.ping()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running in Standalone Mode.")
        self.redis = None  # Fallback
```

La app entra en **modo Standalone**: todos los métodos comprueban `if not self.redis: return` y degradan graciosamente. Funcionalidad perdida: pub/sub, cache, batching, discovery. La API REST y la DB siguen funcionando.

---

#### 20. ¿Qué es el canal `demeter:commands` y quién publica/suscribe en él?

Es un canal Redis pub/sub para despacho de comandos:

- **Publica:** `command_router.py` cuando recibe `POST /api/command` → `redis.publish("demeter:commands", json)`
- **Suscribe:** `start_redis_listener()` en `dispatcher.py` — background task que valida con Pydantic y reenvía comandos a la Raspberry via WebSocket

Este desacoplamiento permite que el endpoint HTTP sea fire-and-forget (202) sin esperar al gateway.

---

### Nivel 5: Autenticación y Seguridad

#### 21. ¿Qué flujo sigue un login? ¿Qué formato tiene el token devuelto?

1. Frontend envía `POST /api/auth/login` con `username` y `password` (form-data OAuth2)
2. `auth_router` busca al usuario en DB por username
3. Verifica password con `bcrypt.checkpw(plain, hashed)` (timing-attack safe)
4. Si correcto → `create_access_token({"sub": username})` genera JWT firmado con HS256
5. Devuelve:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

El token contiene `{"sub": "admin", "exp": 1741XXX}` y expira en **7 días** (10080 minutos).

---

#### 22. ¿Qué roles existen y qué endpoint tiene restricción de rol?

**Roles:** `admin`, `user`, `operator`

- `POST /api/command` requiere rol **admin** u **operator** (verificado en el router)
- El resto de endpoints protegidos solo requieren `get_current_active_user` (cualquier rol activo)
- `/api/auth/register` y `/api/auth/login` son públicos (sin auth)

---

#### 23. ¿Cómo se autentica el SDK? ¿Dónde se guarda la API key?

Via header `X-API-Key`. Cada `Experiment` tiene un campo `api_key` (UUID auto-generado):

```python
api_key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
```

El endpoint `GET /api/sdk/mediciones/{experimento_id}` usa la dependencia:

```python
async def get_api_key_or_403(experimento_id, api_key_header=Depends(api_key_header_scheme), db=...):
    experiment = await db.execute(select(Experiment).where(Experiment.id == experimento_id))
    if experiment.api_key != api_key_header:
        raise HTTPException(403, "Invalid API Key")
```

No requiere JWT — es un mecanismo independiente para acceso programático del SDK Python.

---

#### 24. ¿Por qué `auth.py` es la única excepción a la convención de usar `datetime.utcnow()`?

Porque la librería `python-jose` (JWT) necesita **datetimes aware** (con `tzinfo`) para comparar la expiración del token correctamente:

```python
# auth.py — usa datetime AWARE (con timezone)
expire = datetime.now(timezone.utc) + timedelta(minutes=15)

# Resto del backend — usa datetime NAIVE (sin timezone)
timestamp = datetime.utcnow()
```

`datetime.utcnow()` devuelve naive (sin tzinfo). JWT necesita aware para calcular `exp` correctamente. El resto del backend usa naive UTC porque SQLAlchemy + PostgreSQL `TIMESTAMP WITHOUT TIME ZONE` lo manejan sin problemas.

---

### Nivel 6: Workers y Tareas en Background

#### 25. ¿Qué es RQ y cómo se usa para las exportaciones?

**RQ** (Redis Queue) es una librería Python de colas de trabajo basada en Redis.

Flujo:
1. `export_router` recibe `POST /api/export/plants` con `{experimento_id, fecha_referencia, rango_dias}`
2. Encola job `Worker.tasks.export_experiment_data` en cola `demeter_tasks` (Redis DB 1, timeout 10 min)
3. Devuelve `{status: "processing", job_id: "abc-123"}`
4. El servicio Docker **math-worker** (worker RQ) consume la cola y ejecuta el pipeline ETL
5. Frontend hace polling con `GET /api/export/status/{job_id}`
6. Cuando `status == "finished"` → descarga via `GET /api/export/download/{job_id}`

---

#### 26. Describe el pipeline ETL de `Worker/tasks.py`: ¿qué extrae, transforma y carga?

| Fase          | Qué hace                                                                                                   |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| **Extract**   | Lee telemetría de Redis cache (`demeter:raw_data:experimento_{id}`) o fallback a DB (TelemetryAmbient por node_id) |
| **Transform** | DataFrame Pandas → agrupa por node_id → `procesar_dataframe()` calcula VPD, punto de rocío, entalpía, heat index, frost risk, Z-scores, GDD, ET₀. Cachea en Redis (TTL 30 días) |
| **Load**      | Genera directorios por fecha/planta → Excel `.xlsx` + gráficas por día                                     |
| **Package**   | Comprime todo en ZIP → devuelve ruta `/app/Backend/exports/reporte_exp_1_xxxxx.zip`                         |

---

#### 27. ¿Qué 3 jobs tiene el Secuenciador (APScheduler) y cuándo se ejecuta cada uno?

| Job | Trigger               | Cuándo               | Función                         | Propósito                          |
| --- | --------------------- | -------------------- | ------------------------------- | ---------------------------------- |
| 1   | `cron(minute=0)`      | Cada hora en punto   | `sync_sensor_data_to_redis`     | Refrescar caché PostgreSQL → Redis |
| 2   | `interval(minutes=30)`| Cada 30 minutos      | `dummy_insert_test_data`        | Insertar telemetría fake para demo |
| 3   | `cron(hour=3, minute=0)` | 3:00 AM diario    | `enqueue_nightly_etl`           | Recalcular datos analíticos        |

---

#### 28. ¿Cómo puede un frontend saber si un job de exportación terminó?

**Polling.** El frontend hace `GET /api/export/status/{job_id}` periódicamente. RQ devuelve el estado:

| Estado     | Significado                                   |
| ---------- | --------------------------------------------- |
| `queued`   | En cola, esperando worker                     |
| `started`  | Worker lo está procesando                     |
| `finished` | Completado — respuesta incluye `download_url` |
| `failed`   | Error — respuesta incluye `error`             |
| `canceled` | Cancelado manualmente                         |

---

### Nivel 7: API Endpoints

#### 29. Nombra los 10 routers del backend y el prefijo URL de cada uno.

| Router             | Prefijo URL completo | Tags               |
| ------------------ | -------------------- | ------------------- |
| `system_router`    | `/api/system`        | System              |
| `ws_router`        | `/ws/{client_id}`    | WebSocket           |
| `command_router`   | `/api/command`       | Commands            |
| `discovery_router` | `/api/devices`       | Discovery           |
| `analysis_router`  | `/api/analysis`      | Analytics           |
| `auth_router`      | `/api/auth`          | Authentication      |
| `export_router`    | `/api/export`        | Exports             |
| `history_router`   | `/api/history`       | History             |
| `sdk_router`       | `/api/sdk`           | SDK Integration     |
| `lims_router`      | `/api/lims`          | LIMS Architecture   |

---

#### 30. ¿Qué hace `POST /api/command`? ¿Es síncrono o fire-and-forget?

**Fire-and-forget** (HTTP 202 ACCEPTED).

1. Valida el body con `TypeAdapter(AnyDemeterCommand).validate_python(body)`
2. Publica el JSON en Redis canal `demeter:commands`
3. Si es `set_gpio`: cachea estado en Redis (60s TTL) + encola evento de actividad
4. Comprueba si RPi está conectada via `registry.is_connected(GATEWAY_ID)`
5. Devuelve inmediatamente:

```json
{
  "status": "queued",
  "message": "Comando 'set_gpio' enqueued correctly.",
  "command_type": "set_gpio"
}
```

**No espera confirmación** del hardware. La confirmación llega asincrónicamente via WebSocket (ACK/NACK).

---

#### 31. ¿Cómo funciona el endpoint de descubrimiento de dispositivos (`/api/devices`)?

Lee la key `demeter:discovery:config` de **Redis** (no de DB). Esta key la setea `handle_gateway_message()` cuando recibe un mensaje `system_config` de la Raspberry:

```python
if msg_type == "system_config":
    await redis_manager.redis.set("demeter:discovery:config", json.dumps(devices))
```

Respuestas:
- Si key existe → `{"status": "online", "devices": {...}}`
- Si no existe → `{"status": "pending"}` (Raspberry nunca envió su config)

Es un **reflejo del estado real** de los dispositivos reportados por el firmware.

---

#### 32. ¿Qué hace el LIMS router? ¿Qué operaciones CRUD permite?

**Plantas:**
| Método | Ruta                          | Propósito                                         |
| ------ | ----------------------------- | ------------------------------------------------- |
| GET    | `/lims/plantas`               | Listar todas las plantas                          |
| GET    | `/lims/plantas/{id}`          | Detalle de planta + experimentos asociados         |
| GET    | `/lims/plantas/{id}/telemetry`| Lee Redis cache directo (0 queries DB, instantáneo)|
| POST   | `/lims/plantas`               | Crear nueva planta                                |
| PATCH  | `/lims/plantas/{id}`          | Actualizar metadata (campos opcionales)           |

**Experimentos:**
| Método | Ruta                          | Propósito                                 |
| ------ | ----------------------------- | ----------------------------------------- |
| GET    | `/lims/experimentos`          | Listar con plantas asociadas              |
| POST   | `/lims/experimentos/generar`  | Crear experimento + vincular plantas M2M  |

**Sensor Map:**
| Método | Ruta                          | Propósito                                 |
| ------ | ----------------------------- | ----------------------------------------- |
| GET    | `/lims/sensor-map`            | Listar todos los mapeos                   |
| POST   | `/lims/sensor-map`            | Upsert mapeo (idempotente)                |
| DELETE | `/lims/sensor-map/{id}`       | Eliminar mapeo                            |

---

### Nivel 8: Cálculos Agronómicos

#### 33. ¿Qué es el VPD y cómo se calcula?

**VPD** = Déficit de Presión de Vapor (kPa). Mide la **capacidad de secado del aire** — la diferencia entre la presión de vapor de saturación y la real. Controla la transpiración de la planta.

**Fórmula (ecuación de Tetens):**
```
es = 0.6108 × exp((17.27 × T) / (T + 237.3))   → presión de saturación (kPa)
ea = es × (HR / 100)                              → presión actual (kPa)
VPD = es - ea                                      → déficit (kPa)
```

| VPD (kPa) | Significado                    |
| ---------- | ------------------------------ |
| < 0.4      | Aire saturado, riesgo fúngico  |
| 0.4 – 1.6  | Rango ideal para cultivos     |
| > 1.6      | Estrés hídrico, cierre estomas |

---

#### 34. ¿Qué otros cálculos implementa `calculos_agronomicos.py`?

| Cálculo                    | Unidad   | Propósito                                |
| -------------------------- | -------- | ---------------------------------------- |
| Punto de rocío             | °C       | Temp. a la que condensa el aire          |
| Temp. bulbo húmedo         | °C       | Enfriamiento evaporativo                 |
| Humedad absoluta           | g/m³     | Agua por volumen de aire                 |
| Humedad específica         | kg/kg    | Agua por masa de aire                    |
| Relación de mezcla         | kg/kg    | Ratio vapor/aire seco                    |
| Entalpía                   | kJ/kg    | Contenido energético del aire húmedo     |
| Heat Index                 | °C       | Sensación térmica                        |
| GDD (Growing Degree Days)  | °C-días  | Acumulación térmica (Tbase=10°C)         |
| Horas frío                 | horas    | Horas entre 0-7.2°C (vernalización)     |
| CHU (Corn Heat Units)      | —        | Índice térmico específico para maíz      |
| ET₀ (Hargreaves)           | mm/día   | Evapotranspiración de referencia         |
| Riesgo Wallin              | 0-4      | Severidad de riesgo fúngico              |
| Z-Scores (temp, humedad)   | SD       | Detección de anomalías                   |
| ΔT/h                       | °C/h     | Tasa de cambio horaria de temperatura    |
| LSD                        | kPa      | Diferencia leaf-air (estrés hídrico)     |
| Frost Point                | °C       | Temperatura de riesgo de helada          |

La función principal `procesar_dataframe(df_crudo)` devuelve:
- `df_horario` — datos horarios con las 18+ columnas calculadas
- `df_resumen` — estadísticas resumidas del periodo

---

### Nivel 9: Configuración y Despliegue

#### 35. ¿Dónde se definen las variables de entorno y cómo las lee el backend?

En `Software/Common/configuration.py`, clase `Settings(BaseSettings)` de Pydantic. Lee automáticamente variables con prefijo `DEMETER_` desde archivos `.env`:

```python
class Settings(BaseSettings):
    APP_NAME: str = "Demeter IoT System"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://..."
    REDIS_URL: str = "redis://redis:6379/0"
    # ...

    class Config:
        env_prefix = "DEMETER_"
        env_file = ".env"
```

Los archivos `.env.local`, `.env.staging`, `.env.prod`, `.env.rpi` se copian a `.env` por los targets del Makefile. `Core/config.py` es un proxy que importa y expone `get_settings()`.

---

#### 36. ¿Qué diferencia hay entre `make dev`, `make staging` y `make rpi-up`?

| Comando          | Env file       | Qué hace                                                        |
| ---------------- | -------------- | ---------------------------------------------------------------- |
| `make dev`       | `.env.local`   | Todo local: frontend :5173 (hot reload) + API :8000              |
| `make staging`   | `.env.staging`  | Pull GHCR + Cloudflare Tunnel a `patata.monters.org`            |
| `make rpi-up`    | `.env.rpi`     | Solo gateway RPi: host networking + serial passthrough `/dev/serial0` |

---

#### 37. ¿Cómo se expone el staging al exterior?

Via **Cloudflare Tunnel** (servicio `cloudflared` en docker-compose de staging). Crea un túnel seguro desde el servidor local hasta `patata.monters.org` sin necesidad de:
- Abrir puertos en el router
- Configurar DNS manualmente
- Gestionar certificados SSL (Cloudflare lo hace automáticamente)

---

#### 38. ¿Por qué el docker-compose base no expone puertos?

Para que cada entorno defina sus propios puertos via **docker-compose overrides**:
- **Dev:** Expone 5173 (frontend) + 8000 (API)
- **Staging:** Usa Cloudflare Tunnel (no necesita puertos expuestos directamente)
- **RPi:** Usa host networking (accede a `/dev/serial0`)

Esto sigue el **principio de composición** de Docker Compose y evita conflictos entre entornos.

---

### Nivel 10: Protocolos Compartidos

#### 39. ¿Qué son las "discriminated unions" de Pydantic y cómo se usan en los comandos?

Es un mecanismo donde Pydantic usa un campo literal (`type`) como **discriminador** para saber qué subclase instanciar automáticamente al deserializar JSON.

Cada comando define su `type` como un `Literal`:
```python
class SetGpio(DemeterCommand):
    type: Literal["set_gpio"] = "set_gpio"
    pin: int
    value: int

class Ping(DemeterCommand):
    type: Literal["ping"] = "ping"
```

Al parsear `{"type": "set_gpio", "pin": 4, "value": 1, "target_id": 2}`, Pydantic automáticamente crea un `SetGpio` sin lógica manual de switch/case. Si el `type` no coincide con ningún Literal, lanza `ValidationError`.

---

#### 40. ¿Qué es `AnyDemeterCommand` y dónde se usa?

Es una **Annotated Union** con discriminador definida en `Software/Common/schemas.py`:

```python
AnyDemeterCommand = Annotated[
    Union[
        SetGpio, SetPwm, ExecSequence, GetSensors,
        Ping, Ack, Nack, Syn, SynAck, RouteAdd,
        TempHumReport, SensorClusterReport, PinReport, SystemReport,
    ],
    Field(discriminator="type"),
]
```

Agrupa los **14 tipos** de comandos/reportes posibles. Se usa con `TypeAdapter`:

```python
cmd = TypeAdapter(AnyDemeterCommand).validate_python(json_dict)
```

**Dónde se usa:**
- `command_router.py` — validar body del `POST /api/command`
- `dispatcher.py` — validar mensajes del canal Redis antes de reenviar a la Raspberry
- RPi `edge_server.py` — deserializar comandos recibidos por WebSocket

Es la **pieza clave** que unifica la serialización JSON entre Frontend, Backend y Raspberry usando el mismo esquema compartido en `Software/Common/`.

---

## Patrones de Diseño del Backend

| Patrón                          | Implementación                                                    |
| ------------------------------- | ----------------------------------------------------------------- |
| **Async Throughout**            | FastAPI + asyncpg + redis.asyncio + `asyncio.create_task()`      |
| **Pub/Sub Desacoplado**         | Redis `demeter:commands` separa HTTP endpoints del gateway WS     |
| **Activity Batching**           | Lista Redis → flush cada 1s → reduce presión DB                  |
| **Sensor Mapping (SoT)**       | Servidor es fuente de verdad; firmware solo reporta datos crudos  |
| **Graceful Degradation**        | Si Redis cae → modo standalone (API + DB siguen funcionando)      |
| **Naive UTC Convention**        | Todos los timestamps sin tzinfo excepto JWT (que necesita aware)  |
| **Discriminated Unions**        | Campo `type` como discriminador en Pydantic para 14 tipos         |
| **Dependency Injection**        | `Depends(get_db)`, `Depends(get_current_active_user)`, etc.      |
| **Singleton Pattern**           | `redis_manager`, `registry` — instancia única global              |
| **Fire-and-Forget Commands**    | HTTP 202 → Redis pub/sub → WS (no espera confirmación hardware)  |

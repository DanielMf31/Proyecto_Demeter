# Backend Demeter — Problemas que Resuelve y Cómo los Implementa

Este documento cataloga **todos los problemas técnicos** que el backend resuelve, agrupados por categoría. Para cada uno se explica el **concepto teórico** y la **implementación concreta** en el código.

---

## Índice

1. [Comunicación en Tiempo Real](#1-comunicación-en-tiempo-real)
2. [Desacoplamiento de Componentes](#2-desacoplamiento-de-componentes)
3. [Concurrencia y Rendimiento](#3-concurrencia-y-rendimiento)
4. [Persistencia y Modelado de Datos](#4-persistencia-y-modelado-de-datos)
5. [Autenticación y Autorización](#5-autenticación-y-autorización)
6. [Procesamiento Pesado en Background](#6-procesamiento-pesado-en-background)
7. [Caching y Acceso Rápido a Datos](#7-caching-y-acceso-rápido-a-datos)
8. [Resiliencia y Tolerancia a Fallos](#8-resiliencia-y-tolerancia-a-fallos)
9. [Gestión Científica de Datos (LIMS)](#9-gestión-científica-de-datos-lims)
10. [Mapeo Hardware-Software](#10-mapeo-hardware-software)
11. [Observabilidad y Auditoría](#11-observabilidad-y-auditoría)
12. [Validación y Seguridad de Tipos](#12-validación-y-seguridad-de-tipos)
13. [Configuración y Despliegue Multi-Entorno](#13-configuración-y-despliegue-multi-entorno)
14. [Inicialización y Arranque Autónomo](#14-inicialización-y-arranque-autónomo)

---

## 1. Comunicación en Tiempo Real

### Problema 1.1: Entregar telemetría al frontend sin polling

**Problema:** Los sensores ESP32 generan datos cada pocos segundos. Si el frontend hiciera polling HTTP cada segundo, la carga en el servidor sería insostenible y la latencia inaceptable.

**Concepto:** WebSocket — protocolo full-duplex sobre TCP que mantiene una conexión abierta. El servidor puede hacer push al cliente sin que este lo pida.

**Implementación:**
- `ws_router.py:28` — Endpoint `/ws/{client_id}` acepta conexiones WebSocket
- `manager.py` — `ConnectionRegistry` mantiene un `Dict[str, WebSocket]` en memoria
- `dispatcher.py:125` — Cuando llega telemetría de la Raspberry, `broadcast_except(GATEWAY_ID, data)` la envía a todos los frontends conectados en tiempo real
- Los frontends se conectan con cualquier `client_id` y reciben push de telemetría sin hacer ninguna petición

### Problema 1.2: Comunicar bidireccional con el edge (Raspberry Pi)

**Problema:** El backend necesita enviar comandos a la Raspberry Y recibir telemetría de vuelta, todo por el mismo canal persistente.

**Concepto:** WebSocket bidireccional con roles asimétricos — el mismo socket transporta comandos (servidor→RPi) y telemetría (RPi→servidor).

**Implementación:**
- La Raspberry se conecta como `client_id="raspberry_gateway"` (`dispatcher.py:56`)
- `ws_router.py:52-54` — Si `is_gateway`, los mensajes entrantes se procesan via `handle_gateway_message(data)`
- `ws_router.py:62-66` — Si NO es gateway (frontend), los mensajes se ignoran y se responde con un aviso informativo
- `dispatcher.py:306` — El listener de Redis envía comandos al gateway via `registry.send(GATEWAY_ID, cmd.model_dump())`

### Problema 1.3: Evitar eco de mensajes al emisor

**Problema:** Si la Raspberry envía telemetría y el servidor la retransmite a TODOS los WebSockets, la Raspberry recibiría su propio mensaje de vuelta — un bucle inútil.

**Concepto:** Broadcast selectivo con exclusión del emisor.

**Implementación:**
- `manager.py:56-63` — `broadcast_except(exclude_id, payload)` itera todos los clientes activos y salta al `exclude_id`
- `dispatcher.py:95,125,165,192,216` — Cada tipo de telemetría usa `broadcast_except(GATEWAY_ID, ...)` para enviar solo a frontends

---

## 2. Desacoplamiento de Componentes

### Problema 2.1: Separar el envío de comandos HTTP del despacho al hardware

**Problema:** Si el endpoint HTTP enviara el comando directamente por WebSocket, quedaría acoplado al estado de la conexión RPi. Si la Raspberry está lenta o desconectada, el endpoint HTTP se bloquearía.

**Concepto:** Patrón Pub/Sub — un intermediario (Redis) desacopla al productor (endpoint HTTP) del consumidor (listener que despacha al WebSocket).

**Implementación:**
- **Productor:** `command_router.py:118-119` — `redis.publish("demeter:commands", payload_json)` y devuelve HTTP 202 inmediatamente
- **Intermediario:** Redis canal `demeter:commands`
- **Consumidor:** `dispatcher.py:259-327` — `start_redis_listener()` se suscribe al canal, valida el mensaje y lo reenvía al gateway via WebSocket
- El endpoint HTTP nunca toca el WebSocket directamente — solo publica en Redis

### Problema 2.2: Frontend desacoplado del protocolo WebSocket para envíos

**Problema:** Gestionar reconexiones WebSocket, heartbeats y estados en el browser es complejo y frágil. Si el WS se cae, los comandos se pierden silenciosamente.

**Concepto:** Separación de canales — HTTP para comandos (request-response fiable), WebSocket solo para recepción de push.

**Implementación:**
- `command_router.py` docstring explica las ventajas: sin gestión de reconexión, respuesta HTTP inmediata, testeable con curl/Swagger
- `ws_router.py:56-66` — Si un frontend intenta enviar comandos por WS, recibe un aviso: *"Para enviar comandos usa POST /api/command"*
- El WS queda reservado exclusivamente para push de telemetría servidor→frontend

### Problema 2.3: Protocolo compartido entre 3 capas (Frontend, Backend, Raspberry)

**Problema:** Si cada capa define sus propios modelos de datos, las incompatibilidades y bugs de serialización son inevitables.

**Concepto:** Esquema compartido (Single Source of Truth) — un único archivo de definiciones usado por todas las capas.

**Implementación:**
- `Software/Common/schemas.py` — Define TODOS los modelos de comandos y reportes
- Backend lo importa en `command_router.py:42` y `dispatcher.py:44-52`
- Raspberry lo importa desde el mismo path compartido
- La serialización JSON incluye el campo `type` para que cualquier extremo pueda deserializar correctamente

---

## 3. Concurrencia y Rendimiento

### Problema 3.1: Manejar miles de conexiones sin threads

**Problema:** Un servidor tradicional (Flask + gunicorn) usa un thread/proceso por conexión. Con WebSockets de larga duración + peticiones HTTP simultáneas, el consumo de RAM escala linealmente.

**Concepto:** Event Loop asíncrono (asyncio) — un solo thread multiplexado. Las operaciones I/O (DB, Redis, WS) son `await` y liberan el loop mientras esperan.

**Implementación:**
- `app.py` — FastAPI es 100% async
- `database.py:8` — `create_async_engine` con driver `asyncpg` (no bloquea el event loop)
- `redis.py:31` — `redis.asyncio.from_url()` (cliente Redis async)
- `database.py:15` — `AsyncSession` con `expire_on_commit=False` y `autoflush=False` para evitar queries implícitos
- `dispatcher.py:67-68` — Background tasks lanzados con `asyncio.create_task()`

### Problema 3.2: Evitar bloqueo de DB por escrituras frecuentes de activity logs

**Problema:** Cada comando `set_gpio` genera un evento de actividad. Si se hace un INSERT síncrono por cada evento, se bloquea el dispatcher y se saturan las conexiones de DB bajo carga.

**Concepto:** Write Batching — acumular eventos en una cola en memoria (Redis list) y vaciarlos periódicamente en un solo commit.

**Implementación:**
- `command_router.py:128-132` — `redis_manager.push_activity_event({...})` hace `LPUSH` a la lista `demeter:activity:batch` (O(1))
- `dispatcher.py:226-254` — `start_activity_batch_flusher()` cada 1 segundo ejecuta:
  - `pop_activity_batch(100)` — extrae y borra atómicamente hasta 100 eventos via pipeline Redis (`LRANGE` + `LTRIM`)
  - Inserta todos en un solo `session.commit()` — 1 transacción en vez de 100
- Si el flusher falla, duerme 5 segundos y reintenta (los eventos no se pierden porque siguen en la lista Redis)

### Problema 3.3: Evitar N+1 en queries de relaciones

**Problema:** Si al listar experimentos SQLAlchemy carga las plantas lazy (una query por experimento), con 50 experimentos serían 51 queries.

**Concepto:** Eager Loading — cargar las relaciones en la misma query (JOIN o subquery).

**Implementación:**
- `lims_router.py:118` — `select(Experiment).options(selectinload(Experiment.plants))` carga plantas en una segunda query SELECT IN (2 queries totales, no N+1)
- `lims_router.py:36` — `selectinload(Plant.experiments)` para el detalle de planta
- `lims_router.py:167-169` — `selectinload(PlantSensorMap.plant)` para sensor maps

---

## 4. Persistencia y Modelado de Datos

### Problema 4.1: Almacenar series temporales eficientemente en SQL

**Problema:** La telemetría genera miles de registros por día. Las queries de rango temporal deben ser rápidas para gráficas y exportaciones.

**Concepto:** Indexación por timestamp en tablas de time series. No es un TSDB dedicado (TimescaleDB), pero los índices B-tree de PostgreSQL en columnas DateTime son eficientes para range scans.

**Implementación:**
- `models.py:186-189` — `TelemetryAmbient`: índices en `timestamp` (range scans) y `node_id` (filtrado por sensor)
- `models.py:200-201` — `TelemetrySoil`: índices en `timestamp` y `plant_id`
- `models.py:215-216` — `PinHistory`: índice en `timestamp` y `node_id`
- `models.py:228-229` — `SystemHistory`: idem
- `models.py:101-103` — `ActivityLog`: índice explícito `idx_activity_log_timestamp`
- `history_router.py:27-30` — Queries usan `timestamp >= limit_date` + `ORDER BY timestamp ASC` para aprovechar los índices

### Problema 4.2: Modelar datos científicos dinámicos sin alterar el esquema

**Problema:** Cada planta puede tener atributos científicos diferentes (variedad, sustrato, CE target, pH, ubicación). No se puede crear una columna por cada atributo posible.

**Concepto:** Columnas semi-estructuradas (JSONB) — permiten almacenar JSON con indexación y consultas a nivel de campo, combinando flexibilidad NoSQL con garantías ACID de PostgreSQL.

**Implementación:**
- `models.py:149` — `metadata_cientifica = Column(JSON().with_variant(JSONB, "postgresql"))`
- `schemas.py:109` — Pydantic lo valida como `Dict[str, Any]` (acepta cualquier estructura)
- `lims_router.py:52` — `PlantUpdate` permite actualizar parcialmente (`PATCH`) incluyendo metadata
- El seed genera datos variados por planta: `{"variedad": "Cherry", "sustrato": "Fibra de coco", ...}`

### Problema 4.3: Modelar relaciones muchos-a-muchos (Plantas ↔ Experimentos)

**Problema:** Una planta puede pertenecer a varios experimentos, y un experimento agrupa varias plantas. No se puede resolver con una FK simple.

**Concepto:** Tabla puente (Junction Table / Association Table) con clave primaria compuesta.

**Implementación:**
- `models.py:105-114` — `ExperimentoPlantaLink` con PK compuesta `(experiment_id, plant_id)`, ambas con `ondelete="CASCADE"`
- `models.py:131` — `Experiment.plants = relationship("Plant", secondary="experimento_planta_link")`
- `models.py:153` — `Plant.experiments = relationship("Experiment", secondary="experimento_planta_link")`
- `lims_router.py:144-149` — Al crear un experimento, se insertan los links uno a uno en la tabla puente

### Problema 4.4: Evolucionar el esquema sin perder datos

**Problema:** Cambiar el nombre de una tabla o añadir columnas en producción requiere migraciones controladas. Un `CREATE TABLE IF NOT EXISTS` no gestiona alteraciones.

**Concepto:** Database Migrations (Alembic) — scripts versionados que aplican cambios incrementales al esquema.

**Implementación:**
- `alembic/` con 3 migraciones encadenadas:
  1. `eb2b85ec72b6` — Esquema inicial (12 tablas base)
  2. `a1b2c3d4e5f6` — Renombra `telemetry_th` → `telemetry_ambient`, añade `telemetry_soil`
  3. `c3f4a5b6d7e8` — Añade `plant_sensor_map`
- `app.py:44` — `init_tables()` deshabilitado en favor de Alembic
- `Makefile` — `make dev-migrate` ejecuta `alembic upgrade head` en el contenedor

### Problema 4.5: Garantizar unicidad de entidades científicas

**Problema:** No puede haber dos plantas con el mismo identificador físico (código de barras) ni dos mapeos sensor-planta para el mismo slot.

**Concepto:** Constraints de unicidad en base de datos — la DB rechaza duplicados a nivel de engine, no depende de lógica de aplicación.

**Implementación:**
- `models.py:145` — `identificador_fisico = Column(String, unique=True, index=True)` en Plant
- `models.py:128` — `api_key = Column(String, unique=True, index=True)` en Experiment
- `models.py:170-172` — `Index('uq_node_slot', 'node_id', 'sensor_slot', unique=True)` en PlantSensorMap
- `lims_router.py:88-90` — Validación adicional en el endpoint antes de INSERT (defensa en profundidad)

---

## 5. Autenticación y Autorización

### Problema 5.1: Proteger endpoints sin estado de sesión en el servidor

**Problema:** En una API REST stateless, el servidor no almacena sesiones. Cada request debe llevar su propia credencial verificable.

**Concepto:** JWT (JSON Web Token) — token firmado criptográficamente que contiene claims (usuario, rol, expiración). El servidor solo necesita la clave secreta para verificarlo, sin consultar ninguna sesión almacenada.

**Implementación:**
- `auth.py:48-63` — `create_access_token()` genera JWT con HS256, payload `{"sub": username, "role": role, "exp": timestamp}`
- `auth.py:65-94` — `get_current_user()` decodifica el JWT, extrae `sub`, busca al usuario en DB y lo retorna
- `auth.py:96-106` — `get_current_active_user()` añade validación `is_active=True`
- `auth.py:22` — `OAuth2PasswordBearer(tokenUrl="/api/auth/login")` integra con Swagger para testing
- Token expira en 7 días (10080 min), configurable via env

### Problema 5.2: Almacenar contraseñas de forma segura

**Problema:** Si se almacena la contraseña en texto plano, un breach de DB expone todas las credenciales.

**Concepto:** Hashing con salt (bcrypt) — función one-way que genera un hash diferente cada vez gracias al salt aleatorio. Verificar es O(1) pero revertir es computacionalmente inviable.

**Implementación:**
- `auth.py:38-46` — `get_password_hash()` usa `bcrypt.gensalt()` + `bcrypt.hashpw()`
- `auth.py:24-36` — `verify_password()` usa `bcrypt.checkpw()` que es timing-attack safe (comparación en tiempo constante)
- `startup.py:27` — Admin por defecto creado con hash bcrypt, nunca texto plano
- `auth_router.py:30` — En registro, la contraseña se hashea antes de persistir

### Problema 5.3: Control de acceso basado en roles (RBAC)

**Problema:** No todos los usuarios deberían poder enviar comandos al hardware. Un "user" puede ver datos pero no activar una bomba.

**Concepto:** RBAC (Role-Based Access Control) — cada usuario tiene un rol, y ciertos endpoints requieren roles específicos.

**Implementación:**
- `models.py:22` — `role = Column(String, default="user")` — roles posibles: `admin`, `user`, `operator`
- `command_router.py:85-90` — Verificación explícita: `if current_user.role not in ["admin", "operator"]: raise HTTPException(403)`
- El resto de endpoints protegidos solo necesitan `Depends(get_current_active_user)` (cualquier rol activo)

### Problema 5.4: Acceso programático sin credenciales de usuario (SDK)

**Problema:** El SDK de Python necesita acceder a datos de un experimento sin hacer login como usuario. Necesita un mecanismo de auth simple y scoped.

**Concepto:** API Key — token opaco asociado a un recurso específico (experimento). Más simple que JWT, sin expiración, ideal para acceso M2M.

**Implementación:**
- `models.py:128` — `api_key = Column(String, unique=True, default=lambda: str(uuid.uuid4()))` — cada experimento genera su propia API key
- `auth.py:109` — `APIKeyHeader(name="X-API-Key")` — esquema de seguridad en header
- `auth.py:111-137` — `get_api_key_or_403()` compara el header con `experiment.api_key` en DB
- `sdk_router.py:22` — `Depends(get_api_key_or_403)` protege el endpoint sin JWT
- Scoped: la key solo da acceso al experimento al que pertenece, no a todo el sistema

---

## 6. Procesamiento Pesado en Background

### Problema 6.1: Exportaciones que tardan minutos sin bloquear la API

**Problema:** Generar un reporte con 6 meses de telemetría, calcular 18 métricas agronómicas, crear gráficas y empaquetar un ZIP puede tardar minutos. No se puede hacer en un request HTTP síncrono.

**Concepto:** Cola de trabajos (Job Queue) — el endpoint HTTP encola la tarea y devuelve un ID inmediatamente. Un worker separado ejecuta la tarea en background. El cliente hace polling para saber cuándo terminó.

**Implementación:**
- **Encolar:** `export_router.py:43-50` — `task_queue.enqueue("Worker.tasks.export_experiment_data", ..., job_timeout='10m')` — RQ (Redis Queue) en Redis DB 1
- **Worker:** Servicio Docker `math-worker` ejecuta `rq worker demeter_tasks`
- **Polling:** `export_router.py:57-75` — `GET /api/export/status/{job_id}` consulta estado del job via `Job.fetch()`
- **Descarga:** `export_router.py:78-99` — `GET /api/export/download/{job_id}` devuelve `FileResponse` del ZIP
- La función importada como string (`"Worker.tasks.export_experiment_data"`) evita cargar librerías pesadas (Pandas, NumPy) en la memoria de la API

### Problema 6.2: Pipeline ETL completo (Extract-Transform-Load)

**Problema:** Los datos crudos de telemetría no son útiles directamente. Necesitan ser extraídos, transformados con cálculos agronómicos, y cargados en formatos consumibles (Excel, gráficas, Redis cache).

**Concepto:** Pipeline ETL — cadena de procesamiento en 3 fases bien separadas.

**Implementación en `Worker/tasks.py`:**
- **Extract (líneas 52-93):** Intenta Redis cache `demeter:raw_data:experimento_{id}` → fallback a PostgreSQL (query TelemetryAmbient por node_ids del experimento, filtrado por rango de fechas)
- **Transform (líneas 100-131):** DataFrame Pandas → `groupby("node_id")` → `procesar_dataframe()` por cada nodo (calcula VPD, entalpía, Z-scores, etc.) → sanitiza NaN → cachea resultados en Redis con TTL 30 días
- **Load (líneas 133-191):** Crea estructura de directorios `Experimento_{id}/{fecha}/{Planta_{node}}/` → genera gráficas y Excel por día y planta → empaqueta en ZIP → limpia temp
- **Entry point:** `export_experiment_data()` (línea 203) es sync wrapper que llama `asyncio.run()` (RQ es síncrono, pero el ETL necesita async para Redis/DB)

### Problema 6.3: Tareas periódicas automatizadas (cronjobs)

**Problema:** Hay trabajo que debe ejecutarse en schedule fijo: refrescar caches, generar datos demo, recalcular analytics nocturnos.

**Concepto:** Task Scheduler (APScheduler) — daemon que ejecuta funciones en triggers configurables (cron, interval).

**Implementación en `Secuenciador/main.py`:**
- `scheduler.add_job(sync_sensor_data_to_redis, 'cron', minute=0)` — Cada hora: PostgreSQL → Redis cache
- `scheduler.add_job(dummy_insert_test_data, 'interval', minutes=30)` — Cada 30 min: datos fake para demo
- `scheduler.add_job(enqueue_nightly_etl, 'cron', hour=3, minute=0)` — 3AM: recalcular datos analíticos
- Corre como servicio Docker independiente (`sequencer`), no dentro de la API

---

## 7. Caching y Acceso Rápido a Datos

### Problema 7.1: Servir 6 meses de telemetría en milisegundos

**Problema:** Una query SQL de 180 días × 24 horas × 20 plantas = ~86,400 registros por planta tarda segundos. El frontend necesita respuesta instantánea para gráficas interactivas.

**Concepto:** Cache aside — precalcular y almacenar el resultado en Redis (memoria). La API lee directo de Redis sin tocar la DB.

**Implementación:**
- `seed_data.py` precalcula y guarda `demeter:plant_telemetry:{plant_id}` con toda la telemetría de 6 meses
- `lims_router.py:64-83` — `GET /lims/plantas/{id}/telemetry` lee directo de Redis: `redis.get(cache_key)` → `json.loads()` → return. **Cero queries a PostgreSQL.**
- `sdk_router.py:33-47` — El SDK intenta Redis primero (`demeter:raw_data:experimento_{id}`), fallback a DB solo si miss

### Problema 7.2: Estado de dispositivos disponible sin query

**Problema:** El frontend necesita saber el último estado conocido de un relé (ON/OFF). Hacer un query a DB por cada dispositivo en cada refresh es ineficiente.

**Concepto:** Cache de estado con TTL — Redis almacena el último estado conocido, con expiración para evitar datos stale.

**Implementación:**
- `redis.py:56-69` — `set_device_state(device_id, state)` → key `device:{id}:state` (sin TTL, persistente)
- `redis.py:71-82` — `cache_device_state(device_id, state, ttl=60)` → key `demeter:cache:device:{id}` (TTL 60s, para comandos recientes)
- `dispatcher.py:189` — Al recibir `pin_report`, actualiza el estado en Redis
- `command_router.py:125` — Al enviar `set_gpio`, cachea el estado esperado por 60s

### Problema 7.3: Telemetría real-time efímera

**Problema:** La última lectura de un sensor necesita ser accesible instantáneamente para dashboards, pero no vale la pena persistir cada lectura intermedia en DB.

**Concepto:** Cache efímero con TTL — la lectura se sobreescribe cada vez que llega una nueva y expira automáticamente si el sensor deja de reportar.

**Implementación:**
- `redis.py:97-108` — `save_telemetry(sensor_id, data, ttl=60)` → key `sensor:{id}:telemetry` (JSON, 60s TTL)
- `dispatcher.py:122` — Cada `temp_hum_report` actualiza la cache: `redis_manager.save_telemetry(node_id, report.model_dump())`
- Si el sensor se desconecta, la key expira sola en 60 segundos

---

## 8. Resiliencia y Tolerancia a Fallos

### Problema 8.1: Redis caído no debe tumbar la aplicación

**Problema:** Redis es útil pero no debe ser un SPOF (Single Point of Failure). Si Redis cae, la API debería seguir sirviendo datos desde PostgreSQL.

**Concepto:** Graceful degradation — detectar la indisponibilidad y continuar con funcionalidad reducida.

**Implementación:**
- `redis.py:28-41` — `connect()` captura excepciones y setea `self.redis = None` sin hacer raise
- `redis.py:64,79,105,121,137,145,153` — **Cada método** empieza con `if not self.redis: return` (o return valor por defecto)
- `command_router.py:106-114` — Si Redis no está disponible, el endpoint devuelve HTTP 503 con mensaje claro en vez de crash
- La API REST y PostgreSQL siguen funcionando. Se pierden: pub/sub, cache, batching, discovery.

### Problema 8.2: Gateway desconectado no debe bloquear comandos

**Problema:** Si la Raspberry se desconecta, los comandos no pueden llegar al hardware. Pero el usuario no debe quedarse sin feedback.

**Concepto:** Feedback inmediato con estado degradado — informar al usuario que el comando se aceptó pero no se puede entregar.

**Implementación:**
- `command_router.py:135-147` — Comprueba `registry.is_connected(GATEWAY_ID)`, devuelve `"status": "gateway_offline"` si no está
- `dispatcher.py:308-319` — El listener de Redis broadcast a los frontends: `{"type": "dispatcher_status", "status": "gateway_offline", "message": "Comando descartado: Raspberry no conectada"}`
- El comando se pierde (no hay cola de reintentos), pero el usuario lo sabe inmediatamente

### Problema 8.3: Errores de WebSocket no deben crashear el servidor

**Problema:** Un WebSocket puede cerrar inesperadamente (corte de red, crash del cliente). Si no se maneja, puede dejar recursos huérfanos.

**Concepto:** Cleanup explícito en desconexión — eliminar la referencia al cerrar, manejar excepciones de envío.

**Implementación:**
- `ws_router.py:68-73` — `except WebSocketDisconnect: registry.disconnect(client_id)` limpia el dict
- `manager.py:46-49` — `send()` envuelve en try/except; si falla, desconecta al cliente automáticamente
- `manager.py:53` — `broadcast()` itera sobre `list(self.active)` (copia) para evitar modificar el dict durante iteración

### Problema 8.4: Flusher de actividad tolerante a errores

**Problema:** Si el batch flusher falla (error de DB, conexión perdida), no debe morir permanentemente ni perder los eventos pendientes.

**Concepto:** Retry con backoff — ante error, esperar más tiempo antes de reintentar. Los eventos quedan seguros en la lista Redis.

**Implementación:**
- `dispatcher.py:250-254` — `except asyncio.CancelledError: break` (shutdown limpio) vs `except Exception: sleep(5)` (reintentar tras pausa)
- Los eventos no procesados permanecen en la lista Redis `demeter:activity:batch` hasta el próximo flush exitoso

---

## 9. Gestión Científica de Datos (LIMS)

### Problema 9.1: CRUD completo de inventario botánico

**Problema:** El sistema necesita registrar, consultar y actualizar plantas físicas con metadata científica rica (especie, variedad, fecha siembra, estado vital, sustrato, CE, pH...).

**Concepto:** LIMS (Laboratory Information Management System) — gestión de muestras físicas con trazabilidad completa.

**Implementación:**
- `models.py:133-153` — Modelo `Plant` con campos LIMS: `identificador_fisico` (barcode/etiqueta), `especie_variedad`, `fecha_siembra`, `estado_vital`, `metadata_cientifica` (JSONB)
- `schemas.py:99-125` — `PlantCreate` valida entrada, `PlantUpdate` permite PATCH parcial (`exclude_unset=True`)
- `lims_router.py:26-109` — CRUD completo: GET list, GET detail, POST create, PATCH update, GET telemetry

### Problema 9.2: Agrupar plantas en diseños experimentales

**Problema:** Un investigador necesita definir "Ensayo de Estrés Salino" con un subconjunto de plantas y obtener datos agregados solo de esas.

**Concepto:** Modelo experimental con agrupación flexible (M2M) y acceso por API Key para automatización.

**Implementación:**
- `models.py:116-131` — `Experiment` con `name`, `description`, `api_key` auto-generada, relación M2M con Plant
- `lims_router.py:123-156` — `POST /lims/experimentos/generar` recibe `plant_ids`, valida que existan, crea el experimento y los links M2M
- `sdk_router.py` — El SDK accede a los datos del experimento via API Key, obteniendo solo la telemetría de las plantas vinculadas

### Problema 9.3: Cálculos agronómicos completos desde datos crudos

**Problema:** Los datos de temperatura y humedad por sí solos no son accionables. El investigador necesita métricas derivadas: VPD para riego, GDD para fenología, riesgo Wallin para fumigación.

**Concepto:** Motor de cálculos agronómicos — biblioteca de funciones que transforma series temporales crudas en indicadores científicos.

**Implementación en `Analisis_datos/calculos_agronomicos.py`:**

| Categoría | Funciones | Indicadores | Uso agrícola |
|-----------|-----------|-------------|--------------|
| Termodinámica | `calcular_vpd`, `calcular_punto_rocio`, `calcular_entalpia`, `calcular_bulbo_humedo_stull` | VPD, Td, h, Twb | Control de riego, HVAC invernadero |
| Psicrometría | `calcular_humedad_absoluta`, `calcular_humedad_especifica`, `calcular_relacion_mezcla` | AH, SH, MR | Caracterización microclima |
| Fenología | `calcular_gdd`, `calcular_horas_frio`, `calcular_chu_maiz` | GDD, CH, CHU | Predicción cosecha, dormancia frutales |
| Estrés | `calcular_heat_index`, `calcular_lsd`, `calcular_frost_point` | HI, LSD, Tfrost | Alerta calor, estrés hídrico, helada |
| Hidrología | `calcular_eto_hargreaves` | ET₀ | Demanda hídrica de referencia |
| Fitopatología | `calcular_riesgo_wallin` | Wallin 0-4 | Riesgo tizón en solanáceas |
| Anomalías | `calcular_z_score` | Z-score | Detección sensores rotos/outliers |
| Estadística | `calcular_estadisticas` | μ, σ, CV, SEM | Resumen descriptivo |

- `procesar_dataframe(df_crudo)` es el motor central: toma un DataFrame con `[timestamp, temperature, humidity]` y devuelve `df_horario` (18+ columnas calculadas) + `df_resumen` (GDD total, ET₀, promedios, niveles riesgo)
- Llamado desde `Worker/tasks.py:110` en el pipeline ETL

---

## 10. Mapeo Hardware-Software

### Problema 10.1: Resolver qué planta corresponde a qué sensor físico

**Problema:** El firmware envía `(node_id=3, sensor_slot=0, temperature=23.5)`. La DB necesita saber que eso corresponde a `plant_id=7`. Hardcodear esto es frágil y no escalable.

**Concepto:** Tabla de mapeo configurable (indirection layer) — el servidor es Source of Truth del mapeo, no el firmware.

**Implementación:**
- `models.py:156-172` — `PlantSensorMap(node_id, sensor_slot, plant_id)` con constraint único
- `dispatcher.py:138-153` — Al recibir `sensor_cluster_report`:
  1. Query `SELECT * FROM plant_sensor_map WHERE node_id = X`
  2. Construye dict `{slot: plant_id}`
  3. Para cada entry del report, resuelve `plant_id = mappings.get(idx)`
  4. Si no hay mapping → `logger.warning()` y skip (no crash)
  5. Si hay → INSERT `TelemetrySoil(plant_id=plant_id, ...)`
- `lims_router.py:175-203` — CRUD de sensor maps: POST (upsert idempotente), GET (listar), DELETE (borrar)

### Problema 10.2: Descubrir dispositivos conectados dinámicamente

**Problema:** El frontend necesita saber qué bombas y válvulas hay conectadas sin hardcodear la lista. Si se añade un nuevo dispositivo, debe aparecer automáticamente.

**Concepto:** Service Discovery — el edge device (Raspberry) reporta su configuración al backend, que la cachea para consulta.

**Implementación:**
- `dispatcher.py:84-89` — Al recibir `system_config` del gateway: `redis.set("demeter:discovery:config", json.dumps(devices))`
- `discovery_router.py:25-52` — `GET /api/devices` lee la key de Redis y devuelve `{"status": "online"|"pending", "devices": {...}}`
- Zero hardcoding — si la Raspberry reporta nuevos dispositivos, el frontend los ve al siguiente refresh

---

## 11. Observabilidad y Auditoría

### Problema 11.1: Saber quién operó qué dispositivo y cuándo

**Problema:** En un entorno de investigación, se necesita trazabilidad completa: quién encendió la bomba, cuándo, y qué descripción tiene la acción.

**Concepto:** Audit Trail — tabla inmutable de eventos con timestamp, actor, acción y contexto.

**Implementación:**
- `models.py:82-103` — `ActivityLog(timestamp, user_id, device_id, action_type, description)` con índice en timestamp
- `command_router.py:128-132` — Cada `set_gpio` genera un evento: `{"action_type": "button_press", "description": "Manual toggle Node:X Pin:Y -> Z"}`
- `dispatcher.py:226-254` — El flusher persiste los eventos en batch a DB

### Problema 11.2: Logging estructurado por módulo

**Problema:** Con 10+ módulos (routers, dispatcher, redis, auth...), los logs sin estructura son ilegibles.

**Concepto:** Named loggers — cada módulo crea su propio logger con nombre identificable.

**Implementación:**
- `Core/logger.py` — `setup_logger(name)` crea un logger con formato `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`
- Cada archivo usa su nombre: `setup_logger("dispatcher")`, `setup_logger("ws_registry")`, `setup_logger("redis_manager")`
- Nivel configurable via `settings.DEBUG` (True=DEBUG, False=INFO)

---

## 12. Validación y Seguridad de Tipos

### Problema 12.1: Deserializar comandos heterogéneos desde un solo endpoint

**Problema:** `POST /api/command` recibe `set_gpio`, `ping`, `exec_sequence`, etc. — todos con campos diferentes. Necesita saber qué tipo es y validar los campos específicos de ese tipo.

**Concepto:** Discriminated Union (Tagged Union) — un campo (`type`) indica qué variante es. Pydantic instancia automáticamente la subclase correcta.

**Implementación:**
- `Common/schemas.py:154-172` — `AnyDemeterCommand = Annotated[Union[SetGpio, SetPwm, ..., SystemReport], Field(discriminator="type")]`
- Cada subclase define `type: Literal["set_gpio"]`, `type: Literal["ping"]`, etc.
- `command_router.py:56,94` — `TypeAdapter(AnyDemeterCommand).validate_python(body)` — una línea para deserializar y validar cualquier tipo de comando
- `dispatcher.py:60,294` — El listener reutiliza el mismo TypeAdapter para validar mensajes de Redis
- Si el `type` no coincide con ningún Literal → `ValidationError` con mensaje claro

### Problema 12.2: Validar inputs y serializar outputs consistentemente

**Problema:** Sin validación, un campo faltante o un tipo incorrecto causa un error 500 críptico. Los responses deben tener formato predecible.

**Concepto:** Schema-first validation (Pydantic) — modelos declarativos que validan automáticamente inputs y serializan outputs.

**Implementación:**
- `BD/schemas.py` — Jerarquía `Base → Create → Response` por cada entidad:
  - `UserBase → UserCreate(+password) → UserResponse(+id)`
  - `PlantBase → PlantCreate → PlantUpdate(all Optional) → PlantResponse(+id)`
- `schemas.py:121` — `ConfigDict(from_attributes=True)` permite crear Pydantic models directamente desde objetos SQLAlchemy
- `lims_router.py:26` — `response_model=List[PlantResponse]` en el decorator valida automáticamente el output
- Errores de validación devuelven 422 con detalle específico del campo fallido

### Problema 12.3: Prevenir ataques de path traversal en descargas

**Problema:** Si el endpoint de descarga acepta un filename arbitrario, un atacante podría acceder a archivos fuera del directorio de exports (e.g., `../../etc/passwd`).

**Concepto:** Input sanitization — rechazar patrones peligrosos antes de construir la ruta del filesystem.

**Implementación:**
- `analysis_router.py:83-84` — `if ".." in filename or "/" in filename: raise HTTPException(400, "Invalid filename")` — bloquea traversal
- `export_router.py:84-91` — Usa el resultado del job RQ como ruta (controlada por el servidor, no por el usuario) y verifica `os.path.exists()`

---

## 13. Configuración y Despliegue Multi-Entorno

### Problema 13.1: Misma codebase, diferentes configuraciones por entorno

**Problema:** Dev, staging, producción y RPi necesitan diferentes URLs de DB, Redis, puertos, y flags de debug. No se puede hardcodear nada.

**Concepto:** 12-Factor App (Factor III) — configuración via variables de entorno, con valores por defecto sensatos.

**Implementación:**
- `Software/Common/configuration.py` — `Settings(BaseSettings)` con prefijo `DEMETER_` — lee automáticamente de `.env` y env vars del sistema
- `Core/config.py` — Proxy singleton: `get_settings()` devuelve siempre la misma instancia
- Archivos `.env.local`, `.env.staging`, `.env.prod`, `.env.rpi` — el Makefile copia al `.env` activo
- `database.py:9` — `settings.DATABASE_URL` construido dinámicamente desde `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.

### Problema 13.2: Docker Compose composable por entorno

**Problema:** Dev necesita hot reload y puertos expuestos, staging necesita tunnel, RPi necesita host networking y serial. No se puede tener un solo docker-compose.

**Concepto:** Docker Compose override files — un base sin puertos + overrides por entorno que añaden lo específico.

**Implementación:**
- `docker-compose.yml` (base) — define los 5 servicios sin exponer puertos
- Overrides por entorno añaden: ports (dev), Cloudflare tunnel (staging), host networking + `/dev/serial0` (RPi)
- Makefile targets: `make dev`, `make staging`, `make rpi-up` aplican el override correcto

---

## 14. Inicialización y Arranque Autónomo

### Problema 14.1: Sistema funcional desde el primer arranque sin setup manual

**Problema:** Un desarrollador nuevo hace `make dev` y espera ver datos y poder operar. Si necesita crear usuario admin manualmente, correr seeds, migrar la DB... es una barrera de entrada.

**Concepto:** Self-bootstrapping — el sistema se autoinicializa al arrancar: crea usuario por defecto, siembra datos de prueba, conecta a servicios.

**Implementación en `app.py:35-74` (lifespan):**
1. `await asyncio.sleep(2)` — Espera warmup de PostgreSQL
2. `await create_default_admin(session)` — Crea usuario admin/admin si no existe (`startup.py:10-40`)
3. `await seed_historical_data(session)` — Siembra 20 plantas, 3 experimentos, 6 meses de telemetría, sensor maps (`seed_data.py`)
4. `await redis_manager.connect()` — Conecta a Redis (o entra en modo standalone)
5. `asyncio.create_task(start_redis_listener())` — Arranca el dispatcher
6. `asyncio.create_task(start_activity_batch_flusher())` — Arranca el flusher

### Problema 14.2: IDs deterministas para compatibilidad firmware

**Problema:** Si los IDs de planta se generan con auto-increment sin control, después de borrar y re-insertar, los IDs cambian. El firmware tiene hardcodeados `plantId=1..20`.

**Concepto:** Sequence reset — forzar que los IDs empiecen siempre desde 1 al hacer seed.

**Implementación:**
- `seed_data.py` ejecuta `ALTER SEQUENCE plants_id_seq RESTART WITH 1` y `ALTER SEQUENCE experiments_id_seq RESTART WITH 1` antes de insertar
- Cada planta se crea con `node_id = plant_id` (1-20), asegurando correspondencia 1:1 con el firmware
- Después de `make dev-seed`, los IDs son siempre predecibles

---

## Resumen Visual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PROBLEMAS RESUELTOS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COMUNICACIÓN          DESACOPLAMIENTO       CONCURRENCIA               │
│  ├ WebSocket push      ├ Redis Pub/Sub       ├ asyncio event loop       │
│  ├ Bidireccional RPi   ├ HTTP cmd / WS push  ├ Activity batching        │
│  └ Broadcast selectivo └ Esquema compartido  └ selectinload (N+1)      │
│                                                                         │
│  PERSISTENCIA          AUTENTICACIÓN         BACKGROUND JOBS            │
│  ├ Time series + idx   ├ JWT stateless       ├ RQ (Redis Queue)         │
│  ├ JSONB metadata      ├ bcrypt passwords    ├ Pipeline ETL             │
│  ├ M2M join table      ├ RBAC por roles      └ APScheduler cronjobs    │
│  ├ Alembic migrations  └ API Key para SDK                               │
│  └ Unique constraints                                                   │
│                                                                         │
│  CACHING               RESILIENCIA           LIMS CIENTÍFICO            │
│  ├ Redis cache aside   ├ Graceful degrade    ├ CRUD botánico            │
│  ├ Estado dispositivos ├ Gateway offline     ├ Diseño experimental      │
│  └ Telemetría efímera  ├ WS cleanup          └ 18+ métricas agronómicas│
│                        └ Flusher retry                                  │
│                                                                         │
│  HARDWARE MAPPING      OBSERVABILIDAD        VALIDACIÓN                 │
│  ├ PlantSensorMap      ├ Audit trail         ├ Discriminated unions     │
│  └ Service discovery   └ Named loggers       ├ Schema-first (Pydantic) │
│                                              └ Path traversal guard     │
│                                                                         │
│  CONFIGURACIÓN         BOOTSTRAPPING                                    │
│  ├ 12-Factor envvars   ├ Auto admin + seed                              │
│  └ Compose overrides   └ Sequence reset IDs                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

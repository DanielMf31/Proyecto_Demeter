# Arquitectura del Backend de Demeter

Este documento describe en profundidad la estructura y funcionamiento del Backend situado en `Software/Servidor/Backend`.

## Visión General

El backend está construido sobre **FastAPI**, un framework moderno y de alto rendimiento para Python, diseñado para ejecutar operaciones asíncronas (`async/await`), lo cual es crítico para manejar múltiples conexiones IoT simultáneamente.

### Tecnologías Principales
*   **Lenguaje**: Python 3.11+
*   **Framework Web**: FastAPI
*   **Servidor ASGI**: Uvicorn
*   **Base de Datos Relacional**: PostgreSQL (con driver `asyncpg` y ORM `SQLAlchemy`).
*   **Base de Datos en Memoria / Caché**: Redis (para estados volátiles y mensajería Pub/Sub).
*   **Validación de Datos**: Pydantic.

---

## Estructura de Directorios

La organización del código sigue una arquitectura modular para separar responsabilidades:

```text
Software/Servidor/Backend/
├── app.py              # Punto de entrada. Inicializa la app y los routers.
├── .env                # Variables de entorno (Credenciales, URLs).
├── Core/               # Núcleo de la infraestructura.
│   ├── config.py       # Carga y validación de variables de entorno.
│   ├── database.py     # Configuración de sesión y motor de PostgreSQL.
│   ├── redis.py        # Wrapper para cliente Redis y funciones Pub/Sub.
│   └── logger.py       # Configuración centralizada de logs.
├── API/                # Capa REST (HTTP).
│   ├── routers/        # Definición de endpoints (rutas).
│   └── ...
├── WS_Manager/         # Capa WebSockets (Tiempo Real).
│   ├── router.py       # Endpoint único del WS (/ws/{client_id}).
│   ├── manager.py      # Gestor de conexiones activas (Connection Manager).
│   └── handlers/       # Lógica específica por tipo de mensaje (comandos, telemetría).
└── BD/                 # Capa de Datos.
    ├── models.py       # Modelos ORM (tablas de PostgreSQL).
    ├── schemas.py      # Esquemas Pydantic (validación de entrada/salida).
    └── init_db.py      # Script de inicialización de tablas.
```

---

## Componentes Detallados

### 1. Core (Infraestructura)

*   **`Core/config.py`**: Utiliza `pydantic-settings` para cargar el `.env`. Esto asegura que si falta una variable crítica (como la URL de la DB), el servidor no arranque.
*   **`Core/database.py`**: Configura el motor asíncrono de SQLAlchemy. Provee la función `get_db` que se inyecta como dependencia en los endpoints para obtener una sesión segura.
*   **`Core/redis.py`**: Implementa la clase `RedisManager`.
    *   Mantiene una conexión persistente.
    *   Métodos para guardar estado de dispositivos (`set_device_state`).
    *   Canal Pub/Sub `iot_events` para notificar a otros servicios.

### 2. Capa de Datos (BD)

*   **`BD/models.py`**: Define las tablas `users`, `devices`, `sequences`, `activity_log`. Usa claves foráneas para integridad referencial.
*   **`BD/schemas.py`**: Define *cómo* se ven los datos al entrar y salir de la API, previniendo que datos corruptos lleguen a la lógica de negocio.

### 3. Gestor de WebSockets (WS_Manager)

Esta es la pieza clave para el IoT.

*   **`WS_Manager/router.py`**: Acepta la conexión WS.
*   **`WS_Manager/manager.py`**:
    *   `active_connections`: Lista en memoria de clientes conectados.
    *   `connect()`: Acepta el socket y lo registra.
    *   `broadcast()`: Envía un mensaje a todos.
    *   `send_personal_message()`: Envía mensaje a un ID específico (ej: a la Raspberry).
*   **Flujo de Mensajería**:
    1.  Raspberry envía JSON con telemetría.
    2.  `router.py` recibe el JSON.
    3.  Se procesa (ej: se guarda en Redis).
    4.  Se publica un evento en el canal `iot_events` de Redis.
    5.  El Frontend (suscrito) recibe la actualización instantáneamente.

---

## Flujo de una Petición (Request Flow)

### Ejemplo: Crear un Usuario (REST)

1.  **Petición**: `POST /api/v1/users/` con JSON `{ "username": "admin", ... }`.
2.  **Router**: FastAPI valida el JSON contra `schemas.UserCreate`.
3.  **Dependencia**: Se obtiene una sesión de DB (`async_session`).
4.  **Lógica**: Se crea una instancia de `models.User`.
5.  **Persistencia**: `session.add(user)` -> `session.commit()`.
6.  **Respuesta**: Se devuelve el usuario creado (sin el password hash) convertido a JSON.

### Ejemplo: Encender una Bomba (WebSocket)

1.  **Frontend**: Envía `POST /api/v1/devices/pump_01/command`.
2.  **API**: Valida y llama a `redis_manager.publish_event(...)`.
3.  **Redis**: Distribuye el mensaje al servicio WS.
4.  **WS Manager**: Detecta el evento, busca la conexión abierta de la Raspberry Pi.
5.  **Envío**: Manda `{ "command": "ON" }` por el socket de la Raspberry.
6.  **Actuación**: La Raspberry recibe y activa el GPIO.

---

## Despliegue (Docker)

El servicio corre dentro del contenedor `backend`, expuesto en el puerto 8000.
*   **Working Directory**: `/app/Software/Servidor/Backend`.
*   **Comando de Inicio**: `uvicorn app:app --host 0.0.0.0 --port 8000`.

Prompt para tu Agente de IA (Cópialo y pégalo):
"Actúa como un Arquitecto de Software y Administrador de Bases de Datos Senior. Estoy construyendo un sistema IoT industrial y necesito que generes el código del backend (modelos y esquemas) basado en las siguientes especificaciones técnicas.

1. Contexto y Stack Tecnológico:

Base de Datos: PostgreSQL.

Entorno: Sistema Dockerizado gestionado por docker-compose. La API y la Base de Datos corren en contenedores separados dentro de la misma red de Docker.

Backend: Python (asume el uso de SQLAlchemy como ORM y Pydantic para la validación de datos).

2. Diseño del Esquema Relacional (Tablas requeridas):
Necesito que generes los modelos de SQLAlchemy (models.py) y sus respectivos esquemas de Pydantic (schemas.py) para las siguientes 5 entidades, aplicando las mejores prácticas de integridad referencial:

Tabla users (Usuarios):

Campos: id (UUID o Integer PK), username (String, unique), password_hash (String), role (String), is_active (Boolean, default True).

Regla de negocio: Implementar lógica de Soft Delete. Nunca se borran registros, solo se cambia is_active a False.

Tabla devices (Catálogo de Hardware):

Campos: id (PK), name (String), device_type (String, ej: 'pump', 'valve'), gpio_pin (Integer).

Nota: El estado en tiempo real (ON/OFF) NO va aquí (se gestiona en Redis), esta tabla es solo inventario.

Tabla sequences (Cabecera del Planificador):

Campos: id (PK), name (String), created_by (Foreign Key a users.id), created_at (Timestamp, default now).

Tabla sequence_steps (Detalle de la Secuencia):

Campos: id (PK), sequence_id (Foreign Key a sequences.id), device_id (Foreign Key a devices.id), step_order (Integer), target_state (Boolean), duration_seconds (Integer).

Regla de negocio: Relación 1-a-N con sequences. Debe permitir el borrado en cascada (Cascade Delete) si se elimina la cabecera de la secuencia.

Tabla activity_log (Historial de Auditoría):

Campos: id (PK), timestamp (Timestamp, indexed), user_id (Foreign Key a users.id), device_id (Foreign Key a devices.id, nullable), action_type (String), description (Text).

Regla de negocio: Es obligatorio crear un Índice (Index) en la columna timestamp para optimizar las consultas históricas, ya que esta tabla crecerá masivamente.

3. Entregables esperados:

El código de los modelos de SQLAlchemy definiendo las relaciones (relationship), claves foráneas y el índice mencionado.

Los modelos de Pydantic básicos para crear y leer estos datos (Create schemas y Response schemas).

Un bloque de código de ejemplo para la configuración de conexión (database.py), mostrando cómo leer la URL de la base de datos desde una variable de entorno, teniendo en cuenta que el host será el nombre del servicio en Docker (ej: postgresql://user:pass@db:5432/iot_db)."
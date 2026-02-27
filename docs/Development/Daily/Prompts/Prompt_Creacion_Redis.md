Prompt para tu Agente de IA (Cópialo y pégalo):
"Actúa como un Arquitecto de Software y Experto en Sistemas de Tiempo Real. Estoy construyendo el backend de un sistema IoT industrial con FastAPI y necesito implementar la capa de caché y mensajería utilizando Redis.

1. Contexto y Stack Tecnológico:

Tecnología: Redis (in-memory data structure store).

Entorno: Sistema Dockerizado (docker-compose). El backend y Redis corren en contenedores separados en la misma red. El host de Redis será una variable de entorno, por defecto redis.

Backend: Python con FastAPI. Es estrictamente obligatorio usar la librería asíncrona redis.asyncio (no la síncrona) para no bloquear el event loop de FastAPI.

2. Arquitectura de Claves (Key Design) y Funcionalidades:
Necesito que generes un módulo limpio (ej: core/redis_manager.py o similar) que maneje tres responsabilidades principales con la siguiente nomenclatura de claves (Key Prefixing):

A. Estado en Tiempo Real de Dispositivos (Device State):

Clave: device:{device_id}:state

Función: Guardar y recuperar el estado actual (ON/OFF) de bombas y válvulas. Este dato no debe expirar, pero debe sobrescribirse en cada cambio.

B. Telemetría Efímera (Sensors / TTL):

Clave: sensor:{sensor_id}:telemetry

Función: Guardar lecturas de sensores (ej: flujo, presión).

Regla de negocio crítica: Estos datos DEBEN guardarse con un TTL (Time To Live) de 60 segundos usando SETEX. Si el hardware deja de enviar datos, la clave debe desaparecer para evitar mostrar información fantasma en el frontend.

C. Sistema de Eventos (Pub/Sub para WebSockets):

Canal (Channel): iot_events

Función: Implementar métodos para publicar (publish) mensajes JSON en este canal cuando un estado cambie, y un método para suscribirse (subscribe) que será consumido posteriormente por el WebSocket Manager de FastAPI.

3. Entregables esperados:

Código de configuración y conexión asíncrona a Redis (get_redis_client), manejando el cierre de la conexión en los eventos de startup y shutdown (o lifespan) de FastAPI.

Funciones helper asíncronas para leer/escribir los estados de los dispositivos y la telemetría (aplicando el TTL mencionado).

Funciones helper para el patrón Pub/Sub (publish_event y un generador asíncrono para escuchar mensajes).

Un ejemplo breve de cómo inyectar el cliente de Redis en un endpoint de FastAPI usando Depends()."
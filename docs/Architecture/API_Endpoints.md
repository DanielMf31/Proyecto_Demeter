# Demeter API Endpoints Documentation
Estado: Activo v1.0
Capa: HTTP REST & WebSockets

Este documento describe todos los routers y endpoints disponibles en el Backend FastAPI de Demeter, su propósito y los flujos asíncronos en los que participan.

## 1. System (`/api/v1/system`)
Endpoints de utilidad para monitorización pasiva (Health checks).

- `GET /system/status`: Devuelve el estado operacional de la API FastAPI.
- `GET /system/db-check`: Verifica rápidamente la disponibilidad de la conexión a PostgreSQL.

## 2. Authentication (`/api/v1/`)
Gestión del ciclo de vida de usuarios y control de acceso mediante tokens JWT (OAuth2).

- `POST /register`: Da de alta a un usuario estándar en el sistema (requiere privilegios o estar habilitado públicamente).
- `POST /login`: Recibe `username` y `password` en formato form-data (OAuth2PasswordRequestForm). Si las credenciales son válidas, retorna un `access_token` JWT.
- `GET /me`: Obtiene los datos del usuario logueado actualmente enviando el token en la cabecera `Authorization: Bearer <token>`.

## 3. History (`/api/v1/history`)
Acceso rápido a los históricos de telemetría de un nodo específico, ideal para el visor del Dashboard principal.

- `GET /history/node/{node_id}?days=30`: Devuelve un arreglo serializado con todos los registros cronológicos (Temperatura y Humedad) de los últimos `days` días correspondientes a un sensor.

## 4. Export (`/api/v1/export`)
Descarga asíncrona de datos pesados (ETL) delegada a RQ (Redis Queue) y Worker.

- `POST /export/plants`: Encola una tarea en el worker para calcular el VPD y recuperar un gran volumen de datos de un experimento. Devuelve un `job_id` inmediatamente (202 Accepted).
- `GET /export/status/{job_id}`: Polling endpoint para que el frontend revise si la tarea terminó (`status: queued, started, finished, failed`).
- `GET /export/download/{job_id}`: Devuelve el `.zip` resultante (con Excels y PNGs) usando un `FileResponse`. Solo funciona si el estado previo era `finished`.

## 5. Commands (`/api/v1/command`)
Vía HTTP oficial para inyectar paquetes de instrucciones hacia los nodos hardware, evitando el acoplamiento estrecho con WebSockets desde el frontend web.

- `POST /command`: API general para mandar comandos (`set_gpio`, `set_pwm`, `exec_sequence`) hacia la Raspberry Gateway. Valida estrictamente el payload con Pydantic y publica en el canal de Pub/Sub `demeter:commands`.

## 6. Discovery (`/api/v1/devices`)
Gestión de topología del hub de sensores y actuadores.

- `GET /devices`: Recupera de la memoria caché conectada (Redis) la configuración hardware reportada por última vez por la Raspberry Pi. Si está ausente, indica que la Gateway no ha reportado su startup.

## 7. WebSockets (`/ws`)
Capa de transporte ultra-rápida y persistente, optimizada puramente para telemetría binaria y confirmación de hardware.

- `WS /ws/{client_id}`: 
  - Si el cliente es `raspberry_gateway`, acepta los datos de sensores entrantes (Sensor TH/Suelo) y las confirmaciones.
  - Si el cliente es el `Frontend` web u otro cliente de monitorización, sirve como canal de suscripción de **solo lectura**. El Dispatcher le replicará la telemetría en vivo, pero el frontend no puede mandar comandos POST por aquí.

## 8. Análisis (Legacy/Internal) (`/api/v1/analysis`)
Testing inicial para cálculo asíncrono.
- `POST /analysis/generate`: Encola una tarea puramente estadística (dummy).
- `GET /analysis/status/{task_id}` y `GET /analysis/download/{filename}` equivalentes al flujo de Exportación.
0
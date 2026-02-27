# Contexto y Rol
Eres un Ingeniero Full-Stack y Arquitecto de Software Senior, experto en FastAPI, React, Pandas, Matplotlib, Docker y sistemas distribuidos con colas de tareas (Redis Queue). 
# Objetivo del Proyecto
Implementar un flujo completo de autenticación segura, generación de datos de prueba (seeding) y un motor asíncrono y escalable de exportación de datos científicos pesados para la plataforma IoT "Demeter". Todo esto debe estar preparado para desplegarse en un entorno de pruebas mediante Docker, utilizando contenedores separados para la API, la base de datos, Redis y múltiples Workers.
# Instrucciones detalladas por Módulos:
## Módulo 1: Autenticación Segura (FastAPI)
- Implementa un sistema de login usando `OAuth2PasswordBearer` y JWT (JSON Web Tokens).
- Usa `passlib[bcrypt]` para hashear las contraseñas. NO guardes contraseñas en texto plano.
- Crea las rutas `POST /api/auth/register`, `POST /api/auth/login` (que devuelve el access token) y una dependencia `get_current_user` para proteger el resto de rutas.
- **Dato por defecto:** Crea automáticamente un usuario admin (usuario: `admin`, contraseña: `admin`) con todos los permisos al arrancar si no existe.
## Módulo 2: Seeding de Datos (Entorno de Pruebas)
- Crea un script o función `seed_test_data(db: Session)` que se ejecute al iniciar la base de datos en modo de pruebas.
- Debe inyectar en la base de datos 10 Nodos/Plantas (ej. Planta_1 a Planta_10).
- Para cada planta, debe generar 24 mediciones (una por hora del último día) con valores realistas de Temperatura (15-30°C) y Humedad (40-80%).
## Módulo 3: Infraestructura y Escalabilidad (Docker Compose + Redis)
- Diseña un archivo [docker-compose.yml](cci:7://file:///home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/docker-compose.yml:0:0-0:0) que levante:
  1. El Backend en FastAPI.
  2. Un servidor **Redis** (broker de mensajería).
  3. **Múltiples contenedores Worker** (usando la librería `rq` de Python). Configura el `docker-compose` de manera que sea fácil escalar los workers (ej. `docker-compose up --scale worker=4`).
  4. (Opcional si es necesario) Base de datos PostgreSQL o SQLite local mapeado en un volumen.
## Módulo 4: El Motor de Exportación Asíncrona Distribuido (FastAPI + RQ + Pandas)
- Crea un endpoint protegido `POST /api/export/plants`.
- Al recibir la petición, este endpoint **NO** debe procesar los datos directamente. Debe encolar un trabajo en **Redis Queue (RQ)** llamando a una tarea en segundo plano y devolver inmediatamente un `Job ID` o "Task ID" al frontend.
- Crea un segundo endpoint protegido `GET /api/export/status/{job_id}` que permita al frontend consultar si la tarea ha terminado y obtener el enlace de descarga, o `GET /api/export/download/{job_id}` para bajar el archivo.
**Lógica del Worker (La tarea pesada):**
1. **Flujo de extracción:** El worker obtiene los IDs de las 10 plantas y extrae sus 24 mediciones de DB, cargándolas en memoria RAM (`pandas.DataFrame`).
2. **Estructura de Archivos:** Usa `tempfile` o `pathlib` para crear esta estructura:
   - `/Exportacion_Demeter/`
     - `/Comparacion_Global/` (Contendrá un Excel y gráfica comparando la media de todas las plantas).
     - `/Planta_1/`
       - `datos_planta_1.xlsx` (Generado con pandas `to_excel`).
       - `grafica_planta_1.pdf` (Generado con matplotlib: evolución de temp y humedad 24h).
     - `/Planta_2/ ...` (y así para las 10 plantas).
3. **Empaquetado y almacenamiento:** Comprime la carpeta usando `shutil.make_archive`. Guarda el zip resultante en un volumen compartido o memoria caché temporal que el servidor FastAPI pueda leer para entregárselo al usuario.
## Módulo 5: Interfaz de Exportación (React + Tailwind)
- Integra en la app actual una **pantalla de Login** que consuma el endpoint de FastAPI. Si el usuario ingresa admin/admin, ingresa al Dashboard.
- En el Dashboard, crea un componente `ExportDrawer.tsx`. Botón: "Exportar Datos".
- Al hacer clic, abre un menú deslizante lateral (Drawer/Slide-over) u Offcanvas.
- Pregunta: "Rango de datos a descargar" (opción "Últimas 24h (Datos de Prueba)" seleccionada por defecto).
- Al confirmar, el Frontend llama a `POST /api/export/plants`, obtiene el `job_id`, y muestra un estado de "Cargando/Generando informe..." haciendo polling (cada 2 segundos) al endpoint de status hasta que esté listo, y luego descarga automáticamente el zip.
# Entregables Esperados:
1. [docker-compose.yml](cci:7://file:///home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/docker-compose.yml:0:0-0:0) y `Dockerfile` (preparados para workers en RQ).
2. Código de Autenticación (`auth.py`).
3. Script de Seeding (`seed.py`).
4. Motor de exportación (`worker_tasks.py`, `export_router.py`).
5. Frontend: Pantalla de Login y Componente de Exportación (`ExportDrawer.tsx`) con lógica de polling.
Por favor, genera primero el **plan de implementación detallado paso a paso** para revisar que la arquitectura es correcta antes de escribir todo el código final.
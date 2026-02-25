# Arquitectura de Contenedores: Docker Compose en Demeter

El proyecto Demeter utiliza una arquitectura profesional de **Docker Compose Tripartita**. Esto significa que en lugar de mezclar la configuración de desarrollo y la de producción en un solo archivo inmenso y confuso, se separan los "contextos" o entornos en tres archivos distintos.

A continuación, se explica el propósito de cada uno.

## 1. `docker-compose.yml` (El Archivo Base)
**Propósito:** Definir la infraestructura fundamental y la topología de la red.
Este archivo describe la arquitectura agnóstica del entorno. Define *qué* contenedores existen, cómo se llaman (`container_name`), a qué red interna se conectan (`demeter-net`) y qué volúmenes de datos necesitan retener.

**Características Clave:**
- **No expone puertos al exterior:** Por seguridad, ningún servicio expone el puerto `8000` ni el `5432` a la máquina física. Todos se comunican privadamente por la red interna.
- Es la "receta" universal. Nadie puede levantar este archivo solo y esperar acceder a la app web desde su navegador.

## 2. `docker-compose.override.yml` (El Entorno de Desarrollo)
**Propósito:** Convertir la infraestructura base en un entorno de programación amigable (Local Dev Experience).
Docker tiene una regla mágica: si existe un archivo llamado `docker-compose.override.yml`, lo une automáticamente con el archivo base cuando escribes `docker compose up`.

**Características Clave (Exclusivas de este archivo):**
- **Apertura de Puertos (`ports`):** Aquí es donde mapeamos el puerto `5173` (Frontend Vite) al puerto `80` (HTTP local), y abrimos el `8000` del Backend y el `5432` de Postgres para que puedas conectarte desde tu máquina host (Ej. DBeaver o Postman).
- **Hot-Reloading (`volumes`):** Se hace un "Bind Mount" de tus carpetas locales (`./Software/Servidor/Frontend/Demeter-React`) hacia adentro del contenedor (`/app`). Esto permite que cuando guardes un archivo TypeScript en tu VSCode, Vite se entere instantáneamente (Hot Module Replacement) sin tener que reconstruir la imagen de Docker.
- **Vite Dev Server:** Sobrescribe el comando del frontend para que ejecute `npm run dev` en lugar de servir archivos estáticos compilados de producción.

## 3. `docker-compose.prod.yml` (El Entorno de Producción)
**Propósito:** Desplegar el sistema en un servidor real de forma resiliente y segura.
Para correr producción, se ignora explícitamente el archivo de override y se unen el base con el de producción: 
`docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

**Características Clave:**
- **`restart: always`:** Le dice al daemon de Docker que si un contenedor (por ejemplo, el Backend) crashea por un error de RAM, o si la Raspberry Pi se reinicia, el contenedor debe volver a levantarse por sí solo. 
- **Traefik Labels / Reverse Proxy:** En lugar de exponer puertos desnudos (que es inseguro), este archivo incluye etiquetas que un Reverse Proxy lee automáticamente para generar certificados SSL (HTTPS) y enrutamiento por nombres de dominio (ej. `demeter.monters.org`).
- **No hay Hot-Reloading:** Todo el código fuente está rígidamente horneado dentro de las imágenes en su estado de construcción (`build`).

---

## ¿Por qué parecía que no había contenedor Frontend?
En el registro superior de tu consola (`12 seconds ago`), el contenedor `demeter-frontend` **está activo y mapeando los puertos `80` y `5173`** correctamente, así como los 4 trabajadores del backend. Esto sucedió cuando tú corriste el comando del workflow `/reiniciar-entorno` (`docker compose up -d --build`).

En tu segundo registro inferior (`About a minute ago`), faltan tres contenedores importantes. Eso es porque, un minuto de antes de que tú usaras el `/reiniciar-entorno`, **el sistema de Inteligencia Artificial corrió un despliegue focalizado:**
`docker compose up -d db redis api`

Ese comando explícito que ejecuté me permitía aislar únicamente los contenedores transaccionales para poder forzar la regeneración pura del archivo inicial de migraciones de base de datos de Alembic, descartando cualquier problema con trabajadores colindantes o interfaces web. 

Actualmente los 3 archivos de Docker configuran el entorno a la perfección. He estructurado sus archivos localmente para fortalecer y aclarar sus intenciones.

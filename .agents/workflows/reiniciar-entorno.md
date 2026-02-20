---
description: Reinicia agresivamente todo el entorno de Desarrollo (Frontend Angular/React, Backend FastAPI, Redis, DB) y repuebla la base de datos con mediciones de prueba del día anterior.
---

Este flujo de trabajo se encarga de derribar limpiamente todos los contenedores en ejecución, forzar su recompilación para incrustar cambios en el código de librerías, levantarlos en segundo plano de manera orquestada y, finalmente, inyectar el set de datos de prueba (24h estables para los 10 nodos).

// turbo-all

1. Apaga y elimina los contenedores actuales y sus redes asociadas.
`docker compose down`

2. Recompila las imágenes e inicia todos los servicios orquestados en segundo plano.
`docker compose up --build -d`

3. Espera 10 segundos para dar tiempo a que PostgreSQL y Redis acepten conexiones estables.
`sleep 10`

4. Ejecuta el módulo de Inyección de Semillas (Seeder) directamente en el contenedor del Backend para poblar la BD.
`docker compose exec api python -m BD.seed`

---
description: Reinicia agresivamente todo el entorno de Desarrollo (Frontend Angular/React, Backend FastAPI, Redis, DB) y repuebla la base de datos con mediciones de prueba del día anterior.
---
Este workflow está diseñado para destruir por completo el entorno actual (incluyendo volúmenes huérfanos y datos "cacheados" que a veces persisten) y reconstruirlo desde un estado totalmente en blanco, aplicando las migraciones y sembrando nuevamente los históricos.

// turbo-all
1. Bajamos contenedores, eliminando también redes, imágenes huérfanas y volúmenes persistentes locales.
```bash
docker compose down -v --remove-orphans
```

2. Reconstruimos y levantamos en modo detached.
```bash
docker compose up -d --build
```

3. Esperamos a que la base de datos esté lista, aplicamos las migraciones estructurales LIMS, e inyectamos el histórico base (seeder).
```bash
sleep 5 && docker compose exec api alembic upgrade head && docker compose exec api python -m BD.seed_data
```

4. Verificamos que los servicios están activos.
```bash
docker compose ps
```

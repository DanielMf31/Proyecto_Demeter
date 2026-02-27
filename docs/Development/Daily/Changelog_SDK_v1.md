# Changelog de la Sesión — SDK v1.0, Staging e Infraestructura

**Fecha:** 24-26 Feb 2026  
**Rama:** `feature/sdk-v1`  

---

## Índice de Cambios

1. [SDK Python v1.0](#1-sdk-python-v10)
2. [Tests del SDK](#2-tests-del-sdk)
3. [Publicación en Test PyPI](#3-publicación-en-test-pypi)
4. [Frontend: Fix TypeScript build](#4-frontend-fix-typescript-build)
5. [Nginx: Fix upstream name](#5-nginx-fix-upstream-name)
6. [Docker Compose: Staging](#6-docker-compose-staging)
7. [Entorno `.env.staging`](#7-entorno-envstaging)
8. [Makefile de Despliegue](#8-makefile-de-despliegue)
9. [Documentación](#9-documentación)
10. [Google Colab Notebook](#10-google-colab-notebook)
11. [Git: Rama y commits](#11-git-rama-y-commits)

---

## 1. SDK Python v1.0

**Directorio:** `SDK/demeter_sdk/`

| Archivo | Qué hace |
|---|---|
| `_types.py` | `SDKConfig` dataclass, `COLS` registro de columnas, TypedDicts de la API |
| `_session.py` | Sesión HTTPS con retry exponencial y header `X-API-Key` |
| `fetcher.py` | Caché Parquet transparente con TTL + `force_refresh` |
| `transform.py` | ETL pipeline: `to_dataframe → clean → fill_gaps → resample → pipeline()` |
| `science.py` | 15 fórmulas vectorizadas (VPD, punto rocío, bulbo húmedo, ET0, GDD, DAP…) + `enrich()` |
| `viz.py` | 4 gráficas: `plot_timeseries`, `plot_vpd` (con zonas), `plot_boxplot`, `plot_heatmap` |
| `export.py` | `to_csv` (UTF-8 BOM) y `to_excel` (3 hojas: Resumen, Enriquecidos, Crudos) |
| `client.py` | Orquestador: expone `.ping()`, `.get_raw_data()`, `.get_enriched_data()`, `.plot.*`, `.export.*` |
| `__init__.py` | Exporta `DemeterClient` + todos los módulos como API pública |

**Package:** `SDK/pyproject.toml` — reemplaza `setup.py`, incluye extras `[dev]` y `[plotly]`.

---

## 2. Tests del SDK

**Directorio:** `SDK/tests/`

| Archivo | Tests | Qué cubre |
|---|---|---|
| `conftest.py` | — | Fixtures: `raw_records`, `clean_df`, `enriched_df` (sin servidor) |
| `test_science.py` | 30 | Todas las fórmulas: termodinámica, fenología, estadística, `enrich()` |
| `test_transform.py` | 15 | `to_dataframe`, `clean`, `fill_gaps`, `resample`, `pipeline()` |
| `test_export.py` | 7 | CSV roundtrip, Excel 3 hojas, hoja Resumen con estadísticas |
| `test_client_offline.py` | 7 | `DemeterClient` con HTTP mockeado (sin servidor real) |

**Total: 59 tests, todos pasan** (`pytest SDK/tests/ -v`)

---

## 3. Publicación en Test PyPI

- Token configurado en `~/.pypirc` (chmod 600)  
- Email del autor corregido (`.local` → `gmail.com`) para cumplir validación PyPI  
- SDK v1.0.0 publicado: **[test.pypi.org/project/demeter-sdk/1.0.0](https://test.pypi.org/project/demeter-sdk/1.0.0/)**

Instalación desde Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            demeter_sdk
```

---

## 4. Frontend: Fix TypeScript build

**Archivo:** `Software/Servidor/Frontend/Demeter-React/src/components/dashboard/SensorChart.tsx`

**Problema:** `MetricType = 'temperatura' | 'humedad' | 'vpd'` pero `metricConfigs` no tenía entrada `vpd` → error TS7053 en build de producción.

**Solución:**
- Tipado explícito: `Record<MetricType, {...}>` en `metricConfigs`  
- Añadida entrada `vpd` (color teal `#14b8a6`, unidad `kPa`)  
- Añadido gradiente SVG `colorVpd` en los `<defs>`  

**Commit:** `62de277`

---

## 5. Nginx: Fix upstream name

**Archivo:** `Software/Servidor/Backend/Nginx/nginx.conf`

**Problema:** `proxy_pass http://backend:8000` → Docker no conoce ningún servicio llamado `backend`, el contenedor real es `demeter-api`.

**Solución:** Cambiado a `http://demeter-api:8000` en los bloques `/api/` y `/ws/`. Añadidas cabeceras `X-Real-IP` y `X-Forwarded-*` al bloque `/api/`.

**Commit:** `9f03b20`

---

## 6. Docker Compose: Staging

**Archivo nuevo:** `docker-compose.staging.yml`

Configura el stack para ejecutarse en el portátil con puertos alternativos (sin chocar con dev) y apuntando a `patata.monters.org`:

| Servicio | Puerto staging | Puerto dev |
|---|---|---|
| Frontend | 5175 | 80 / 5173 |
| API | 8001 | 8000 |
| PostgreSQL | 5433 | 5432 |
| Redis | 6381 | 6380 |

Volumen DB aislado: `postgres_staging` (no mezcla datos con dev).

---

## 7. Entorno `.env.staging`

**Archivo:** `.env.staging`

Cambios respecto a la versión anterior:
- Credenciales DB alineadas con el volumen real (`postgres` / `postgres_local_pass`)  
- `VITE_API_URL=https://patata.monters.org/api` (Cloudflare Tunnel)  
- `VITE_WS_URL=wss://patata.monters.org/ws`  
- `DEBUG=True` para poder acceder a `/api/docs` en staging  
- Variables Redis y DB server explícitas  

---

## 8. Makefile de Despliegue

**Archivo nuevo:** `Makefile`

| Comando | Qué hace |
|---|---|
| `make help` | Lista todos los comandos con colores |
| `make dev` | Dev con hot-reload en localhost |
| `make dev-build` | Dev con rebuild forzado |
| `make dev-down` | Para dev |
| `make dev-seed` | Siembra datos en dev |
| `make staging` | Staging con `patata.monters.org` desde portátil |
| `make staging-build` | Staging con rebuild completo |
| `make staging-down` | Para staging |
| `make staging-seed` | Siembra datos en staging |
| `make staging-logs` | Logs de staging |
| `make prod` | Muestra instrucciones SSH para producción |
| `make seed` | Siembra DB activa |
| `make logs-api` | Logs de FastAPI |
| `make logs-db` | Logs de PostgreSQL |
| `make status` | Estado de todos los contenedores Demeter |
| `make clean` | Para contenedores (mantiene datos) |
| `make clean-all` | Para + borra volúmenes ( borra datos) |
| `make tunnel-staging` | Instrucciones para Cloudflare tunnel |
| `make api-key` | Muestra API keys de experimentos en DB |

---

## 9. Documentación

| Archivo | Contenido |
|---|---|
| `docs/Design/Conceptos/DevOp.md` | Guía completa de entornos, docker-compose, .env, comandos y CI/CD |
| `docs/Design/Conceptos/Objetivos.md` | Guía práctica PostgreSQL + Redis con comandos reales para contenedores |
| `SDK/docs/index.md` | Índice de la documentación del SDK |
| `SDK/docs/quickstart.md` | Guía de inicio rápido del SDK |

---

## 10. Google Colab Notebook

**Archivo:** `SDK/examples/demeter_colab_demo.ipynb`

Notebook de 11 celdas que:
1. Instala `demeter_sdk` desde Test PyPI
2. Conecta a `https://patata.monters.org`
3. Descarga y enriquece telemetría real
4. Genera 4 gráficas (VPD, timeseries, boxplot, heatmap)
5. Exporta Excel + CSV con descarga automática en Colab

Incluye **Celda 4b** (comentada) para datos offline sin servidor.

**Para obtener la API key:**
```bash
docker exec demeter-db psql -U postgres -d demeter_db \
  -c "SELECT id, name, api_key FROM experimentos;"
```

---

## 11. Git: Rama y commits

**Rama:** `feature/sdk-v1` en `github.com/DanielMf31/Proyecto_Demeter`

| Commit | Descripción |
|---|---|
| `0fece06` | SDK v1.0 completo — 6 módulos, docs, LIMS UI |
| `4c32d90` | Tests (59), staging compose, Colab, pyproject.toml fix email |
| `62de277` | Fix TS build: `vpd` en `SensorChart.metricConfigs` |
| `9f03b20` | Fix nginx: upstream `backend` → `demeter-api` |
| `0cb3e77` | Colab actualizado con URL `patata.monters.org` |

---

## Próximos pasos sugeridos

- [ ] Crear `.env.prod` definitivo con contraseñas seguras en el servidor
- [ ] Ejecutar `make staging` y verificar con el Colab
- [ ] Abrir PR de `feature/sdk-v1` → `main`
- [ ] Publicar SDK en PyPI real (cuando estén todos los tests pasando en CI)

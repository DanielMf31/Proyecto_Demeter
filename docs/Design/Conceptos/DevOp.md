# Entornos, Docker Compose y `.env` — Guía Completa

## El problema que resuelve esta separación

Una misma aplicación se comporta de forma diferente según dónde corre:

| Necesidad | Desarrollo | Staging | Producción |
|---|---|---|---|
| Recarga automática del código | ✅ Sí | ❌ No | ❌ No |
| Puertos expuestos en el host | ✅ Para debugging | Parcialmente | ❌ Nunca |
| Base de datos con datos reales | ❌ Datos de prueba | Datos de prueba | ✅ Reales |
| Restart automático si falla | ❌ No molesta | ✅ Sí | ✅ Sí |
| Debug / Swagger UI visible | ✅ Sí | ✅ Sí | ❌ No |

Si tuvieras un solo `docker-compose.yml` con todo mezclado, tendrías que editar el archivo cada vez que cambias de entorno → errores humanos, configuraciones que se cuelan a producción, etc.

## La arquitectura de archivos del proyecto

```
docker-compose.yml           ← BASE: servicios, redes, volúmenes comunes a TODOS
docker-compose.override.yml  ← DEV: se fusiona AUTOMÁTICAMENTE en local
docker-compose.staging.yml   ← STAGING: se aplica manualmente con -f
docker-compose.prod.yml       ← PROD: se aplica manualmente con -f
```

```
.env.example   ← Plantilla documentada (sí va a Git, sin secretos reales)
.env.local     ← Tu máquina local (NO va a Git)
.env.staging   ← Variables de staging (NO va a Git con contraseñas reales)
.env.prod      ← Variables de producción (NUNCA a Git)
.env           ← El archivo que Docker usa realmente (lo copias antes de arrancar)
```

> [!CAUTION]
> `.env`, `.env.local`, `.env.staging`, `.env.prod` están en `.gitignore`.
> Nunca subas contraseñas reales al repositorio.

---

## Qué hace cada `docker-compose`

### `docker-compose.yml` — La BASE

Define la estructura común que **siempre** existe:
- Qué servicios hay (`api`, `frontend`, `db`, `redis`, `math-worker`, `sequencer`)
- Variables de entorno base
- La red interna `demeter-net`
- Los volúmenes persistentes

**Nunca** lo ejecutas solo. Siempre se combina con un override.

---

### `docker-compose.override.yml` — Desarrollo (DEV)

> **Se fusiona automáticamente** cuando haces `docker compose up`. Docker lo detecta solo.

Añade sobre la base:
- **Bind mounts** — tu código local se monta dentro del contenedor, los cambios se reflejan en tiempo real sin rebuild
- **Puertos expuestos** — `5173:5173` (frontend Vite), `8000:8000` (API), `5432:5432` (DB), `6380:6379` (Redis)
- **Hot reload** — `npm run dev` con `--host 0.0.0.0`

```bash
# Arrancar en modo desarrollo (usa base + override automáticamente)
docker compose up -d

# Rebuildar si cambias el Dockerfile
docker compose up -d --build
```

---

### `docker-compose.staging.yml` — Staging

Simula producción en el portátil o servidor con datos de prueba.

Diferencias clave respecto a dev:
- **Build de producción** del frontend (no Vite dev server)
- **Puertos distintos** para no chocar con el stack de dev: `5175` (frontend), `8001` (API), `5433` (DB), `6381` (Redis)
- **`restart: unless-stopped`** — si falla, se reinicia
- **Volumen DB separado** (`postgres_staging`) — no mezcla datos con dev

```bash
# Arrancar staging (fusiona base + staging.yml)
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

# Acceso:
# Frontend → http://localhost:5175
# API docs → http://localhost:8001/api/docs
```

---

### `docker-compose.prod.yml` — Producción

Para el servidor real (`patata.monters.org`).

Diferencias clave:
- **`restart: always`** — siempre se reinicia, incluso tras reboot del servidor
- **Labels de Traefik** — el proxy inverso (Traefik) usa estas etiquetas para enrutar `patata.monters.org` → contenedor correcto
- **Puertos NO expuestos** en DB y Redis — solo accesibles dentro de la red Docker interna
- No hay bind mounts ni hot reload

```bash
# Arrancar producción (en el servidor)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Cómo se relacionan los `.env` con Docker Compose

Docker Compose **siempre** lee el archivo `.env` de la raíz del proyecto automáticamente y sustituye las variables `${VARIABLE}` que encuentre en los yml.

```
.env  ←── Docker Compose lo lee automáticamente
 │
 ├── DEMETER_POSTGRES_USER=postgres
 ├── DEMETER_POSTGRES_PASSWORD=postgres_local_pass
 └── DEMETER_ENV=development
         │
         ▼
docker-compose.yml usa ${DEMETER_POSTGRES_USER} en:
  environment:
    - POSTGRES_USER=${DEMETER_POSTGRES_USER}
```

### El flujo correcto antes de arrancar

```bash
# 1. Elige el .env del entorno que quieres usar
cp .env.staging .env       # para staging
cp .env.prod .env          # para producción

# 2. Edita los secretos reales (contraseñas, API keys)
nano .env

# 3. Arranca con el compose del entorno
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### Jerarquía de variables (de mayor a menor prioridad)

```
Variables de entorno del sistema (export VAR=valor)
    ↓
Variables en el docker-compose.yml directamente (environment:)
    ↓
Archivo .env en la raíz del proyecto   ← lo que usamos nosotros
    ↓
Valores por defecto en el yml (${VAR:-valor_defecto})
```

---

## Qué ejecutar según el entorno

| Entorno | Comando | `.env` a usar |
|---|---|---|
| **Desarrollo (portátil)** | `docker compose up -d` | `.env.local` → copiar como `.env` |
| **Staging (portátil)** | `docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build` | `.env.staging` → `.env` |
| **Producción (servidor)** | `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build` | `.env.prod` → `.env` |

---

## Automatizar los despliegues con scripts Makefile

Crea un `Makefile` en la raíz del proyecto:

```makefile
# ─── Desarrollo ───────────────────────────────────────────────────────────────
dev:
	cp .env.local .env
	docker compose up -d

dev-build:
	cp .env.local .env
	docker compose up -d --build

dev-down:
	docker compose down

# ─── Staging ──────────────────────────────────────────────────────────────────
staging:
	cp .env.staging .env
	docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

staging-down:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml down

# ─── Producción ───────────────────────────────────────────────────────────────
prod:
	cp .env.prod .env
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# ─── Seeder ───────────────────────────────────────────────────────────────────
seed:
	docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data

# ─── Logs ─────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f --tail=50

logs-api:
	docker logs demeter-api -f --tail=50
```

Uso:
```bash
make dev        # Arranca en desarrollo
make staging    # Arranca staging
make prod       # Arranca producción en el servidor
make seed       # Puebla la DB con datos de prueba
make logs-api   # Sigue los logs de la API
```

---

## Flujo de CI/CD futuro (GitHub Actions)

```
Push a main
    └─► GitHub Actions
            ├─► Tests
            ├─► Docker build
            └─► SSH al servidor
                    ├─► git pull
                    ├─► cp .env.prod .env
                    └─► docker compose -f ... up -d --build
```

El secreto `.env.prod` se guarda en GitHub Secrets, nunca en el repositorio.

---

## Resumen en una línea

> **Base** define qué existe, **override** añade comodidades de desarrollo, **staging/prod** endurecen la configuración para entornos reales. El `.env` activo es siempre el que llamas `.env` — tú decides cuál copiar antes de arrancar.

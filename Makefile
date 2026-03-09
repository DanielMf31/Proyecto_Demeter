# =============================================================================
# DEMETER — Makefile de Despliegue
# =============================================================================
# Uso: make <comando>
# Requiere: docker, docker compose, git
#
# ENTORNOS:
#   local    -> localhost (dev, hot-reload)
#   staging  -> patata.monters.org desde portátil (tunnel Cloudflare)
#   prod     -> servidor remoto (SSH manual)
# =============================================================================

.PHONY: help \
        dev dev-build dev-down dev-logs dev-seed \
        staging staging-build staging-down staging-logs staging-seed staging-restart \
        prod \
        migrate dev-migrate \
        rpi-up rpi-build rpi-pull rpi-down rpi-logs rpi-shell rpi-status \
        fw-build fw-build-gateway fw-build-sensor fw-build-actuador \
        fw-flash fw-flash-gateway fw-flash-sensor fw-flash-actuador fw-flash-sensor-test \
        fw-monitor fw-monitor-gateway fw-monitor-sensor fw-monitor-actuador \
        seed logs logs-api logs-db logs-redis logs-frontend \
        clean clean-all status ps pull \
        tunnel-staging api-key test-all

RPI_COMPOSE = docker compose -f docker-compose.rpi.yml --env-file .env.rpi

# Imágenes remotas en GitHub Container Registry
GHCR_REPO    = ghcr.io/danielmf31/proyecto_demeter
GHCR_GATEWAY = $(GHCR_REPO)/gateway:latest
GHCR_UI      = $(GHCR_REPO)/local-ui:latest

STAGING_COMPOSE = docker compose -f docker-compose.yml -f docker-compose.staging.yml

# ─── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  DEMETER - Comandos de Despliegue"
	@echo ""
	@echo "  DESARROLLO (localhost)"
	@echo "  -----------------------------------------------"
	@echo "  dev              Arranca dev con hot-reload (localhost:5173 / API:8000)"
	@echo "  dev-build        Arranca dev forzando rebuild"
	@echo "  dev-down         Para el entorno de desarrollo"
	@echo "  dev-seed         Puebla la DB de dev con datos de prueba"
	@echo "  dev-logs         Sigue los logs de desarrollo"
	@echo ""
	@echo "  STAGING (patata.monters.org desde portátil)"
	@echo "  -----------------------------------------------"
	@echo "  staging          Arranca staging (necesita CLOUDFLARE_TUNNEL_TOKEN en .env.staging)"
	@echo "  staging-build    Arranca staging con rebuild completo"
	@echo "  staging-down     Para el entorno de staging"
	@echo "  staging-seed     Puebla la DB de staging con datos de prueba"
	@echo "  staging-logs     Sigue los logs de staging"
	@echo "  staging-restart  Reinicia staging sin borrar volúmenes"
	@echo ""
	@echo "  TESTING"
	@echo "  -----------------------------------------------"
	@echo "  test-all         Ejecuta las 4 suites de tests (Firmware, Backend, Frontend, Raspberry)"
	@echo ""
	@echo "  UTILIDADES"
	@echo "  -----------------------------------------------"
	@echo "  migrate          Corre migraciones Alembic en staging (upgrade head)"
	@echo "  dev-migrate      Corre migraciones Alembic en dev"
	@echo "  seed             Puebla la DB activa con datos de prueba"
	@echo "  logs             Todos los logs del stack activo"
	@echo "  logs-api         Logs de la API (FastAPI)"
	@echo "  logs-db          Logs de PostgreSQL"
	@echo "  logs-redis       Logs de Redis"
	@echo "  logs-frontend    Logs del frontend/nginx"
	@echo "  status           Estado de los contenedores Demeter"
	@echo "  ps               Lista todos los contenedores"
	@echo "  pull             Descarga la ultima version del codigo"
	@echo "  clean            Para contenedores (mantiene datos)"
	@echo "  clean-all        Para y borra volúmenes (pierde datos DB)"
	@echo "  api-key          Muestra API keys de experimentos en la DB"
	@echo ""
	@echo "  FIRMWARE (PlatformIO, ejecutar EN la Raspberry)"
	@echo "  -----------------------------------------------"
	@echo "  fw-build            Compila los 3 firmwares"
	@echo "  fw-build-gateway    Compila solo gateway"
	@echo "  fw-build-sensor     Compila solo sensor cluster"
	@echo "  fw-build-actuador   Compila solo actuador"
	@echo "  fw-flash            Flashea los 3 nodos"
	@echo "  fw-flash-gateway    Flashea gateway (ttyACM0)"
	@echo "  fw-flash-sensor     Flashea sensor cluster (ttyACM3)"
	@echo "  fw-flash-actuador   Flashea actuador (ttyACM2)"
	@echo "  fw-monitor          Monitor serie gateway (ttyACM0)"
	@echo "  fw-monitor-sensor   Monitor serie sensor (ttyACM3)"
	@echo "  fw-monitor-actuador Monitor serie actuador (ttyACM2)"
	@echo ""
	@echo "  RASPBERRY PI (ejecutar EN la Raspberry)"
	@echo "  -----------------------------------------------"
	@echo "  rpi-up           Arranca con imagen local (build previo o pull previo)"
	@echo "  rpi-build        Construye la imagen localmente y arranca"
	@echo "  rpi-pull         Descarga imagen de ghcr.io y arranca"
	@echo "  rpi-down         Para el gateway"
	@echo "  rpi-logs         Sigue los logs del gateway en tiempo real"
	@echo "  rpi-shell        Abre una shell dentro del contenedor gateway"
	@echo "  rpi-status       Estado del contenedor gateway"
	@echo ""

# ─── DESARROLLO ───────────────────────────────────────────────────────────────
dev:
	@echo "Arrancando entorno de desarrollo..."
	@cp .env.local .env
	docker compose up -d
	@echo "Dev listo -> http://localhost:5173 | API: http://localhost:8000/api/docs"

dev-build:
	@echo "Rebuildeando entorno de desarrollo..."
	@cp .env.local .env
	docker compose up -d --build

dev-down:
	@echo "Parando dev..."
	docker compose down

dev-logs:
	docker compose logs -f --tail=80

dev-migrate:
	@echo "Corriendo migraciones Alembic (dev)..."
	docker exec demeter-api sh -c "cd /app/Software/Servidor/Backend && alembic upgrade head"
	@echo "Migraciones completadas"

dev-seed: dev-migrate
	@echo "Seeding dev DB..."
	docker exec demeter-api python -m BD.seed_data
	@echo "Seed completado"

# ─── STAGING ──────────────────────────────────────────────────────────────────
staging:
	@echo "Arrancando entorno de staging..."
	@cp .env.staging .env
	$(STAGING_COMPOSE) up -d
	@echo "Staging listo:"
	@echo "  -> https://patata.monters.org (si el tunel esta activo)"
	@echo "  -> http://localhost:5175 (acceso directo)"
	@echo "  -> http://localhost:8001/api/docs (Swagger)"

staging-build:
	@echo "Rebuildeando staging completo..."
	@cp .env.staging .env
	$(STAGING_COMPOSE) up -d --build

staging-down:
	@echo "Parando staging..."
	$(STAGING_COMPOSE) down

staging-restart:
	@echo "Reiniciando staging..."
	$(STAGING_COMPOSE) restart

staging-logs:
	$(STAGING_COMPOSE) logs -f --tail=80

migrate:
	@echo "Corriendo migraciones Alembic (staging)..."
	docker exec demeter-api sh -c "cd /app/Software/Servidor/Backend && alembic upgrade head"
	@echo "Migraciones completadas"

staging-seed: migrate
	@echo "Seeding staging DB..."
	docker exec demeter-api python -m BD.seed_data
	@echo "Seed completado"

# ─── PRODUCCION ───────────────────────────────────────────────────────────────
prod:
	@echo ""
	@echo "  Despliegue en PRODUCCION (servidor remoto)"
	@echo ""
	@echo "  1. SSH al servidor:"
	@echo "     ssh danielmf31@patata.monters.org"
	@echo ""
	@echo "  2. En el servidor:"
	@echo "     cd ~/Proyecto_Demeter"
	@echo "     git pull origin feature/sdk-v1"
	@echo "     cp .env.prod .env"
	@echo "     docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
	@echo ""
	@echo "  3. Semilla (solo primera vez):"
	@echo "     docker exec demeter-api python -m BD.seed_data"
	@echo ""

# ─── UTILIDADES ───────────────────────────────────────────────────────────────
seed: migrate
	@echo "Seeding DB activa..."
	docker exec demeter-api python -m BD.seed_data

logs:
	docker compose logs -f --tail=50

logs-api:
	docker logs demeter-api -f --tail=80

logs-db:
	docker logs demeter-db -f --tail=50

logs-redis:
	docker logs demeter-redis -f --tail=50

logs-frontend:
	docker logs demeter-frontend -f --tail=50

status:
	@echo "Estado de contenedores Demeter:"
	@docker ps --filter "name=demeter" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

ps:
	@docker ps -a --filter "name=demeter" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

pull:
	@echo "Actualizando codigo..."
	git pull
	@echo "Codigo actualizado"

clean:
	@echo "Limpiando contenedores..."
	docker compose down
	$(STAGING_COMPOSE) down 2>/dev/null || true
	@echo "Contenedores eliminados (datos DB conservados)"

clean-all:
	@echo "ATENCION: Se borraran todos los volúmenes (datos BD incluidos)"
	@read -p "Continuar? [s/N] " confirm && [ "$$confirm" = "s" ] || exit 1
	docker compose down -v
	$(STAGING_COMPOSE) down -v 2>/dev/null || true
	@echo "Limpieza completa"

api-key:
	@echo "API Keys de experimentos:"
	@docker exec demeter-db psql -U postgres -d demeter_staging \
		-c "SELECT id, name, api_key FROM experiments ORDER BY id;" 2>/dev/null || \
	docker exec demeter-db psql -U postgres -d demeter_db \
		-c "SELECT id, name, api_key FROM experiments ORDER BY id;" 2>/dev/null || \
	echo "No se pudo conectar. Asegurate de que el stack esta levantado."

# ─── FIRMWARE ─────────────────────────────────────────────────────────────────
# Dispositivos:
#   /dev/ttyACM0 → Gateway   (9C:13:9E:A8:6F:CC) Node 1
#   /dev/ttyACM2 → Actuador  (9C:13:9E:AC:50:C4) Node 3
#   /dev/ttyACM3 → Sensor    (20:6E:F1:85:58:D0) Node 2

fw-build:
	@echo "Compilando todos los firmwares..."
	cd Firmware && pio run -e gateway -e sensor_cluster -e actuador
	@echo "Firmwares compilados"

fw-build-gateway:
	cd Firmware && pio run -e gateway

fw-build-sensor:
	cd Firmware && pio run -e sensor_cluster

fw-build-actuador:
	cd Firmware && pio run -e actuador

fw-flash:
	@echo "Flasheando los 3 nodos..."
	cd Firmware && pio run -e gateway -t upload
	cd Firmware && pio run -e sensor_cluster -t upload
	cd Firmware && pio run -e actuador -t upload
	@echo "Los 3 nodos flasheados"

fw-flash-gateway:
	@echo "Flasheando gateway (ttyACM0)..."
	cd Firmware && pio run -e gateway -t upload

fw-flash-sensor:
	@echo "Flasheando sensor cluster (ttyACM3)..."
	cd Firmware && pio run -e sensor_cluster -t upload

fw-flash-actuador:
	@echo "Flasheando actuador (ttyACM2)..."
	cd Firmware && pio run -e actuador -t upload

fw-flash-sensor-test:
	@echo "Flasheando sensor_test al ESP32..."
	cd Firmware && pio run -e sensor_test -t upload

fw-monitor:
	@echo "Monitor serie del gateway (ttyACM0)..."
	cd Firmware && pio device monitor -p /dev/ttyACM0 -b 115200

fw-monitor-gateway: fw-monitor

fw-monitor-sensor:
	@echo "Monitor serie del sensor cluster (ttyACM3)..."
	cd Firmware && pio device monitor -p /dev/ttyACM3 -b 115200

fw-monitor-actuador:
	@echo "Monitor serie del actuador (ttyACM2)..."
	cd Firmware && pio device monitor -p /dev/ttyACM2 -b 115200

# ─── RASPBERRY PI ─────────────────────────────────────────────────────────────
rpi-up:
	@echo "Arrancando Gateway Orchestrator en la Raspberry Pi..."
	$(RPI_COMPOSE) up -d
	@echo "Gateway listo. Logs: make rpi-logs"

rpi-build:
	@echo "Construyendo imagen localmente..."
	$(RPI_COMPOSE) up -d --build
	@echo "Imagen construida y gateway arrancado"

rpi-pull:
	@echo "Descargando imagenes de ghcr.io..."
	DEMETER_GATEWAY_IMAGE=$(GHCR_GATEWAY) DEMETER_UI_IMAGE=$(GHCR_UI) $(RPI_COMPOSE) pull
	@echo "Arrancando con imagenes remotas..."
	DEMETER_GATEWAY_IMAGE=$(GHCR_GATEWAY) DEMETER_UI_IMAGE=$(GHCR_UI) $(RPI_COMPOSE) up -d
	@echo "Gateway listo (imagen remota). Logs: make rpi-logs"

rpi-down:
	@echo "Parando Gateway Orchestrator..."
	$(RPI_COMPOSE) down

rpi-logs:
	$(RPI_COMPOSE) logs -f --tail=100

rpi-shell:
	@echo "Abriendo shell en el contenedor gateway..."
	docker exec -it demeter-gateway /bin/bash

rpi-status:
	@echo "Estado del Gateway Orchestrator:"
	@docker ps --filter "name=demeter-gateway" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
	@echo ""
	@echo "Variables activas:"
	@docker exec demeter-gateway env 2>/dev/null | grep DEMETER_ | sort || echo "  (contenedor no arrancado)"

rpi-pio-list:
	@echo "Listando dispositivos conectados a la Raspberry Pi..."
	pio device list

rpi-pio-monitor:
	@echo "Abriendo monitor serie (PlatformIO)..."
	@echo "Uso: make rpi-pio-monitor PORT=/dev/ttyUSB0"
	pio device monitor -p $(or $(PORT),/dev/ttyS0) -b 115200

# ─── TESTING UNIVERAL ─────────────────────────────────────────────────────────
test-all:
	@echo "======================================================"
	@echo " Ejecutando Suite Universal de Tests DEMETER "
	@echo "======================================================"
	@echo ""
	@echo "[1/4] Firmware C++ (PlatformIO)"
	cd Firmware && bash -c "set -o pipefail; pio test -e native | sed '/Verbosity level can be increased/d'"
	@echo ""
	@echo "[2/4] Backend (pytest)"
	cd Software/Servidor/Backend && pytest tests/
	@echo ""
	@echo "[3/4] Frontend (Vitest)"
	cd Software/Servidor/Frontend/Demeter-React && npm run test -- --run
	@echo ""
	@echo "[4/4] Raspberry Gateway (pytest)"
	cd Software/Raspberry && PYTHONPATH=src:../Common pytest tests/
	@echo ""
	@echo "======================================================"
	@echo " Todos los tests han pasado exitosamente "
	@echo "======================================================"

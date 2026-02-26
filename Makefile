# =============================================================================
# DEMETER — Makefile de Despliegue
# =============================================================================
# Uso: make <comando>
# Requiere: docker, docker compose, git
#
# ENTORNOS:
#   local    → localhost (dev, hot-reload)
#   staging  → patata.monters.org desde portátil (tunnel Cloudflare)
#   prod     → servidor remoto (SSH manual)
# =============================================================================

.PHONY: help \
        dev dev-build dev-down dev-logs dev-seed \
        staging staging-build staging-down staging-logs staging-seed staging-restart \
        prod prod-down \
        seed logs logs-api logs-db logs-redis logs-frontend \
        clean clean-all status ps pull \
        tunnel-staging api-key

# ─── Help ─────────────────────────────────────────────────────────────────────
help: ## Muestra esta ayuda
	@echo ""
	@echo "  🌿 DEMETER — Comandos de Despliegue"
	@echo ""
	@echo "  DESARROLLO (localhost)"
	@echo "  ─────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*##"} /^dev/ {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "  STAGING (patata.monters.org desde portátil)"
	@echo "  ─────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*##"} /^staging/ {printf "  \033[35m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "  UTILIDADES"
	@echo "  ─────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*##"} /^(seed|logs|clean|status|ps|pull|tunnel|api)/ {printf "  \033[33m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# ─── DESARROLLO (localhost) ───────────────────────────────────────────────────
dev: ## Arranca en dev (hot-reload, localhost:5173 / API:8000)
	@echo "🔧 Arrancando entorno de desarrollo..."
	@cp .env.local .env
	docker compose up -d
	@echo "✅ Dev listo → http://localhost:5173 | API: http://localhost:8000/api/docs"

dev-build: ## Arranca dev forzando rebuild de imágenes
	@echo "🔧 Rebuildeando entorno de desarrollo..."
	@cp .env.local .env
	docker compose up -d --build

dev-down: ## Para el entorno de desarrollo
	@echo "🛑 Parando dev..."
	docker compose down

dev-logs: ## Sigue los logs del entorno de desarrollo
	docker compose logs -f --tail=80

dev-seed: ## Puebla la DB de dev con datos de prueba
	@echo "🌱 Seeding dev DB..."
	docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data
	@echo "✅ Seed completado"

# ─── STAGING (patata.monters.org desde portátil) ─────────────────────────────
STAGING_COMPOSE = docker compose -f docker-compose.yml -f docker-compose.staging.yml

staging: ## Arranca staging (patata.monters.org → portátil via Cloudflare)
	@echo "🎭 Arrancando entorno de staging..."
	@cp .env.staging .env
	$(STAGING_COMPOSE) up -d
	@echo "✅ Staging listo:"
	@echo "   → Frontend: http://localhost:5175  (o https://patata.monters.org si el túnel está activo)"
	@echo "   → API docs: http://localhost:8001/api/docs"
	@echo "   → DB:       localhost:5433"

staging-build: ## Arranca staging forzando rebuild completo
	@echo "🎭 Rebuildeando staging completo..."
	@cp .env.staging .env
	$(STAGING_COMPOSE) up -d --build

staging-down: ## Para el entorno de staging
	@echo "🛑 Parando staging..."
	$(STAGING_COMPOSE) down

staging-restart: ## Reinicia staging sin borrar volúmenes
	@echo "🔄 Reiniciando staging..."
	$(STAGING_COMPOSE) restart

staging-logs: ## Sigue los logs de staging
	$(STAGING_COMPOSE) logs -f --tail=80

staging-seed: ## Puebla la DB de staging con datos de prueba
	@echo "🌱 Seeding staging DB..."
	docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data
	@echo "✅ Seed completado"

# ─── PRODUCCIÓN (instrucciones SSH) ───────────────────────────────────────────
prod: ## Muestra instrucciones para desplegar en producción via SSH
	@echo ""
	@echo "  🚀 Despliegue en PRODUCCIÓN (patata.monters.org — servidor remoto)"
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
	@echo "     docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data"
	@echo ""

# ─── UTILIDADES ───────────────────────────────────────────────────────────────
seed: ## Puebla la DB activa con datos de prueba
	@echo "🌱 Seeding DB activa..."
	docker exec demeter-api python -m Software.Servidor.Backend.BD.seed_data

logs: ## Sigue todos los logs del stack activo
	docker compose logs -f --tail=50

logs-api: ## Logs solo de la API (FastAPI)
	docker logs demeter-api -f --tail=80

logs-db: ## Logs de PostgreSQL
	docker logs demeter-db -f --tail=50

logs-redis: ## Logs de Redis
	docker logs demeter-redis -f --tail=50

logs-frontend: ## Logs del contenedor frontend/nginx
	docker logs demeter-frontend -f --tail=50

status: ## Estado de todos los contenedores Demeter
	@echo "📊 Estado de contenedores Demeter:"
	@docker ps --filter "name=demeter" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

ps: ## Lista todos los contenedores (incluyendo parados)
	@docker ps -a --filter "name=demeter" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

pull: ## Descarga la última versión del código
	@echo "⬇️  Actualizando código..."
	git pull
	@echo "✅ Código actualizado"

clean: ## Para y borra contenedores (mantiene volúmenes DB)
	@echo "🧹 Limpiando contenedores..."
	docker compose down
	$(STAGING_COMPOSE) down 2>/dev/null || true
	@echo "✅ Contenedores eliminados (datos DB conservados)"

clean-all: ## ⚠️  Para todo y BORRA también los volúmenes (pierde datos DB)
	@echo "⚠️  ATENCIÓN: Se borrarán todos los volúmenes (datos BD incluidos)"
	@read -p "¿Continuar? [s/N] " confirm && [ "$$confirm" = "s" ] || exit 1
	docker compose down -v
	$(STAGING_COMPOSE) down -v 2>/dev/null || true
	@echo "✅ Limpieza completa"

tunnel-staging: ## Arranca el túnel Cloudflare apuntando al staging local (puerto 80)
	@echo "🌐 Iniciando túnel Cloudflare para staging..."
	@echo "   Asegúrate de tener cloudflared instalado: sudo snap install cloudflared"
	@echo "   Necesitas también: cloudflared tunnel login"
	@echo ""
	@echo "   Apuntando puerto 80 a patata.monters.org..."
	cloudflared tunnel --url http://localhost:80
	@echo ""
	@echo "   Alternativa con ngrok (sin cuenta Cloudflare):"
	@echo "   ngrok http 8001  ← para exponer solo la API"

api-key: ## Muestra las API keys de los experimentos en la DB activa
	@echo "🔑 API Keys de experimentos:"
	@docker exec demeter-db psql -U postgres -d demeter_db \
		-c "SELECT id, name, api_key FROM experimentos ORDER BY id;" 2>/dev/null || \
	docker exec demeter-db psql -U postgres -d demeter_staging \
		-c "SELECT id, name, api_key FROM experimentos ORDER BY id;" 2>/dev/null || \
	echo "❌ No se pudo conectar. Asegúrate de que el stack está levantado."

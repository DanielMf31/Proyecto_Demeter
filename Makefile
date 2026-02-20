.PHONY: help dev staging prod logs down clean

help:
	@echo "Demeter Platform - Operations Manager"
	@echo "====================================="
	@echo "make dev       - Start the local development environment (hot-reload, ports exposed)."
	@echo "make staging   - Start the testing/staging environment (requires .env.staging)."
	@echo "make prod      - Start the production environment (requires .env.prod)."
	@echo "make logs      - View logs of all running containers."
	@echo "make down      - Stop and remove all containers, networks, and volumes."
	@echo "make clean     - Destroy all containers, dangling images, and anonymous volumes."

dev:
	@echo "--> Preparing Local Environment"
	@if [ ! -f .env ]; then cp .env.local .env; echo "Copied .env.local to .env"; fi
	@echo "--> Starting Local Containers"
	docker compose up -d --build

staging:
	@echo "--> Preparing Staging Environment"
	@cp .env.staging .env
	@echo "--> Starting Staging Containers"
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod:
	@echo "--> Preparing Production Environment"
	@cp .env.prod .env
	@echo "--> Starting Production Containers"
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

logs:
	docker compose logs -f

down:
	docker compose down -v

clean: down
	docker system prune -f

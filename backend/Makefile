# Makefile for managing backend with Docker

.DEFAULT_GOAL := help

YELLOW=\033[1;33m
RESET=\033[0m

help:
	@echo "$(YELLOW)Available commands:$(RESET)"
	@echo "  make dev       -> Start backend in development mode (with override, runs migrations)"
	@echo "  make prod      -> Start backend in production mode (runs migrations)"
	@echo "  make migrate   -> Run Alembic migrations inside backend container"
	@echo "  make down      -> Stop containers"
	@echo "  make logs      -> Show logs (backend container)"
	@echo "  make build     -> Build dev images"
	@echo "  make rebuild   -> Force rebuild images (no cache)"
	@echo "  make ps        -> Show running containers"
	@echo "  make shell     -> Open a shell inside backend container"

# Development (docker-compose.yml + override)
dev:
	docker compose --env-file .env.dev up -d --build
	$(MAKE) migrate ENV=.env.dev

# Production (only base file, no override)
prod:
	docker compose -f docker-compose.yml --env-file .env.prod up -d --build
	$(MAKE) migrate ENV=.env.prod

# Stop dev environment
stop-dev:
	docker compose --env-file .env.dev down

# Stop prod environment
stop-prod:
	docker compose --env-file .env.prod down

# Full cleanup (⚠️ removes containers, images, networks, and volumes!)
clean:
	docker stop $$(docker ps -q) || true
	docker system prune -a --volumes -f

# Run Alembic migrations
migrate:
	@if [ -z "$(ENV)" ]; then \
		echo "Usage: make migrate ENV=.env.dev (or .env.prod)"; \
		exit 1; \
	fi
	docker compose --env-file $(ENV) run --rm backend alembic upgrade head

# Stop containers
down:
	docker compose down

# Logs
logs:
	docker compose logs -f backend

# Build dev
build:
	docker compose --env-file .env.dev build

# Rebuild dev (no cache)
rebuild:
	docker compose --env-file .env.dev build --no-cache

# Show running containers
ps:
	docker compose ps

# Open shell inside backend container
shell:
	docker compose exec backend /bin/bash

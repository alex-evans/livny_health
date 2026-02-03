.PHONY: dev frontend backend install db test dev-inmemory docker docker-build docker-down

# Database URL for local development
export LIVNY_DATABASE_URL := postgresql+asyncpg://postgres:postgres@localhost:5432/livny

dev:
	@echo "Starting all services..."
	@$(MAKE) db
	@LIVNY_STORAGE_BACKEND=postgres $(MAKE) -j2 frontend backend

dev-inmemory:
	@echo "Starting all services with in-memory database..."
	LIVNY_STORAGE_BACKEND=memory $(MAKE) -j2 frontend backend

frontend:
	cd frontend && npm run dev

backend:
	cd backend \
	&& source .venv/bin/activate \
	&& uv sync \
	&& uv run uvicorn main:app --reload --port 8000

db:
	cd backend \
	&& docker-compose up -d \
	&& echo "Waiting for database to be ready..." \
	&& until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done \
	&& source .venv/bin/activate \
	&& uv run alembic upgrade head \
	&& LIVNY_STORAGE_BACKEND=postgres python seed_postgres.py \
	&& echo "Database is set up."

install:
	cd frontend && npm install
	cd backend && uv sync

test:
	cd backends && source .venv/bin/activate && uv sync && pytest
	cd frontend && npm test

# Docker commands (no local dependencies needed except Docker)
docker:
	@echo "Starting all services with Docker..."
	docker compose up

docker-build:
	@echo "Building and starting all services..."
	docker compose up --build

docker-down:
	@echo "Stopping all services..."
	docker compose down


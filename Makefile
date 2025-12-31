.PHONY: dev frontend services bff install

dev:
	@echo "Starting all services..."
	@make -j3 frontend services bff

frontend:
	cd frontend && npm run dev

services:
	cd backend/services && uv run uvicorn main:app --reload --port 8001

bff:
	cd backend/bff && uv run uvicorn main:app --reload --port 8000

install:
	cd frontend && npm install
	cd backend/services && uv sync
	cd backend/bff && uv sync

test:
	cd backend/services && source .venv/bin/activate && uv sync && pytest
	deactivate && cd backend/bff && source .venv/bin/activate && uv sync && pytest
	deactivate && cd frontend && npm test
 

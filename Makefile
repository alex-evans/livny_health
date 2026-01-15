.PHONY: dev frontend backend install

dev:
	@echo "Starting all services..."
	@make -j3 frontend backend

frontend:
	cd frontend && npm run dev

backend:
	cd backend \
	&& source .venv/bin/activate \
	&& uv sync \
	&& uv run uvicorn main:app --reload --port 8000

install:
	cd frontend && npm install
	cd backend && uv sync

test:
	cd backends && source .venv/bin/activate && uv sync && pytest
	cd frontend && npm test
 

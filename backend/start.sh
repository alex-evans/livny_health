#!/bin/bash
# Startup script for backend in Docker
# Runs migrations then starts the server

set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Seeding database..."
uv run python seed_postgres.py

echo "Starting server..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

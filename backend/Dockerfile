# Backend Dockerfile for development
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync

# Copy source code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose FastAPI port
EXPOSE 8000

# Start with the startup script (runs migrations + server)
CMD ["./start.sh"]

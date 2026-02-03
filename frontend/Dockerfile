# Frontend Dockerfile for development
FROM node:22-alpine

WORKDIR /app

# Install dependencies first (better caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start dev server with host flag for Docker networking
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

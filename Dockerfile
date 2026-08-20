# Stage 1: Pull HydraDB binary
FROM ghcr.io/hydra-db/hydradb:latest AS hydradb

# Stage 2: Build frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 3: Final image
FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl supervisor nginx && \
    rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /app /data/store /data/cache /data/auth-token

# Copy HydraDB binary from GHCR image
COPY --from=hydradb /usr/local/bin/graph-node /app/hydradb/graph-node
RUN chmod +x /app/hydradb/graph-node

# Copy backend
COPY backend/ /app/backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir neo4j fastapi uvicorn pydantic python-dotenv

# Copy frontend build
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy frontend nginx config (static for single container)
COPY nginx-single.conf /etc/nginx/conf.d/default.conf

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy seed script
COPY backend/seed_on_startup.py /app/backend/seed_on_startup.py

# Setup auth token
RUN echo "local-development-token-32-bytes" > /data/auth-token

# Working directory
WORKDIR /app

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

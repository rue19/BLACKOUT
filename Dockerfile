# Stage 1: Pull HydraDB binary and libraries
FROM ghcr.io/hydra-db/hydradb:latest AS hydradb

# Stage 2: Build frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
ARG VITE_API_BASE_URL=/
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 3: Final image
FROM python:3.11-slim

# Install system deps (envsubst from gettext-base)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl supervisor nginx ca-certificates gettext-base && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /etc/nginx/sites-enabled/default

# Create directories
RUN mkdir -p /app /data/store /data/cache

# Setup auth token
RUN echo "local-development-token-32-bytes" > /data/auth-token

# Copy HydraDB binary and required shared libraries from GHCR image
COPY --from=hydradb /usr/local/bin/graph-node /app/hydradb/graph-node
COPY --from=hydradb /usr/lib/x86_64-linux-gnu/libgraphblas.so* /usr/lib/x86_64-linux-gnu/
COPY --from=hydradb /usr/lib/x86_64-linux-gnu/libgomp.so* /usr/lib/x86_64-linux-gnu/
RUN chmod +x /app/hydradb/graph-node && ldconfig

# Copy backend and ingestion
COPY backend/ /app/backend/
COPY ingestion/ /app/ingestion/
WORKDIR /app/backend
RUN pip install --no-cache-dir neo4j fastapi uvicorn pydantic python-dotenv

# Copy frontend build
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy nginx config as template (envsubst at runtime for PORT)
COPY nginx-single.conf /etc/nginx/nginx-single.conf.template

# Copy startup scripts
COPY start-nginx.sh /app/start-nginx.sh
RUN chmod +x /app/start-nginx.sh

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Working directory
WORKDIR /app

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

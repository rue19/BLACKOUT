#!/bin/bash
set -e

echo "==================================="
echo "BLACKOUT Setup Script"
echo "==================================="

# Check prerequisites
echo ""
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

echo "Prerequisites check passed!"

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your ANTHROPIC_API_KEY"
fi

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data

# Start services
echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "==================================="
echo "BLACKOUT is running!"
echo "==================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "HydraDB Bolt: neo4j://localhost:7687"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Place your dataset in ./data/"
echo "3. Run the ingestion pipeline:"
echo "   docker compose exec backend python -m ingestion.run_pipeline /data"
echo ""

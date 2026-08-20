#!/bin/bash
# BLACKOUT - Start all services
# Usage: ./start_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

echo "============================================"
echo "  BLACKOUT - Starting all services"
echo "============================================"

# Check HydraDB is running
echo ""
echo "[1/3] Checking HydraDB..."
if curl -fsS http://127.0.0.1:9090/readyz >/dev/null 2>&1; then
    echo "  HydraDB is ready"
else
    echo "  HydraDB is NOT running!"
    echo "  Start it with: docker compose up -d hydradb"
    exit 1
fi

# Start backend
echo ""
echo "[2/3] Starting backend..."
export HYDRADB_BOLT_URI=bolt://127.0.0.1:7687
export HYDRADB_AUTH_TOKEN=local-development-token-32-bytes
cd "$SCRIPT_DIR/backend"
setsid "$VENV/bin/uvicorn" main:app --host 0.0.0.0 --port 8000 > /tmp/blackout-backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/blackout-backend.pid
sleep 2
if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    echo "  Backend is ready (port 8000, PID $BACKEND_PID)"
else
    echo "  Backend failed to start. Check /tmp/blackout-backend.log"
    exit 1
fi

# Start frontend
echo ""
echo "[3/3] Starting frontend..."
cd "$SCRIPT_DIR/frontend"
setsid npm run dev > /tmp/blackout-frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/blackout-frontend.pid
sleep 3
if curl -fsS http://localhost:5173 >/dev/null 2>&1; then
    echo "  Frontend is ready (port 5173, PID $FRONTEND_PID)"
else
    echo "  Frontend failed to start. Check /tmp/blackout-frontend.log"
    exit 1
fi

echo ""
echo "============================================"
echo "  All services running!"
echo "============================================"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  HydraDB:   bolt://127.0.0.1:7687"
echo ""
echo "  Stop with: ./stop_all.sh"
echo "============================================"

#!/bin/bash
# BLACKOUT - Stop all services

echo "Stopping BLACKOUT services..."

# Stop frontend
if [ -f /tmp/blackout-frontend.pid ]; then
    kill $(cat /tmp/blackout-frontend.pid) 2>/dev/null
    rm /tmp/blackout-frontend.pid
    echo "  Frontend stopped"
fi

# Stop backend
if [ -f /tmp/blackout-backend.pid ]; then
    kill $(cat /tmp/blackout-backend.pid) 2>/dev/null
    rm /tmp/blackout-backend.pid
    echo "  Backend stopped"
fi

# Stop HydraDB
docker compose down 2>/dev/null
echo "  HydraDB stopped"

echo "All services stopped."

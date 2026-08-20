#!/bin/bash
# BLACKOUT - Deploy to Railway
# Usage: ./deploy_railway.sh

set -e

echo "============================================"
echo "  BLACKOUT - Railway Deployment"
echo "============================================"

# Check railway CLI
if ! command -v railway &> /dev/null; then
    echo ""
    echo "Installing Railway CLI..."
    npm install -g @railway/cli 2>/dev/null || {
        echo "Failed to install Railway CLI."
        echo "Install manually: npm install -g @railway/cli"
        exit 1
    }
fi

# Check login
echo ""
echo "Checking Railway login..."
if ! railway whoami &> /dev/null; then
    echo "Not logged in. Running: railway login"
    railway login
fi

# Check if project exists
echo ""
echo "Checking Railway project..."
if ! railway status &> /dev/null 2>&1; then
    echo "No project linked. Creating new project..."
    railway init
fi

echo ""
echo "============================================"
echo "  Deploying services..."
echo "============================================"

# Deploy HydraDB first
echo ""
echo "[1/3] Deploying HydraDB..."
railway service hydradb 2>/dev/null || railway service create hydradb
railway up --service hydradb --docker docker-compose.railway.yml

# Deploy Backend
echo ""
echo "[2/3] Deploying Backend..."
railway service backend 2>/dev/null || railway service create backend
railway up --service backend

# Deploy Frontend
echo ""
echo "[3/3] Deploying Frontend..."
railway service frontend 2>/dev/null || railway service create frontend
railway up --service frontend

echo ""
echo "============================================"
echo "  Deployment complete!"
echo "============================================"
echo ""
echo "  Check your services:"
echo "  railway status"
echo ""
echo "  View logs:"
echo "  railway logs --service backend"
echo ""
echo "  Open dashboard:"
echo "  railway open"
echo "============================================"

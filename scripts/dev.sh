#!/usr/bin/env bash
set -e

echo "================================================="
echo "  Starting QUANTARA Local Development Stack      "
echo "================================================="

# Export PYTHONPATH
export PYTHONPATH=.

# Seed Database if not exists
python -m database.seeds.seed_data

# Start FastAPI Gateway in Background
echo "[INFO] Starting FastAPI Gateway on http://localhost:8000..."
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Start Next.js Web App
echo "[INFO] Starting Next.js Web Terminal on http://localhost:3000..."
cd apps/web && npm run dev &
WEB_PID=$!

trap "kill $API_PID $WEB_PID" EXIT
wait

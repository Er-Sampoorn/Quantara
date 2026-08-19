@echo off
echo =================================================
echo   Starting QUANTARA Local Development Stack
echo =================================================

set PYTHONPATH=.

echo [INFO] Seeding Database...
python -m database.seeds.seed_data

echo [INFO] Launching FastAPI Gateway...
start "Quantara API" uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

echo [INFO] Launching Next.js Web Terminal...
cd apps\web
start "Quantara Web" npm run dev

echo [READY] Quantara stack is running at http://localhost:3000 (Web) and http://localhost:8000 (API)

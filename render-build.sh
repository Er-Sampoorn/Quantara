#!/usr/bin/env bash
# Render Build Script
set -e

echo "[BUILD] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[BUILD] Initializing database..."
python -m database.seeds.seed_data

echo "[BUILD] Build complete!"

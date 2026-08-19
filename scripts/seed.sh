#!/usr/bin/env bash
set -e

echo "[INFO] Seeding Quantara Database..."
export PYTHONPATH=.
python -m database.seeds.seed_data

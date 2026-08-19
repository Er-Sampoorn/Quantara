#!/usr/bin/env bash
set -e

echo "[WARNING] Resetting Quantara Database..."
rm -f quantara.db
export PYTHONPATH=.
python -m database.seeds.seed_data
echo "[SUCCESS] Database reset and re-seeded."

@echo off
echo [INFO] Seeding Quantara Database...
set PYTHONPATH=.
python -m database.seeds.seed_data

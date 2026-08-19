@echo off
echo [WARNING] Resetting Quantara Database...
if exist quantara.db del quantara.db
set PYTHONPATH=.
python -m database.seeds.seed_data
echo [SUCCESS] Database reset and re-seeded.

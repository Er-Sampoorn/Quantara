@echo off
echo =================================================
echo   Running QUANTARA Test Suite
echo =================================================

set PYTHONPATH=.
pytest tests\ -v

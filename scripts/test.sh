#!/usr/bin/env bash
set -e

echo "================================================="
echo "  Running QUANTARA Test Suite                    "
echo "================================================="

export PYTHONPATH=.
pytest tests/ -v

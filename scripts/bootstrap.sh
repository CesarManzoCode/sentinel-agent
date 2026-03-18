#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
mkdir -p data/logs data/audit data/vector data/cache data/runtime
sentinel config validate

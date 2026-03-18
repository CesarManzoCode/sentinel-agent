#!/usr/bin/env bash
set -euo pipefail

export SENTINEL_ENV=development
export SENTINEL_PROFILE=debug
export SENTINEL_LOG_LEVEL=DEBUG
python -m sentinel chat

#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/setup_scrapling.sh            # minimal parser mode
#   bash scripts/setup_scrapling.sh --full     # full mode (fetchers/shell/ai + browser deps)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
FULL_MODE="false"

if [[ "${1:-}" == "--full" ]]; then
  FULL_MODE="true"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
python -m pip install -U pip setuptools wheel

if [[ "$FULL_MODE" == "true" ]]; then
  pip install "scrapling[all]"
  # Browser dependencies installer from Scrapling CLI
  scrapling install || true
else
  pip install scrapling
fi

echo "✅ Scrapling setup completed."
echo "Venv: $VENV_DIR"
if [[ "$FULL_MODE" == "true" ]]; then
  echo "Mode: full"
else
  echo "Mode: minimal"
fi

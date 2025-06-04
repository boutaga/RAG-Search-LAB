#!/usr/bin/env bash
# Run metrics exporter for RAG-Search-LAB

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."

source "$SCRIPT_DIR/config.env"

if [[ -n "$METRICS_EXPORTER_VENV_PATH" && -d "$METRICS_EXPORTER_VENV_PATH" ]]; then
    source "$METRICS_EXPORTER_VENV_PATH/bin/activate"
fi

exec python "$REPO_ROOT/monitoring/metrics_exporter.py"

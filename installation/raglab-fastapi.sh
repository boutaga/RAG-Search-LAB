#!/usr/bin/env bash
# Run FastAPI backend for RAG-Search-LAB

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."

# Load config
source "$SCRIPT_DIR/config.env"

# Activate venv
source "$FASTAPI_VENV_PATH/bin/activate"

# Export environment variables for DB connection, etc.
export PG_HOST
export PG_PORT
export PG_DOCUMENTS_DB
export PG_SD_DB
export PG_AI_AGENT_DB
export PG_APP_USER
export PG_APP_PASSWORD

# Run FastAPI app
cd "$REPO_ROOT/RAG_Scripts"
exec uvicorn main:app --host "$FASTAPI_HOST" --port "$FASTAPI_PORT"

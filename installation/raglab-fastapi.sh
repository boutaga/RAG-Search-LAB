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

# Build SQLAlchemy URLs for the FastAPI app
export DATABASE_URL="postgresql+asyncpg://${PG_APP_USER}:${PG_APP_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_AI_AGENT_DB}"
export DOCUMENT_DB_URL="postgresql+asyncpg://${PG_APP_USER}:${PG_APP_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DOCUMENTS_DB}"
export SD_DB_URL="postgresql+asyncpg://${PG_APP_USER}:${PG_APP_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_SD_DB}"
export MCP_SERVERS="http://${MCP_HOST}:${MCP_PORT}"

# Run FastAPI app
cd "$REPO_ROOT/RAG_Scripts"
exec uvicorn main:app --host "$FASTAPI_HOST" --port "$FASTAPI_PORT"

#!/usr/bin/env bash
# Run MCP server for RAG-Search-LAB

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."

# Load config
source "$SCRIPT_DIR/config.env"

# Activate venv
source "$MCP_VENV_PATH/bin/activate"

# Export environment variables for DB connection, etc.
export PG_HOST
export PG_PORT
export PG_DOCUMENTS_DB
export PG_SD_DB
export PG_AI_AGENT_DB
export PG_APP_USER
export PG_APP_PASSWORD

# Build connection strings for the MCP server
export AI_AGENT_DB_URL="dbname=${PG_AI_AGENT_DB} user=${PG_APP_USER} password=${PG_APP_PASSWORD} host=${PG_HOST} port=${PG_PORT}"
export PGVECTOR_CONN_STR="postgresql+psycopg2://${PG_APP_USER}:${PG_APP_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_AI_AGENT_DB}"

# Run MCP server (FastAPI app)
cd "$REPO_ROOT/custom-agent-tools-py"
exec uvicorn main:app --host "$MCP_HOST" --port "$MCP_PORT"

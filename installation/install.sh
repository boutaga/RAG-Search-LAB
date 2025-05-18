#!/usr/bin/env bash

# =========================
# RAG-Search-LAB Automated Installer
# =========================

set -e

# --- Helper: Print error and exit ---
function die() {
  echo "ERROR: $1" >&2
  exit 1
}

# --- Check for root privileges ---
if [[ $EUID -ne 0 ]]; then
  die "This script must be run as root (use sudo)."
fi

# --- Check config file ---
CONFIG_FILE="$(dirname "$0")/config.env"
if [[ ! -f "$CONFIG_FILE" ]]; then
  die "Config file not found: $CONFIG_FILE"
fi

# --- Source config ---
set -a
source "$CONFIG_FILE"
set +a

echo "Loaded configuration from $CONFIG_FILE"

# --- Detect OS Distribution ---
function detect_os() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
  else
    die "Cannot detect OS distribution (missing /etc/os-release)"
  fi
}

detect_os
echo "Detected OS: $DISTRO $VERSION"

# --- Install required packages based on distro ---
function install_packages() {
  echo "Installing required packages for $DISTRO..."

  case "$DISTRO" in
    debian|ubuntu)
      apt-get update
      apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib sudo
      ;;
    rhel|rocky|almalinux|centos)
      dnf install -y python3 python3-venv python3-pip postgresql-server postgresql-contrib sudo
      ;;
    suse|opensuse-leap|opensuse-tumbleweed)
      zypper refresh
      zypper install -y python3 python3-venv python3-pip postgresql-server sudo
      ;;
    *)
      die "Unsupported distribution: $DISTRO"
      ;;
  esac
}

install_packages

# --- Create install base directory ---
echo "Creating base directory: $INSTALL_BASE"
mkdir -p "$INSTALL_BASE"
chown "$INSTALL_USER":"$INSTALL_USER" "$INSTALL_BASE"

# --- PostgreSQL setup and database initialization ---
echo "=== PostgreSQL setup and database initialization ==="

# Start and enable PostgreSQL service
case "$DISTRO" in
  debian|ubuntu)
    systemctl enable postgresql
    systemctl start postgresql
    ;;
  rhel|rocky|almalinux|centos)
    systemctl enable postgresql
    systemctl start postgresql
    ;;
  suse|opensuse-leap|opensuse-tumbleweed)
    systemctl enable postgresql
    systemctl start postgresql
    ;;
esac

# Wait for PostgreSQL to be ready
sleep 3

# Function to run SQL as postgres superuser
function psql_super() {
  # Always include -p "$PG_PORT" and -h "$PG_HOST" if set
  local PGPORT_OPT=""
  local PGHOST_OPT=""
  if [[ -n "$PG_PORT" ]]; then
    PGPORT_OPT="-p $PG_PORT"
  fi
  if [[ -n "$PG_HOST" ]]; then
    PGHOST_OPT="-h $PG_HOST"
  fi
  if [[ -n "$PSQL_PATH" ]]; then
    sudo -u postgres "$PSQL_PATH" $PGHOST_OPT $PGPORT_OPT -v ON_ERROR_STOP=1 "$@"
  else
    sudo -u postgres psql $PGHOST_OPT $PGPORT_OPT -v ON_ERROR_STOP=1 "$@"
  fi
}

# Create application user if not exists
psql_super -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$PG_APP_USER') THEN CREATE ROLE $PG_APP_USER LOGIN PASSWORD '$PG_APP_PASSWORD'; END IF; END \$\$;"

# Create databases if not exist and grant privileges
for DB in "$PG_DOCUMENTS_DB" "$PG_SD_DB" "$PG_AI_AGENT_DB"; do
  # Check if database exists
  if ! psql_super -lqt | cut -d \| -f 1 | grep -qw "$DB"; then
    echo "Creating database $DB..."
    psql_super -c "CREATE DATABASE $DB OWNER $PG_APP_USER;"
  else
    echo "Database $DB already exists."
  fi
  psql_super -d "$DB" -c "GRANT ALL PRIVILEGES ON DATABASE $DB TO $PG_APP_USER;"
done

# Run schema and data SQL files for each database
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

declare -A DB_SQLS=(
  ["$PG_DOCUMENTS_DB"]="$REPO_ROOT/database_documents/database_structure.sql $REPO_ROOT/database_documents/populate_document_database.sql"
  ["$PG_SD_DB"]="$REPO_ROOT/database_SD/database_structure.sql $REPO_ROOT/database_SD/populate_sd_database.sql"
  ["$PG_AI_AGENT_DB"]="$REPO_ROOT/database_AI_agent/database_structure.sql"
)

for DB in "${!DB_SQLS[@]}"; do
  for SQLFILE in ${DB_SQLS[$DB]}; do
    if [[ -f "$SQLFILE" ]]; then
      echo "Applying $SQLFILE to $DB..."
      psql_super -d "$DB" -f "$SQLFILE"
    else
      echo "WARNING: SQL file not found: $SQLFILE"
    fi
  done
done

echo "PostgreSQL setup and database initialization complete."

# --- Python virtual environments and dependencies ---
echo "=== Python virtual environments and dependencies ==="

# Helper to create venv and install requirements
function setup_python_venv() {
  local SRC_DIR="$1"
  local VENV_PATH="$2"
  echo "Setting up Python venv at $VENV_PATH for $SRC_DIR"
  python3 -m venv "$VENV_PATH"
  chown -R "$INSTALL_USER":"$INSTALL_USER" "$VENV_PATH"
  # shellcheck disable=SC1090
  source "$VENV_PATH/bin/activate"
  if [[ -f "$SRC_DIR/requirements.txt" ]]; then
    pip install --upgrade pip
    pip install -r "$SRC_DIR/requirements.txt"
  else
    echo "WARNING: requirements.txt not found in $SRC_DIR"
  fi
  deactivate
}

# FastAPI backend venv
FASTAPI_SRC="$REPO_ROOT/RAG_Scripts"
setup_python_venv "$FASTAPI_SRC" "$FASTAPI_VENV_PATH"

# MCP server venv
MCP_SRC="$REPO_ROOT/custom-agent-tools-py"
setup_python_venv "$MCP_SRC" "$MCP_VENV_PATH"

echo "Python virtual environments and dependencies setup complete."

# --- Placeholder: FastAPI backend setup ---
echo "=== [TODO] FastAPI backend setup ==="

# --- Placeholder: MCP server setup ---
echo "=== [TODO] MCP server setup ==="

# --- Systemd service creation ---
echo "=== Systemd service creation ==="

# Copy systemd unit files
cp "$REPO_ROOT/installation/raglab-fastapi.service" /etc/systemd/system/"$FASTAPI_SERVICE_NAME".service
cp "$REPO_ROOT/installation/raglab-mcp.service" /etc/systemd/system/"$MCP_SERVICE_NAME".service

# Replace variables in service files
sed -i "s|\${INSTALL_USER}|$INSTALL_USER|g" /etc/systemd/system/"$FASTAPI_SERVICE_NAME".service
sed -i "s|\${INSTALL_BASE}|$INSTALL_BASE|g" /etc/systemd/system/"$FASTAPI_SERVICE_NAME".service
sed -i "s|\${INSTALL_USER}|$INSTALL_USER|g" /etc/systemd/system/"$MCP_SERVICE_NAME".service
sed -i "s|\${INSTALL_BASE}|$INSTALL_BASE|g" /etc/systemd/system/"$MCP_SERVICE_NAME".service

# Reload systemd, enable and start services
systemctl daemon-reload
systemctl enable "$FASTAPI_SERVICE_NAME"
systemctl start "$FASTAPI_SERVICE_NAME"
systemctl enable "$MCP_SERVICE_NAME"
systemctl start "$MCP_SERVICE_NAME"

echo "Systemd services created and started:"
echo "  - $FASTAPI_SERVICE_NAME.service"
echo "  - $MCP_SERVICE_NAME.service"

# --- Frontend UI setup ---
echo "=== Frontend UI setup ==="

# Check for Node.js and npm
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm not found. Installing Node.js..."
  case "$DISTRO" in
    debian|ubuntu)
      apt-get install -y nodejs npm
      ;;
    rhel|rocky|almalinux|centos)
      dnf install -y nodejs npm
      ;;
    suse|opensuse-leap|opensuse-tumbleweed)
      zypper install -y nodejs npm
      ;;
    *)
      echo "WARNING: Please install Node.js and npm manually for your distribution."
      ;;
  esac
fi

FRONTEND_DIR="$REPO_ROOT/frontend"
if [[ -d "$FRONTEND_DIR" ]]; then
  echo "Installing frontend dependencies in $FRONTEND_DIR"
  cd "$FRONTEND_DIR"
  sudo -u "$INSTALL_USER" npm install
  # Set VITE_API_URL if not present
  if [[ ! -f .env ]]; then
    echo "VITE_API_URL=http://localhost:8000" > .env
    chown "$INSTALL_USER":"$INSTALL_USER" .env
  fi
  echo "Building frontend for production..."
  sudo -u "$INSTALL_USER" npm run build
  echo "Frontend build complete. The app will be served by FastAPI at the root path."
else
  echo "WARNING: Frontend directory not found at $FRONTEND_DIR"
fi

echo "Installation complete. All components are set up."

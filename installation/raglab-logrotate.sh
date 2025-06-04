#!/usr/bin/env bash
# Rotate RAG-Search-LAB logs
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env"
TMP_CONF="/tmp/raglab-logrotate.conf"
cat > "$TMP_CONF" <<CFG
$LOG_PATH/*.log {
    rotate $LOG_RETENTION_DAYS
    daily
    missingok
    notifempty
    compress
    delaycompress
}
CFG
logrotate -s "$LOG_PATH/logrotate.status" "$TMP_CONF"
rm -f "$TMP_CONF"

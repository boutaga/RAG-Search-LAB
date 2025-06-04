# RAG-Search-LAB Installation Guide

This guide explains how to install and configure all components of RAG-Search-LAB (PostgreSQL, FastAPI backend, MCP server) on a single Linux server.

---

## Prerequisites

- Linux server: Debian 12, Ubuntu 24.04, RHEL 9, or Suse (root access required)
- Git (to clone the repository)
- Internet access (for package installation)

---

## 1. Download the Repository

Choose one of the following methods to download the RAG-Search-LAB files to your Linux server:

**Using Git (recommended):**
```sh
git clone https://github.com/boutaga/RAG-Search-LAB.git

cd RAG-Search-LAB
```

**Using wget (if git is not available):**
```sh
wget https://github.com/boutaga/RAG-Search-LAB/archive/refs/heads/main.zip
unzip main.zip
cd RAG-Search-LAB-main
```

---

## 2. Configuration

Edit `installation/config.env` to set all required parameters:

- PostgreSQL superuser and app user credentials
- Database names
- Ports and paths for FastAPI and MCP server
- Installation user and base directory

**Example:**
```sh
nano installation/config.env
```

---

## 3. Run the Installer

From the repository root:

```sh
sudo bash installation/install.sh
```

The script will:
- Detect your Linux distribution
- Install required packages (PostgreSQL, Python, etc.)
- Set up databases and users
- Initialize all schemas and data
- Create Python virtual environments and install dependencies
- Set up and start systemd services for FastAPI and MCP server

---

## 4. Service Management

To check status:
```sh
systemctl status raglab-fastapi
systemctl status raglab-mcp
```

To restart a service:
```sh
systemctl restart raglab-fastapi
systemctl restart raglab-mcp
```

To view logs:
```sh
journalctl -u raglab-fastapi -f
journalctl -u raglab-mcp -f
```

---

## 5. Monitoring and Logs

- A Prometheus metrics exporter is installed as the `raglab-metrics` service.
  Metrics are served on `http://<server>:<METRICS_EXPORTER_PORT>/`.
- Log files under `${LOG_PATH}` are rotated daily by the `raglab-logrotate`
  service and timer. The number of rotations kept is controlled by
  `LOG_RETENTION_DAYS` in `config.env`.

---
## 6. Customization

- All ports, paths, and credentials are set in `installation/config.env`.
- To change service names, update the config and re-run the installer.

---

## 7. Troubleshooting

- Ensure you run the installer as root (with `sudo`).
- Check the output for any errors during installation.
- Verify PostgreSQL is running and accessible.
- Check service logs for FastAPI and MCP server for runtime issues.

---

## 8. Uninstallation

To remove services:
```sh
systemctl stop raglab-fastapi raglab-mcp
systemctl disable raglab-fastapi raglab-mcp
rm /etc/systemd/system/raglab-fastapi.service
rm /etc/systemd/system/raglab-mcp.service
systemctl daemon-reload
```
Remove the install base directory if desired:
```sh
rm -rf /opt/raglab
```

---

## 9. Frontend UI Setup

A full-featured React + Tailwind frontend is now included in `frontend/`. It provides a split-pane chat UI, streaming answers, and citation viewing.

**To set up the frontend:**
```sh
cd frontend
npm install
# Set the FastAPI backend URL in .env:
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```
- The UI expects the FastAPI backend to be running and accessible at the URL set in `VITE_API_URL`.
- For production, use `npm run build` and serve the static files.

**Key Endpoints Used by the Frontend:**
- `POST /chat/stream` — Streams chat responses (Server-Sent Events)
- `GET /chat/citations/{msg_id}` — Returns citations for a message

---

## 10. Next Steps

- The backend API will be available at `http://<server>:<FASTAPI_PORT>/`
- The MCP server will be available at `http://<server>:<MCP_PORT>/`
- The frontend UI will be available at `http://<server>:<FRONTEND_PORT>/` (default: 5173 for Vite dev server)
- See the main `README.md` for more details on endpoints and usage.

---

## 11. Support

For more details, see the main `README.md` or open an issue in the repository.

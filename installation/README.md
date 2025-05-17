# RAG-Search-LAB Installation Guide

This guide explains how to install and configure all components of RAG-Search-LAB (PostgreSQL, FastAPI backend, MCP server) on a single Linux server.

---

## Prerequisites

- Linux server: Debian 12, Ubuntu 24.04, RHEL 9, or Suse (root access required)
- Git (to clone the repository)
- Internet access (for package installation)

---

## 1. Configuration

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

## 2. Run the Installer

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

## 3. Service Management

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

## 4. Customization

- All ports, paths, and credentials are set in `installation/config.env`.
- To change service names, update the config and re-run the installer.

---

## 5. Troubleshooting

- Ensure you run the installer as root (with `sudo`).
- Check the output for any errors during installation.
- Verify PostgreSQL is running and accessible.
- Check service logs for FastAPI and MCP server for runtime issues.

---

## 6. Uninstallation

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

## 7. Next Steps

- The backend API will be available at `http://<server>:<FASTAPI_PORT>/`
- The MCP server will be available at `http://<server>:<MCP_PORT>/`
- (Frontend UI integration is planned for future releases.)

---

## 8. Support

For more details, see the main `README.md` or open an issue in the repository.

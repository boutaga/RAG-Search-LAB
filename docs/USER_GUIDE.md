# RAG-Search-LAB User Guide

This guide provides step-by-step instructions for setting up, running, and using the RAG-Search-LAB platform, including the FastAPI backend, MCP server, and database components.

---

## 1. Prerequisites

- Python 3.9+ (for FastAPI and MCP server)
- Node.js (optional, for deprecated TypeScript MCP server)
- PostgreSQL 13+ (for all databases)
- (Optional) Docker for running PostgreSQL or other services

---

## 2. Database Setup

1. **Create the databases:**
   - Documents database
   - Service Desk database
   - RAG/AI Agent database

2. **Run the provided SQL scripts:**
   - `database_documents/database_structure.sql`
   - `database_SD/database_structure.sql`
   - `database_AI_agent/database_structure.sql`
   - Use the `insert_documents.sql` and `populate_document_database.sql` scripts to add sample data.

3. **Configure PostgreSQL connection strings in your environment or `.env` files.**

---

## 3. FastAPI Backend Setup (`RAG_Scripts`)

```bash
cd RAG_Scripts
pip install -r requirements.txt  # requirements.txt now included
uvicorn main:app --reload
```

- Edit `main.py` or your environment to set the correct database URLs.
- The backend will be available at `http://localhost:8000`.

---

## 4. MCP Server Setup (`custom-agent-tools-py`)

```bash
cd custom-agent-tools-py
python -m venv venv
venv/Scripts/activate  # On Windows
pip install -r requirements.txt  # requirements.txt now included
uvicorn main:app --reload
```

- Set environment variables for database and integrations (see `custom-agent-tools-py/README.md`).
- The MCP server will be available at `http://localhost:8000` (or another port if specified).

---

## 5. Frontend/UI (Planned)

- A React/Vue/Angular frontend can be built to interact with the FastAPI and MCP server endpoints.
- UI components: chat, ticket management, analytics dashboards, feedback forms, real-time updates.

---

## 6. API Usage Examples

### Create a Ticket (curl)
```bash
curl -X POST 'http://localhost:8000/ticket' -d 'id=123&title=Example Ticket'
```

### Search Knowledge (Python)
```python
import requests
response = requests.get('http://localhost:8000/search', params={'query': 'error'})
print(response.json())
```

### Submit Feedback (Postman)
POST http://localhost:8000/feedback
```json
{
  "log_id": "some-log-id",
  "rating": 5,
  "comments": "Great answer!"
}
```

### Get Filter Metadata
The frontend uses the `/metadata` endpoint to populate search filters.

```bash
curl http://localhost:8000/metadata
```
This returns JSON lists of available categories, ticket fields, and document types.

---

## 7. Authentication/Authorization

- JWT/OAuth2 authentication and role-based access are stubbed and can be enabled for both backend and MCP server.
- Example login endpoint: `/auth/login`

---

## 8. Environment Variables

- `AI_AGENT_DB_URL` - PostgreSQL connection string for the AI agent database
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM` - Email integration
- `SLACK_WEBHOOK_URL` - Slack alerting integration
- `TEAMS_WEBHOOK_URL` - Microsoft Teams incoming webhook
- `PAGERDUTY_ROUTING_KEY` - PagerDuty Events API routing key


## 9. Monitoring and Logs

- The installer sets up a Prometheus metrics exporter running as the
  `raglab-metrics` service. Metrics are available at
  `http://<server>:<METRICS_EXPORTER_PORT>/`.
- Log files are stored in `${LOG_PATH}` and rotated daily by the
  `raglab-logrotate` service and timer. The number of archives kept is
  controlled by `LOG_RETENTION_DAYS` in `config.env`.

---
## 10. Troubleshooting
- Ensure all databases are running and accessible.
- Check environment variables for correct configuration.
- Use the `/usage/example` endpoint for more API usage examples.
- For issues with LLMs or Langchain, check API keys and model access.

---

## 11. Further Reading

- See `custom-agent-tools-py/README.md` for MCP server details and advanced features.
- See the main `README.md` for architecture, release notes, and project overview.

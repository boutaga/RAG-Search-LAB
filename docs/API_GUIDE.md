# RAG-Search-LAB API Usage Guide

This guide provides an overview and usage examples for the main API endpoints exposed by the FastAPI backend (`RAG_Scripts`) and the MCP server (`custom-agent-tools-py`).

---

## 1. FastAPI Backend (`RAG_Scripts`)

### Ticket Management

- **Create/Update Ticket**
  ```
  POST /ticket
  Body: id, title, status, assignee, note (optional)
  ```
  Example (curl):
  ```bash
  curl -X POST 'http://localhost:8000/ticket' -d 'id=123&title=Example Ticket'
  ```

- **List Tickets**
  ```
  GET /ticket
  ```

### Solutions

- **Create Solution Proposal**
  ```
  POST /solutions
  Body: problem_id, title, description, proposed_by_user_id (optional)
  ```

- **Validate/Update Solution**
  ```
  PUT /solutions/{solution_id}
  Body: title, description, is_validated, validator_user_id (all optional)
  ```

### Chat Logging

- **Add Chat Log**
  ```
  POST /chatlog
  Body: conversation_id, role, content
  ```

- **List Chat Logs**
  ```
  GET /chatlog
  ```

### Feedback

- **Submit Feedback**
  ```
  POST /feedback
  Body: log_id, rating, comments (optional)
  ```

- **List Feedback**
  ```
  GET /feedback
  ```

### Problem Linking

- **Link Problem**
  ```
  POST /problem-link
  Body: ticket_id, problem_id, link_type (optional)
  ```

- **List Problem Links**
  ```
  GET /problem-link
  ```

### Hybrid RAG Search

- **Search**
  ```
  GET /search?query=your_query&limit=5
  ```

### LLM Orchestration

- **Summarize Ticket**
  ```
  POST /llm/summarize_ticket
  Body: ticket_id
  ```

- **Triage Ticket**
  ```
  POST /llm/triage_ticket
  Body: ticket_id, provider (optional)
  ```

- **Root Cause Analysis**
  ```
  POST /llm/root_cause
  Body: ticket_id, provider (optional)
  ```

- **Recommend Solution**
  ```
  POST /llm/recommend_solution
  Body: ticket_id, provider (optional)
  ```

- **Summarize Conversation**
  ```
  POST /llm/summarize_conversation
  Body: conversation_id, provider (optional)
  ```

- **Extract Entities**
  ```
  POST /llm/extract_entities
  Body: text, provider (optional)
  ```

- **Follow-up Actions**
  ```
  POST /llm/followup_actions
  Body: ticket_id, conversation_id, provider (optional)
  ```

- **Feedback Loop**
  ```
  POST /feedback-loop
  Body: query, llm_output, rating, comments (optional)
  ```

### Email/Alerting

- **Send Email**
  ```
  POST /notify/email
  Body: to, subject, body
  ```

- **Send Alert**
  ```
  POST /notify/alert
  Body: message, severity (optional)
  ```

### Analytics

- **Ticket Volume Over Time**
  ```
  GET /analytics/ticket-volume?start=2024-01-01&end=2024-01-31
  ```
  Response:
  ```json
  {
    "ticket_volume": [
      {"day": "2024-01-01", "count": 5},
      {"day": "2024-01-02", "count": 8}
    ]
  }
  ```

- **Average Resolution Time**
  ```
  GET /analytics/resolution-times
  ```
  Response:
  ```json
  {"average_resolution_hours": 4.2}
  ```

- **SLA Compliance**
  ```
  GET /analytics/sla-compliance?hours=48
  ```
  Response:
  ```json
  {"sla_compliance_percent": 92.5}
  ```

- **Agent Leaderboard**
  ```
  GET /analytics/agent-leaderboard?limit=5
  ```
  Response:
  ```json
  {
    "leaderboard": [
      {"metric_name": "agent_alice", "metric_value": 120},
      {"metric_name": "agent_bob", "metric_value": 110}
    ]
  }
  ```

- **Document Usage**
  ```
  GET /analytics/document-usage
  ```
  Response:
  ```json
  {
    "document_usage": [
      {"document_id": 1, "title": "Onboarding Guide", "count": 20}
    ]
  }
  ```

- **Export Analytics**
  ```
  GET /analytics/export?type=ticket_volume&format=csv
  ```

### Authentication/Authorization

- **Login**
  ```
  POST /auth/login
  Body: username, password
  ```

- **Get Current User**
  ```
  GET /auth/me
  Header: token (stub)
  ```

---

## 2. MCP Server (`custom-agent-tools-py`)

- All endpoints above are available via the MCP server as well, with the same or similar routes.
- The MCP server can be called via HTTP or via the Model Context Protocol for tool/resource orchestration.

---

## 3. Usage Examples

### Curl

```bash
curl -X POST 'http://localhost:8000/ticket' -d 'id=123&title=Example Ticket'
curl 'http://localhost:8000/search?query=error'
curl -X POST 'http://localhost:8000/llm/triage_ticket' -d 'ticket_id=123'
curl -X POST 'http://localhost:8000/llm/root_cause' -d 'ticket_id=123'
curl -X POST 'http://localhost:8000/llm/summarize_ticket' -d 'ticket_id=123'
curl -X POST 'http://localhost:8000/llm/followup_actions' -d 'ticket_id=123'
```

### Python

```python
import requests
response = requests.get('http://localhost:8000/search', params={'query': 'error'})
print(response.json())
```

### Postman

- Import the OpenAPI schema from the FastAPI backend to generate all endpoints.
- Example: POST to `/feedback` with JSON body.

---

## 4. Further Reading

- See `USER_GUIDE.md` for setup and onboarding.
- See `ARCHITECTURE.md` for system architecture and data flow.
- See the main `README.md` for release notes and project overview.

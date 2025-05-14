# custom-agent-tools-py (v0.9)

Python/Langchain MCP Server for SD Agent

**This is the actively maintained MCP server for the Service Desk AI Agent. The previous TypeScript version (`custom-agent-tools`) is now deprecated.**

This project is a Python-based MCP server for the Service Desk AI Agent, providing modular tools and resources for chat logging, ticket management, search, feedback, problem linking, advanced LLM orchestration, email, alerting, analytics, advanced LLM chains, and now hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops.

## Features

- Chat interaction logging (resource + tool, PostgreSQL-backed)
- Ticket management (resource + tool, PostgreSQL-backed)
- Search tool for chat logs and tickets (hybrid: dense/vector + sparse/keyword, Langchain + SQL)
- Feedback submission tool and resource (PostgreSQL-backed)
- Problem linking tool and resource (PostgreSQL-backed)
- Advanced LLM orchestration endpoints (summarization, classification, etc.)
- Email and alerting tool endpoints (real SMTP and Slack integration)
- Analytics endpoints (e.g., ticket counts, volume over time, agent leaderboard, document usage)
- Export endpoints for analytics (CSV, Excel, PDF)
- UI integration endpoints (for frontend)
- Multi-step LLM chains for ticket triage, root cause analysis, solution recommendation
- Conversation summarization, entity extraction, follow-up actions
- **Hybrid reranking, context window optimization, dynamic prompt engineering, feedback loops**
- Authentication/authorization endpoints (JWT/OAuth2, role-based access)
- Designed for easy extension with Langchain, FastAPI, and PostgreSQL

## Setup

```bash
cd custom-agent-tools-py
python -m venv venv
venv/Scripts/activate  # On Windows
pip install -r requirements.txt  # or see below for manual install
```

### Manual install

```bash
pip install langchain langchain-community fastapi uvicorn pydantic psycopg2-binary
```

## Running the MCP server

```bash
uvicorn main:app --reload
```

## Email/Alerting Configuration

Set the following environment variables for email and Slack integration:

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`
- `SLACK_WEBHOOK_URL`

## Release Notes

### v0.9 (Current)

- Hybrid reranking: combine dense and sparse retrieval results with configurable weights or LLM-based scoring
- Context window optimization: select most relevant chunks for LLM context, respect token limits
- Dynamic prompt engineering: adapt prompts based on context, user, and query
- Feedback loops: endpoints and logic for collecting and using user feedback to improve retrieval and LLM output
- All previous features (analytics, UI integration, LLM chains, hybrid RAG, email/alerting, PostgreSQL-backed storage)

### v0.8

- Expanded analytics and reporting endpoints:
  - Ticket volume over time, average resolution time, open/closed ratios, SLA compliance
  - Agent leaderboard, satisfaction scores, escalation rates
  - Document usage, SOP reference tracking, knowledge gaps
  - Export analytics as CSV, Excel, or PDF
  - BI tool integration (Power BI, Tableau) via API (planned)
- UI integration and usage examples:
  - React/Vue/Angular frontend integration
  - UI components for chat, ticket management, analytics dashboards, feedback forms
  - Real-time updates for alerts and ticket changes (WebSocket/polling)
  - Example API calls (curl, Python, Postman) and sample workflows
  - Authentication/authorization (JWT/OAuth2, role-based access)
- All previous features (LLM chains, hybrid RAG, email/alerting, analytics, PostgreSQL-backed storage)

### v0.7

- Multi-step LLM chains for ticket triage, root cause analysis, solution recommendation
- Conversation summarization, entity extraction, follow-up actions
- LLM provider selection (OpenAI, Azure, HuggingFace)
- Hybrid reranking, context window optimization, dynamic prompt engineering, feedback loops (stubs)
- All previous features (email, alerting, analytics, UI integration, PostgreSQL-backed storage, hybrid RAG)

### v0.6

- Real email integration via SMTP (configurable)
- Real alerting integration via Slack webhook (configurable)
- Analytics endpoints (e.g., ticket counts)
- UI integration endpoints (for frontend)
- All core tools use PostgreSQL-backed storage
- Hybrid RAG search with Langchain and SQL
- Advanced LLM orchestration endpoints and Langchain chains (summarization, classification, etc.)
- Documentation and setup instructions

### v0.4-v0.5

- Advanced LLM orchestration endpoints and Langchain chains (summarization, classification, etc.)
- Email and alerting tool endpoints (stubs, ready for integration)
- Analytics endpoints (e.g., ticket counts)
- UI integration endpoints (for frontend)

### v0.3

- Hybrid RAG search using Langchain (OpenAI embeddings, PGVector, RetrievalQA)
- All core tools (chat logging, ticket management, feedback, problem linking) now use PostgreSQL-backed storage in the AI agent database
- FastAPI endpoints for all tools/resources
- Search endpoint combines dense (vector) and sparse (keyword) retrieval

### v0.2

- Initial migration from TypeScript MCP agent to Python/Langchain
- In-memory storage for rapid prototyping

## Upcoming Tasks

- Integrate additional alerting/email providers (e.g., Microsoft Teams, PagerDuty)
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## Deprecated

> **The TypeScript MCP server (`custom-agent-tools`) is now deprecated. Please use this Python/Langchain version for all new development.**

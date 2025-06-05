# RAG-Search-LAB

This repository has educational purpose on advanced RAG Search techniques based on PostgreSQL-pgvector-pgvectorscale-pgai...

---

## Solution Features

RAG-Search-LAB demonstrates how to combine a traditional service desk workflow
with modern Retrieval Augmented Generation (RAG).  Key capabilities include:

- **Hybrid retrieval** using pgvector and SQL for dense and sparse search.
- **Ticket and document management** stored in PostgreSQL databases.
- **FastAPI backend** orchestrating RAG queries and business logic.
- **MCP server** exposing modular tools for chat logging, ticket updates,
  analytics, and advanced LLM chains.
- **React/Tailwind frontend** with streaming chat and citation viewing.
- **Email/Slack alerting**, analytics endpoints and authentication hooks to
  support production use cases.

---

## Architecture Overview

```
+-------------------+      +-------------------+      +-------------------+
| Documents DB      |      | Service Desk DB   |      | RAG/AI Agent DB   |
+-------------------+      +-------------------+      +-------------------+
         |                          |                          |
         +--------------------------+--------------------------+
                                    |
                             +----------------+
                             |   FastAPI      |
                             |  (RAG_Scripts) |
                             +----------------+
                                    |
                             +----------------+
                             |   MCP Server   |
                             | (custom tools) |
                             +----------------+
                                    |
                             +----------------+
                             |   Frontend UI  |
                             +----------------+
```

- **Documents DB:** SOPs, document metadata, file links
- **Service Desk DB:** Tickets, users, organizations, configuration items
- **RAG/AI Agent DB:** Embeddings, chat logs, retrieval history, feedback, agent context, links to tickets/problems
- **FastAPI Backend:** RAG search, ticket management, document retrieval, LLM orchestration, business logic
- **MCP Server:** Modular tools for analytics, LLM chains, feedback, notifications, UI integration
- **Frontend UI:** React + Tailwind app for chat, streaming answers, citation viewing (see `frontend/`)

---

---

## Getting Started

**Automated installation is now available!**

See [installation/README.md](installation/README.md) for step-by-step instructions to install and configure all components (PostgreSQL, FastAPI backend, MCP server) on a single Linux server.

---

## Manual Setup (Legacy)

If you prefer to set up components manually, see the instructions below.

This project consists of several main components:

### 1. PostgreSQL Databases

- **Documents Database:** Stores SOPs and document metadata.
- **Service Desk Database:** Stores tickets, users, organizations, and related service desk data.
- **RAG/AI Agent Database:** Stores embeddings, chat logs, retrieval history, feedback, and agent context.

**Manual Setup:**  
- Use the provided SQL files in `database_documents/`, `database_SD/`, and `database_AI_agent/` to create and populate the databases.
- Ensure PostgreSQL is running and accessible.

### 2. FastAPI Backend (`RAG_Scripts/main.py`)

- Handles RAG search, ticket management, document retrieval, and agent workflows.
- Connects to all three PostgreSQL databases.
- Implements hybrid RAG, LLM orchestration, and business logic.

**Manual Setup:**
```bash
cd RAG_Scripts
pip install -r requirements.txt  # requirements.txt now included
uvicorn main:app --reload
```
- Configure database connection strings as needed in the environment or code.

### 3. MCP Server (`custom-agent-tools-py`)

- Python/Langchain-based modular server for chat logging, ticket management, search, feedback, problem linking, LLM chains, analytics, notifications, and UI integration.
- All new development should use this Python version (TypeScript version is deprecated).

**Manual Setup:**
```bash
cd custom-agent-tools-py
python -m venv venv
venv/Scripts/activate  # On Windows
pip install -r requirements.txt  # requirements.txt now included
uvicorn main:app --reload
```
- Set environment variables for database and integrations (see README in the directory).

### 4. Frontend/UI

A full-featured React + Tailwind frontend is included in `frontend/`. It provides a split-pane chat UI, streams answers from the backend, and displays citations in a dialog.

**Setup:**
```bash
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

UI components: chat, ticket management, analytics dashboards, feedback forms, real-time updates.

### 5. Usage Examples

- Example API calls (curl, Python, Postman) are provided in the documentation and `/usage/example` endpoint of the MCP server.
- The generated OpenAPI schemas are available under `docs/` for easy client generation.
- Sample workflows: creating a ticket, searching knowledge, submitting feedback, analytics export.

### 6. Authentication/Authorization

- JWT/OAuth2 authentication and role-based access are stubbed and can be enabled for both backend and MCP server.

---

## MCP Server for SD Agent

A new MCP server project `custom-agent-tools` (TypeScript, v0.1, **deprecated**) and `custom-agent-tools-py` (Python/Langchain, v0.2+) have been added to this repository to support the Service Desk AI Agent with modular tools and resources.

### Features added in MCP server:

- Chat interaction logging as resources and tool to add chat logs
- Ticket management as resources and tool to update tickets
- Search tool to query chat logs and tickets by keyword
- Feedback submission tool and resources
- Problem linking tool and resources
- (v0.3+) Hybrid RAG search with Langchain and PostgreSQL-backed storage
- (v0.4+) Advanced LLM orchestration, email/alerting/analytics tools, and UI integration endpoints
- (v0.6+) Real email/alerting integration, analytics, and UI endpoints
- (v0.7) Multi-step LLM chains for ticket triage, root cause analysis, solution recommendation, conversation summarization, entity extraction, follow-up actions, hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops
- (v0.8) Expanded analytics and reporting endpoints, UI integration, usage examples, authentication/authorization
- **(v0.9) Hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops (fully implemented in code)**

**Note:** The TypeScript MCP server (`custom-agent-tools`) is now deprecated. Please use the Python/Langchain version for all new development.

The MCP server projects are located in the `custom-agent-tools` (TypeScript) and `custom-agent-tools-py` (Python) directories and can be built and run independently.

### How to build and run the Python MCP server:

```bash
cd custom-agent-tools-py
python -m venv venv
venv/Scripts/activate  # On Windows
pip install -r requirements.txt  # requirements.txt now included
uvicorn main:app --reload
```

After the server starts, its manifest can be retrieved from
`http://localhost:8000/.well-known/ai-plugin.json` for FastMCP discovery.

### Integration

Once running, the MCP server exposes tools and resources accessible via the Model Context Protocol, allowing the AI Agent to offload these responsibilities.

Please refer to the `custom-agent-tools/README.md` and `custom-agent-tools-py/README.md` for more details on the MCP server implementation and usage.

# Release Notes

## v0.9 (Hybrid Reranking, Context Window, Dynamic Prompting, Feedback Loops)

### Features
- Hybrid reranking: combine dense and sparse retrieval results with configurable weights or LLM-based scoring
- Context window optimization: select most relevant chunks for LLM context, respect token limits
- Dynamic prompt engineering: adapt prompts based on context, user, and query
- Feedback loops: endpoints and logic for collecting and using user feedback to improve retrieval and LLM output
- All previous features (analytics, UI integration, LLM chains, hybrid RAG, email/alerting, PostgreSQL-backed storage)

### Upcoming Tasks
- Integrate additional alerting/email providers (e.g., Microsoft Teams, PagerDuty)
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## v0.8 (Analytics, Reporting, UI Integration)

### Features
- Expanded analytics and reporting endpoints:
  - Ticket volume over time, average resolution time, open/closed ratios, SLA compliance
  - Agent leaderboard, satisfaction scores, escalation rates
  - Document usage, SOP reference tracking, knowledge gaps
  - Export analytics as CSV, Excel, or PDF
  - BI tool integration (Power BI, Tableau) via API (planned)
- UI integration and usage examples:
  - React frontend integration (see `frontend/`)
  - UI components for chat, ticket management, analytics dashboards, feedback forms
  - Real-time updates for alerts and ticket changes (WebSocket/polling)
  - Example API calls (curl, Python, Postman) and sample workflows
  - Authentication/authorization (JWT/OAuth2, role-based access)
- All previous features (LLM chains, hybrid RAG, email/alerting, analytics, PostgreSQL-backed storage)

### Upcoming Tasks
- Integrate additional alerting/email providers (e.g., Microsoft Teams, PagerDuty)
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## v0.7 (Advanced LLM Chains, RAG Enhancements)

### Features
- Multi-step LLM chains for ticket triage, root cause analysis, solution recommendation
- Conversation summarization, entity extraction, follow-up actions
- LLM provider selection (OpenAI, Azure, HuggingFace)
- Hybrid reranking, context window optimization, dynamic prompt engineering, feedback loops (stubs)
- All previous features (email, alerting, analytics, UI integration, PostgreSQL-backed storage, hybrid RAG)

### Upcoming Tasks
- Integrate additional alerting/email providers (e.g., Microsoft Teams, PagerDuty)
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## v0.6 (Real Email/Alerting, Analytics, UI Integration)

### Features
- Real email integration via SMTP (configurable via environment variables)
- Real alerting integration via Slack webhook (configurable)
- Analytics endpoints (e.g., ticket counts)
- UI integration endpoints (for frontend)
- All core tools use PostgreSQL-backed storage
- Hybrid RAG search with Langchain and SQL
- Advanced LLM orchestration endpoints and Langchain chains (summarization, classification, etc.)
- Documentation and setup instructions

### Upcoming Tasks
- Integrate additional alerting/email providers (e.g., Microsoft Teams, PagerDuty)
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## v0.4 - v0.5 (Advanced LLM, Email, Analytics, UI Integration)

### Features
- Advanced LLM orchestration endpoints and Langchain chains (summarization, classification, etc.)
- Email and alerting tool endpoints (stubs, ready for integration)
- Analytics endpoints (e.g., ticket counts)
- UI integration endpoints (for frontend)
- All core tools use PostgreSQL-backed storage
- Hybrid RAG search with Langchain and SQL
- Documentation and setup instructions

### Upcoming Tasks
- Integrate real email/alerting services
- Expand analytics and reporting endpoints
- Complete UI integration and provide usage examples
- Add more advanced LLM chains and workflows
- Further production hardening and monitoring

## v0.3 (Hybrid RAG & PostgreSQL-backed MCP Agent)

### Features
- Python-based MCP server (`custom-agent-tools-py`) now uses Langchain for hybrid RAG search (dense + sparse retrieval)
- All core tools (chat logging, ticket management, feedback, problem linking) now use PostgreSQL-backed storage in the AI agent database
- FastAPI endpoints for all tools/resources
- Search endpoint combines dense (vector) and sparse (keyword) retrieval using Langchain and SQL
- Ready for further LLM orchestration and production database integration

### Upcoming Tasks
- Add advanced LLM orchestration endpoints and Langchain chains
- Expand MCP tools for email, alerting, and analytics
- UI improvements and integration with frontend
- More robust error handling and monitoring
- Usage examples and API documentation

## v0.2 (Python/Langchain MCP Agent Migration)

### Features
- Python-based MCP server (`custom-agent-tools-py`) using FastAPI and Langchain
- Modular tools for chat logging, ticket management, search, feedback, and problem linking
- In-memory storage for rapid prototyping (to be replaced with database integration)
- Ready for integration with Langchain for advanced RAG and LLM workflows
- Documentation and setup instructions

### Upcoming Tasks
- Integrate Langchain for hybrid RAG search and LLM orchestration
- Add database-backed storage to MCP tools (currently in-memory)
- Implement event-driven embedding refresh for live data
- Expand MCP tools for email, alerting, and advanced analytics
- UI improvements and integration with frontend
- More robust error handling and monitoring
- Usage examples and API documentation

## v0.1 (Initial Release)

### Features
- Three PostgreSQL databases: Documents, Service Desk, and RAG/AI Agent
- FastAPI backend for RAG search and agent workflows
- MCP server (`custom-agent-tools`) for modular agent tools:
  - Chat logging
  - Ticket management
  - Search
  - Feedback submission
  - Problem linking
- Hybrid RAG search with dense and sparse retrieval
- Dynamic embedding refresh and weighting
- Realistic data ingestion and chunking

### Upcoming Tasks
- Integrate PostgreSQL agent (e.g., xataio/agent) for database assessments
- Add database-backed storage to MCP tools (currently in-memory)
- Implement event-driven embedding refresh for live data
- Expand MCP tools for email, alerting, and advanced analytics
- UI improvements and integration with frontend
- More robust error handling and monitoring
- Documentation and usage examples

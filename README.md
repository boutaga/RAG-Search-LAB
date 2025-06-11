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

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for version history.

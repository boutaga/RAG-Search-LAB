# RAG-Search-LAB Architecture

This document provides an overview of the architecture for the RAG-Search-LAB platform, including its main components, data flow, and integration points.

---

## High-Level Architecture

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

---

## Components

### 1. PostgreSQL Databases

- **Documents Database:**  
  Stores SOPs, document metadata, and links to files.
- **Service Desk Database:**  
  Stores tickets, users, organizations, configuration items, and relationships.
- **RAG/AI Agent Database:**  
  Stores embeddings, chat logs, retrieval history, feedback, agent context, and links to external tickets/problems.

### 2. FastAPI Backend (`RAG_Scripts`)

- Handles RAG search, ticket management, document retrieval, and agent workflows.
- Connects to all three PostgreSQL databases.
- Implements hybrid RAG, LLM orchestration, and business logic.
- Exposes REST API endpoints for the frontend and MCP server.

### 3. MCP Server (`custom-agent-tools-py`)

- Python/Langchain-based modular server for chat logging, ticket management, search, feedback, problem linking, LLM chains, analytics, notifications, and UI integration.
- Exposes advanced RAG, LLM, analytics, and notification tools as API endpoints.
- All new development should use this Python version (TypeScript version is deprecated).

### 4. Frontend/UI (Planned)

- React/Vue/Angular frontend to interact with FastAPI and MCP server endpoints.
- UI components: chat, ticket management, analytics dashboards, feedback forms, real-time updates.

---

## Data Flow

1. **User interacts with the Frontend UI** (chat, ticket, analytics, feedback).
2. **Frontend sends requests to FastAPI backend** (`RAG_Scripts`) and/or MCP server (`custom-agent-tools-py`).
3. **FastAPI backend**:
   - Handles RAG search, ticket management, and document retrieval.
   - Calls MCP server endpoints for advanced analytics, LLM chains, notifications, etc.
   - Reads/writes to PostgreSQL databases.
4. **MCP server**:
   - Provides modular tools for analytics, LLM chains, feedback, notifications, and more.
   - Reads/writes to the AI agent database and other sources as needed.
5. **Databases**:
   - Store all persistent data for documents, tickets, embeddings, logs, feedback, and analytics.

---

## Integration Points

- **Database:**  
  Both FastAPI backend and MCP server use the same PostgreSQL databases for shared state.
- **API:**  
  FastAPI and MCP server expose REST endpoints for the frontend and for each other.
- **MCP Protocol:**  
  The MCP server can be called via the Model Context Protocol for tool/resource orchestration.
- **Environment Variables:**  
  Used for database URLs, email/alerting configuration, and API keys.

---

## Extensibility

- New tools and endpoints can be added to the MCP server without disrupting the main backend.
- The architecture supports easy integration of new LLM providers, analytics, and UI features.
- The system is modular and designed for experimentation and educational use.

---

## Diagrams

For more detailed diagrams, see the main README or future updates to this document.

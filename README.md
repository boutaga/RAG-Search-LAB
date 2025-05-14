# RAG-Search-LAB

This repository has educational purpose on advanced RAG Search techniques based on PostgreSQL-pgvector-pgvectorscale-pgai...

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

**Note:** The TypeScript MCP server (`custom-agent-tools`) is now deprecated. Please use the Python/Langchain version for all new development.

The MCP server projects are located in the `custom-agent-tools` (TypeScript) and `custom-agent-tools-py` (Python) directories and can be built and run independently.

### How to build and run the Python MCP server:

```bash
cd custom-agent-tools-py
python -m venv venv
venv/Scripts/activate  # On Windows
pip install -r requirements.txt  # or see README for manual install
uvicorn main:app --reload
```

### Integration

Once running, the MCP server exposes tools and resources accessible via the Model Context Protocol, allowing the AI Agent to offload these responsibilities.

Please refer to the `custom-agent-tools/README.md` and `custom-agent-tools-py/README.md` for more details on the MCP server implementation and usage.

# Release Notes

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

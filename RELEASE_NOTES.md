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

# RAG-Search-LAB

This repository has educational purpose on advanced RAG Search techniques based on PostgreSQL-pgvector-pgvectorscale-pgai...

## MCP Server for SD Agent

A new MCP server project `custom-agent-tools` (TypeScript, v0.1) and `custom-agent-tools-py` (Python/Langchain, v0.2+) have been added to this repository to support the Service Desk AI Agent with modular tools and resources.

### Features added in MCP server:

- Chat interaction logging as resources and tool to add chat logs
- Ticket management as resources and tool to update tickets
- Search tool to query chat logs and tickets by keyword
- Feedback submission tool and resources
- Problem linking tool and resources
- (v0.3+) Hybrid RAG search with Langchain and PostgreSQL-backed storage
- (v0.4) Advanced LLM orchestration, email/alerting/analytics tools, and UI integration endpoints

This MCP server enables flexible and extensible integration of these functionalities with the AI Agent backend.

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


## The AI agent Service Desk example

In order to expose a real use cases and prove the point and added value of advanced RAG Search techniques, I created the following data sources
and the associated scenario of a Service Desk team that would take leverage of AI/LLM and RAG Search techniques.   
An AI Agent for the Service Desk team is holding the business logic and has deferent tools like email, document management,... This AI Agent also take leverage of
the RAG Search process that is at the center of experiment. The goal is to explain how different RAG search techniques can impact the response of the Agent.


Intent of the solution and added value expected : 

- Faster Time to Resolution for teams.
- Improvements on the quality of service. 
    - avoid having twice the same error by learning from past resolution
    - link alerts with solutions
    - link SOP with best practices
    - no hanging tickets with automated routing
    - KPI generation for mgmt


## Architecture

The architecture consists of three main PostgreSQL databases (Documents, Service Desk, and RAG/AI Agent), a FastAPI backend (RAG_Scripts), and an MCP server for modular agent tools. The AI agent interacts with all databases and the MCP server to provide advanced RAG search, ticket management, and feedback workflows.

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
```

# Documents database

This is a sample database that is storing information about document storage applications like Sharepoint or M-Files. 
The intent is to store SOP (Standard Operational Procedures) in various formats like PDF or Markdown to allow retrieval from the RAG Search workflow. 
The database holds metadata information of the documents and links to their real paths on the file system. 

## Description of the data model

- `users`: Authors and reviewers of documents
- `categories`: Document categories (e.g., expertise areas)
- `document`: Partitioned table for document metadata (title, description, version, status, author, reviewer, category, file path, format, etc.)
- Full-text search vector for efficient retrieval

# Service Desk database 

This database is a sample database of customer service requests made on technologies like PostgreSQL, SQL Server, Oracle, RHEL, Ubuntu, etc. 
It is designed to simulate a real-world service desk environment for testing RAG search and AI agent workflows.

## Description of the data model

- `ticket`: Partitioned table for service desk tickets (title, description, status, priority, type, organization, requester, assignee, SLA, etc.)
- Lookup tables for status, priority, type, SLA, organization, user, configuration items, and relationships
- Partitioning by closure date for efficient management of open/closed tickets

# RAG database (AI Agent database)

This database manages the RAG search process and agent context. It holds user profile information, document embeddings, chat logs, retrieval history, feedback, and links to external tickets and problems.

## Description of the data model 

- `documents`: Metadata for documents referenced in RAG search
- `kb_chunks`: Chunks of documents with dense and sparse embeddings (pgvector, vectorscale)
- `conversations`, `chat_logs`, `retrieval_history`: Tracks user-agent interactions and retrievals
- `external_tickets`, `problems`, `solutions`, `ticket_problem_links`: Links to service desk tickets, known problems, and validated solutions
- `feedback`, `escalation_rules`, `applied_solutions`, `alerts`: Feedback, escalation, and alert tracking

# Hybrid RAG Search design 

The system supports hybrid RAG search using both dense (vector) and sparse (keyword) retrieval, with dynamic weighting and reranking. Embeddings are refreshed as needed based on ticket/document changes.

## refresh embeddings 

Embeddings are refreshed for tickets/documents when significant changes are detected (e.g., ticket status changes, new information added). The system tracks changes to fields that are part of the embedding and triggers re-embedding as needed.

## manual vs dynamic weights 

The agent dynamically adjusts the weighting between dense and sparse retrieval based on the query type (e.g., technical/keyword vs. conceptual/natural language). Manual override is also possible for advanced users.

# Data ingestion

To test the relevance of this model and find its limits, the databases are populated with realistic data that provides examples of nuances found in technical environments. The AI agent must provide highly technical information to experienced users, so data quality and embedding processing are critical.

## Chunk sizes 

Documents are chunked using heuristics (e.g., by section, paragraph, or token count) to optimize retrieval granularity and embedding quality.

## Tokenization 

Tokenization is performed using the embedding model's tokenizer to ensure compatibility and maximize embedding efficiency.

## Embeddings refresh 

Embeddings are refreshed periodically or when significant changes are detected in the source data.

# Data retrieval 

The system uses advanced indexing (pgvector, pgvectorscale) and hybrid search to retrieve relevant chunks, tickets, and solutions efficiently.

## Indexes on pgvector-pgvectorscale 

Indexes are created on embedding columns for fast vector search and on metadata for efficient filtering.

# Limitations 

- The databases are static in this example; in production, they would be live and require event-driven embedding refresh.
- The AI agent currently uses hardcoded SQL queries and in-memory storage for some MCP tools; future work will include database-backed MCP tools and more dynamic workflows.
- The system is designed for educational and experimental purposes and may require adaptation for production use.

# Data flow 

In this example, the databases are static. Realistically, the Service Desk and Documents databases would be live with continuously incoming data.
The document database would require periodic batch embedding refresh, while the Service Desk database would need event-driven embedding refresh based on ticket lifecycle changes.

# Release Notes

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

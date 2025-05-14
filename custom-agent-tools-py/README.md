# custom-agent-tools-py (v0.7)

Python/Langchain MCP Server for SD Agent

**This is the actively maintained MCP server for the Service Desk AI Agent. The previous TypeScript version (`custom-agent-tools`) is now deprecated.**

This project is a Python-based MCP server for the Service Desk AI Agent, providing modular tools and resources for chat logging, ticket management, search, feedback, problem linking, advanced LLM orchestration, email, alerting, analytics, and now advanced LLM chains and workflows.

## Features

- Chat interaction logging (resource + tool, PostgreSQL-backed)
- Ticket management (resource + tool, PostgreSQL-backed)
- Search tool for chat logs and tickets (hybrid: dense/vector + sparse/keyword, Langchain + SQL)
- Feedback submission tool and resource (PostgreSQL-backed)
- Problem linking tool and resource (PostgreSQL-backed)
- Advanced LLM orchestration endpoints (summarization, classification, etc.)
- Email and alerting tool endpoints (real SMTP and Slack integration)
- Analytics endpoints (e.g., ticket counts)
- UI integration endpoints (for frontend)
- Multi-step LLM chains for ticket triage, root cause analysis, solution recommendation
- Conversation summarization, entity extraction, follow-up actions
- Hybrid reranking, context window optimization, dynamic prompt engineering, feedback loops
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

### v0.7 (Current)

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

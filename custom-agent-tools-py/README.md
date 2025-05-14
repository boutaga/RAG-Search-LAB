# custom-agent-tools-py (v0.2)

Python/Langchain MCP Server for SD Agent

This project is a Python-based MCP server for the Service Desk AI Agent, providing modular tools and resources for chat logging, ticket management, search, feedback, and problem linking. It is a migration and enhancement of the previous TypeScript MCP agent, now leveraging the Python ecosystem and Langchain for advanced RAG and LLM workflows.

## Features

- Chat interaction logging (resource + tool)
- Ticket management (resource + tool)
- Search tool for chat logs and tickets (keyword, hybrid, or vector search)
- Feedback submission tool and resource
- Problem linking tool and resource
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

A FastAPI app or MCP stdio server entrypoint will be provided in `main.py` (to be implemented).

```bash
uvicorn main:app --reload
# or for stdio MCP server (to be implemented)
python main.py
```

## Migration Notes

- This Python MCP server is a migration of the TypeScript MCP agent, now using Langchain for RAG, LLM, and agent workflows.
- All core tools and resources from the TypeScript version are being ported and enhanced.
- The server is designed for easy integration with the main RAG-Search-LAB backend and PostgreSQL databases.

## Upcoming Tasks

- Implement FastAPI endpoints and/or MCP stdio server for all tools/resources
- Integrate Langchain for advanced RAG and LLM orchestration
- Add database-backed storage for chat logs, tickets, feedback, and problem links
- Implement hybrid search (dense/sparse) using Langchain and pgvector
- Add email/notification tool integration
- Provide usage examples and documentation

## Version

- v0.2 (Python/Langchain MCP server initial migration)

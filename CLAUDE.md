# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG-Search-LAB is an educational Retrieval-Augmented Generation (RAG) search platform that combines traditional service desk workflow with modern AI capabilities. It demonstrates enterprise RAG search using PostgreSQL with pgvector extension, hybrid dense/sparse embeddings, and streaming chat interfaces.

## Architecture

The system uses three PostgreSQL databases:
- **documents_db**: SOPs, document metadata, file links
- **sd_db**: Service desk tickets, users, organizations, configuration items
- **ai_agent_db**: Embeddings, chat logs, retrieval history, feedback

Key components:
- **FastAPI Backend** (`RAG_Scripts/`): Core RAG search, ticket management, document retrieval
- **MCP Server** (`custom-agent-tools-py/`): Advanced analytics, LLM chains, notifications
- **Frontend** (`frontend/`): React/TypeScript UI with streaming chat
- **Installation Scripts** (`installation/`): Automated Linux deployment

## Development Commands

### Backend (FastAPI)
```bash
cd RAG_Scripts
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### MCP Server (Python)
```bash
cd custom-agent-tools-py
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
npm run build
```

### Database Setup
```bash
# Create databases and run schema files
psql -U postgres -c "CREATE DATABASE documents_db;"
psql -U postgres -c "CREATE DATABASE sd_db;"
psql -U postgres -c "CREATE DATABASE ai_agent_db;"

# Load schemas
psql -U postgres -d documents_db < database_documents/database_structure.sql
psql -U postgres -d sd_db < database_SD/database_structure.sql  
psql -U postgres -d ai_agent_db < database_AI_agent/database_structure.sql

# Enable pgvector extension
psql -U postgres -d ai_agent_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Embedding Generation
```bash
cd RAG_Scripts
python embed_docs.py  # Generate embeddings for documents
python create_emb_sparse.py  # Create sparse embeddings
```

## Key Implementation Details

### FastAPI Endpoints
- All API endpoints use async/await pattern
- SSE streaming for chat responses: `/api/chat/stream`
- JWT authentication on protected endpoints
- CORS configured for frontend communication

### RAG Retrieval
- Hybrid search combines pgvector similarity and SPLADE sparse retrieval
- Default similarity threshold: 0.7
- Citations tracked in `ai_agent_db.retrieval_history`
- Embeddings use OpenAI's text-embedding-ada-002 model

### MCP Server Tools
- Analytics dashboard generation
- LLM chains for complex workflows
- Webhook notifications (Slack, Teams, PagerDuty)
- Direct database queries with safety controls

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- PostgreSQL connection strings for all 3 databases
- OpenAI API key and model settings
- JWT secret for authentication
- Webhook URLs for notifications
- Frontend API URL

## Production Deployment

Use the installation scripts for systemd service deployment:
```bash
cd installation
sudo ./install.sh
```

This creates services:
- `raglab-fastapi.service`: Main FastAPI backend
- `raglab-mcp.service`: MCP server
- `raglab-logrotate.service`: Log rotation
- `metrics-exporter.service`: Prometheus metrics

## Testing Approach

Currently no automated tests. For manual testing:
- Use the frontend chat interface at `http://localhost:3000`
- Test API endpoints via Swagger UI at `http://localhost:8000/docs`
- MCP server testing via `http://localhost:8001/docs`
- Check logs in `/var/log/raglab/`

## Common Tasks

### Add New Documents
1. Insert document metadata in `documents_db.documents` table
2. Run `python RAG_Scripts/embed_docs.py` to generate embeddings
3. Optionally run sparse embedding generation

### Update RAG Model
1. Modify `OPENAI_MODEL` in `.env`
2. Update embedding dimension in `ai_agent_db.embeddings` if changing embedding model
3. Re-run embedding generation for all documents

### Debug RAG Retrieval
1. Check `ai_agent_db.retrieval_history` for search queries
2. Verify embeddings exist in `ai_agent_db.embeddings`
3. Test similarity search directly in PostgreSQL with pgvector

## Database Considerations

- All timestamps use `TIMESTAMP WITH TIME ZONE`
- Vector dimensions must match embedding model output (1536 for ada-002)
- Indexes exist on vector columns for performance
- Regular VACUUM recommended for vector tables
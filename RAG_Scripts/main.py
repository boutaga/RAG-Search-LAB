# main.py

import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pathlib
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from langchain.embeddings import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector  # PGVector integration
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient  # MCP integration
from sqlalchemy import text
import torch
from torch import Tensor
from typing import List, Dict, Tuple, Any, Optional, AsyncGenerator
import numpy as np
from fastapi.concurrency import run_in_threadpool
import asyncio

# Import functions from create_emb_sparse.py
from create_emb_sparse import get_sparse, get_dense, MODEL_NAME

# Constants for RAG search configuration
TOP_K = 5
DENSE_WEIGHT = 0.7  # Default weight for dense vectors
SPARSE_WEIGHT = 0.3  # Default weight for sparse vectors

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/agentdb")
DOCUMENT_DB_URL = os.getenv("DOCUMENT_DB_URL", "postgresql+asyncpg://user:pass@localhost/documentdb")
SD_DB_URL = os.getenv("SD_DB_URL", "postgresql+asyncpg://user:pass@localhost/sddb")
VECTOR_DIM = 1536
MCP_SERVERS = os.getenv("MCP_SERVERS", "http://localhost:8001")  # MCP server URL

# Database setup
agent_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncAgentSessionLocal = sessionmaker(agent_engine, class_=AsyncSession, expire_on_commit=False)

document_engine = create_async_engine(DOCUMENT_DB_URL, echo=True)
AsyncDocumentSessionLocal = sessionmaker(document_engine, class_=AsyncSession, expire_on_commit=False)

sd_engine = create_async_engine(SD_DB_URL, echo=True)
AsyncSDSessionLocal = sessionmaker(sd_engine, class_=AsyncSession, expire_on_commit=False)

# FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
solutions_router = APIRouter()
tickets_router = APIRouter()
chat_router = APIRouter()

# Serve frontend build (React) from /
FRONTEND_DIST = pathlib.Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount(
        "/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend"
    )
    # Optionally, add a catch-all route for client-side routing
    from fastapi.responses import FileResponse
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"detail": "Frontend build not found"}, 404

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
async def get_agent_db():
    async with AsyncAgentSessionLocal() as session:
        yield session

async def get_document_db():
    async with AsyncDocumentSessionLocal() as session:
        yield session

async def get_sd_db():
    async with AsyncSDSessionLocal() as session:
        yield session

# MCP client initialization
mcp_client = MultiServerMCPClient([MCP_SERVERS])
tools = None

def get_mcp_tools_for_request(request_type: str) -> List[Tuple[str, str]]:
    """Return a list of (server, tool) pairs for the given request type."""
    mapping = {
        "solution_created": [("email_server", "send_email")],
        "ticket_alert": [
            ("teams_server", "notify_teams"),
            ("pagerduty_server", "trigger_pagerduty"),
        ],
    }
    return mapping.get(request_type, [])

def adjust_weights(query: str) -> Tuple[float, float]:
    """Dynamically adjust weights between sparse and dense vectors based on query type"""
    # Simple heuristics for weight adjustment
    query_lower = query.lower()
    
    # Prefer sparse for keyword/technical searches
    if any(kw in query_lower for kw in ["error", "bug", "crash", "code", "command", "syntax"]):
        return 0.4, 0.6  # More weight to sparse
    
    # Prefer dense for conceptual questions
    if any(kw in query_lower for kw in ["how", "why", "explain", "difference", "compare"]):
        return 0.8, 0.2  # More weight to dense
    
    # Default weights for balanced queries
    return DENSE_WEIGHT, SPARSE_WEIGHT

# Create a solution proposal and notify consultants via MCP
@solutions_router.post("/solutions")
async def create_temporary_solution(
    req: TemporarySolutionCreateRequest,
    agent_db: AsyncSession = Depends(get_agent_db)
):
    insert_sql = text("""
        INSERT INTO solutions (problem_id, title, description, is_validated, created_at)
        VALUES (:problem_id, :title, :description, FALSE, now())
        RETURNING solution_id
    """)
    result = await agent_db.execute(insert_sql.bindparams(
        problem_id=req.problem_id,
        title=req.title,
        description=req.description
    ))
    solution_id = result.scalar_one()

    await agent_db.commit()

    # Notify consultant(s) via predefined MCP tools
    consultant_email = os.getenv("CONSULTANT_EMAIL", "consultant@example.com")
    subject = f"New Solution Pending Approval: {req.title}"
    body = (
        f"A new solution has been proposed for problem ID {req.problem_id}.\n\n"
        f"Title: {req.title}\nDescription: {req.description}\n\nPlease review and validate the solution."
    )

    params = {"to": consultant_email, "subject": subject, "body": body}
    for server, tool in get_mcp_tools_for_request("solution_created"):
        try:
            await mcp_client.call_tool(server, tool, params)
        except Exception as e:
            print(f"Failed to call {tool} on {server}: {e}")

    return {"solution_id": solution_id, "status": "pending_validation"}

@app.on_event("startup")
async def startup():
    global qa_chain, embeddings, dense_retriever
    # Load OpenAI embeddings and PGVector retriever (dense)
    embeddings = OpenAIEmbeddings()
    vectorstore = PGVector.from_existing_table(
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
        table_name="kb_chunks",
        column_name="embedding",
        dimension=1536
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    # Base QA chain (will use in final step)
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0.2),
        chain_type="stuff",
        retriever=dense_retriever  # placeholder
    )

# Pydantic models
class ChatStreamRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, List[str]]] = None

class ChatRequest(BaseModel):
    message: str

class TicketUpdate(BaseModel):
    ticket_id: int
    status_id: Optional[int] = None
    assignee_user_id: Optional[int] = None
    notes: Optional[str] = None

class FeedbackRequest(BaseModel):
    log_id: int
    rating: int
    comments: Optional[str] = None

class ProblemLink(BaseModel):
    ticket_id: int
    problem_id: int
    link_type: str = "related"

class TemporarySolutionCreateRequest(BaseModel):
    problem_id: int
    title: str
    description: str
    proposed_by_user_id: Optional[int] = None  # ID of the user proposing the solution

class SolutionValidationRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_validated: Optional[bool] = None
    validator_user_id: Optional[int] = None  # ID of the consultant validating the solution

# Routes
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # TODO: implement real authentication
    session_id = str(uuid.uuid4())
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("session", session_id)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_agent_db)):
    # Fetch ticket data from AI agent database external_tickets table
    result = await db.execute("SELECT ticket_id, external_id, ticket_summary, current_status FROM external_tickets;")
    tickets = result.fetchall()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

# Endpoint to expose metadata for UI filters
@app.get("/metadata")
async def get_metadata(
    document_db: AsyncSession = Depends(get_document_db),
    sd_db: AsyncSession = Depends(get_sd_db),
):
    """Return lists of values that can be used to build filter controls."""
    cat_rows = await document_db.execute(text("SELECT name FROM categories ORDER BY name"))
    categories = [r.name for r in cat_rows.fetchall()]

    status_rows = await sd_db.execute(text("SELECT name FROM ticket_status ORDER BY name"))
    ticket_statuses = [r.name for r in status_rows.fetchall()]

    prio_rows = await sd_db.execute(text("SELECT name FROM ticket_priority ORDER BY name"))
    ticket_priorities = [r.name for r in prio_rows.fetchall()]

    type_rows = await sd_db.execute(text("SELECT name FROM ticket_type ORDER BY name"))
    ticket_types = [r.name for r in type_rows.fetchall()]

    fmt_rows = await document_db.execute(
        text("SELECT unnest(enum_range(NULL::doc_format)) AS fmt")
    )
    doc_formats = [r.fmt for r in fmt_rows.fetchall()]

    sop_rows = await document_db.execute(
        text("SELECT unnest(enum_range(NULL::sop_status)) AS s")
    )
    sop_statuses = [r.s for r in sop_rows.fetchall()]

    return {
        "categories": categories,
        "ticket_statuses": ticket_statuses,
        "ticket_priorities": ticket_priorities,
        "ticket_types": ticket_types,
        "doc_formats": doc_formats,
        "sop_statuses": sop_statuses,
    }

# New endpoint: List open tickets from SD database
@tickets_router.get("/api/sd/open-tickets")
async def list_open_tickets(sd_db: AsyncSession = Depends(get_sd_db)):
    ticket_sql = text("""
        SELECT t.ticket_id, t.title, ts.name AS status, tp.name AS priority, 
               tt.name AS type, t.description 
        FROM ticket t
        JOIN ticket_status ts ON t.status_id = ts.status_id
        JOIN ticket_priority tp ON t.priority_id = tp.priority_id
        JOIN ticket_type tt ON t.type_id = tt.type_id
        WHERE t.closure_date IS NULL
        ORDER BY 
            CASE 
                WHEN tp.name = 'Critical' THEN 1
                WHEN tp.name = 'High' THEN 2
                WHEN tp.name = 'Medium' THEN 3
                ELSE 4
            END
        LIMIT 20
    """)
    ticket_rows = await sd_db.execute(ticket_sql)
    tickets = ticket_rows.fetchall()
    return {"open_tickets": [dict(t) for t in tickets]}

# New endpoint: Get similar problems and solutions for a given ticket
@tickets_router.get("/api/tickets/{ticket_id}/related-solutions")
async def get_related_solutions(
    ticket_id: int,
    agent_db: AsyncSession = Depends(get_agent_db)
):
    # Find the external_ticket_id in AI agent database
    ext_ticket_sql = text("""
        SELECT ticket_id FROM external_tickets WHERE external_id = :ext_id AND system_source = 'internal_sd'
    """)
    ext_ticket_result = await agent_db.execute(ext_ticket_sql.bindparams(ext_id=str(ticket_id)))
    ext_ticket_id = ext_ticket_result.scalar_one_or_none()
    if not ext_ticket_id:
        raise HTTPException(status_code=404, detail="Ticket not found in AI agent database")

    # Find problems linked to this ticket
    problems_sql = text("""
        SELECT p.problem_id, p.title, p.description, p.status
        FROM problems p
        JOIN ticket_problem_links tpl ON p.problem_id = tpl.problem_id
        WHERE tpl.ticket_id = :ticket_id
    """)
    problems_result = await agent_db.execute(problems_sql.bindparams(ticket_id=ext_ticket_id))
    problems = problems_result.fetchall()

    # For each problem, find validated solutions
    solutions = []
    for problem in problems:
        solutions_sql = text("""
            SELECT solution_id, title, description, effectiveness
            FROM solutions
            WHERE problem_id = :problem_id AND is_validated = TRUE
            ORDER BY effectiveness DESC
            LIMIT 5
        """)
        solutions_result = await agent_db.execute(solutions_sql.bindparams(problem_id=problem.problem_id))
        sol_list = solutions_result.fetchall()
        solutions.append({
            "problem": dict(problem),
            "solutions": [dict(s) for s in sol_list]
        })

    return {"related_solutions": solutions}

# Validate and update a solution
@solutions_router.put("/solutions/{solution_id}")
async def validate_solution(
    solution_id: int,
    req: SolutionValidationRequest,
    agent_db: AsyncSession = Depends(get_agent_db)
):
    # Build update fields dynamically
    update_fields = []
    params = {"solution_id": solution_id}
    if req.title is not None:
        update_fields.append("title = :title")
        params["title"] = req.title
    if req.description is not None:
        update_fields.append("description = :description")
        params["description"] = req.description
    if req.is_validated is not None:
        update_fields.append("is_validated = :is_validated")
        params["is_validated"] = req.is_validated
    if req.validator_user_id is not None:
        update_fields.append("validator_id = :validator_user_id")
        params["validator_user_id"] = req.validator_user_id

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_sql = text(f"""
        UPDATE solutions
        SET {', '.join(update_fields)}, updated_at = now()
        WHERE solution_id = :solution_id
        RETURNING solution_id
    """)
    result = await agent_db.execute(update_sql.bindparams(**params))
    updated_id = result.scalar_one_or_none()
    if not updated_id:
        raise HTTPException(status_code=404, detail="Solution not found")

    await agent_db.commit()
    return {"solution_id": updated_id, "status": "updated"}

@chat_router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatStreamRequest,
    agent_db: AsyncSession = Depends(get_agent_db),
    document_db: AsyncSession = Depends(get_document_db),
    sd_db: AsyncSession = Depends(get_sd_db)
):
    """
    Streams the assistant's response token-by-token using StreamingResponse.
    """
    query = req.query
    filters = req.filters or {}
    conversation_id = uuid.uuid4()

    dense_weight, sparse_weight = adjust_weights(query)
    dense_q = await run_in_threadpool(lambda: get_dense(query))
    sparse_q = await run_in_threadpool(lambda: get_sparse(query))

    vectorstore = PGVector.from_existing_table(
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
        table_name="kb_chunks",
        column_name="embedding",
        dimension=VECTOR_DIM
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    dense_docs = await run_in_threadpool(lambda: dense_retriever.get_relevant_documents(query))

    sparse_sql = text("""
      SELECT kc.chunk_id, kc.chunk_text, d.title, 
             kc.sparse_embedding <=> :q AS dist,
             d.document_id
      FROM kb_chunks kc
      JOIN documents d ON kc.document_id = d.document_id
      ORDER BY kc.sparse_embedding <=> :q
      LIMIT :k
    """)
    sparse_rows = await agent_db.execute(sparse_sql.bindparams(q=sparse_q, k=TOP_K))
    sparse_results = sparse_rows.fetchall()

    merged = {}
    for doc, score in zip(dense_docs, [0.5] * len(dense_docs)):
        merged[doc.page_content] = {
            "dense": score, 
            "sparse": float("inf"),
            "doc_id": getattr(doc.metadata, "document_id", None) if hasattr(doc, "metadata") else None
        }
    for row in sparse_results:
        if row.chunk_text in merged:
            merged[row.chunk_text]["sparse"] = row.dist
            if not merged[row.chunk_text]["doc_id"]:
                merged[row.chunk_text]["doc_id"] = row.document_id
        else:
            merged[row.chunk_text] = {
                "dense": float("inf"), 
                "sparse": row.dist,
                "doc_id": row.document_id
            }

    combined = sorted(
        merged.items(),
        key=lambda x: dense_weight * x[1]["dense"] + sparse_weight * x[1]["sparse"]
    )[:TOP_K]
    doc_ids = [item[1]["doc_id"] for item in combined if item[1]["doc_id"]]
    context = "\n\n".join(f"{t}" for t, _ in combined)

    # Compose context as in the main chat endpoint
    ticket_info = ""
    if any(kw in query.lower() for kw in ["ticket", "issue", "problem", "incident"]):
        ticket_sql = text("""
            SELECT t.ticket_id, t.title, ts.name AS status, tp.name AS priority, 
                   tt.name AS type, t.description 
            FROM ticket t
            JOIN ticket_status ts ON t.status_id = ts.status_id
            JOIN ticket_priority tp ON t.priority_id = tp.priority_id
            JOIN ticket_type tt ON t.type_id = tt.type_id
            WHERE t.closure_date IS NULL
            ORDER BY 
                CASE 
                    WHEN tp.name = 'Critical' THEN 1
                    WHEN tp.name = 'High' THEN 2
                    WHEN tp.name = 'Medium' THEN 3
                    ELSE 4
                END
            LIMIT 5
        """)
        ticket_rows = await sd_db.execute(ticket_sql)
        tickets = ticket_rows.fetchall()
        if tickets:
            ticket_info = "Relevant tickets:\n" + "\n".join(
                f"#{t.ticket_id}: {t.title} ({t.status}, {t.priority})" 
                for t in tickets
            )
            context += "\n\n" + ticket_info

    problems_info = ""
    solutions_sql = text("""
        SELECT p.problem_id, p.title AS problem_title, p.description AS problem_desc,
               s.solution_id, s.title AS solution_title, s.description AS solution_desc,
               s.effectiveness
        FROM problems p
        JOIN solutions s ON p.problem_id = s.problem_id
        WHERE s.is_validated = TRUE
        ORDER BY s.effectiveness DESC
        LIMIT 3
    """)
    solutions_rows = await agent_db.execute(solutions_sql)
    solutions = solutions_rows.fetchall()
    if solutions:
        problems_info = "Known solutions that might help:\n" + "\n".join(
            f"Problem: {s.problem_title}\nSolution: {s.solution_title} (Effectiveness: {s.effectiveness}/5)" 
            for s in solutions
        )
        context += "\n\n" + problems_info

    # Streaming generator
    async def token_stream() -> AsyncGenerator[bytes, None]:
        # Simulate token streaming from LLM
        answer = await run_in_threadpool(lambda: qa_chain.run({"query": query, "context": context}))
        # For demonstration, split by whitespace as tokens
        for token in answer.split():
            yield (token + " ").encode("utf-8")
            await asyncio.sleep(0.01)  # Simulate delay
        # Optionally, yield a special end marker
        # yield b"[END]"

        # Log the chat interaction in AI agent database (as in /api/chat)
        log_sql = text("""
            INSERT INTO chat_logs 
                (conversation_id, role, content, model_name, prompt_tokens, response_tokens, total_tokens)
            VALUES (:conv_id, 'user', :msg, 'openai', :p_tokens, 0, :p_tokens)
            RETURNING log_id
        """)
        user_log = await agent_db.execute(
            log_sql.bindparams(
                conv_id=conversation_id, 
                msg=query, 
                p_tokens=len(query.split())
            )
        )
        user_log_id = user_log.scalar_one()
        agent_log = await agent_db.execute(
            text("""
                INSERT INTO chat_logs 
                    (conversation_id, role, content, model_name, prompt_tokens, response_tokens, total_tokens)
                VALUES (:conv_id, 'agent', :msg, 'openai', 0, :r_tokens, :r_tokens)
                RETURNING log_id
            """).bindparams(
                conv_id=conversation_id, 
                msg=answer, 
                r_tokens=len(answer.split())
            )
        )
        agent_log_id = agent_log.scalar_one()
        for i, doc_id in enumerate(doc_ids):
            if doc_id:
                await agent_db.execute(
                    text("""
                        INSERT INTO retrieval_history
                            (log_id, chunk_id, similarity_score, retrieved_at)
                        VALUES (:log_id, :chunk_id, :score, now())
                    """).bindparams(
                        log_id=user_log_id,
                        chunk_id=doc_id,
                        score=1.0/(i+1)
                    )
                )
        await agent_db.commit()

    return StreamingResponse(token_stream(), media_type="text/event-stream")

@chat_router.get("/chat/citations/{msg_id}")
async def get_citations(msg_id: str, agent_db: AsyncSession = Depends(get_agent_db)):
    """
    Returns citations (retrieved chunks) for a given message/log_id.
    """
    # Find retrievals for this log_id
    retrievals_sql = text("""
        SELECT rh.chunk_id, d.title AS source, kc.page
        FROM retrieval_history rh
        JOIN kb_chunks kc ON rh.chunk_id = kc.chunk_id
        JOIN documents d ON kc.document_id = d.document_id
        WHERE rh.log_id = :log_id
        ORDER BY rh.similarity_score DESC
        LIMIT 10
    """)
    rows = await agent_db.execute(retrievals_sql.bindparams(log_id=msg_id))
    citations = [
        {
            "chunk_id": r.chunk_id,
            "source": r.source,
            "page": r.page
        }
        for r in rows.fetchall()
    ]
    return citations

@tickets_router.put("/api/tickets/{ticket_id}")
async def update_ticket(
    ticket_update: TicketUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update ticket status, assignee, or add notes"""
    updates = []
    params = {"ticket_id": ticket_update.ticket_id}
    
    if ticket_update.status_id:
        updates.append("status_id = :status_id")
        params["status_id"] = ticket_update.status_id
    
    if ticket_update.assignee_user_id:
        updates.append("assignee_user_id = :assignee_user_id")
        params["assignee_user_id"] = ticket_update.assignee_user_id
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Update the ticket
    update_sql = text(f"""
        UPDATE ticket 
        SET {", ".join(updates)}, updated_at = now() 
        WHERE ticket_id = :ticket_id
        RETURNING ticket_id
    """)
    
    result = await db.execute(update_sql.bindparams(**params))
    updated_id = result.scalar_one_or_none()
    
    if not updated_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Add notes if provided
    if ticket_update.notes:
        # This assumes you have a notes or comments table - adjust as needed
        await db.execute(
            text("""
                INSERT INTO ticket_comments (ticket_id, comment_text, created_at)
                VALUES (:ticket_id, :notes, now())
            """).bindparams(ticket_id=ticket_update.ticket_id, notes=ticket_update.notes)
        )
    
    await db.commit()
    return {"ticket_id": updated_id, "status": "updated"}

@chat_router.post("/api/feedback")
async def submit_feedback(
    feedback: FeedbackRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for a chat response"""
    # Validate the rating is between 1 and 5
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if the log_id exists
    log_check = await db.execute(
        text("SELECT log_id FROM chat_logs WHERE log_id = :log_id"),
        {"log_id": feedback.log_id}
    )
    if not log_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chat log not found")
    
    # Insert feedback
    await db.execute(
        text("""
            INSERT INTO feedback (log_id, rating, comments, created_at)
            VALUES (:log_id, :rating, :comments, now())
        """).bindparams(
            log_id=feedback.log_id,
            rating=feedback.rating,
            comments=feedback.comments or ""
        )
    )
    
    await db.commit()
    return {"status": "feedback received", "log_id": feedback.log_id}

@tickets_router.post("/api/link-problem")
async def link_ticket_to_problem(
    link_data: ProblemLink,
    db: AsyncSession = Depends(get_db)
):
    """Link a ticket to a known problem"""
    # Validate the ticket exists
    ticket_check = await db.execute(
        text("SELECT ticket_id FROM ticket WHERE ticket_id = :ticket_id"),
        {"ticket_id": link_data.ticket_id}
    )
    if not ticket_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Validate the problem exists
    problem_check = await db.execute(
        text("SELECT problem_id FROM problems WHERE problem_id = :problem_id"),
        {"problem_id": link_data.problem_id}
    )
    if not problem_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create external ticket record if it doesn't exist
    await db.execute(
        text("""
            INSERT INTO external_tickets 
                (external_id, system_source, ticket_summary, current_status, created_at)
            SELECT 
                :ticket_id::varchar, 'internal_sd', t.title, ts.name, t.created_at
            FROM ticket t
            JOIN ticket_status ts ON t.status_id = ts.status_id
            WHERE t.ticket_id = :ticket_id
            ON CONFLICT (external_id, system_source) DO NOTHING
            RETURNING ticket_id
        """).bindparams(ticket_id=link_data.ticket_id)
    )
    
    # Get the external_ticket_id
    ext_ticket = await db.execute(
        text("""
            SELECT ticket_id FROM external_tickets 
            WHERE external_id = :ext_id AND system_source = 'internal_sd'
        """).bindparams(ext_id=str(link_data.ticket_id))
    )
    ext_ticket_id = ext_ticket.scalar_one()
    
    # Create the link
    await db.execute(
        text("""
            INSERT INTO ticket_problem_links
                (ticket_id, problem_id, link_type, created_at)
            VALUES
                (:ticket_id, :problem_id, :link_type, now())
            ON CONFLICT (ticket_id, problem_id) 
            DO UPDATE SET link_type = :link_type
        """).bindparams(
            ticket_id=ext_ticket_id,
            problem_id=link_data.problem_id,
            link_type=link_data.link_type
        )
    )
    
    await db.commit()
    return {
        "status": "linked",
        "ticket_id": link_data.ticket_id,
        "problem_id": link_data.problem_id
    }

# Register routers with the main app
app.include_router(solutions_router)
app.include_router(tickets_router)
app.include_router(chat_router)

# NGINX config snippet (to be placed in /etc/nginx/sites-available/agent):
# server {
#     listen 80;
#     server_name your.domain.com;
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     }
# }

# To run:
# uvicorn main:app --host 0.0.0.0 --port 8000

"""
custom-agent-tools-py v0.4

Python/Langchain MCP Server for SD Agent
Implements modular tools for chat logging, ticket management, search, feedback, problem linking, and now advanced LLM orchestration, email, alerting, and analytics.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_community.vectorstores.pgvector import PGVector
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA, LLMChain, SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

app = FastAPI(
    title="SD-MCP Python Agent",
    version="0.4",
    description="Python/Langchain MCP server for Service Desk Agent with hybrid RAG, LLM orchestration, and advanced tools"
)

# Database connection (AI agent database)
PG_CONN_STR = os.getenv("AI_AGENT_DB_URL", "dbname=agentdb user=user password=pass host=localhost")
def get_pg_conn():
    return psycopg2.connect(PG_CONN_STR, cursor_factory=RealDictCursor)

# Langchain setup for hybrid RAG search and LLM orchestration
embeddings = OpenAIEmbeddings()
vectorstore = PGVector.from_existing_table(
    connection_string="postgresql+psycopg2://user:pass@localhost/agentdb",
    embedding_function=embeddings,
    table_name="kb_chunks",
    column_name="embedding",
    dimension=1536
)
dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0.2),
    chain_type="stuff",
    retriever=dense_retriever
)

# Example advanced LLM orchestration: Summarize and classify a ticket
summary_prompt = PromptTemplate(
    input_variables=["ticket"],
    template="Summarize the following ticket and classify its urgency:\n\n{ticket}\n\nSummary and Urgency:"
)
summary_chain = LLMChain(llm=OpenAI(temperature=0.2), prompt=summary_prompt)

# Models
class ChatLog(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str

class Ticket(BaseModel):
    id: str
    title: str
    status: str
    assignee: str
    notes: List[str]

class Feedback(BaseModel):
    id: str
    log_id: str
    rating: int
    comments: Optional[str]
    created_at: str

class ProblemLink(BaseModel):
    id: str
    ticket_id: str
    problem_id: str
    link_type: str
    created_at: str

# Chat log endpoints (PostgreSQL-backed)
@app.post("/chatlog", response_model=ChatLog)
def add_chat_log(conversation_id: str, role: str, content: str):
    log_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_logs (log_id, conversation_id, role, content, created_at) VALUES (%s, %s, %s, %s, %s)",
                (log_id, conversation_id, role, content, created_at)
            )
            conn.commit()
    return ChatLog(id=log_id, conversation_id=conversation_id, role=role, content=content, created_at=created_at)

@app.get("/chatlog", response_model=List[ChatLog])
def list_chat_logs():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT log_id as id, conversation_id, role, content, created_at FROM chat_logs ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
    return [ChatLog(**row) for row in rows]

# Ticket endpoints (PostgreSQL-backed)
@app.post("/ticket", response_model=Ticket)
def update_ticket(id: str, title: str, status: str = "Open", assignee: str = "Unassigned", note: Optional[str] = None):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO external_tickets (external_id, ticket_summary, current_status, assignee, created_at) VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (external_id) DO UPDATE SET ticket_summary = EXCLUDED.ticket_summary, current_status = EXCLUDED.current_status, assignee = EXCLUDED.assignee",
                (id, title, status, assignee, datetime.utcnow())
            )
            if note:
                cur.execute(
                    "INSERT INTO ticket_comments (ticket_id, comment_text, created_at) VALUES (%s, %s, %s)",
                    (id, note, datetime.utcnow())
                )
            conn.commit()
            cur.execute(
                "SELECT external_id as id, ticket_summary as title, current_status as status, assignee, ARRAY(SELECT comment_text FROM ticket_comments WHERE ticket_id = %s) as notes FROM external_tickets WHERE external_id = %s",
                (id, id)
            )
            row = cur.fetchone()
    return Ticket(**row)

@app.get("/ticket", response_model=List[Ticket])
def list_tickets():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT external_id as id, ticket_summary as title, current_status as status, assignee, ARRAY(SELECT comment_text FROM ticket_comments WHERE ticket_id = external_id) as notes FROM external_tickets ORDER BY created_at DESC LIMIT 100"
            )
            rows = cur.fetchall()
    return [Ticket(**row) for row in rows]

# Feedback endpoints (PostgreSQL-backed)
@app.post("/feedback", response_model=Feedback)
def submit_feedback(log_id: str, rating: int, comments: Optional[str] = None):
    fb_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (feedback_id, log_id, rating, comments, created_at) VALUES (%s, %s, %s, %s, %s)",
                (fb_id, log_id, rating, comments or "", created_at)
            )
            conn.commit()
    return Feedback(id=fb_id, log_id=log_id, rating=rating, comments=comments or "", created_at=created_at)

@app.get("/feedback", response_model=List[Feedback])
def list_feedbacks():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT feedback_id as id, log_id, rating, comments, created_at FROM feedback ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
    return [Feedback(**row) for row in rows]

# Problem link endpoints (PostgreSQL-backed)
@app.post("/problem-link", response_model=ProblemLink)
def link_problem(ticket_id: str, problem_id: str, link_type: str = "related"):
    link_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ticket_problem_links (link_id, ticket_id, problem_id, link_type, created_at) VALUES (%s, %s, %s, %s, %s)",
                (link_id, ticket_id, problem_id, link_type, created_at)
            )
            conn.commit()
    return ProblemLink(id=link_id, ticket_id=ticket_id, problem_id=problem_id, link_type=link_type, created_at=created_at)

@app.get("/problem-link", response_model=List[ProblemLink])
def list_problem_links():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT link_id as id, ticket_id, problem_id, link_type, created_at FROM ticket_problem_links ORDER BY created_at DESC LIMIT 100")
            rows = cur.fetchall()
    return [ProblemLink(**row) for row in rows]

# Hybrid RAG search endpoint using Langchain
@app.get("/search")
def search(query: str, limit: int = 5):
    # Hybrid RAG: dense retrieval via Langchain, sparse via SQL
    dense_docs = dense_retriever.get_relevant_documents(query)
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT chunk_id, chunk_text FROM kb_chunks WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery(%s) LIMIT %s",
                (query, limit)
            )
            sparse_docs = cur.fetchall()
    # Merge and deduplicate results
    seen = set()
    results = []
    for doc in dense_docs:
        if doc.page_content not in seen:
            results.append({"type": "dense", "content": doc.page_content})
            seen.add(doc.page_content)
    for doc in sparse_docs:
        if doc["chunk_text"] not in seen:
            results.append({"type": "sparse", "content": doc["chunk_text"]})
            seen.add(doc["chunk_text"])
    return results[:limit]

# Advanced LLM orchestration endpoint: summarize and classify a ticket
@app.post("/llm/summarize_ticket")
def summarize_ticket(ticket_id: str):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_summary FROM external_tickets WHERE external_id = %s", (ticket_id,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    summary = summary_chain.run(ticket=row["ticket_summary"])
    return {"ticket_id": ticket_id, "summary_and_urgency": summary}

# Email/alerting/analytics tool endpoints (stubs for v0.4)
@app.post("/notify/email")
def send_email(to: str, subject: str, body: str):
    # TODO: Integrate with real email service
    print(f"Email sent to {to}: {subject}\n{body}")
    return {"status": "sent", "to": to, "subject": subject}

@app.post("/notify/alert")
def send_alert(message: str, severity: str = "info"):
    # TODO: Integrate with real alerting system
    print(f"Alert ({severity}): {message}")
    return {"status": "alerted", "severity": severity}

@app.get("/analytics/ticket-counts")
def ticket_counts():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_status, COUNT(*) FROM external_tickets GROUP BY current_status")
            rows = cur.fetchall()
    return {"ticket_counts": rows}

# TODO: Add more analytics endpoints as needed
# TODO: Add UI integration endpoints (for frontend)

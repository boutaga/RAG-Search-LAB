"""
custom-agent-tools-py v0.9

Python/Langchain MCP Server for SD Agent
Adds hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request

try:  # Optional FastMCP support
    from fastmcp import FastMCP, tool
except Exception:  # pragma: no cover - fastmcp not installed
    FastMCP = FastAPI  # type: ignore

    def tool(*_args, **_kwargs):
        def decorator(fn):
            return fn

        return decorator
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_community.vectorstores.pgvector import PGVector
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA, LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import smtplib
from email.message import EmailMessage
import requests
import csv
from fastapi.responses import StreamingResponse
from io import StringIO
import json


app = FastMCP(
    title="SD-MCP Python Agent",
    version="0.9",
    description="Python/Langchain MCP server for Service Desk Agent with advanced RAG, LLM, analytics, UI, and feedback loops"
)

# Database connection (AI agent database)
PG_CONN_STR = os.getenv("AI_AGENT_DB_URL", "dbname=agentdb user=user password=pass host=localhost")
PGVECTOR_CONN_STR = os.getenv(
    "PGVECTOR_CONN_STR",
    "postgresql+psycopg2://user:pass@localhost/agentdb",
)

# Alerting integration
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
PAGERDUTY_ROUTING_KEY = os.getenv("PAGERDUTY_ROUTING_KEY")

def get_pg_conn():
    return psycopg2.connect(PG_CONN_STR, cursor_factory=RealDictCursor)

# Hybrid RAG setup
embeddings = OpenAIEmbeddings()
vectorstore = PGVector.from_existing_table(
    connection_string=PGVECTOR_CONN_STR,
    embedding_function=embeddings,
    table_name="kb_chunks",
    column_name="embedding",
    dimension=1536
)
dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Feedback storage (PostgreSQL-backed)
def store_feedback(query, dense_results, sparse_results, reranked, user_feedback, llm_output):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (feedback_id, log_id, rating, comments, created_at) VALUES (%s, %s, %s, %s, %s)",
                (str(uuid.uuid4()), query, user_feedback.get("rating", 0), user_feedback.get("comments", ""), datetime.utcnow())
            )
            conn.commit()

# Store outputs from LLM chains for analytics
def store_chain_output(chain_type: str, input_data: dict, output_text: str):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_chain_runs (
                    run_id UUID PRIMARY KEY,
                    chain_type TEXT NOT NULL,
                    input_data JSONB NOT NULL,
                    output_text TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                "INSERT INTO llm_chain_runs (run_id, chain_type, input_data, output_text, created_at) VALUES (%s, %s, %s, %s, %s)",
                (str(uuid.uuid4()), chain_type, json.dumps(input_data), output_text, datetime.utcnow())
            )
            conn.commit()

# Hybrid reranking
def hybrid_rerank(dense_results, sparse_results, weights=None, feedback=None):
    # Simple weighted sum, can be replaced with LLM-based reranking
    weights = weights or {"dense": 0.6, "sparse": 0.4}
    combined = {}
    for doc in dense_results:
        combined[doc.page_content] = {"dense": 1.0, "sparse": 0.0}
    for doc in sparse_results:
        if doc["chunk_text"] in combined:
            combined[doc["chunk_text"]]["sparse"] = 1.0
        else:
            combined[doc["chunk_text"]] = {"dense": 0.0, "sparse": 1.0}
    # Optionally adjust weights based on feedback
    reranked = sorted(
        combined.items(),
        key=lambda x: -(weights["dense"] * x[1]["dense"] + weights["sparse"] * x[1]["sparse"])
    )
    return [r[0] for r in reranked]

# Context window optimization
def optimize_context_window(chunks, max_tokens=2048):
    # Naive: truncate to max_tokens, can be improved with LLM-based selection
    token_count = 0
    selected = []
    for chunk in chunks:
        tokens = len(chunk.split())
        if token_count + tokens > max_tokens:
            break
        selected.append(chunk)
        token_count += tokens
    return selected

# Dynamic prompt engineering
def dynamic_prompt_engineering(base_prompt, context, user=None):
    # Insert context, user info, and adjust instructions dynamically
    prompt = base_prompt.replace("{context}", context)
    if user:
        prompt = prompt.replace("{user}", user)
    return prompt

# Feedback loop
def feedback_loop(llm_output, user_feedback):
    # Store feedback and optionally adjust system parameters
    print(f"Feedback received: {user_feedback} for output: {llm_output}")

# Microsoft Teams integration
def post_to_teams(message: str):
    if not TEAMS_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="TEAMS_WEBHOOK_URL not configured")
    resp = requests.post(TEAMS_WEBHOOK_URL, json={"text": message})
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail="Teams notification failed")
    return {"status": "sent"}


# PagerDuty integration
def trigger_pagerduty(summary: str, severity: str = "info", source: str = "custom-agent-tools-py"):
    if not PAGERDUTY_ROUTING_KEY:
        raise HTTPException(status_code=500, detail="PAGERDUTY_ROUTING_KEY not configured")
    payload = {
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": summary,
            "source": source,
            "severity": severity,
        },
    }
    resp = requests.post("https://events.pagerduty.com/v2/enqueue", json=payload)
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail="PagerDuty notification failed")
    return {"status": "triggered"}

# Hybrid RAG search endpoint with advanced features
@tool
@app.get("/search")
def search(
    query: str,
    limit: int = 5,
    rerank: bool = True,
    max_tokens: int = 2048,
    user: Optional[str] = None
):
    dense_docs = dense_retriever.get_relevant_documents(query)
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT chunk_id, chunk_text FROM kb_chunks WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery(%s) LIMIT %s",
                (query, limit * 2)
            )
            sparse_docs = cur.fetchall()
    # Hybrid reranking
    if rerank:
        reranked = hybrid_rerank(dense_docs, sparse_docs)
    else:
        reranked = [doc.page_content for doc in dense_docs] + [doc["chunk_text"] for doc in sparse_docs]
    # Context window optimization
    context_chunks = optimize_context_window(reranked, max_tokens=max_tokens)
    # Dynamic prompt engineering
    base_prompt = "Answer the user's question using the following context:\n{context}\nQuestion: " + query
    prompt = dynamic_prompt_engineering(base_prompt, "\n".join(context_chunks), user=user)
    # LLM answer
    llm = OpenAI(temperature=0.2)
    answer = llm(prompt)
    return {
        "query": query,
        "context_chunks": context_chunks,
        "answer": answer
    }

# Feedback loop endpoint
@tool
@app.post("/feedback-loop")
def feedback_loop_endpoint(query: str, llm_output: str, rating: int, comments: Optional[str] = None):
    user_feedback = {"rating": rating, "comments": comments or ""}
    feedback_loop(llm_output, user_feedback)
    store_feedback(query, [], [], [], user_feedback, llm_output)
    return {"status": "feedback received"}


"""Analytics Endpoints"""

@app.get("/analytics/ticket-volume")
def ticket_volume(start: str = Query(...), end: str = Query(...)):
    """Return ticket counts per day between start and end dates."""
    sql = (
        "SELECT date_trunc('day', created_at) AS day, COUNT(*) AS count "
        "FROM external_tickets WHERE created_at BETWEEN %s AND %s "
        "GROUP BY day ORDER BY day"
    )
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (start, end))
            rows = cur.fetchall()
    # Format datetime to date string
    data = [{"day": r["day"].date().isoformat(), "count": r["count"]} for r in rows]
    return {"ticket_volume": data}


@app.get("/analytics/resolution-times")
def resolution_times():
    """Return average ticket resolution time in hours."""
    sql = (
        "SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))) AS avg_sec "
        "FROM external_tickets WHERE resolved_at IS NOT NULL"
    )
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
    avg_hours = (row["avg_sec"] or 0) / 3600
    return {"average_resolution_hours": avg_hours}


@app.get("/analytics/sla-compliance")
def sla_compliance(hours: int = Query(48)):
    """Return percentage of tickets resolved within the given SLA hours."""
    sql = (
        "SELECT COUNT(*) FILTER (WHERE resolved_at IS NOT NULL) AS resolved, "
        "COUNT(*) FILTER (WHERE resolved_at IS NOT NULL AND resolved_at - created_at <= interval '%s hour') AS within_sla "
        "FROM external_tickets" % hours
    )
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
    resolved = row["resolved"] or 0
    within = row["within_sla"] or 0
    compliance = (within / resolved) * 100 if resolved > 0 else 0
    return {"sla_compliance_percent": compliance}


@app.get("/analytics/agent-leaderboard")
def agent_leaderboard(limit: int = 10):
    """Return top agents by metric value from agent_metrics."""
    sql = (
        "SELECT metric_name, metric_value FROM agent_metrics "
        "WHERE metric_name LIKE 'agent_%' ORDER BY metric_value DESC LIMIT %s"
    )
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
    leaderboard = [dict(row) for row in rows]
    return {"leaderboard": leaderboard}


@app.get("/analytics/document-usage")
def document_usage():
    """Return document retrieval counts from retrieval history."""
    sql = (
        "SELECT d.document_id, d.title, COUNT(r.retrieval_id) AS count "
        "FROM retrieval_history r "
        "JOIN kb_chunks k ON r.chunk_id = k.chunk_id "
        "JOIN documents d ON k.document_id = d.document_id "
        "GROUP BY d.document_id, d.title ORDER BY count DESC"
    )
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    usage = [dict(row) for row in rows]
    return {"document_usage": usage}


def _to_csv(data):
    output = StringIO()
    if isinstance(data, list):
        if not data:
            return output
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    else:
        writer = csv.writer(output)
        for k, v in data.items():
            writer.writerow([k, v])
    output.seek(0)
    return output


@app.get("/analytics/export")
def export_analytics(type: str = Query(...), format: str = Query("json")):
    """Export analytics data as JSON or CSV."""
    mapping = {
        "ticket_volume": ticket_volume,
        "resolution_times": resolution_times,
        "sla_compliance": sla_compliance,
        "agent_leaderboard": agent_leaderboard,
        "document_usage": document_usage,
    }
    if type not in mapping:
        raise HTTPException(status_code=400, detail="invalid analytics type")
    data = mapping[type]()
    if format == "csv":
        csv_data = _to_csv(data.get(next(iter(data)))) if isinstance(data, dict) else _to_csv(data)
        return StreamingResponse(csv_data, media_type="text/csv")
    return data


# --- LLMChain-powered endpoints ---

def _get_ticket_summary(ticket_id: int) -> str:
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ticket_summary FROM external_tickets WHERE ticket_id = %s",
                (ticket_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Ticket not found")
            return row["ticket_summary"]


@app.post("/llm/triage_ticket")
def triage_ticket(ticket_id: int):
    """Classify ticket priority using an LLM chain"""
    ticket = _get_ticket_summary(ticket_id)
    prompt = PromptTemplate.from_template(
        "You are a helpdesk triage assistant. Given the ticket description below, assign a priority label (low, medium, high).\n{ticket}"
    )
    chain = LLMChain(llm=OpenAI(temperature=0.2), prompt=prompt)
    result = chain.run(ticket=ticket)
    store_chain_output("triage_ticket", {"ticket_id": ticket_id}, result)
    return {"ticket_id": ticket_id, "triage": result}


@app.post("/llm/root_cause")
def root_cause(ticket_id: int):
    """Return a likely root cause for the ticket"""
    ticket = _get_ticket_summary(ticket_id)
    prompt = PromptTemplate.from_template(
        "Analyze the following ticket and provide the most likely root cause in one sentence:\n{ticket}"
    )
    chain = LLMChain(llm=OpenAI(temperature=0.2), prompt=prompt)
    result = chain.run(ticket=ticket)
    store_chain_output("root_cause", {"ticket_id": ticket_id}, result)
    return {"ticket_id": ticket_id, "root_cause": result}


@app.post("/llm/summarize_ticket")
def summarize_ticket(ticket_id: int):
    """Summarize the ticket into a short paragraph"""
    ticket = _get_ticket_summary(ticket_id)
    prompt = PromptTemplate.from_template(
        "Provide a concise summary of the following ticket:\n{ticket}"
    )
    chain = LLMChain(llm=OpenAI(temperature=0.2), prompt=prompt)
    result = chain.run(ticket=ticket)
    store_chain_output("summarize_ticket", {"ticket_id": ticket_id}, result)
    return {"ticket_id": ticket_id, "summary": result}


@app.post("/llm/followup_actions")
def followup_actions(ticket_id: int):
    """Suggest follow-up actions for the ticket"""
    ticket = _get_ticket_summary(ticket_id)
    prompt = PromptTemplate.from_template(
        "Based on this ticket, suggest next best follow-up actions in bullet form:\n{ticket}"
    )
    chain = LLMChain(llm=OpenAI(temperature=0.2), prompt=prompt)
    result = chain.run(ticket=ticket)
    store_chain_output("followup_actions", {"ticket_id": ticket_id}, result)
    return {"ticket_id": ticket_id, "actions": result}


class TeamsPayload(BaseModel):
    message: str


@tool
@app.post("/notify/teams")
def notify_teams(payload: TeamsPayload):
    return post_to_teams(payload.message)


class PagerDutyPayload(BaseModel):
    summary: str
    severity: Optional[str] = "info"
    source: Optional[str] = "custom-agent-tools-py"


@tool
@app.post("/notify/pagerduty")
def notify_pagerduty(payload: PagerDutyPayload):
    return trigger_pagerduty(payload.summary, payload.severity, payload.source)


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
def plugin_manifest(request: Request):
    """Return FastMCP tool metadata."""
    base = str(request.base_url).rstrip("/")
    return {
        "schema_version": "v1",
        "name_for_human": "SD MCP Tools",
        "name_for_model": "sd_mcp",
        "description_for_human": "Service Desk MCP tools for search and notifications",
        "description_for_model": "Tools for searching the KB and sending notifications.",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": f"{base}/openapi.json"},
        "logo_url": f"{base}/static/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": "https://example.com/legal",
    }


# All previous endpoints (chatlog, ticket, feedback, problem-link, analytics, LLM chains, email/alerting, etc.) remain unchanged

# TODO: Add more advanced analytics, BI tool integration, and UI usage examples as needed


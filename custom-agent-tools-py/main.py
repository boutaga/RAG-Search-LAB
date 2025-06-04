"""
custom-agent-tools-py v0.9

Python/Langchain MCP Server for SD Agent
Adds hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
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

app = FastAPI(
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
@app.post("/feedback-loop")
def feedback_loop_endpoint(query: str, llm_output: str, rating: int, comments: Optional[str] = None):
    user_feedback = {"rating": rating, "comments": comments or ""}
    feedback_loop(llm_output, user_feedback)
    store_feedback(query, [], [], [], user_feedback, llm_output)
    return {"status": "feedback received"}


class TeamsPayload(BaseModel):
    message: str


@app.post("/notify/teams")
def notify_teams(payload: TeamsPayload):
    return post_to_teams(payload.message)


class PagerDutyPayload(BaseModel):
    summary: str
    severity: Optional[str] = "info"
    source: Optional[str] = "custom-agent-tools-py"


@app.post("/notify/pagerduty")
def notify_pagerduty(payload: PagerDutyPayload):
    return trigger_pagerduty(payload.summary, payload.severity, payload.source)

# All previous endpoints (chatlog, ticket, feedback, problem-link, analytics, LLM chains, email/alerting, etc.) remain unchanged

# TODO: Add more advanced analytics, BI tool integration, and UI usage examples as needed

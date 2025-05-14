"""
custom-agent-tools-py v0.7

Python/Langchain MCP Server for SD Agent
Adds advanced LLM chains and workflows: multi-step ticket triage, root cause analysis, solution recommendation, conversation summarization, entity extraction, follow-up actions, hybrid reranking, context window optimization, dynamic prompt engineering, and feedback loops.
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
from langchain.llms import OpenAI, AzureOpenAI, HuggingFaceHub
from langchain.prompts import PromptTemplate

app = FastAPI(
    title="SD-MCP Python Agent",
    version="0.7",
    description="Python/Langchain MCP server for Service Desk Agent with advanced LLM chains, hybrid RAG, email, alerting, and analytics"
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

# LLM provider selection
def get_llm(provider: str = "openai"):
    if provider == "openai":
        return OpenAI(temperature=0.2)
    elif provider == "azure":
        return AzureOpenAI(temperature=0.2)
    elif provider == "huggingface":
        return HuggingFaceHub(repo_id="google/flan-t5-large")
    else:
        raise HTTPException(status_code=400, detail="Unknown LLM provider")

# Advanced LLM chains and workflows

# Ticket triage chain
triage_prompt = PromptTemplate(
    input_variables=["ticket"],
    template="Classify the following ticket for urgency, category, and required action:\n\n{ticket}\n\nClassification:"
)
triage_chain = LLMChain(llm=get_llm("openai"), prompt=triage_prompt)

# Root cause analysis chain
root_cause_prompt = PromptTemplate(
    input_variables=["ticket", "history"],
    template="Given the ticket and its history, identify the most likely root cause:\n\nTicket: {ticket}\nHistory: {history}\n\nRoot Cause:"
)
root_cause_chain = LLMChain(llm=get_llm("openai"), prompt=root_cause_prompt)

# Solution recommendation chain
solution_prompt = PromptTemplate(
    input_variables=["ticket", "root_cause"],
    template="Recommend a solution for the following ticket and root cause:\n\nTicket: {ticket}\nRoot Cause: {root_cause}\n\nSolution:"
)
solution_chain = LLMChain(llm=get_llm("openai"), prompt=solution_prompt)

# Conversation summarization chain
conversation_summary_prompt = PromptTemplate(
    input_variables=["conversation"],
    template="Summarize the following conversation:\n\n{conversation}\n\nSummary:"
)
conversation_summary_chain = LLMChain(llm=get_llm("openai"), prompt=conversation_summary_prompt)

# Entity extraction chain
entity_prompt = PromptTemplate(
    input_variables=["text"],
    template="Extract all key entities (people, systems, errors, etc.) from the following text:\n\n{text}\n\nEntities:"
)
entity_chain = LLMChain(llm=get_llm("openai"), prompt=entity_prompt)

# Follow-up action chain
followup_prompt = PromptTemplate(
    input_variables=["ticket", "conversation"],
    template="Based on the ticket and conversation, suggest follow-up actions:\n\nTicket: {ticket}\nConversation: {conversation}\n\nActions:"
)
followup_chain = LLMChain(llm=get_llm("openai"), prompt=followup_prompt)

# Hybrid reranking, context window optimization, dynamic prompt engineering, feedback loop (stubs)
def hybrid_rerank(dense_results, sparse_results):
    # TODO: Implement hybrid reranking logic (e.g., weighted, LLM-based)
    return dense_results + sparse_results

def optimize_context_window(chunks, max_tokens=2048):
    # TODO: Implement context window optimization (e.g., select most relevant chunks)
    return chunks[:max_tokens]

def dynamic_prompt_engineering(base_prompt, context):
    # TODO: Implement dynamic prompt engineering (e.g., insert context, adjust instructions)
    return base_prompt.format(**context)

def feedback_loop(llm_output, user_feedback):
    # TODO: Implement feedback loop for LLM output quality improvement
    print(f"Feedback received: {user_feedback} for output: {llm_output}")

# Models (same as previous version)
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

# ... (all previous endpoints remain unchanged)

# Advanced LLM orchestration endpoints
@app.post("/llm/triage_ticket")
def triage_ticket(ticket_id: str, provider: str = "openai"):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_summary FROM external_tickets WHERE external_id = %s", (ticket_id,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    triage = LLMChain(llm=get_llm(provider), prompt=triage_prompt).run(ticket=row["ticket_summary"])
    return {"ticket_id": ticket_id, "triage": triage}

@app.post("/llm/root_cause")
def root_cause(ticket_id: str, provider: str = "openai"):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_summary FROM external_tickets WHERE external_id = %s", (ticket_id,))
            ticket_row = cur.fetchone()
            cur.execute("SELECT array_agg(comment_text) as history FROM ticket_comments WHERE ticket_id = %s", (ticket_id,))
            history_row = cur.fetchone()
    if not ticket_row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    history = "\n".join(history_row["history"] or [])
    root_cause = LLMChain(llm=get_llm(provider), prompt=root_cause_prompt).run(ticket=ticket_row["ticket_summary"], history=history)
    return {"ticket_id": ticket_id, "root_cause": root_cause}

@app.post("/llm/recommend_solution")
def recommend_solution(ticket_id: str, provider: str = "openai"):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_summary FROM external_tickets WHERE external_id = %s", (ticket_id,))
            ticket_row = cur.fetchone()
            cur.execute("SELECT array_agg(comment_text) as history FROM ticket_comments WHERE ticket_id = %s", (ticket_id,))
            history_row = cur.fetchone()
    if not ticket_row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    history = "\n".join(history_row["history"] or [])
    root_cause = LLMChain(llm=get_llm(provider), prompt=root_cause_prompt).run(ticket=ticket_row["ticket_summary"], history=history)
    solution = LLMChain(llm=get_llm(provider), prompt=solution_prompt).run(ticket=ticket_row["ticket_summary"], root_cause=root_cause)
    return {"ticket_id": ticket_id, "solution": solution}

@app.post("/llm/summarize_conversation")
def summarize_conversation(conversation_id: str, provider: str = "openai"):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT content FROM chat_logs WHERE conversation_id = %s ORDER BY created_at", (conversation_id,))
            rows = cur.fetchall()
    conversation = "\n".join([row["content"] for row in rows])
    summary = LLMChain(llm=get_llm(provider), prompt=conversation_summary_prompt).run(conversation=conversation)
    return {"conversation_id": conversation_id, "summary": summary}

@app.post("/llm/extract_entities")
def extract_entities(text: str, provider: str = "openai"):
    entities = LLMChain(llm=get_llm(provider), prompt=entity_prompt).run(text=text)
    return {"entities": entities}

@app.post("/llm/followup_actions")
def followup_actions(ticket_id: str, conversation_id: str, provider: str = "openai"):
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_summary FROM external_tickets WHERE external_id = %s", (ticket_id,))
            ticket_row = cur.fetchone()
            cur.execute("SELECT content FROM chat_logs WHERE conversation_id = %s ORDER BY created_at", (conversation_id,))
            chat_rows = cur.fetchall()
    if not ticket_row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    conversation = "\n".join([row["content"] for row in chat_rows])
    actions = LLMChain(llm=get_llm(provider), prompt=followup_prompt).run(ticket=ticket_row["ticket_summary"], conversation=conversation)
    return {"ticket_id": ticket_id, "conversation_id": conversation_id, "actions": actions}

# Feedback loop endpoint (stub)
@app.post("/llm/feedback_loop")
def llm_feedback_loop(llm_output: str, user_feedback: str):
    feedback_loop(llm_output, user_feedback)
    return {"status": "feedback received"}

# TODO: Implement hybrid reranking, context window optimization, and dynamic prompt engineering in search endpoint as needed

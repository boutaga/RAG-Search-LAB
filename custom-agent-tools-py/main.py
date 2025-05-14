"""
custom-agent-tools-py v0.2

Python/Langchain MCP Server for SD Agent
Implements modular tools for chat logging, ticket management, search, feedback, and problem linking.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="SD-MCP Python Agent",
    version="0.2",
    description="Python/Langchain MCP server for Service Desk Agent"
)

# In-memory storage (to be replaced with database integration)
chat_logs = []
tickets = []
feedbacks = []
problem_links = []

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

# Endpoints

@app.post("/chatlog", response_model=ChatLog)
def add_chat_log(conversation_id: str, role: str, content: str):
    log = ChatLog(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow().isoformat()
    )
    chat_logs.append(log)
    return log

@app.get("/chatlog", response_model=List[ChatLog])
def list_chat_logs():
    return chat_logs

@app.post("/ticket", response_model=Ticket)
def update_ticket(id: str, title: str, status: str = "Open", assignee: str = "Unassigned", note: Optional[str] = None):
    ticket = next((t for t in tickets if t.id == id), None)
    if not ticket:
        ticket = Ticket(id=id, title=title, status=status, assignee=assignee, notes=[])
        tickets.append(ticket)
    else:
        ticket.status = status
        ticket.assignee = assignee
    if note:
        ticket.notes.append(note)
    return ticket

@app.get("/ticket", response_model=List[Ticket])
def list_tickets():
    return tickets

@app.post("/feedback", response_model=Feedback)
def submit_feedback(log_id: str, rating: int, comments: Optional[str] = None):
    fb = Feedback(
        id=str(uuid.uuid4()),
        log_id=log_id,
        rating=rating,
        comments=comments or "",
        created_at=datetime.utcnow().isoformat()
    )
    feedbacks.append(fb)
    return fb

@app.get("/feedback", response_model=List[Feedback])
def list_feedbacks():
    return feedbacks

@app.post("/problem-link", response_model=ProblemLink)
def link_problem(ticket_id: str, problem_id: str, link_type: str = "related"):
    link = ProblemLink(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        problem_id=problem_id,
        link_type=link_type,
        created_at=datetime.utcnow().isoformat()
    )
    problem_links.append(link)
    return link

@app.get("/problem-link", response_model=List[ProblemLink])
def list_problem_links():
    return problem_links

@app.get("/search")
def search(query: str, limit: int = 10):
    results = []
    for log in chat_logs:
        if query.lower() in log.content.lower():
            results.append({"type": "chat_log", "id": log.id, "content": log.content})
            if len(results) >= limit:
                return results
    for ticket in tickets:
        if query.lower() in ticket.title.lower() or any(query.lower() in n.lower() for n in ticket.notes):
            results.append({"type": "ticket", "id": ticket.id, "title": ticket.title})
            if len(results) >= limit:
                return results
    return results

# TODO: Integrate Langchain for advanced RAG, LLM, and hybrid search workflows
# TODO: Add database-backed storage for production use
# TODO: Add email/notification tool integration

# main.py

import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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


# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/agentdb")
VECTOR_DIM = 1536
MCP_SERVERS = os.getenv("MCP_SERVERS", "http://localhost:8001")  # MCP server URL

# Database setup
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# MCP client initialization
mcp_client = MultiServerMCPClient([MCP_SERVERS])
tools = None


@app.on_event("startup")
async def startup():
    global qa_chain, embeddings, tokenizer, splade_model
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

    # Load SPLADE sparse model
    tokenizer, splade_model = initialize_sparse_model_and_tokenizer(MODEL_NAME)

    # Base QA chain (will use in final step)
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0.2),
        chain_type="stuff",
        retriever=dense_retriever  # placeholder
    )


# @app.on_event("startup")
# async def startup():
#     global tools, qa_chain
#     # Initialize MCP toolkit
#     tools = await mcp_client.initialize()

#     # Setup RAG vectorstore with pgvectorscale for performance
#     embeddings = OpenAIEmbeddings()
#     vectorstore = PGVector.from_existing_table(
#         connection_string=DATABASE_URL,
#         embedding_function=embeddings,
#         table_name="kb_chunks",
#         column_name="embedding",
#         dimension=VECTOR_DIM
#     )
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=OpenAI(temperature=0.2),
#         chain_type="stuff",
#         retriever=retriever
#     )

# Pydantic models
class ChatRequest(BaseModel):
    message: str

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
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # Fetch ticket data from Postgres
    result = await db.execute("SELECT ticket_id, title, status_id FROM ticket;")
    tickets = result.fetchall()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    query = req.message

    # 1. Compute embeddings
    dense_q = await run_in_threadpool(get_dense, query)
    sparse_q = await run_in_threadpool(get_sparse, query)

    # 2. Dense retrieval (LangChain)
    dense_docs = await dense_retriever.get_relevant_documents(query)

    # 3. Sparse retrieval via SQL
    sql = text("""
      SELECT chunk_text, sparse_embedding <=> :q AS dist
      FROM kb_chunks
      ORDER BY sparse_embedding <=> :q
      LIMIT :k
    """)
    rows = await db.execute(sql.bindparams(q=sparse_q, k=TOP_K))
    sparse_docs = [r.chunk_text for r in rows.fetchall()]

    # 4. Merge & rerank by weighted distance
    merged = {}
    for doc, score in zip(dense_docs, [d.score for d in dense_docs]):
        merged[doc.page_content] = {"dense": score, "sparse": float("inf")}
    for text, dist in zip(sparse_docs, [r.dist for r in rows.fetchall()]):
        if text in merged:
            merged[text]["sparse"] = dist
        else:
            merged[text] = {"dense": float("inf"), "sparse": dist}

    # Weighted combine
    combined = sorted(
        merged.items(),
        key=lambda x: DENSE_WEIGHT * x[1]["dense"] + SPARSE_WEIGHT * x[1]["sparse"]
    )[:TOP_K]
    context = "\n\n".join(f"{t}" for t,_ in combined)

    # 5. Ask LLM with fused context
    answer = qa_chain.run({"query": query, "context": context})

    # (Logging to chat_logs omitted for brevity)

    return {"answer": answer}



# @app.post("/api/chat")
# async def chat_endpoint(req: ChatRequest, db: AsyncSession = Depends(get_db)):
#     # Log user prompt to DB
#     await db.execute(
#         "INSERT INTO chat_logs (conversation_id, role, content, model_name, prompt_tokens, total_tokens) "
#         "VALUES ($1, 'user', $2, 'openai', 0, 0);",
#         (uuid.uuid4(), req.message)
#     )
#     await db.commit()

#     # Run the RAG QA chain
#     resp = await qa_chain.acall({"query": req.message})
#     answer = resp["result"]

#     # Log agent response
#     await db.execute(
#         "INSERT INTO chat_logs (conversation_id, role, content, model_name, response_tokens, total_tokens) "
#         "VALUES ($1, 'agent', $2, 'openai', 0, 0);",
#         (uuid.uuid4(), answer)
#     )
#     await db.commit()

#     return {"answer": answer}

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

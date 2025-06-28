#!/usr/bin/env python3
"""Question answering using LangChain and PostgreSQL.

This script connects to the Wikipedia database via LangChain's
``SQLDatabase`` utility and builds a ``RetrievalQA`` chain with a
``PGVector`` vector store. It demonstrates a modular RAG setup
with separate embedding, retrieval and prompting components.
"""
from __future__ import annotations
import os

from langchain.chains import RetrievalQA
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import PGVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

MODEL_EMBED = "text-embedding-3-small"
MODEL_CHAT = "gpt-4o"
TOP_K = 5


def main() -> None:
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/wikipedia")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY environment variable not set")

    question = input("Enter your question: ").strip()
    if not question:
        print("No question provided")
        return

    # LangChain components
    sql_db = SQLDatabase.from_uri(db_url)
    try:
        table_info = sql_db.get_table_info(["articles"])
        print("Using table schema:\n", table_info)
    except Exception as exc:  # pragma: no cover - informational
        print("Could not retrieve table info:", exc)

    embeddings = OpenAIEmbeddings(model=MODEL_EMBED, api_key=api_key)
    vectorstore = PGVector(
        connection_string=db_url,
        embedding_function=embeddings,
        collection_name="articles",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    llm = ChatOpenAI(model=MODEL_CHAT, temperature=0.2, openai_api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    answer = qa_chain.run(question)
    print("\nAnswer:", answer)


if __name__ == "__main__":
    main()

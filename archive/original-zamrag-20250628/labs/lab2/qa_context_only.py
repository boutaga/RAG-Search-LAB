#!/usr/bin/env python3
"""Answer questions using only context retrieved from PostgreSQL."""

from __future__ import annotations
import os
import json
import psycopg2
import openai

MODEL_EMBED = "text-embedding-3-small"
MODEL_CHAT = "gpt-4o"
TOP_N = 5

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/wikipedia")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def get_embedding(text: str, model: str = MODEL_EMBED) -> list[float]:
    resp = openai.embeddings.create(input=text, model=model)
    return resp.data[0].embedding


def query_similar_items(query_embedding: list[float], limit: int = TOP_N):
    vec_str = json.dumps(query_embedding)
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    sql = """
    SELECT title, content, content_vector <-> %s::vector AS distance
    FROM public.articles
    WHERE content_vector IS NOT NULL
    ORDER BY content_vector <-> %s::vector
    LIMIT %s;
    """
    cur.execute(sql, (vec_str, vec_str, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


def generate_answer(query: str, context: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. You must answer the following question "
                "using only the context provided from the local database. Do not include "
                "any external information. If the answer is not present in the context, "
                "respond with 'No relevant information is available.'"
            ),
        },
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    resp = openai.chat.completions.create(
        model=MODEL_CHAT,
        messages=messages,
        max_tokens=150,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def main():
    query = input("Enter your question: ")
    qvec = get_embedding(query)
    items = query_similar_items(qvec)
    if not items:
        print("No relevant documents were found.")
        return
    context = ""
    for title, content, _ in items:
        context += f"Title: {title}\nContent: {content}\n\n"
    answer = generate_answer(query, context)
    print("\nAnswer:", answer)


if __name__ == "__main__":
    main()

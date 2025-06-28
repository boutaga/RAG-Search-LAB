#!/usr/bin/env python3
"""Simple similarity search using L2 (Euclidean) distance.

Embeds the query and executes SQL directly, ranking articles by title
and content similarity with pgvector's ``<->`` operator.
"""

from __future__ import annotations
import argparse
import os
import sys
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from tabulate import tabulate

MODEL = "text-embedding-3-small"
TOP_N = 5

def embed_query(text: str, client: OpenAI) -> List[float]:
    resp = client.embeddings.create(model=MODEL, input=[text])
    return resp.data[0].embedding


def pretty(rows, header: str):
    table = [[r["id"], r["title"], f"{r['distance']:.4f}"] for r in rows]
    print(f"\n=== Top {len(rows)} {header} ===")
    print(tabulate(table, headers=["id", "title", "distance"], tablefmt="github"))


def main():
    parser = argparse.ArgumentParser(description="Simple L2 similarity search")
    parser.add_argument("query", nargs="*", help="search terms")
    parser.add_argument("--title-like", dest="title_like")
    parser.add_argument("--page", type=int, default=1)
    args = parser.parse_args()

    query_text = " ".join(args.query).strip() or input("Enter search query: ").strip()
    if not query_text:
        print("No query provided")
        return

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    qvec = embed_query(query_text, client)

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/wikipedia")
    with psycopg2.connect(db_url, cursor_factory=RealDictCursor) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            offset = (args.page - 1) * TOP_N
            title_clause = ""
            params = [qvec]
            if args.title_like:
                title_clause = " AND title ILIKE %s"
                params.append(f"%{args.title_like}%")
            params.extend([qvec, TOP_N, offset])
            cur.execute(
                f"""
                SELECT id, title, url, title_vector <-> %s::vector AS distance
                FROM public.articles
                WHERE title_vector IS NOT NULL{title_clause}
                ORDER BY title_vector <-> %s::vector
                LIMIT %s OFFSET %s;
                """,
                params,
            )
            title_rows = cur.fetchall()

            params = [qvec]
            if args.title_like:
                params.append(f"%{args.title_like}%")
            params.extend([qvec, TOP_N, offset])
            cur.execute(
                f"""
                SELECT id, title, url, content_vector <-> %s::vector AS distance
                FROM public.articles
                WHERE content_vector IS NOT NULL{title_clause}
                ORDER BY content_vector <-> %s::vector
                LIMIT %s OFFSET %s;
                """,
                params,
            )
            content_rows = cur.fetchall()

    pretty(title_rows, "by title")
    pretty(content_rows, "by content")


if __name__ == "__main__":
    main()

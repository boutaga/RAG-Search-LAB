#!/usr/bin/env python3
"""Interactive similarity search across article titles and contents.

Embeds a query using OpenAI and prints the closest matches from the
``public.articles`` table by title and by content.
"""

from __future__ import annotations

import argparse
import os
import sys
import hashlib
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


def search(
    query: List[float],
    conn,
    title_like: str | None = None,
    page: int = 1,
) -> tuple[list[dict], list[dict]]:
    offset = (page - 1) * TOP_N
    title_clause = ""
    params_title = [query]
    if title_like:
        title_clause = " AND title ILIKE %s"
        params_title.append(f"%{title_like}%")
    params_title.extend([query, TOP_N, offset])

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, title, url, title_vector <-> %s::vector AS distance
            FROM public.articles
            WHERE title_vector IS NOT NULL{title_clause}
            ORDER BY title_vector <-> %s::vector
            LIMIT %s OFFSET %s;
            """,
            params_title,
        )
        title_rows = cur.fetchall()

        params_content = [query]
        if title_like:
            params_content.append(f"%{title_like}%")
        params_content.extend([query, TOP_N, offset])
        cur.execute(
            f"""
            SELECT id, title, url, content_vector <-> %s::vector AS distance
            FROM public.articles
            WHERE content_vector IS NOT NULL{title_clause}
            ORDER BY content_vector <-> %s::vector
            LIMIT %s OFFSET %s;
            """,
            params_content,
        )
        content_rows = cur.fetchall()

    return title_rows, content_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Wikipedia articles")
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
    qhash = hashlib.md5(query_text.encode("utf-8")).hexdigest()[:8]

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/wikipedia")
    with psycopg2.connect(db_url, cursor_factory=RealDictCursor) as conn:
        register_vector(conn)
        title_rows, content_rows = search(qvec, conn, args.title_like, args.page)

        # Log the query to search_metrics if table exists
        try:
            top_dist = content_rows[0]["distance"] if content_rows else None
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.search_metrics(query_id, query_time, mode, top_score, token_usage) VALUES (%s, NOW(), %s, %s, %s);",
                    (qhash, "cli_l2", float(top_dist) if top_dist is not None else None, None),
                )
            conn.commit()
        except Exception:
            pass

    pretty(title_rows, "by title")
    pretty(content_rows, "by content")


if __name__ == "__main__":
    main()

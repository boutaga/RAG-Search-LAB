#!/usr/bin/env python3
"""
Embed documents with BOTH dense (OpenAI) and sparse (local) vectors and write them
back to PostgreSQL.  Designed to live next to `create_emb_sparse.py` in the
RAG‑Search‑LAB repo so that you have *one* ingestion entry point that populates
`dense_embedding` **and** `sparse_embedding` columns.

Assumptions
-----------
* The target table already contains the two pgvector columns **dense_embedding**
  (dimension 1536) and **sparse_embedding** (dimension N given by the sparse
  encoder – default 768 for MiniLM‑L6).
* You already ran the accompanying DDL in `database_AI_agent/schema.sql` that
  creates those columns and adds `CREATE INDEX … USING hnsw` on each.
* `create_emb_sparse.py` exposes a *callable* named **SparseEmbedder** with an
  `.embed(texts: List[str]) -> List[np.ndarray]` method.  If you followed the
  repo’s original script this will be true; otherwise just adapt the import
  block below.
* Environment variables:
    - `OPENAI_API_KEY` – dense embeddings
    - `DATABASE_URL`  – PostgreSQL URI (e.g. `postgresql://user:pass@host/db`)
    - Optional `OPENAI_MODEL` – override dense model (default
      `text-embedding-ada-002`)
    - Optional `BATCH_SIZE` – override batch size (default 32)

Install deps
------------
```bash
pip install psycopg2-binary pgvector openai sentence-transformers
```

Run it
------
```bash
export OPENAI_API_KEY="sk‑…"
export DATABASE_URL="postgresql://postgres@localhost/mydb"
python embed_dense_sparse.py --table documents --id id --text body
```
"""

import os
import sys
import argparse
import time
from typing import List, Tuple

import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI

try:
    # Local sparse embedder that ships with the repo
    from create_emb_sparse import SparseEmbedder  # type: ignore
except ImportError as err:
    raise SystemExit(
        "✖ Cannot import SparseEmbedder from create_emb_sparse.py. "
        "Make sure it is on PYTHONPATH."
    ) from err

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DENSE_MODEL = os.getenv("OPENAI_MODEL", "text-embedding-ada-002")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
MAX_RETRIES = 5
RETRY_BASE_DELAY = 0.25  # seconds

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
embedder = SparseEmbedder()  # uses MiniLM‑L6 by default

# ---------------------------------------------------------------------------
# Dense embeddings with exponential‑backoff retry
# ---------------------------------------------------------------------------

def get_dense_embeddings(texts: List[str]) -> List[List[float]]:
    """Call OpenAI in *one* batch and return the embeddings list."""
    delay = RETRY_BASE_DELAY
    for _ in range(MAX_RETRIES):
        try:
            resp = client.embeddings.create(input=texts, model=DENSE_MODEL)
            return [item.embedding for item in resp.data]
        except Exception as exc:  # pragma: no cover – OpenAI specific
            err = str(exc)
            if "429" in err or "insufficient_quota" in err:
                print(f"⚠ Rate–limit: sleeping {delay:.2f}s for batch size {len(texts)}")
                time.sleep(delay)
                delay *= 2
            else:
                raise
    raise RuntimeError("Exceeded max retries for dense embedding batch")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def batched(iterable: List[Tuple], size: int):
    """Yield *size*‑chunks from *iterable*."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def update_embeddings(
    conn: psycopg2.extensions.connection,
    table: str,
    id_col: str,
    text_col: str,
):
    """Embed *all* rows from *table* and update dense & sparse columns."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT {id_col}, {text_col} FROM {table};")
        rows = cur.fetchall()

    if not rows:
        print(f"ℹ Table {table} is empty – nothing to do")
        return

    total = len(rows)
    print(f"Embedding {total} rows from {table} … (batch {BATCH_SIZE})")

    for batch in batched(rows, BATCH_SIZE):
        batch_ids = [row[0] for row in batch]
        batch_texts = [row[1] or "" for row in batch]

        dense_vecs = get_dense_embeddings(batch_texts)
        sparse_vecs = embedder.embed(batch_texts)

        with conn.cursor() as cur:
            for rid, dvec, svec in zip(batch_ids, dense_vecs, sparse_vecs):
                cur.execute(
                    f"""
                    UPDATE {table}
                       SET dense_embedding  = %s::vector,
                           sparse_embedding = %s::vector
                     WHERE {id_col} = %s;""",
                    (dvec, svec.tolist(), rid),
                )
        conn.commit()
        print(f"✔ Updated IDs {batch_ids[0]}…{batch_ids[-1]}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Create dense + sparse embeddings")
    parser.add_argument("--table", required=True, help="Target DB table")
    parser.add_argument("--id", dest="id_col", default="id", help="Primary‑key column")
    parser.add_argument("--text", dest="text_col", default="content", help="Text column")

    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.exit("✖ DATABASE_URL not set")

    with psycopg2.connect(db_url) as conn:
        register_vector(conn)
        update_embeddings(conn, args.table, args.id_col, args.text_col)


if __name__ == "__main__":
    main()

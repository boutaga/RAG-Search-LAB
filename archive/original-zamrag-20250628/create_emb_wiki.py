#!/usr/bin/env python3
"""
Update title and content embedding vectors for the `public.articles` table **with live percentage progress**.

Key additions
-------------
* **Percentage progress logging** for both title and content phases.
    * Titles – `processed_rows / total_title_rows`.
    * Contents – `processed_chunks / total_content_chunks` (each 800‑token
      chunk counts toward progress).
* No behavioural change to the actual embedding logic.

Dependencies and environment remain the same.
"""

from __future__ import annotations

import os
import time
import logging
import statistics
from collections import defaultdict
from typing import Iterable, List, Dict, Tuple, Set

import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from openai import OpenAI, RateLimitError, APIConnectionError, APIError
import tiktoken

# ----------------------------------------------------------------------------
# Config ---------------------------------------------------------------------
# ----------------------------------------------------------------------------
MODEL = "text-embedding-3-small"  # 1 536‑dim, 8 191‑token cap
BATCH_TOKEN_LIMIT = 7_500         # leave headroom below 8 191
BATCH_ITEM_LIMIT = 2_000          # < 2 048 items per call
CHUNK_TOKEN_SIZE = 800            # length of each content chunk
CHUNK_TOKEN_OVERLAP = 100         # overlap between successive chunks
MAX_RETRIES = 6
RETRY_BACKOFF = 0.5               # seconds; doubles each retry
PROGRESS_EVERY = 1.0              # log at least every X percent

# ----------------------------------------------------------------------------
# Init -----------------------------------------------------------------------
# ----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
enc = tiktoken.encoding_for_model(MODEL)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------------------------------------------------------
# Helpers --------------------------------------------------------------------
# ----------------------------------------------------------------------------

def num_tokens(text: str) -> int:
    return len(enc.encode(text))

def chunk_text(text: str) -> List[str]:
    toks = enc.encode(text)
    step = CHUNK_TOKEN_SIZE - CHUNK_TOKEN_OVERLAP
    return [enc.decode(toks[i : i + CHUNK_TOKEN_SIZE]) for i in range(0, len(toks), step)]

def iter_batches(rows: Iterable[Tuple[int, str]]) -> Iterable[Tuple[List[int], List[str]]]:
    ids, texts, tok_sum = [], [], 0

    def flush():
        nonlocal ids, texts, tok_sum
        if ids:
            yield ids, texts
            ids, texts, tok_sum = [], [], 0

    for rid, txt in rows:
        toks = num_tokens(txt)
        if toks > BATCH_TOKEN_LIMIT:
            txt = enc.decode(enc.encode(txt)[:BATCH_TOKEN_LIMIT])
            toks = BATCH_TOKEN_LIMIT
        if ids and (tok_sum + toks > BATCH_TOKEN_LIMIT or len(ids) >= BATCH_ITEM_LIMIT):
            yield from flush()
        ids.append(rid)
        texts.append(txt)
        tok_sum += toks
    yield from flush()


def get_embeddings(texts: List[str]) -> List[List[float]]:
    delay = RETRY_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.embeddings.create(model=MODEL, input=texts)
            return [d.embedding for d in resp.data]
        except (RateLimitError, APIConnectionError, APIError) as e:
            logging.warning(
                "Transient API error (%s) – retry %d/%d in %.1fs",
                type(e).__name__, attempt, MAX_RETRIES, delay,
            )
            time.sleep(delay)
            delay *= 2
        except Exception:
            raise  # non‑retryable
    raise RuntimeError("Exceeded maximum retries to OpenAI")


def avg_vec(vectors: List[List[float]]) -> List[float]:
    return [float(statistics.fmean(col)) for col in zip(*vectors)]

# ----------------------------------------------------------------------------
# Embedding routines ---------------------------------------------------------
# ----------------------------------------------------------------------------

def embed_titles(cur, table: str):
    cur.execute(f"SELECT id, title FROM {table};")
    rows = [(i, t) for i, t in cur.fetchall() if isinstance(t, str) and t.strip()]
    total = len(rows)
    logging.info("%d valid titles found", total)
    if not rows:
        return

    processed = 0
    next_log_pct = PROGRESS_EVERY

    for ids, texts in iter_batches(rows):
        vecs = get_embeddings(texts)
        processed += len(ids)
        pct = processed * 100.0 / total
        if pct >= next_log_pct or processed == total:
            logging.info("Title progress: %.1f%% (%d/%d)", pct, processed, total)
            next_log_pct += PROGRESS_EVERY

        data = list(zip(ids, vecs))
        stmt = (
            f"UPDATE {table} AS t SET title_vector = v.vec "
            f"FROM (VALUES %s) AS v(id, vec) WHERE t.id = v.id;"
        )
        execute_values(cur, stmt, data, template="(%s::int,%s::vector)")

    logging.info("Title vectors updated.")


def embed_contents(cur, table: str):
    cur.execute(f"SELECT id, content FROM {table};")
    rows = [(i, c) for i, c in cur.fetchall() if isinstance(c, str) and c.strip()]
    logging.info("%d valid contents found", len(rows))
    if not rows:
        return

    # Pre‑compute total chunks for progress estimation (extra CPU but cheap)
    total_chunks = sum(len(chunk_text(txt)) for _, txt in rows)
    processed_chunks = 0
    next_log_pct = PROGRESS_EVERY

    article_vecs: Dict[int, List[List[float]]] = defaultdict(list)

    def chunked():
        for rid, txt in rows:
            for ch in chunk_text(txt):
                yield rid, ch

    for ids, texts in iter_batches(chunked()):
        vecs = get_embeddings(texts)
        processed_chunks += len(texts)
        pct = processed_chunks * 100.0 / total_chunks
        if pct >= next_log_pct or processed_chunks == total_chunks:
            logging.info("Content progress: %.1f%% (%d/%d chunks)", pct, processed_chunks, total_chunks)
            next_log_pct += PROGRESS_EVERY

        for rid, vec in zip(ids, vecs):
            article_vecs[rid].append(vec)
        if len(article_vecs) >= 2_000:
            _flush(cur, table, article_vecs)
            article_vecs.clear()

    _flush(cur, table, article_vecs)
    logging.info("Content vectors updated.")


def _flush(cur, table: str, cache: Dict[int, List[List[float]]]):
    if not cache:
        return
    data = [(rid, avg_vec(vecs)) for rid, vecs in cache.items()]
    stmt = (
        f"UPDATE {table} AS t SET content_vector = v.vec "
        f"FROM (VALUES %s) AS v(id, vec) WHERE t.id = v.id;"
    )
    execute_values(cur, stmt, data, template="(%s::int,%s::vector)")

# ----------------------------------------------------------------------------
# Main -----------------------------------------------------------------------
# ----------------------------------------------------------------------------

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/wikipedia")
    with psycopg2.connect(db_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            logging.info("Embedding titles …")
            embed_titles(cur, "public.articles")
            conn.commit()

            logging.info("Embedding contents …")
            embed_contents(cur, "public.articles")
            conn.commit()

    logging.info("✓ All embeddings updated")

if __name__ == "__main__":
    main()
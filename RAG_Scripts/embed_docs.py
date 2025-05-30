#!/usr/bin/env python3
"""RAG-Search-LAB - Document bootstrap

Walk a folder (or individual file), split every document into chunks, generate
both **dense** (OpenAI) and **sparse** (SPLADE) vectors, and upsert them into
the `documents` table of *documents_db*.

Usage
-----
```bash
python embed_documents.py ./data/sops/*.pdf                             \
       --db $POSTGRES_URL_DOCUMENTS                                      \
       --table documents                                                 \
       --batch 32                                                       
```
If no arguments are given, the script falls back to environment variables:

* `DATABASE_URL` - Postgres URI (falls back to POSTGRES_URL_DOCUMENTS)
* `OPENAI_API_KEY` - used for dense embeddings
* `OPENAI_MODEL` - dense model name (default text‑embedding‑ada‑002)
* `BATCH_SIZE`    - batch size (default 32)

Schema (auto-created if missing)
--------------------------------
```sql
CREATE TABLE documents (
    id                bigserial PRIMARY KEY,
    path              text UNIQUE,
    chunk_index       integer,
    content           text,
    dense_embedding   vector(1536),
    sparse_embedding  vector(768)
);
CREATE INDEX ON documents USING hnsw (dense_embedding vector_cosine_ops);
CREATE INDEX ON documents USING hnsw (sparse_embedding vector_ip_ops);
```
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from itertools import islice
from pathlib import Path
from typing import Iterable, List

import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI

try:
    # Local helper from create_emb_sparse.py
    from create_emb_sparse import SparseEmbedder  # type: ignore
except ImportError as exc:  # pragma: no cover
    print("✖ Could not import SparseEmbedder – ensure create_emb_sparse.py is on PYTHONPATH")
    raise exc

# Third‑party: install langchain if you want fancy chunking, else we roll simple.
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
except ImportError:
    RecursiveCharacterTextSplitter = None  # type: ignore

########################################
# Config from env with sane fallbacks
########################################
DENSE_MODEL = os.getenv("OPENAI_MODEL", "text-embedding-ada-002")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
SPARSE_MODEL = os.getenv("SPARSE_MODEL", "splade_en_semble_distil")

#########################
# Helper: batch an iterable
#########################

def batched(it: Iterable, size: int):
    """Yield lists of length *size* until the iterable is exhausted."""
    it = iter(it)
    while (chunk := list(islice(it, size))):
        yield chunk

###########################################
# Document loading & simple text splitter
###########################################

def load_documents(paths: List[Path]) -> List[tuple[str, str]]:
    """Return list of (doc_id, text) where *doc_id* is path + ::chunk_index."""
    docs: List[tuple[str, str]] = []
    splitter = None
    if RecursiveCharacterTextSplitter:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for p in paths:
        if p.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader  # lazy import; optional
            except ImportError:
                sys.exit("Install pypdf to read PDFs or convert them beforehand")
            reader = PdfReader(str(p))
            raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            raw_text = p.read_text(encoding="utf-8", errors="ignore")

        # choose splitting strategy
        if splitter:
            chunks = [c.page_content for c in splitter.create_documents([raw_text])]
        else:
            # naive fixed‑width split
            chunks = [raw_text[i : i + 1000] for i in range(0, len(raw_text), 1000)]

        for idx, chunk in enumerate(chunks):
            docs.append((f"{p}::${idx}", chunk))
    return docs

##########################################
# Embedding utilities
##########################################
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
if client.api_key is None:
    sys.exit("✖ OPENAI_API_KEY not set")

sparse = SparseEmbedder(model_name=SPARSE_MODEL)  # splade mini by default


def dense_embed(texts: List[str]) -> List[List[float]]:
    delay = 0.3
    for attempt in range(5):
        try:
            resp = client.embeddings.create(input=texts, model=DENSE_MODEL)
            return [item.embedding for item in resp.data]
        except Exception as err:  # pragma: no cover
            if "429" in str(err) or "insufficient_quota" in str(err):
                print(f"Rate‑limit retry {attempt+1}: sleeping {delay}s …")
                time.sleep(delay)
                delay *= 2
            else:
                raise
    raise RuntimeError("Failed to get dense embeddings after retries")

########################################
# Database insertion / upsert
########################################

def ensure_schema(cur, table: str):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id               bigserial PRIMARY KEY,
            path             text UNIQUE,
            chunk_index      integer,
            content          text,
            dense_embedding  vector(1536),
            sparse_embedding vector(768)
        );
        """
    )
    # Create indices if they do not exist
    cur.execute(
        f"""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE schemaname = current_schema()
                                      AND tablename = '{table}'
                                      AND indexname = '{table}_dense_hnsw') THEN
                CREATE INDEX {table}_dense_hnsw ON {table}
                    USING hnsw (dense_embedding vector_cosine_ops);
            END IF;
        END $$;
        """
    )
    cur.execute(
        f"""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE schemaname = current_schema()
                                      AND tablename = '{table}'
                                      AND indexname = '{table}_sparse_hnsw') THEN
                CREATE INDEX {table}_sparse_hnsw ON {table}
                    USING hnsw (sparse_embedding vector_ip_ops);
            END IF;
        END $$;
        """
    )


def upsert_batch(cur, table: str, records: List[tuple]):
    cur.executemany(
        f"""
        INSERT INTO {table} (path, chunk_index, content, dense_embedding, sparse_embedding)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (path) DO UPDATE SET
            content          = EXCLUDED.content,
            dense_embedding  = EXCLUDED.dense_embedding,
            sparse_embedding = EXCLUDED.sparse_embedding;
        """,
        records,
    )

########################################
# Main logic
########################################

def main():
    parser = argparse.ArgumentParser(description="Embed a folder of documents")
    parser.add_argument("inputs", nargs="+", help="Files or directories to ingest")
    parser.add_argument("--db", default=os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL_DOCUMENTS")), help="Postgres URI")
    parser.add_argument("--table", default="documents", help="Target table name")
    parser.add_argument("--batch", type=int, default=BATCH_SIZE, help="Batch size for embedding calls")

    args = parser.parse_args()

    uri = args.db
    if not uri:
        sys.exit("✖ Provide --db or set DATABASE_URL / POSTGRES_URL_DOCUMENTS")

    # Gather all file paths
    paths: List[Path] = []
    for input_path in args.inputs:
        p = Path(input_path)
        if p.is_dir():
            paths.extend(sorted(p.rglob("*.*")))
        elif p.exists():
            paths.append(p)
        else:
            print(f"⚠ Skipping non‑existent path {p}")
    if not paths:
        sys.exit("✖ No files found to embed")

    docs = load_documents(paths)
    print(f"Loaded {len(docs)} chunks from {len(paths)} files")

    with psycopg2.connect(uri) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            ensure_schema(cur, args.table)
            conn.commit()

        # Process in batches
        for chunk in batched(docs, args.batch):
            doc_ids, texts = zip(*chunk)
            dense_vecs = dense_embed(list(texts))
            sparse_vecs = sparse.embed(list(texts))

            records = []
            for full_id, text, dvec, svec in zip(doc_ids, texts, dense_vecs, sparse_vecs):
                path, _, idx = full_id.partition("::$")
                records.append((path, int(idx) if idx else 0, text, dvec, svec.tolist()))

            with conn.cursor() as cur:
                upsert_batch(cur, args.table, records)
            conn.commit()
            print(f"✔ Upserted {len(records)} chunks (last: {records[-1][0]})")
    print("✓ Done – embeddings ready.")


if __name__ == "__main__":
    main()

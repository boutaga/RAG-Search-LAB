-- Table to log search metrics for RAG experiments
CREATE TABLE public.search_metrics (
    log_id serial PRIMARY KEY,
    query_id text,
    description text,
    query_time timestamptz,
    mode text,
    top_score real,
    token_usage integer,
    precision real DEFAULT 0,
    embedding_ms real,
    db_ms real,
    llm_ms real,
    total_ms real
);

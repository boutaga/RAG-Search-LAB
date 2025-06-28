-- Table for storing human readable descriptions of metrics
CREATE TABLE IF NOT EXISTS public.metric_descriptions (
    metric_name text PRIMARY KEY,
    description text NOT NULL
);

INSERT INTO public.metric_descriptions(metric_name, description) VALUES
    ('query_id', 'Short hash representing the query text'),
    ('description', 'First 20 characters of the query'),
    ('query_time', 'Timestamp when the query was executed'),
    ('mode', 'Search mode used for this query'),
    ('top_score', 'Best similarity distance or score'),
    ('token_usage', 'Total tokens used in the LLM call'),
    ('precision', 'Proportion of relevant results'),
    ('embedding_ms', 'Milliseconds spent generating the embedding'),
    ('db_ms', 'Milliseconds spent executing the database search'),
    ('llm_ms', 'Milliseconds spent generating the LLM answer'),
    ('total_ms', 'Total execution time in milliseconds')
    ON CONFLICT DO NOTHING;

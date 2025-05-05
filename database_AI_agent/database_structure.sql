-- 1.1 Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1.2 Documents metadata (optional: full documents)
CREATE TABLE documents (
  document_id   BIGSERIAL PRIMARY KEY,
  title         TEXT NOT NULL,
  source_path   TEXT NOT NULL,       -- URL or filesystem path
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

-- 1.3 Knowledge base chunks with embeddings
CREATE TABLE kb_chunks (
  chunk_id      BIGSERIAL PRIMARY KEY,
  document_id   BIGINT NOT NULL REFERENCES documents(document_id),
  chunk_text    TEXT NOT NULL,
  embedding     VECTOR(1536) NOT NULL,  -- dimension per your embedding model
  metadata      JSONB,                  -- e.g., page number, section
  inserted_at   TIMESTAMPTZ DEFAULT now()
);
-- Enable pgvector for vector data types
CREATE EXTENSION IF NOT EXISTS vector;  
-- Enable vectorscale (includes the DiskANN index type)
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;


-- 1.2 Add sparse_embedding alongside existing dense embeddings
ALTER TABLE kb_chunks
  ADD COLUMN sparse_embedding vector(32768) SPARSE;  -- vocabulary‐sized sparse embeddings :contentReference[oaicite:5]{index=5}

-- Create a GIN index on the metadata JSONB column for fast filtering
CREATE INDEX kb_chunks_metadata_gin_idx
  ON kb_chunks
  USING GIN (metadata);

-- Create a DiskANN index on the dense embedding column for ANN search
CREATE INDEX kb_chunks_embedding_diskann_idx
  ON kb_chunks
  USING diskann (embedding vector_l2_ops);

-- Create a combined DiskANN index that also filters by labels
CREATE INDEX documents_diskann_labels_idx
  ON documents
  USING diskann (embedding vector_cosine_ops, labels);



-- 2.1 Conversation sessions
CREATE TABLE conversations (
  conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         BIGINT,               -- optional FK to a users table
  started_at      TIMESTAMPTZ DEFAULT now(),
  ended_at        TIMESTAMPTZ
);

-- 2.2 Prompt/response entries
CREATE TABLE chat_logs (
  log_id           BIGSERIAL PRIMARY KEY,
  conversation_id  UUID NOT NULL REFERENCES conversations(conversation_id),
  role             VARCHAR(10) NOT NULL,      -- 'user' or 'agent'
  content          TEXT NOT NULL,             -- prompt or response
  model_name       TEXT NOT NULL,
  prompt_tokens    INT NOT NULL,
  response_tokens  INT,
  total_tokens     INT NOT NULL,
  created_at       TIMESTAMPTZ DEFAULT now()
);


CREATE TABLE retrieval_history (
  retrieval_id     BIGSERIAL PRIMARY KEY,
  log_id           BIGINT NOT NULL REFERENCES chat_logs(log_id),
  chunk_id         BIGINT NOT NULL REFERENCES kb_chunks(chunk_id),
  similarity_score FLOAT NOT NULL,
  retrieved_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agent_parameters (
  param_id       BIGSERIAL PRIMARY KEY,
  name           TEXT NOT NULL,            -- e.g., 'temperature'
  value          TEXT NOT NULL,            -- stored as text or JSON
  description    TEXT,
  effective_from TIMESTAMPTZ DEFAULT now(),
  effective_to   TIMESTAMPTZ
);

CREATE UNIQUE INDEX ON agent_parameters (name, effective_from);


-- 5.1 User feedback on individual messages
CREATE TABLE feedback (
  feedback_id   BIGSERIAL PRIMARY KEY,
  log_id        BIGINT NOT NULL REFERENCES chat_logs(log_id),
  rating        SMALLINT CHECK (rating BETWEEN 1 AND 5),
  comments      TEXT,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- 5.2 Escalation rules definition
CREATE TABLE escalation_rules (
  rule_id       BIGSERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  condition     JSONB NOT NULL,             -- e.g., threshold on sentiment or keywords
  priority      INT NOT NULL,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- 5.3 Records of triggered escalations
CREATE TABLE escalations (
  escalation_id BIGSERIAL PRIMARY KEY,
  log_id        BIGINT NOT NULL REFERENCES chat_logs(log_id),
  rule_id       BIGINT NOT NULL REFERENCES escalation_rules(rule_id),
  triggered_at  TIMESTAMPTZ DEFAULT now(),
  notes         TEXT
);


CREATE TABLE agent_metrics (
  metric_id     BIGSERIAL PRIMARY KEY,
  metric_name   TEXT NOT NULL,               -- e.g., 'avg_response_time_ms'
  metric_value  DOUBLE PRECISION NOT NULL,
  measured_at   TIMESTAMPTZ DEFAULT now()
);


-- Connection to external ticketing system
CREATE TABLE external_tickets (
  ticket_id        BIGSERIAL PRIMARY KEY,
  external_id      VARCHAR(100) NOT NULL,
  system_source    TEXT NOT NULL,          -- name of ticketing system
  ticket_summary   TEXT NOT NULL,
  current_status   TEXT NOT NULL,
  resolution       TEXT,                   -- resolution from ticket system
  created_at       TIMESTAMPTZ NOT NULL,
  resolved_at      TIMESTAMPTZ,
  UNIQUE(external_id, system_source)
);

-- Link conversations to tickets
CREATE TABLE conversation_ticket_links (
  link_id         BIGSERIAL PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(conversation_id),
  ticket_id       BIGINT NOT NULL REFERENCES external_tickets(ticket_id),
  created_at      TIMESTAMPTZ DEFAULT now()
);


-- Track identified problems
CREATE TABLE problems (
  problem_id      BIGSERIAL PRIMARY KEY,
  title           TEXT NOT NULL,
  description     TEXT NOT NULL,
  category        TEXT,
  severity        SMALLINT CHECK (severity BETWEEN 1 AND 5),
  status          TEXT NOT NULL,           -- 'identified', 'in_progress', 'resolved'
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Store validated solutions
CREATE TABLE solutions (
  solution_id     BIGSERIAL PRIMARY KEY,
  problem_id      BIGINT REFERENCES problems(problem_id),
  title           TEXT NOT NULL,
  description     TEXT NOT NULL,
  implementation  TEXT,                   -- implementation steps
  effectiveness   SMALLINT CHECK (effectiveness BETWEEN 1 AND 5),
  is_validated    BOOLEAN DEFAULT false,
  validator_id    BIGINT,                 -- Who validated this solution
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Link tickets to problems
CREATE TABLE ticket_problem_links (
  link_id         BIGSERIAL PRIMARY KEY,
  ticket_id       BIGINT NOT NULL REFERENCES external_tickets(ticket_id),
  problem_id      BIGINT NOT NULL REFERENCES problems(problem_id),
  link_type       TEXT DEFAULT 'related', -- 'related', 'root_cause', 'duplicate'
  created_at      TIMESTAMPTZ DEFAULT now()
);


-- Link documents/KB chunks to problems and solutions
CREATE TABLE knowledge_links (
  link_id         BIGSERIAL PRIMARY KEY,
  chunk_id        BIGINT REFERENCES kb_chunks(chunk_id),
  document_id     BIGINT REFERENCES documents(document_id),
  problem_id      BIGINT REFERENCES problems(problem_id),
  solution_id     BIGINT REFERENCES solutions(solution_id),
  relevance_score FLOAT CHECK (relevance_score BETWEEN 0 AND 1),
  link_type       TEXT NOT NULL,          -- 'sop', 'best_practice', 'reference'
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- Track which solutions were applied to which conversations
CREATE TABLE applied_solutions (
  applied_id      BIGSERIAL PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(conversation_id),
  solution_id     BIGINT NOT NULL REFERENCES solutions(solution_id),
  success_rating  SMALLINT CHECK (success_rating BETWEEN 1 AND 5),
  notes           TEXT,
  applied_at      TIMESTAMPTZ DEFAULT now()
);


-- Track system alerts that may relate to known problems
CREATE TABLE alerts (
  alert_id        BIGSERIAL PRIMARY KEY,
  source_system   TEXT NOT NULL,
  alert_type      TEXT NOT NULL,
  description     TEXT NOT NULL,
  severity        SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 5),
  status          TEXT NOT NULL,          -- 'active', 'acknowledged', 'resolved'
  problem_id      BIGINT REFERENCES problems(problem_id),
  created_at      TIMESTAMPTZ DEFAULT now(),
  resolved_at     TIMESTAMPTZ
);
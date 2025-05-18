-- 1. Controlled-Vocabulary Types 
CREATE TYPE sop_status AS ENUM ('draft', 'active', 'archived');
CREATE TYPE doc_format AS ENUM ('pdf', 'md');

-- 2. Users Table (user information)
CREATE TABLE users (
  user_id       BIGSERIAL    PRIMARY KEY,
  name          VARCHAR(200) NOT NULL,
  email         VARCHAR(255) NOT NULL UNIQUE,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 3. Categories Table (expertise areas + Service Desk role)
CREATE TABLE categories (
  category_id   BIGSERIAL    PRIMARY KEY,
  name          VARCHAR(100) NOT NULL UNIQUE
);

-- 4. Join Table for User ↔ Category Many-to-Many
CREATE TABLE user_categories (
  user_id       BIGINT NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
  category_id   BIGINT NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, category_id)
);


-- 5. Create the partitioned parent table
CREATE TABLE document (
  document_id    BIGSERIAL,
  title          VARCHAR(255)  NOT NULL,
  description    TEXT,
  version        VARCHAR(50)   NOT NULL,
  status         sop_status    NOT NULL DEFAULT 'draft',
  created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
  effective_date DATE          NOT NULL,
  archived_date  DATE,                                        -- key for partitioning
  author_id      BIGINT       NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
  reviewer_id    BIGINT        REFERENCES users(user_id) ON DELETE SET NULL,
  category_id    BIGINT        REFERENCES categories(category_id) ON DELETE SET NULL,
  file_path      TEXT          NOT NULL,
  format         doc_format    NOT NULL,
  file_size      BIGINT,
  page_count     INT,
  search_vector  TSVECTOR GENERATED ALWAYS AS (
                    to_tsvector('english',
                      coalesce(title,'') || ' ' || coalesce(description,'')
                    )
                  ) STORED,
  PRIMARY KEY (document_id, archived_date)
) PARTITION BY RANGE (archived_date);

-- 5.1 Catches rows where archived_date IS NULL (i.e., still active)
CREATE TABLE document_current PARTITION OF document
  DEFAULT;


-- 5.2 Dynamically create yearly partitions for the next 10 years
DO $$
DECLARE
  start_year INT := EXTRACT(YEAR FROM CURRENT_DATE)::INT;
  end_year   INT := start_year + 10;
  yr         INT;
BEGIN
  FOR yr IN start_year..end_year LOOP
    EXECUTE FORMAT(
      'CREATE TABLE IF NOT EXISTS document_%s PARTITION OF document
         FOR VALUES FROM (%L) TO (%L);',
      yr,
      TO_CHAR(MAKE_DATE(yr,1,1),   'YYYY-MM-DD'),
      TO_CHAR(MAKE_DATE(yr+1,1,1), 'YYYY-MM-DD')
    );
  END LOOP;
END
$$;


-- 6. Indexes for Performance
CREATE INDEX idx_document_category        ON document (category_id);
CREATE INDEX idx_document_effective_date  ON document (effective_date);
CREATE INDEX idx_document_archived_date   ON document (archived_date);

-- optional: tighter index only for “active” documents
CREATE INDEX idx_document_status_active
            ON document (archived_date)
         WHERE status = 'active';

CREATE INDEX idx_document_search_vec      ON document USING GIN (search_vector);
CREATE UNIQUE INDEX idx_document_file_path ON document (file_path);
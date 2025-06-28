# Comparing Keyword, Full-Text and Vector Search

This lab shows how to enable PostgreSQL full-text search and run the same query through three methods: `LIKE`, full-text and pgvector similarity. It also introduces a metrics table for logging query precision.

## Introduction

In our Wikipedia assistant scenario this first exercise lays the groundwork for reliable document retrieval. By experimenting with keyword, full-text and vector search you will see how different techniques surface relevant passages—knowledge that the later labs build on to power the assistant.

## 1. Enable Full-Text Search

Execute `sql/full_text_setup.sql` to add the `content_tsv` column and GIN index:

```bash
psql $DATABASE_URL -f sql/full_text_setup.sql
```

## 2. Example Search Queries

`sql/search_methods_example.sql` contains three queries for the phrase *"biggest animal in the ocean"*:

```sql
-- A) Keyword search using ILIKE
SELECT id, title
FROM public.articles
WHERE content ILIKE '%biggest animal in the ocean%';

-- B) Full-text search
SELECT id, title, ts_rank_cd(content_tsv, plainto_tsquery('english', 'biggest animal in the ocean')) AS rank
FROM public.articles
WHERE content_tsv @@ plainto_tsquery('english', 'biggest animal in the ocean')
ORDER BY rank DESC
LIMIT 5;

-- C) Vector search
SELECT id, title, content_vector <-> (
    SELECT content_vector FROM public.articles WHERE title ILIKE '%Blue Whale%' LIMIT 1
) AS distance
FROM public.articles
WHERE content_vector IS NOT NULL
ORDER BY content_vector <-> (
    SELECT content_vector FROM public.articles WHERE title ILIKE '%Blue Whale%' LIMIT 1
)
LIMIT 5;
```

Run the file with:

```bash
psql $DATABASE_URL -f sql/search_methods_example.sql
```

## 3. Chunking Strategies

Experiment with different chunk sizes when creating embeddings. Sentence level, paragraph level and fixed token lengths all have trade-offs. Use the `create_emb_chunked.py` script with the `--strategy` flag to try each approach.
The script only updates the `Sweden` and `Switzerland` articles by default; supply a comma-separated list with `--titles` to change this.

Example commands:

```bash
python create_emb_chunked.py --strategy sentence
python create_emb_chunked.py --strategy paragraph
python create_emb_chunked.py --strategy tokens --token-size 500 --titles "Norway,Denmark"
```

Example snippet to test chunking with NLTK:

```python
import nltk
from textwrap import wrap

text = "Climate change is accelerating. Scientists observe shifts..."

# Sentence chunks
sentences = nltk.sent_tokenize(text)

# Paragraph chunks
paragraphs = text.split("\n\n")

# Fixed length (approx 100 words)
words = text.split()
chunk_size = 100
fixed_chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
```

## 4. Logging Search Precision

Create the metrics table with:

```bash
psql $DATABASE_URL -f sql/search_metrics_table.sql
psql $DATABASE_URL -f sql/metric_descriptions_table.sql
```

Each query is logged with a `query_id`, timestamp, search mode and top similarity score. Both the CLI scripts and the Flask app have integration points to record these metrics for later analysis.

## 5. Example Queries

Try running a few searches after re-embedding with different strategies to see how the results change:

```bash
python article_similarity_search.py "largest animal in the ocean"
python article_similarity_search.py "French mathematician who invented calculus"
python article_similarity_search.py "fastest land mammal"
```

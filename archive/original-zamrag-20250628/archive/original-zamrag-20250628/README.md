# RAG-essentials

This repository contains scripts and SQL utilities for experimenting with semantic search on a PostgreSQL database of Wikipedia articles.

Throughout the labs we walk through building a lightweight assistant that can answer questions about Wikipedia. Each exercise introduces a new building block—from enabling full-text search to wiring up a retrieval-augmented generation (RAG) pipeline—until you have a small Q&A bot able to consult the embedded articles.

## Workshop Overview & Objectives

This short workshop is split across two days to build skills incrementally.

### Day 1 – Semantic Search with pgvector
Explore how to embed Wikipedia articles, store vectors in PostgreSQL, and run similarity queries using the lab scripts.

### Day 2 – Building a RAG Pipeline
Use those search results to feed a basic retrieval‑augmented generation workflow, following the examples in `labs/lab2`.

Detailed setup instructions are available in [LAB-setups.md](LAB-setups.md).

## Setup

Step-by-step instructions to prepare the environment can be found in [LAB-setups.md](LAB-setups.md). You will need PostgreSQL with the pgvector extension, the embedded dataset from OpenAI and the following environment variables:

```bash
export DATABASE_URL="postgresql://postgres@localhost/wikipedia"
export OPENAI_API_KEY="<your OpenAI API key>"
```

## Scripts

### `create_emb_wiki.py`
Embeds article titles and contents using OpenAI's `text-embedding-3-small` model. Progress is logged as embeddings are generated.

### `create_emb_chunked.py`
Variant of the embedding script with a `--strategy` flag to experiment with
token, sentence or paragraph level chunking. It also accepts `--no-overlap`
to disable the default token overlap and `--first-chunk-only` to store just
the first chunk vector. By default it only re-embeds the `Sweden` and
`Switzerland` articles – use `--titles` to customise this list.
Run it with for example:

```bash
python create_emb_chunked.py --strategy sentence
```
Add `--first-chunk-only` to store only the first chunk vector.

### `article_similarity_search.py`
Interactive console program that prompts for a query, generates its embedding and prints the closest matches by title and by content.

### Lab 0
The `labs/lab0` directory introduces full-text search and logging utilities.

* `search_comparison.md` – steps to enable full-text search and compare keyword, full-text and vector queries. Includes chunking tips and metrics logging.

To prepare the metrics table and FTS column, run:

```bash
psql $DATABASE_URL -f sql/full_text_setup.sql
psql $DATABASE_URL -f sql/search_metrics_table.sql
psql $DATABASE_URL -f sql/metric_descriptions_table.sql
```

### Lab 1
The `labs/lab1` directory contains material for the first lab.

* `similarity_search_l2.py` – L2 distance search using inline SQL.
* `similarity_search_cosine.py` – Cosine distance variant.

Run the lab with one of the search scripts:

```bash
python labs/lab1/similarity_search_l2.py "What article talks about Switzerland?"
# or
python labs/lab1/similarity_search_cosine.py "What article talks about Switzerland?"
```

### Lab 2
The `labs/lab2` directory adds simple question answering on top of the similarity search.

* `qa_context_only.py` – answers strictly from the retrieved articles.
* `qa_external_fallback.py` – falls back to general knowledge if the context lacks the answer.

Run the lab with either script:

```bash
python labs/lab2/qa_context_only.py
# or
python labs/lab2/qa_external_fallback.py
```

### Lab 3
The `labs/lab3` directory showcases a modular Retrieval-Augmented Generation workflow using LangChain.

* `langchain_retrieval_qa.py` – builds a `RetrievalQA` chain backed by PostgreSQL and OpenAI.

Run the lab with:

```bash
python labs/lab3/langchain_retrieval_qa.py
```

### Capstone
The `labs/capstone` folder combines the Flask backend from `chatbotUI` with a Streamlit interface for an end-to-end search app.

Start the backend:

```bash
python chatbotUI/app.py
```

Then launch the UI:

```bash
streamlit run labs/capstone/app.py
```

The Streamlit app now includes a checkbox to record timing metrics for each
query and a separate **Metrics** page to view all logged executions. Metrics are
stored in the `search_metrics` table, which now captures a short description of
the query along with the time spent on the embedding call, database retrieval
and LLM request.



## Cosine vs. L2 distance

The `<->` operator computes L2 (Euclidean) distance. If your vectors are L2 normalised, using cosine distance usually yields more accurate semantic matches. Recreate the indexes with `cosine_ops` to switch:

```sql
DROP INDEX IF EXISTS articles_title_vector_idx;
DROP INDEX IF EXISTS articles_content_vector_idx;

CREATE INDEX articles_title_vector_idx ON public.articles USING ivfflat (title_vector cosine_ops)   WITH (lists = 1000);
CREATE INDEX articles_content_vector_idx ON public.articles USING ivfflat (content_vector cosine_ops) WITH (lists = 1000);
```

## Best Practices

See [docs/best_practices.md](docs/best_practices.md) for tips on tracking precision/recall, token budgeting and index tuning.


## License

This project is licensed under the [MIT License](LICENSE).


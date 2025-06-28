# **Script Documentation: `create_emb_wiki.py`**

This script generates embeddings for every article in the `public.articles` table. It processes both titles and article contents, storing the resulting vectors back into PostgreSQL.

## Overview

- Articles are split into 800‑token chunks with a 100‑token overlap.
- Batches of text are sent to the OpenAI API (`text-embedding-3-small` model).
- Progress for titles and content embedding is logged in percentage increments.

The script is useful when first creating or refreshing embeddings for the whole dataset.

## Main Components

1. **Helper Functions**
   - `chunk_text(text)` – divides article content into fixed‑size token windows.
   - `iter_batches(rows)` – groups records into batches that stay under OpenAI's token limits.
   - `get_embeddings(texts)` – calls the API with retry logic on transient errors.
   - `avg_vec(vectors)` – averages vectors from multiple chunks of the same article.
2. **Embedding Functions**
   - `embed_titles(cur, table)` – embeds all article titles and updates the `title_vector` column.
   - `embed_contents(cur, table)` – embeds article content in chunks and updates the `content_vector` column.
3. **`main()`**
   - Connects to PostgreSQL using `DATABASE_URL`.
   - Calls the title and content embedding routines in sequence.

## Usage

Set your environment variables first:

```bash
export OPENAI_API_KEY="your-key"
export DATABASE_URL="postgresql://postgres@localhost/wikipedia"
```

Then run:

```bash
python create_emb_wiki.py
```

The script will log progress until all embeddings are written.

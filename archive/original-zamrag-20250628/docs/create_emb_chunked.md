# **Script Documentation: `create_emb_chunked.py`**

This utility generates embeddings for Wikipedia articles with customizable chunking. It is adapted from `create_emb_wiki.py` but adds options to experiment with how article text is split before embedding.

## Overview

The script reads article titles and contents from a PostgreSQL table, divides the text into chunks, and sends those chunks to the OpenAI API to obtain vector embeddings. The resulting vectors are stored back in the database.

Chunking strategies:

- `tokens` (default) – fixed‑size windows using token counts with overlap. Use
  `--no-overlap` to disable this behaviour.
- `sentence` – one sentence per chunk using NLTK.
- `paragraph` – split on blank lines.
- `--first-chunk-only` – skip averaging and store only the first chunk.

Progress is logged as a percentage so you can monitor long runs.

## How It Works

1. **Chunking helpers**
   - `chunk_text(text)` splits article text based on the chosen strategy.
   - `iter_batches(rows)` groups pieces of text into API batches without exceeding token limits.
2. **Embedding calls**
   - `get_embeddings(texts)` sends a batch to OpenAI with automatic retry logic on transient errors.
   - `avg_vec(vectors)` averages vectors from multiple chunks of the same article.
3. **Database updates**
   - `embed_titles(cur, table, titles)` processes title strings and writes `title_vector` values.
   - `embed_contents(cur, table, titles)` processes article bodies in chunks and writes `content_vector` values.
   - `_flush(cur, table, cache)` updates accumulated vectors for a set of articles.
4. **Main routine**
   - Parses command‑line flags (`--strategy`, `--token-size`, `--no-overlap`, `--titles`, `--first-chunk-only`).
   - Connects to PostgreSQL using the `DATABASE_URL` environment variable.
   - Calls the embedding functions for titles then contents.

## Usage

Set the required environment variables:

```bash
export OPENAI_API_KEY="your-key"
export DATABASE_URL="postgresql://postgres@localhost/wikipedia"
```

Run the script, for example with sentence-level chunking:

```bash
python create_emb_chunked.py --strategy sentence
```

You can experiment with other strategies as well:

```bash
python create_emb_chunked.py --strategy paragraph
python create_emb_chunked.py --strategy tokens --token-size 500 --titles "Norway,Denmark" --no-overlap
python create_emb_chunked.py --first-chunk-only
```

Use `--titles` to limit which articles are re-embedded or to process only a specific subset.
Add `--no-overlap` to remove the default 100-token overlap when chunking by tokens.

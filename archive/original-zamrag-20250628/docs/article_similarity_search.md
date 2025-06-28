# **Script Documentation: `article_similarity_search.py`**

This command-line tool lets you query the Wikipedia embeddings stored in PostgreSQL. It embeds your search terms and returns the nearest articles by title and by content.

## Overview

1. The script obtains a query from arguments or prompts you to type one.
2. It calls OpenAI to embed the query using the `text-embedding-3-small` model.
3. Two SQL queries rank articles by similarity: one against `title_vector` and one against `content_vector`.
4. Results are printed in a simple table using the `tabulate` library.
5. Basic metrics are logged to the `search_metrics` table if it exists.

## Key Functions

- `embed_query(text, client)` – returns the embedding vector for the search text.
- `search(query_vec, conn, title_like, page)` – runs the similarity queries and fetches results.
- `pretty(rows, header)` – helper to display rows in a readable format.
- `main()` – ties everything together: parses options, gets the embedding, runs the search, and prints the tables.

## Usage

Ensure you have the required environment variables:

```bash
export OPENAI_API_KEY="your-key"
export DATABASE_URL="postgresql://postgres@localhost/wikipedia"
```

Example search:

```bash
python article_similarity_search.py "largest animal in the ocean"
```

Use `--title-like` to filter titles and `--page` to paginate through results.

# Best Practices

This page collects a few tips for measuring the effectiveness of your searches and tuning the PostgreSQL vector index.

## Measuring Precision and Recall

Create the metrics table defined in [`sql/search_metrics_table.sql`](../sql/search_metrics_table.sql) to capture search logs. Optionally load [`sql/metric_descriptions_table.sql`](../sql/metric_descriptions_table.sql) to annotate each column. Each entry stores the query id, the first 20 characters of the text as a description, timestamp, search mode, highest similarity score, token usage and precision value.

To calculate recall as well as precision, join these logs with a ground‑truth table of expected results. For example:

```sql
SELECT m.query_id,
       SUM(CASE WHEN r.expected_id = l.id THEN 1 ELSE 0 END)::float / COUNT(r.expected_id) AS recall,
       AVG(m.precision) AS precision
FROM public.search_metrics m
JOIN public.relevance_labels r ON m.query_id = r.query_id
LEFT JOIN public.articles l ON r.expected_id = l.id
GROUP BY m.query_id;
```

This allows tracking how search tweaks impact quality over time.

## Token Budgeting

Large language models have fixed context windows. When retrieving context for RAG, keep track of token counts so that the query, retrieved text and prompt stay within the model limits. The `search_metrics` table logs token usage from the `chatbotUI` app as a starting point. Summing the tokens in your query, system prompt and candidate passages helps decide how many articles or chunks to include.

## Index Tuning Tips

The example scripts create `ivfflat` indexes with 1,000 lists. For smaller datasets this may be excessive, while for larger corpora it may be insufficient. Experiment with the number of lists:

```sql
CREATE INDEX articles_content_vector_idx
ON public.articles USING ivfflat (content_vector cosine_ops)
WITH (lists = 500);
```

More lists generally mean better recall but slower inserts and larger indexes. Fewer lists speed up indexing but can reduce accuracy. Test different settings and vacuum analyze the table after creating the index.

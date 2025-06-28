# **Script Documentation: `qa_external_fallback.py`**

This script demonstrates a more advanced **Retrieval-Augmented Generation (RAG)** workflow. It mirrors `qa_context_only.py` but with a key difference: it allows the language model to use its own general knowledge if the retrieved documents do not contain the answer, but only if it provides a clear disclaimer.

## Introduction

This final lab completes the assistant by giving it a graceful fallback. When the context does not contain the answer, the LLM may use external knowledge but must clearly say so. This mirrors how a production assistant can remain helpful without misleading the user.

```
 [question]
     |
     v
get_embedding() -----+
                     |
            +--------+-----------+
            | query_similar_items| (Retrieval)
            +--------+-----------+
                     |
              build context
                     |
        +------------+------------+
        | generate_answer()       | (Generation w/ Fallback)
        +-------------------------+
```

## **How It Works & Code Explanation**

The script's structure is very similar to the context-only version, but the logic inside the `generate_answer` function is critically different due to more sophisticated prompt engineering.

1. get_embedding(text) & query_similar_items(query_embedding)
    
    These functions for embedding the query and retrieving documents are identical to the ones in the qa_context_only.py script. The "Retrieval" step remains the same.
    
2. generate_answer(query, context) (The "Generation with Fallback" Step)
    
    This function instructs the LLM on how to behave when the provided context is insufficient.
    
    - **Advanced Prompt Engineering:** The `system` message provides a multi-step set of instructions to the LLM:
        1. First, try to answer using _only_ the provided context.
        2. If the context is not enough, then (and only then) use your general knowledge.
        3. If you use general knowledge, you **must** start your response with a specific disclaimer: `"The provided context did not contain the relevant information. Based on external information:"`
    - **Purpose:** This creates a more flexible and robust assistant. It prefers to use the trusted, local data but can still provide a helpful answer if that data is incomplete. The disclaimer is crucial for transparency, as it clearly informs the user about the source of the information (trusted documents vs. the model's general knowledge).
3. main()
    
    The main function follows the exact same orchestration logic as the context-only version: get question -> embed -> retrieve -> build context -> generate answer -> print. The difference in outcome is determined entirely by the prompt sent in the generate_answer function.
    

## **SQL Query Explained**

The SQL query for the retrieval step is the same L2 similarity search used in the previous script.

SQL

```
SELECT title, content, content_vector <-> %s::vector AS distance
FROM public.articles
WHERE content_vector IS NOT NULL
ORDER BY content_vector <-> %s::vector
LIMIT %s;
```

## **Prerequisites and Limitations**

- **Prerequisites:**
    
    - `psycopg2` and `openai` Python libraries installed.
    - `DATABASE_URL` and `OPENAI_API_KEY` environment variables set.
- **Required Index:** An `ivfflat` index on `content_vector` is necessary for fast retrieval.
    
    SQL
    
    ```
    CREATE INDEX articles_content_vector_idx
      ON public.articles USING ivfflat (content_vector)
      WITH (lists = 1000);
    ```
    
- **Production Warning:**
    
    - This script uses a direct database connection per query. Use a connection pool in production.
    - **Trust and Safety:** Allowing a fallback to external knowledge can be risky. The model could provide incorrect, biased, or outdated information. The disclaimer helps mitigate this, but for applications requiring high levels of accuracy, it may be safer to disable this fallback mechanism and only use trusted data.
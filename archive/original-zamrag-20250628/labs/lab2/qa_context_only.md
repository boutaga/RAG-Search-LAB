# **Script Documentation: `qa_context_only.py`**

This script demonstrates a foundational **Retrieval-Augmented Generation (RAG)** workflow. It first retrieves relevant documents from the database based on a user's question and then uses a Large Language Model (LLM) to generate an answer based **only** on the information found in those documents.

## Introduction

This lab stitches together the retrieval and generation pieces to create our first working version of the Wikipedia assistant. By forcing the LLM to answer strictly from the retrieved context, you see how RAG can provide grounded responses.

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
        | generate_answer()       | (Generation)
        +-------------------------+
```

## **How It Works & Code Explanation**

This script introduces a two-stage process: first retrieve, then generate.

1. get_embedding(text)
    
    This function is the entry point, turning the user's natural language question into a vector embedding that can be used for a database search.
    
2. query_similar_items(query_embedding) (The "Retrieval" Step)
    
    This function performs a similarity search to find the most relevant articles from the database to answer the question.
    
    - **Purpose:** To find a small, relevant subset of documents from a large corpus, which can then be passed to an LLM. This is far more efficient and scalable than sending the entire database to the LLM.
    - **Code:** It connects to the PostgreSQL database and executes a `SELECT` query using the L2 distance operator (`<->`) to find the top N most similar articles based on their `content_vector`. It returns the raw database rows.
3. generate_answer(query, context) (The "Generation" Step)
    
    This function takes the original question and the context (the text from the retrieved documents) and asks the LLM to generate a final, human-readable answer.
    
    - **System Prompt Engineering:** This is the most critical part. The `system` message given to the OpenAI API is carefully crafted to control the LLM's behavior:
        
        > "You must answer the following question using only the context provided... If the answer is not present in the context, respond with 'No relevant information is available.'"
        
    - **Purpose:** This instruction prevents the LLM from "hallucinating" or using its general knowledge. It forces the model to ground its answer strictly in the provided text, which is essential for applications requiring factual accuracy based on a specific knowledge base.
4. main()
    
    The main function orchestrates the RAG pipeline:
    
    - It gets the user's question.
    - It calls `get_embedding()` to vectorize the question.
    - It calls `query_similar_items()` to retrieve relevant document snippets.
    - It concatenates the content of the retrieved items into a single `context` string.
    - It calls `generate_answer()` with the question and the newly built context to get the final answer.
    - It prints the answer to the console.

## **SQL Query Explained**

The query used in the retrieval step is a standard L2 similarity search.

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
    
    - `psycopg2` and `openai` libraries installed.
    - `DATABASE_URL` and `OPENAI_API_KEY` environment variables must be set.
- **Required Index:** Requires an `ivfflat` index on `content_vector` for fast retrieval.
    
    SQL
    
    ```
    CREATE INDEX articles_content_vector_idx
      ON public.articles USING ivfflat (content_vector)
      WITH (lists = 1000);
    ```
    
- **Production Warning:**
    
    - The script uses a direct database connection per query. A connection pool is necessary for production environments.
    - The context passed to the LLM has a limited size. If `TOP_N` is too large, the context string may exceed the token limit of the AI model, causing an error. This needs to be carefully managed in a real application.

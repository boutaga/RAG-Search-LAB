# **Script Documentation: `similarity_search_cosine.py`**

This script performs a semantic search using **Cosine Distance**. It's a variation of `similarity_search_l2.py` but uses the `<=>` operator, which is often more effective for comparing text embeddings because it measures the angle between vectors rather than their magnitude.

## Introduction

This lab refines the retrieval step for our Wikipedia Q&A assistant. By switching to cosine distance you will compare how different similarity metrics affect the results, preparing the ground for the question-answering pipeline in the next lab.

```
 [query]
    |
    v
embed_query() ------+
                     |
            +--------+-----------+
            | execute SQL        |
            +--------+-----------+
                     |
            +--------+-------+
            | pretty() output |
            +----------------+
```

## **How It Works & Code Explanation**

The script's structure and workflow are identical to the L2 search version, with the key difference being the SQL operator used.

1. embed_query(text, client)
    
    This function converts the user's plain-text query into a numerical vector embedding using the OpenAI API. This process is the same as in the L2 search script.
    
2. main()
    
    This is the central function that controls the script's execution.
    
    - **Get User Input:** Reads the search query from command-line arguments or user prompt.
    - **Get Embedding:** Calls `embed_query()` to get the query's vector.
    - **Connect to PostgreSQL:** Connects to the database using `psycopg2`, configured to use `RealDictCursor` for easy data access and registering the `vector` type.
    - **Execute SQL Queries:** The main difference is here. It executes two SQL queries that use the `<=>` operator for Cosine Distance.
    - **Display Results:** Calls the `pretty()` function to format and print the results.
3. pretty(rows, header)
    
    A helper function that uses the tabulate library to display the search results in a clean, readable table format in the console.
    

## **SQL Query Explained**

The SQL query is modified to use the Cosine Distance operator.

SQL

```
SELECT 
    id, 
    title, 
    url, 
    content_vector <=> %s::vector AS distance
FROM 
    public.articles
WHERE 
    content_vector IS NOT NULL
ORDER BY 
    content_vector <=> %s::vector
LIMIT %s;
```

- **`content_vector <=> %s::vector`**: This is the key change. The `<=>` operator calculates the **Cosine Distance** between the stored vector and the query vector. A smaller distance means the vectors are more aligned (i.e., more semantically similar). This is generally preferred for normalized text embeddings as it focuses on the "direction" or "topic" of the vectors, ignoring their length.
- **`ORDER BY ...`**: As before, this sorts the results to return the most similar articles first.

## **Prerequisites and Limitations**

- **Prerequisites:**
    
    - `psycopg2`, `openai`, and `tabulate` libraries installed.
    - `DATABASE_URL` and `OPENAI_API_KEY` environment variables set.
- **Required Index:** For Cosine Distance searches to be fast, the `ivfflat` index **must** be created with the `cosine_ops` operator class. Using the wrong index will result in a slow sequential scan.
    
    SQL
    
    ```
    CREATE INDEX articles_content_vector_cosine_idx
      ON public.articles USING ivfflat (content_vector cosine_ops)
      WITH (lists = 1000);
    ```
    
- **Production Warning:** Like the L2 script, this opens a new database connection each time it is run. For any real application, use a persistent connection or a connection pool to avoid performance bottlenecks.

## Usage Examples

Basic search:

```bash
python similarity_search_cosine.py "chatbots"
```

Search only titles containing "Wiki" on page 2:

```bash
python similarity_search_cosine.py "chatbots" --title-like Wiki --page 2
```
    

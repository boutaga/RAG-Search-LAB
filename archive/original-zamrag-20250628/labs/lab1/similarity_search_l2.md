# Script Documentation: similarity_search_l2.py

This script demonstrates a basic semantic search over the `public.articles` table using pgvector's **L2 distance** operator (`<->`). It is intended as an educational example of how to embed a user query and rank rows by Euclidean distance.

## Introduction

Continuing the Wikipedia assistant scenario, this lab focuses on the retrieval step. You will write a simple script that takes a question, embeds it and finds the closest matching articles. Accurate retrieval is essential before the assistant can generate answers.

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

## How It Works & Code Explanation

The script follows a simple, three-step process to perform the similarity search.

### 1. `embed_query(text, client)`

This function takes the user's plain-text query and converts it into a numerical representation called a vector embedding using the OpenAI API.

- **Purpose:** Machine learning models and databases cannot understand text directly. They work with numbers. This function transforms the query "What about Switzerland?" into a high-dimensional vector (an array of 1536 numbers) that captures its semantic meaning.
    
- **Code:** It makes an API call to OpenAI's embedding endpoint, specifying the model (`text-embedding-3-small`), and returns the resulting vector.
    

### 2. `main()`

This is the core function that orchestrates the entire workflow.

1. **Get User Input:** It first reads the search query, either from the command-line arguments or by prompting the user directly.
    
2. **Get Embedding:** It calls `embed_query()` to get the vector for the user's query.
    
3. **Connect to PostgreSQL:** It establishes a connection to the database using `psycopg2`.
    
    - `cursor_factory=RealDictCursor`: This is a helpful utility that makes the query results accessible like Python dictionaries (e.g., `row['title']`) instead of tuples (e.g., `row[1]`), making the code more readable.
        
    - `register_vector(conn)`: This crucial step tells `psycopg2` how to handle the `vector` data type from pgvector, ensuring it's correctly interpreted.
        
4. **Execute SQL Queries:** It runs two separate SQL queries: one to search against the `title_vector` and another against the `content_vector`. The results are fetched and stored.
    
5. **Display Results:** It calls the `pretty()` function to display the results of both searches in a clean format.
    

### 3. `pretty(rows, header)`

This is a utility function for formatting the output. It takes the rows returned from the database and uses the `tabulate` library to print them in a nicely formatted, human-readable table.

## SQL Query Explained

The script runs two nearly identical queries. Here is a breakdown of the one searching the `content_vector`:

```
SELECT 
    id, 
    title, 
    url, 
    content_vector <-> %s::vector AS distance
FROM 
    public.articles
WHERE 
    content_vector IS NOT NULL
ORDER BY 
    content_vector <-> %s::vector
LIMIT %s;
```

- **`content_vector <-> %s::vector`**: This is the core of the search. The `<->` operator is provided by `pgvector` and calculates the **L2 distance** (or Euclidean distance) between the `content_vector` of each row and the query vector provided as a parameter (`%s`). The result is aliased as `distance`. 
- **`WHERE content_vector IS NOT NULL`**: This is a performance best practice. It ensures that the query only considers rows that actually have a content vector, allowing the database to potentially use an index more effectively.
- **`ORDER BY distance`**: This sorts the results, bringing the rows with the smallest distance (i.e., the most similar articles) to the top.
- **`LIMIT %s`**: This restricts the output to the top N results, which is essential for performance and usability.
    

## Prerequisites and Limitations

- **Prerequisites:**
    
    - `psycopg2`, `openai`, and `tabulate` Python libraries must be installed.   
    - Environment variables `DATABASE_URL` and `OPENAI_API_KEY` must be set. 
    - The `articles` table must exist and be populated.
        
- **Required Index:** For efficient searches, an `ivfflat` index is required. Without it, the query will perform a slow sequential scan over the entire table.
    
    ```
    CREATE INDEX articles_content_vector_idx
      ON public.articles USING ivfflat (content_vector)
      WITH (lists = 1000);
    ```
    
- **Production Warning:** This script opens a new database connection for each run. In a real application, you should use a connection pool (like `psycopg2.pool`) to manage connections efficiently and avoid overwhelming the database.

## Usage Examples

Basic search:

```bash
python similarity_search_l2.py "chatbots"
```

Filter titles containing "Wiki" and get the second page of results:

```bash
python similarity_search_l2.py "chatbots" --title-like Wiki --page 2
```

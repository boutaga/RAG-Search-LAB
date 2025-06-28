# Lab Setup Guide

This comprehensive guide provides all necessary steps to prepare your environment for the semantic search labs. Following these instructions will result in a fully functional setup, including an interactive chatbot UI for exploring vector search concepts with PostgreSQL and pgvector.




## Core Environment Setup and architecture

This section covers the foundational setup required for all subsequent labs.


```pgsql

 +---------------------------------------------------+
 |                   User                            |
 | (browser via Streamlit or copilot.html, or CLI)   |
 +---------------------------------------------------+
           |   HTTP POST /search or /metrics
           v
 +--------------------------------------------------+
 | Flask backend (chatbotUI/app.py)                 |
 |  - routes: /search, /metrics                     |
 |  - performs embedding, vector search and RAG     |
 +--------------------------------------------------+
           |    SQL queries / pgvector similarity
           v
 +--------------------------------------------------+
 | PostgreSQL + pgvector (articles table)           |
 +--------------------------------------------------+
           ^                                  
           |                                   
           | embeddings created with            
           | create_emb_wiki.py / chunked.py     
           v                                     
 +------------------------------------------------+
 | OpenAI APIs                                    |
 |  - text-embedding-3-small for embeddings       |
 |  - chat completions for RAG answers            |
 +------------------------------------------------+


```

### 1. Environment Variables

To allow the applications to communicate with the database and external services, you must define the following environment variables. They act as secure and flexible ways to configure the connection credentials.

```
# This variable provides the connection string for your PostgreSQL database.
export DATABASE_URL="postgresql://postgres@localhost/wikipedia"

# This variable holds your secret API key for authenticating with OpenAI's services.
export OPENAI_API_KEY="<your OpenAI API key>"
```

### 2. Install pgvector

`pgvector` is the PostgreSQL extension that enables vector similarity search. You will need to compile it from the source to integrate it with your PostgreSQL installation.

```
git clone [https://github.com/pgvector/pgvector.git](https://github.com/pgvector/pgvector.git)
cd pgvector
# The PG_CONFIG variable tells the 'make' command where to find your PostgreSQL installation's configuration. 
# You can find the correct path by running `pg_config --pgxs`.
make PG_CONFIG=/path/to/pg_config
# This command installs the compiled extension into your PostgreSQL directory.
sudo make install PG_CONFIG=/path/to/pg_config
cd ..
```

### 3. Prepare the Database

The following steps will create a dedicated database, enable the vector extension, define the necessary table structure, and populate it with the pre-embedded Wikipedia dataset.

1. Download and unzip the dataset:
    
    This command fetches a zip file containing a CSV of Wikipedia articles that have already been converted into vector embeddings.
    
    ```
    wget [https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip](https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip)
    unzip vector_database_wikipedia_articles_embedded.zip
    ```
    
2. Create the database, extension, and table:
    
    First, create a new database named wikipedia. Then, activate the vector extension within it. Finally, create the articles table which is designed to hold the text data alongside its corresponding vector embeddings.
    
    ```
    psql -c "CREATE DATABASE wikipedia"
    psql -d wikipedia -c "CREATE EXTENSION IF NOT EXISTS vector;"
    psql -d wikipedia -c "
    CREATE TABLE public.articles (
      id               integer       NOT NULL,
      url              text,
      title            text,
      content          text,
      title_vector     vector(1536),
      content_vector   vector(1536),
      vector_id        integer,
      CONSTRAINT articles_pkey PRIMARY KEY (id)
    );"
    ```
    
3. Load data into the table:
    
    This psql command efficiently bulk-loads the data from the CSV file directly into the articles table.
    
    ```
    psql -d wikipedia -c "\COPY public.articles (id, url, title, content, title_vector, content_vector, vector_id) FROM 'vector_database_wikipedia_articles_embedded.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');"
    ```
    
4. Build Indexes:
    
    Indexes are crucial for achieving high-speed vector searches on large datasets. Without them, every search would require a slow "full scan" of the table. We create two different types of ivfflat indexes to support the two main distance metrics you will be testing.
    
    ```
    -- This index is optimized for L2 Distance (<->), which measures the direct Euclidean distance between vectors.
    CREATE INDEX ON public.articles USING ivfflat (content_vector) WITH (lists = 1000);
    
    -- This index uses 'cosine_ops' and is optimized for Cosine Distance (<=>), which measures the angle between vectors. This is often better for semantic text similarity.
    CREATE INDEX ON public.articles USING ivfflat (content_vector cosine_ops) WITH (lists = 1000);
    ```
    

### 4. Setup Python Environment

A Python virtual environment provides an isolated space for installing the project's dependencies without affecting your system-wide Python installation.

```
python3 -m venv pgvector_lab_venv
source pgvector_lab_venv/bin/activate
# This command installs all necessary libraries:
# - psycopg2-binary: The PostgreSQL adapter for Python.
# - openai: The official client for the OpenAI API.
# - flask & flask-cors: For creating the web server and allowing cross-origin requests from the frontend.
# - other packages: For data handling and running the lab scripts.
pip install psycopg2-binary openai pgvector transformers torch sentencepiece tabulate tiktoken flask flask-cors
```

## Lab 0: Full-Text Search and Metrics Logging

This introductory lab shows how to enable PostgreSQL full-text search and create
a metrics table for tracking query precision. Execute the SQL files below to add
the `content_tsv` column, build indexes and create the logging table.

```bash
psql $DATABASE_URL -f sql/full_text_setup.sql
psql $DATABASE_URL -f sql/search_metrics_table.sql
psql $DATABASE_URL -f sql/metric_descriptions_table.sql
psql $DATABASE_URL -f sql/search_methods_example.sql
```

See `labs/lab0/search_comparison.md` for details on chunking strategies and example queries.

## Lab 1: Command-Line Similarity Search

These standalone scripts are designed for initial exploration. They allow you to run similarity queries directly from your terminal and see the raw database output. Ensure your virtual environment is active before running them.

```
# Example L2 distance search. Observe the 'distance' column in the output.
python lab/lab1/similarity_search_l2.py "What article talks about Switzerland?"

# Example Cosine distance search. Compare the results and distances to the L2 search.
python lab/lab1/similarity_search_cosine.py "What article talks about Switzerland?"
```

## Lab 2: Interactive Chatbot UI

The interactive chatbot UI provides a user-friendly web interface for testing all search modes (L2, Cosine, and RAG) without needing to run command-line scripts for each query.

### 1. File Structure

A well-organized file structure is important for keeping the project manageable. Create a `chatbotUI` directory to separate the web application code from the standalone lab scripts.

```
/your-project-folder/
├── chatbotUI/
│   ├── app.py        # The Python Flask backend server logic.
│   └── copilot.html  # The self-contained HTML, CSS, and JS frontend.
├── lab/
│   # ... other lab files
└── vector_database_wikipedia_articles_embedded.csv
```

### 2. Run the Chatbot Backend Server

The Flask backend server acts as the brain of the operation, handling API requests from the frontend. By running it on host `0.0.0.0`, you instruct Flask to listen for connections on all available network interfaces, not just `localhost`. This is what makes the UI accessible from other computers on your network.

```
# First, navigate to the directory containing the web app
cd /path/to/your-project-folder/chatbotUI

# Activate the virtual environment to ensure all packages are available
source ../pgvector_lab_venv/bin/activate

# Set the FLASK_APP environment variable and run the server
export FLASK_APP=app.py
flask run --host=0.0.0.0
```

### 3. Accessing the Chatbot UI

With the backend server running, you can now access the user interface from a web browser on any machine connected to the same local network.

1. Find your Ubuntu server's IP address. You will need this to connect from another machine. Use one of these commands in the Ubuntu terminal:
    
    hostname -I or ip addr show.
    
2. Navigate your browser to the UI. Open a browser on your primary computer and go to http://<YOUR_UBUNTU_SERVER_IP>:5000/copilot.html.
    
    For example, if your server's IP is 192.168.1.105, you would enter http://192.168.1.105:5000/copilot.html.
    

You can now use the UI to experiment with all available search modes and directly compare their outputs.

## Lab 3: LangChain Retrieval QA

Lab 3 demonstrates how to build a Retrieval-Augmented Generation pipeline using
LangChain modules. Install the extra packages and run the example script:

```bash
pip install langchain langchain-openai langchain-community
python labs/lab3/langchain_retrieval_qa.py
```

## Capstone: Streamlit Search App

The capstone combines the Flask backend with a simple Streamlit interface for an
end-to-end search experience.

1. Start the backend service:

   ```bash
   python chatbotUI/app.py
   ```

2. In another terminal launch the Streamlit UI:

   ```bash
   streamlit run labs/capstone/app.py
   ```

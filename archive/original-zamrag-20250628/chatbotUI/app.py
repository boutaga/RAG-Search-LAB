import os
import psycopg2
from openai import OpenAI
import hashlib
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Pre-requisites & Configuration ---
# 1. Environment Variables:
#    - DATABASE_URL: Your PostgreSQL connection string.
#    - OPENAI_API_KEY: Your OpenAI API key.
# 2. Python Packages:
#    - pip install flask flask-cors openai psycopg2-binary tiktoken
# 3. Required Indexes in PostgreSQL:
#    - For Cosine ('<=>'): CREATE INDEX ON articles USING ivfflat (content_vector cosine_ops);
#    - For L2 ('<->'): CREATE INDEX ON articles USING ivfflat (content_vector);

# --- Flask App Initialization ---
app = Flask(
    __name__,
    static_folder=os.path.dirname(os.path.abspath(__file__)),
    static_url_path=""
)
CORS(app)

# --- OpenAI API Key Setup ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Helper Functions ---

def get_embedding(text, model="text-embedding-3-small"):
    """Generates a vector embedding for a given text."""
    if not client.api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    try:
        resp = client.embeddings.create(model=model, input=[text])
        return resp.data[0].embedding
    except Exception as e:
        print(f"Error calling OpenAI Embedding API: {e}")
        raise

def generate_llm_answer(prompt, model="gpt-4o"):
    """Generates an answer using OpenAI's chat completion API."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        usage = response.usage.total_tokens if response.usage else 0
        return text, usage
    except Exception as e:
        print(f"Error calling OpenAI ChatCompletion API: {e}")
        raise

# --- RAG Prompt Engineering Functions ---

def create_rag_context_only_prompt(question, context_articles):
    """Prompt for RAG (Context Only) mode."""
    context = "\n---\n".join(context_articles)
    return f"""Answer the question based *only* on the provided context. If the context does not contain the answer, say so.
Context: {context}\n\nQuestion: {question}\n\nAnswer:"""

def create_rag_open_prompt(question, context_articles):
    """Prompt for RAG (Open Fallback) mode."""
    context = "\n---\n".join(context_articles)
    return f"""First, try to answer the question using *only* the provided context. If the context is not sufficient, use your external knowledge.
If you use external knowledge, you *must* begin your response with: "Based on external information:"
Context: {context}\n\nQuestion: {question}\n\nAnswer:"""


# --- Main Search Endpoint ---
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query_text = data.get('query')
    search_mode = data.get('search_mode', 'cosine')
    filter_text = data.get('filter')
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', 5))
    record_metrics = bool(data.get('record_metrics', True))
    metrics = {}
    total_start = time.perf_counter()

    if not query_text:
        return jsonify({"error": "Query parameter is missing"}), 400

    db_conn = None
    try:
        print(f"Mode: {search_mode}. Generating embedding for: '{query_text}'")
        emb_start = time.perf_counter()
        query_embedding = get_embedding(query_text)
        metrics['embedding_ms'] = round((time.perf_counter() - emb_start) * 1000, 4)
        qhash = hashlib.md5(query_text.encode('utf-8')).hexdigest()[:8]
        
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set.")
        db_conn = psycopg2.connect(db_url)
        cursor = db_conn.cursor()

        # --- **LOGIC SPLIT**: Based on search mode ---
        
        # **Path 1: Similarity Search (Raw SQL Output)**
        if search_mode in ['cosine', 'l2']:
            operator = '<=>' if search_mode == 'cosine' else '<->'
            print(f"Executing raw similarity search with operator: {operator}")

            where_clauses = ["content_vector IS NOT NULL"]
            params = [str(query_embedding)]
            if filter_text:
                where_clauses.append("title ILIKE %s")
                params.append(f"%{filter_text}%")
            where_sql = " AND ".join(where_clauses)
            offset = (page - 1) * page_size
            sql_query = f"""
                SELECT id, title, url, content_vector {operator} %s AS distance
                FROM public.articles
                WHERE {where_sql}
                ORDER BY distance
                LIMIT %s OFFSET %s;
            """
            params.extend([page_size, offset])
            db_start = time.perf_counter()
            cursor.execute(sql_query, tuple(params))
            metrics['db_ms'] = round((time.perf_counter() - db_start) * 1000, 4)
            columns = [desc[0] for desc in cursor.description]
            raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            top_dist = raw_results[0]['distance'] if raw_results else None
            metrics['total_ms'] = round((time.perf_counter() - total_start) * 1000, 4)
            try:
                if record_metrics:
                    cursor.execute(
                        "INSERT INTO public.search_metrics(query_id, description, query_time, mode, top_score, token_usage, precision, embedding_ms, db_ms, llm_ms, total_ms) "
                        "VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            qhash,
                            query_text[:20],
                            search_mode,
                            float(top_dist) if top_dist is not None else None,
                            None,
                            1.0,
                            metrics.get('embedding_ms'),
                            metrics.get('db_ms'),
                            None,
                            metrics.get('total_ms'),
                        ),
                    )
                    db_conn.commit()
            except Exception:
                pass

            return jsonify({"response_type": "raw_sql", "results": raw_results, "metrics": metrics})

        # **Path 2: RAG Search (LLM-Generated Output)**
        elif search_mode in ['rag_context_only', 'rag_open']:
            # For both RAG modes, we'll use L2 distance to retrieve context, as per lab scripts
            operator = '<->'
            print(f"Executing RAG search; retrieving context with operator: {operator}")
            
            where_clauses = ["content_vector IS NOT NULL"]
            params = [str(query_embedding)]
            if filter_text:
                where_clauses.append("title ILIKE %s")
                params.append(f"%{filter_text}%")
            where_sql = " AND ".join(where_clauses)
            offset = (page - 1) * page_size
            sql_query = f"""
                SELECT title, content, url, content_vector {operator} %s AS distance
                FROM public.articles
                WHERE {where_sql}
                ORDER BY distance
                LIMIT %s OFFSET %s;
            """
            params.extend([page_size, offset])
            db_start = time.perf_counter()
            cursor.execute(sql_query, tuple(params))
            metrics['db_ms'] = round((time.perf_counter() - db_start) * 1000, 4)
            rows = cursor.fetchall()
            context_articles = [row[1] for row in rows]
            sources = []
            for title, content, url, _ in rows:
                snippet = content[:200] if content else ""
                sources.append({"title": title, "snippet": snippet, "url": url})

            if not context_articles:
                return jsonify({
                    "response_type": "llm_answer",
                    "answer": "I couldn't find any relevant articles in the database to answer your question."
                })

            # Select the appropriate prompt engineering strategy
            if search_mode == 'rag_context_only':
                prompt = create_rag_context_only_prompt(query_text, context_articles)
            else: # rag_open
                prompt = create_rag_open_prompt(query_text, context_articles)
            
            print("Generating final answer with LLM...")
            llm_start = time.perf_counter()
            final_answer, token_count = generate_llm_answer(prompt)
            metrics['llm_ms'] = round((time.perf_counter() - llm_start) * 1000, 4)
            try:
                best_distance = None
                cursor.execute(
                    "SELECT content_vector <-> %s::vector AS dist FROM public.articles WHERE content_vector IS NOT NULL ORDER BY content_vector <-> %s::vector LIMIT 1",
                    (str(query_embedding), str(query_embedding)),
                )
                row = cursor.fetchone()
                if row:
                    best_distance = row[0]
            except Exception:
                best_distance = None

            metrics['total_ms'] = round((time.perf_counter() - total_start) * 1000, 4)
            try:
                if record_metrics:
                    cursor.execute(
                        "INSERT INTO public.search_metrics(query_id, description, query_time, mode, top_score, token_usage, precision, embedding_ms, db_ms, llm_ms, total_ms) "
                        "VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            qhash,
                            query_text[:20],
                            search_mode,
                            float(best_distance) if best_distance is not None else None,
                            token_count,
                            1.0,
                            metrics.get('embedding_ms'),
                            metrics.get('db_ms'),
                            metrics.get('llm_ms'),
                            metrics.get('total_ms'),
                        ),
                    )
                    db_conn.commit()
            except Exception:
                pass

            return jsonify({"response_type": "llm_answer", "answer": final_answer, "sources": sources, "metrics": metrics})

        else:
            return jsonify({"error": "Invalid search mode specified"}), 400

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred. Check server logs."}), 500
    finally:
        if db_conn:
            db_conn.close()

@app.route('/metrics', methods=['GET'])
def get_metrics():
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT query_id, description, query_time, mode, top_score, token_usage, precision, embedding_ms, db_ms, llm_ms, total_ms FROM public.search_metrics ORDER BY query_time DESC LIMIT 10;")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/all_metrics', methods=['GET'])
def get_all_metrics():
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT query_id, description, query_time, mode, top_score, token_usage, precision, embedding_ms, db_ms, llm_ms, total_ms FROM public.search_metrics ORDER BY query_time DESC;")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/metric_descriptions', methods=['GET'])
def metric_descriptions():
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT metric_name, description FROM public.metric_descriptions;")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify({name: desc for name, desc in rows})

# --- Static Frontend Endpoint ---
@app.route('/copilot.html')
def serve_copilot():
    """Serve the standalone HTML UI."""
    return app.send_static_file('copilot.html')

if __name__ == '__main__':
    app.run(debug=True)

import os, psycopg2, openai, torch
from transformers import AutoTokenizer, AutoModelForMaskedLM
from pgvector.psycopg2 import register_vector

# Config
DATABASE_URL = os.getenv("DATABASE_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "naver/splade-cocondenser-ensembledistil"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Init
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(DEVICE).eval()

def get_dense(text):
    resp = openai.embeddings.create(input=text, model="text-embedding-ada-002")
    return resp.data[0].embedding  # 1536-dim list

def get_sparse(text):
    tokens = tokenizer([text], return_tensors="pt", padding=True, truncation=True, max_length=512)
    tokens = {k: v.to(DEVICE) for k,v in tokens.items()}
    with torch.no_grad():
        logits = model(**tokens).logits
    weights = torch.max(torch.log1p(torch.relu(logits)), dim=1).values[0]
    # build sparsevec string '{idx:val,...}/vocab_size'
    indices = weights.nonzero().squeeze().cpu().tolist()
    values = weights[indices].cpu().tolist()
    pairs = ",".join(f"{i}:{v:.6f}" for i,v in zip(indices,values))
    return f"{{{pairs}}}/{tokenizer.vocab_size}"

# Write to DB
conn = psycopg2.connect(DATABASE_URL)
register_vector(conn)
cur = conn.cursor()
cur.execute("SELECT chunk_id, chunk_text FROM kb_chunks;")
for cid, text in cur.fetchall():
    d = get_dense(text)
    s = get_sparse(text)
    cur.execute(
        "UPDATE kb_chunks SET embedding = %s, sparse_embedding = %s WHERE chunk_id = %s",
        (d, s, cid)
    )
conn.commit()
cur.close()
conn.close()

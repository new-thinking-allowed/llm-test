from mysql.connector import connect
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import faiss
import pickle

# For Hungarian:
# MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" # Or "intfloat/multilingual-e5-small"
MODEL_NAME = "BAAI/bge-small-en-v1.5"
INDEX_PATH = "index.faiss"
BATCH_SIZE = 1000
MAX_LINES_PER_CHUNK = 20
MAX_SECONDS_PER_CHUNK = 30.0
MAX_TOKENS_PER_CHUNK = 300

# Load embedding model and tokenizer
model = SentenceTransformer(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def truncate_text(text, max_tokens=MAX_TOKENS_PER_CHUNK):
    tokens = tokenizer(text, truncation=True, max_length=max_tokens, return_tensors="pt")
    truncated = tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=True)
    return "passage: " + truncated  

def flush_chunk(documents, metadata, chunk_lines, video_id, start_time, end_time, info):
    if not chunk_lines:
        return
    chunk_text = " ".join(chunk_lines)
    chunk_text = truncate_text(chunk_text)
    documents.append(chunk_text)
    metadata.append({
        "video_id": video_id,
        "start_time": start_time,
        "end_time": end_time,
        **info
    })

conn = connect(
    host="localhost",
    user="root",
    password="password",
    database="local"
)
cursor = conn.cursor(dictionary=True)

cursor.execute("""
SELECT 
  c.video_id,
  c.time,
  c.text,
  v.title,
  v.description,
  v.publishedAt,
  v.guest,
  v.tags
FROM caption c
JOIN video v ON c.video_id = v.id
ORDER BY c.video_id, c.time
""")

documents, metadata = [], []
chunk_lines = []
current_video, start_time, end_time, info = None, None, None, {}

while True:
    rows = cursor.fetchmany(BATCH_SIZE)
    if not rows:
        break

    for row in rows:
        video_id, time_sec, text = row["video_id"], float(row["time"]), row["text"]

        # New video = flush previous
        if video_id != current_video:
            flush_chunk(documents, metadata, chunk_lines, current_video, start_time, end_time, info)
            chunk_lines = []
            current_video = video_id
            start_time = end_time = time_sec
            info = {
                "title": row["title"],
                "description": row["description"],
                "publishedAt": str(row["publishedAt"]),
                "guest": row["guest"],
                "tags": row["tags"]
            }

        duration = time_sec - start_time
        if len(chunk_lines) >= MAX_LINES_PER_CHUNK or duration > MAX_SECONDS_PER_CHUNK:
            flush_chunk(documents, metadata, chunk_lines, current_video, start_time, end_time, info)
            chunk_lines = []
            start_time = time_sec

        chunk_lines.append(text)
        end_time = time_sec

# Flush last chunk
flush_chunk(documents, metadata, chunk_lines, current_video, start_time, end_time, info)

cursor.close()
conn.close()

# Embed and save
embeddings = model.encode(documents, convert_to_numpy=True).astype("float32")
index = faiss.IndexHNSWFlat(embeddings.shape[1], 32)
index.add(embeddings)

faiss.write_index(index, INDEX_PATH)
with open("documents.pkl", "wb") as f:
    pickle.dump((documents, metadata), f)

print(f"Built FAISS index with {index.ntotal} entries. Saved to {INDEX_PATH}.")

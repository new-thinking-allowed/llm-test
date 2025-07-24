from mysql.connector import connect
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# Connect to MySQL
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

BATCH_SIZE = 1000

# Parameters for chunking
MAX_LINES_PER_CHUNK = 20
MAX_SECONDS_PER_CHUNK = 30.0

documents = []
metadata = []

current_chunk_lines = []
current_chunk_video = None
current_chunk_start_time = None
current_chunk_end_time = None
current_chunk_info = None

while True:
    rows = cursor.fetchmany(BATCH_SIZE)
    if not rows:
        break

    for row in rows:
        video_id = row['video_id']
        time_sec = float(row['time'])
        text = row['text']

        if current_chunk_video != video_id:
            if current_chunk_lines:
                chunk_text = " ".join(current_chunk_lines)
                metadata.append({
                    "video_id": current_chunk_video,
                    "start_time": current_chunk_start_time,
                    "end_time": current_chunk_end_time,
                    **current_chunk_info
                })
                documents.append(chunk_text)
                current_chunk_lines = []

            current_chunk_video = video_id
            current_chunk_start_time = time_sec
            current_chunk_end_time = time_sec
            current_chunk_info = {
                "title": row["title"],
                "description": row["description"],
                "publishedAt": str(row["publishedAt"]),
                "guest": row["guest"],
                "tags": row["tags"]
            }

        duration = time_sec - current_chunk_start_time

        if (len(current_chunk_lines) >= MAX_LINES_PER_CHUNK) or (duration > MAX_SECONDS_PER_CHUNK):
            chunk_text = " ".join(current_chunk_lines)
            metadata.append({
                "video_id": current_chunk_video,
                "start_time": current_chunk_start_time,
                "end_time": current_chunk_end_time,
                **current_chunk_info
            })
            documents.append(chunk_text)
            current_chunk_lines = []
            current_chunk_start_time = time_sec
            current_chunk_end_time = time_sec

        current_chunk_lines.append(text)
        current_chunk_end_time = time_sec

# Flush the last chunk
if current_chunk_lines:
    chunk_text = " ".join(current_chunk_lines)
    metadata.append({
        "video_id": current_chunk_video,
        "start_time": current_chunk_start_time,
        "end_time": current_chunk_end_time,
        **current_chunk_info
    })
    documents.append(chunk_text)

cursor.close()
conn.close()

# Embedding
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(documents, convert_to_numpy=True).astype('float32')

# FAISS index
dim = embeddings.shape[1]
index = faiss.IndexHNSWFlat(dim, 32)
index.add(embeddings)

print(f"FAISS HNSW index built with {index.ntotal} chunks.")

faiss.write_index(index, "index_hnsw.faiss")
with open("documents.pkl", "wb") as f:
    pickle.dump((documents, metadata), f)

print("FAISS HNSW index written to index_hnsw.faiss")

# tinyllama failed
# mistral 163.7515 seconds.
# llama3  143.6338 seconds; 93 seconds
# phi3 64 seonds; 21 seconds; 161 secs
# gemma:2b 27 seconds, bad json

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from ollama import chat
import time
from datetime import datetime

# --- Load FAISS index and metadata ---
print("Loading FAISS index and documents...")
index = faiss.read_index("index_hnsw.faiss")
index.hnsw.efSearch = 50

with open("documents.pkl", "rb") as f:
    documents, metadata = pickle.load(f)

# --- Initialize embedding model ---
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Define your query ---
query = "What is the consensus on UFOs?"

# --- Embed the query ---
print("Embedding query...")
query_embedding = model.encode([query]).astype('float32')

# --- Search the FAISS index ---
index.nprobe = 10
k = 3

print("Searching FAISS index...")
start_time = time.time()
D, I = index.search(query_embedding, k)
elapsed = time.time() - start_time
print(f"Search took {elapsed:.4f} seconds.")

# --- Helper to format seconds as mm:ss ---
def format_seconds(seconds):
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02}:{sec:02}"

# --- Retrieve and format results with minimal metadata for reference ---
formatted_chunks = []
for rank, (idx, dist) in enumerate(zip(I[0], D[0]), start=1):
    doc = documents[idx].strip()
    meta = metadata[idx]

    video_id = meta.get("video_id", "")
    start_time_sec = int(meta.get("start_time", 0))
    start_time_fmt = format_seconds(start_time_sec)
    title = meta.get("title", "Unknown Title")

    # Format chunk with title and timestamp linked for referencing in answer
    chunk_info = (
        f"From [{title}](https://youtube.com/watch?v={video_id}&t={start_time_sec}s) at {start_time_fmt}:\n"
        f"{doc}"
    )
    formatted_chunks.append(chunk_info)

context = "\n\n---\n\n".join(formatted_chunks)

rag_system_prompt= f"""
Respond in JSON only: 

{{
  "answer": "<detailed answer>",
  "sources": [{"video ID": "...", "timestamp": "...", "video title": "..."}]
}}
"""

# --- Construct RAG-style prompt ---
rag_user_prompt = f"""
Based on ONLY the following information, answer the question:

Question: {query}

Information:
{context}
"""

# --- Send query to Ollama ---
print("Querying via Ollama...")
start_time = time.time()
response = chat(
    model='phi3',
    messages=[
        {"role": "system", "content": rag_system_prompt},
        {"role": "user", "content": rag_user_prompt}
    ]
)

# --- Output the response ---
print("\n--- Response ---")
print(response['message']['content'])

elapsed = time.time() - start_time
print(f"LLM response time: {elapsed:.4f} seconds.")

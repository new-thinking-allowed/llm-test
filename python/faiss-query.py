from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import time

# Load HNSW index and metadata
index = faiss.read_index("index_hnsw.faiss")
with open("documents.pkl", "rb") as f:
    documents, metadata = pickle.load(f)

model = SentenceTransformer('all-MiniLM-L6-v2')

query = "What are UFOs?"

start_time = time.time()

query_embedding = model.encode([query]).astype('float32')

k = 3  # number of results
D, I = index.search(query_embedding, k)

end_time = time.time()
elapsed = end_time - start_time

print(f"Query and search took {elapsed:.3f} seconds\n")

for rank, idx in enumerate(I[0]):
    print(f"\n--- Result #{rank + 1} ---")
    print(f"Video ID: {metadata[idx]['video_id']}")
    print(f"Start time: {metadata[idx]['start_time']}")
    print(f"End time: {metadata[idx]['end_time']}")
    print(documents[idx][:500] + "...")

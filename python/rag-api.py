from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from ollama import chat
import time
import json
import re

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)

print("Loading FAISS index and documents...")
index = faiss.read_index("index_hnsw.faiss")
index.hnsw.efSearch = 50

with open("documents.pkl", "rb") as f:
    documents, metadata = pickle.load(f)

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

class QueryRequest(BaseModel):
    query: str

def format_seconds(seconds: float) -> str:
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02}:{sec:02}"

def extract_json(text: str):
    # Try to extract JSON between ```json ... ``` or just {...}
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return None

@app.post("/query")
async def query_rag(req: QueryRequest):
    query = req.query

    query_embedding = model.encode([query]).astype('float32')
    k = 3
    D, I = index.search(query_embedding, k)

    formatted_chunks = []
    for rank, idx in enumerate(I[0], start=1):
        doc = documents[idx]
        meta = metadata[idx]

        video_id = meta.get("video_id", "")
        start_time = format_seconds(meta.get("start_time", 0))
        end_time = format_seconds(meta.get("end_time", 0))
        title = meta.get("title", "")
        guest = meta.get("guest", "")
        published_at = meta.get("publishedAt", "")
        tags = meta.get("tags", "")
        description = meta.get("description", "")

        url = f"https://youtube.com/watch?v={video_id}&t={int(meta.get('start_time', 0))}s"

        chunk_info = (
            f"Result {rank} ({title}):\n"
            f"URL: {url}\n"
            f"Time: {start_time} - {end_time}\n"
            f"Guest: {guest}\n"
            f"Tags: {tags}\n"
            f"Description: {description}\n\n"
            f"{doc.strip()}"
        )
        formatted_chunks.append(chunk_info)

    context = "\n\n---\n\n".join(formatted_chunks)

    rag_system_prompt= f"""
Respond in JSON only: 

{{
  "answer": "<detailed answer>",
  "sources": [{{"video ID": "...", "timestamp": "...", "video title": "..."}}]
}}
"""

    rag_user_prompt = f"""
Based on ONLY the following information, answer the question:

Question: {query}

Information:
{context}
"""

    start_time = time.time()
    try:
        response = chat(
            model='phi3',
            messages=[
                {"role": "system", "content": rag_system_prompt},
                {"role": "user", "content": rag_user_prompt}
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama query failed: {str(e)}")

    elapsed = time.time() - start_time
    raw_content = response['message']['content']

    json_str = extract_json(raw_content)
    if json_str is None:
        print("Raw model output (failed to find JSON):", repr(raw_content))
        raise HTTPException(status_code=500, detail="Failed to find JSON object in model response")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print("Raw JSON string (failed to parse):", repr(json_str))
        raise HTTPException(status_code=500, detail="Failed to parse JSON response from model")

    cleaned_sources = []
    for source in data.get("sources", []):
        title = source.get("title", "")
        timestamp = source.get("timestamp", "")
        if " at " in title:
            parts = title.rsplit(" at ", 1)
            title = parts[0].strip()
            timestamp = parts[1].strip()
        cleaned_sources.append({"title": title, "timestamp": timestamp})

    data["sources"] = cleaned_sources

    return {
        "answer": data.get("answer", ""),
        "sources": data.get("sources", []),
        "llm_response_time_sec": elapsed
    }

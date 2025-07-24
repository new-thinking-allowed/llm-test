import sys
import pickle
import time
import json
import re
from sentence_transformers import SentenceTransformer
import faiss
from ollama import chat

print("Loading FAISS index and documents...")
index = faiss.read_index("index_hnsw.faiss")
index.hnsw.efSearch = 50

with open("documents.pkl", "rb") as f:
    documents, metadata = pickle.load(f)

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')


def format_seconds(seconds: float) -> str:
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02}:{sec:02}"


def extract_json(text: str):
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return None


def perform_search(query: str, k: int = 3):
    query_embedding = model.encode([query]).astype('float32')
    D, I = index.search(query_embedding, k)
    return D, I


def format_context(I):
    formatted_chunks = []
    source_metas = []
    for rank, idx in enumerate(I[0], start=1):
        doc = documents[idx]
        meta = metadata[idx]

        video_id = meta.get("video_id", "")
        start_time_sec = meta.get("start_time", 0)
        start_time_str = format_seconds(start_time_sec)
        title = meta.get("title", "")
        guest = meta.get("guest", "")

        chunk_info = (
            f"Rank {rank} ({title}):\n"
            f"Video Title: {title}\n"
            f"Start Time: {start_time_str}\n"
            f"Guest: {guest}\n\n"
            f"{doc.strip()}"
        )
        formatted_chunks.append(chunk_info)

        source_metas.append({
            "video_id": video_id,
            "start_time_sec": start_time_sec,
            "timestamp": start_time_str,
            "video_title": title,
        })

    context_str = "\n\n---\n\n".join(formatted_chunks)
    return context_str, source_metas


def call_llm(query: str, context: str):
    rag_system_prompt = """
Return your answer as a JSON object, with all keys and string values enclosed in double quotes:

{
  "answer": "<detailed answer>",
  "sources": [{"timestamp": "...", "video_title": "..."}]
}

Use ONLY the information provided in the context below.
Do NOT invent video IDs or URLs.
Return the exact timestamp and video_title as found in the context.
"""

    rag_user_prompt = f"""
Based ONLY on the following information, answer the question:

Question: {query}

Information:
{context}
"""
    start_time = time.time()
    response = chat(
        model='phi3',
        messages=[
            {"role": "system", "content": rag_system_prompt},
            {"role": "user", "content": rag_user_prompt}
        ]
    )
    elapsed = time.time() - start_time
    raw_content = response['message']['content']

    json_str = extract_json(raw_content)
    if json_str is None:
        raise RuntimeError(f"Failed to find JSON object in model response: {repr(raw_content)}")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON response from model: {repr(json_str)}")

    # Clean and normalize sources from LLM
    cleaned_sources = []
    for source in data.get("sources", []):
        video_title = source.get("video_title", "")
        timestamp = source.get("timestamp", "")
        cleaned_sources.append({"video_title": video_title, "timestamp": timestamp})

    data["sources"] = cleaned_sources
    data["llm_response_time_sec"] = elapsed

    return data


def query_with_sources(query: str, k: int = 3):
    D, I = perform_search(query, k)
    context, source_metas = format_context(I)
    llm_data = call_llm(query, context)

    # Merge reliable source metadata into LLM response
    llm_sources = llm_data.get("sources", [])
    merged_sources = []
    for i, src in enumerate(llm_sources):
        if i < len(source_metas):
            merged = {
                "video_id": source_metas[i]["video_id"],
                "timestamp": src["timestamp"],
                "video_title": src["video_title"]
            }
        else:
            merged = src
        merged_sources.append(merged)

    if not merged_sources:
        merged_sources = source_metas

    llm_data["sources"] = merged_sources

    return llm_data

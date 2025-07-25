import sys
import pickle
import time
import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from ollama import chat

print("Loading FAISS index and documents...")
index = faiss.read_index("index_hnsw.faiss")
index.hnsw.efSearch = 50

with open("documents.pkl", "rb") as f:
    documents, metadata = pickle.load(f)

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
tokenizer = model.tokenizer
MAX_TOKENS_PER_CHUNK = 300


def truncate_text(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> str:
    tokens = tokenizer.encode(text, max_length=max_tokens, truncation=True)
    return tokenizer.decode(tokens, skip_special_tokens=True)


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
    query_embedding = model.encode([f"query: {query}"], normalize_embeddings=True).astype('float32')
    D, I = index.search(query_embedding, k)
    return D, I


def summarize_answer(answer: str) -> str:
    summary_prompt = f"Summarize this answer in one concise sentence:\n\n{answer}"
    response = chat(
        model="phi3",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response["message"]["content"].strip()


def format_context(I):
    formatted_chunks = []
    source_metas = []

    for rank, idx in enumerate(I[0], start=1):
        raw_doc = documents[idx]
        meta = metadata[idx]

        doc = truncate_text(raw_doc)

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
            "title": title,
        })

    context_str = "\n\n---\n\n".join(formatted_chunks)
    return context_str, source_metas


def format_history(history: list[dict[str, str]]) -> str:
    lines = []
    for i, item in enumerate(history, 1):
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()
        lines.append(f"{i}. Q: {q}\n   A: {a}")
    return "\n".join(lines)


def call_llm(query: str, context: str, compressed_history: list = None):
    history_str = format_history(compressed_history or [])

    rag_system_prompt = f"""
You are a helpful assistant answering questions about videos on philosophy and the paranormal.

Here is a summary of the previous conversation:
{history_str}

Return your answer as a JSON object, with all keys and string values enclosed in double quotes:

{{
  "answer": "<detailed answer>",
  "sources": [{{"timestamp": "...", "title": "...", "video_id": "..."}}]
}}

Use ONLY the information provided in the context below.
Do NOT invent video IDs or URLs.
Return the exact timestamp, video_id and title as found in the context.
"""

    rag_user_prompt = f"""
Based on ONLY the following retrieved passages, write a thorough and detailed answer to the user's question. Include context and relevant insights from the sources.

Question: {query}

Passages:
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

    data["llm_response_time_sec"] = elapsed
    return data


def query_with_sources(query: str, k: int = 3, conversation_history: list = None):
    conversation_history = conversation_history or []

    D, I = perform_search(query, k)
    context, source_metas = format_context(I)
    llm_data = call_llm(query, context, conversation_history)

    full_answer = llm_data.get("answer", "")
    conversation_history.append({
        "question": query,
        "answer": summarize_answer(full_answer)
    })

    llm_sources = llm_data.get("sources", [])
    merged_sources = [
        {
            "video_id": meta["video_id"],
            "timestamp": llm_sources[i].get("timestamp", meta["timestamp"]) if i < len(llm_sources) else meta["timestamp"],
            "title": llm_sources[i].get("title", meta["title"]) if i < len(llm_sources) else meta["title"],
        }
        for i, meta in enumerate(source_metas)
    ]

    llm_data["sources"] = merged_sources

    return llm_data, conversation_history


if __name__ == "__main__":
    conversation_history = [
        {
            "question": "What does Bernardo Kastrup say about idealism?",
            "answer": "He argues that idealism explains consciousness better than materialism."
        }
    ]

    user_query = "What does Bernardo Kastrup say about idealism and materialism?"
    result, conversation_history = query_with_sources(user_query, conversation_history=conversation_history)

    print(json.dumps(result, indent=2))

    print("\nUpdated conversation history:")
    for turn in conversation_history:
        print(f"Q: {turn['question']}\nA: {turn['answer']}\n")

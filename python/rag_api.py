import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import rag_lib

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

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # Optional session to identify user/session
    conversation_history: Optional[list] = None  # Optional conversation history passed from client


# Simple in-memory store for conversation histories keyed by session_id
conversation_histories = {}

@app.post("/query")
async def query_rag(req: QueryRequest, request: Request):
    query = req.query
    session_id = req.session_id

    # Get current history for session or empty list
    if session_id:
        history = conversation_histories.get(session_id, [])
    else:
        history = req.conversation_history or []

    try:
        data, updated_history = rag_lib.query_with_sources(query, conversation_history=history)
    except RuntimeError as e:
        print(f"RuntimeError: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # Save updated history back if session_id present
    if session_id:
        conversation_histories[session_id] = updated_history

    return {
        "answer": data.get("answer", ""),
        "sources": data.get("sources", []),
        "llm_response_time_sec": data.get("llm_response_time_sec", 0),
        "conversation_history": updated_history  
    }

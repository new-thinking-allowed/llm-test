from fastapi import APIRouter, HTTPException, Request
from models.query_request import QueryRequest
from services.conversation import conversation_histories
import rag_lib
import sys

router = APIRouter()

@router.post("/query")
async def query_rag(req: QueryRequest, request: Request):
    query = req.query
    session_id = req.session_id

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

    if session_id:
        conversation_histories[session_id] = updated_history

    return {
        "answer": data.get("answer", ""),
        "sources": data.get("sources", []),
        "llm_response_time_sec": data.get("llm_response_time_sec", 0),
        "conversation_history": updated_history
    }

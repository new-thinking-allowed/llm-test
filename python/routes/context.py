from fastapi import APIRouter, HTTPException
from services.conversation import conversation_histories

router = APIRouter()

@router.delete("/context/{session_id}")
async def delete_context(session_id: str):
    if session_id in conversation_histories:
        del conversation_histories[session_id]
        return {"status": "success", "message": f"Context for session {session_id} cleared."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

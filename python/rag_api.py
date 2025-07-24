import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


@app.post("/query")
async def query_rag(req: QueryRequest):
    query = req.query
    try:
        data = rag_lib.query_with_sources(query)
    except RuntimeError as e:
        print(f"RuntimeError: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return {
        "answer": data.get("answer", ""),
        "sources": data.get("sources", []),
        "llm_response_time_sec": data.get("llm_response_time_sec", 0),
    }

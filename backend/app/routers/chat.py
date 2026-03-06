import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import UPLOAD_DIR, STORAGE_DIR, OPENAI_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY
from app.services.rag_service import build_rag_store, get_retriever
from app.services.llm_providers import get_llm_provider
from app.prompts import get_reasoning_prefix


router = APIRouter()

RAG_SYSTEM = """Answer the question based ONLY on the following context from uploaded documents.
If the context does not contain relevant information, say so clearly.
Do not invent or assume information not present in the context.

Context:
{context}

Question: {question}

Answer:"""


class ChatRequest(BaseModel):
    session_id: str
    question: str
    provider: str  # openai, groq, deepseek, huggingface
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 1024
    reasoning_mode: str = "direct"
    chunk_size: int = 512
    top_k: int = 4


def _get_or_build_rag(request: Request, session_id: str, chunk_size: int, top_k: int):
    """Get or build RAG vector store for session."""
    store = getattr(request.app.state, "rag_store", {}) or {}
    key = f"{session_id}_{chunk_size}"
    if key in store:
        return store[key]
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=400, detail="Invalid session_id. Upload documents first.")
    persist = STORAGE_DIR / session_id
    vectorstore = build_rag_store(
        upload_dir=session_dir,
        chunk_size=chunk_size,
        persist_dir=persist,
    )
    retriever = get_retriever(vectorstore, top_k=top_k)
    store[key] = (vectorstore, retriever)
    request.app.state.rag_store = store
    return vectorstore, retriever


async def _stream_chat(req: ChatRequest, request: Request):
    vectorstore, retriever = _get_or_build_rag(
        request, req.session_id, req.chunk_size, req.top_k
    )
    docs = retriever.invoke(req.question)
    context = "\n\n".join(doc.page_content for doc in docs)
    reasoning_prefix = get_reasoning_prefix(req.reasoning_mode)
    system_content = RAG_SYSTEM.format(context=context, question=req.question)
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": req.question},
    ]
    llm = get_llm_provider(
        req.provider,
        openai_api_key=OPENAI_API_KEY,
        groq_api_key=GROQ_API_KEY,
        deepseek_api_key=DEEPSEEK_API_KEY,
    )
    async for chunk in llm.stream_chat(
        messages=messages,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
        reasoning_prefix=reasoning_prefix,
    ):
        yield json.dumps({"text": chunk}) + "\n"


@router.post("/stream")
async def chat_stream(req: ChatRequest, request: Request):
    """Stream chat response. Returns NDJSON lines: {"text": "chunk"}."""
    try:
        return StreamingResponse(
            _stream_chat(req, request),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

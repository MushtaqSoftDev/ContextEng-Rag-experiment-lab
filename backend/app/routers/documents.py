import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.config import UPLOAD_DIR, STORAGE_DIR
from app.services.rag_service import build_rag_store, get_retriever

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
DEFAULT_CHUNK_SIZE = 512
DEFAULT_TOP_K = 4


@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """Upload one or more documents. Returns session_id for chat."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    uploaded = []
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )
        path = session_dir / (f.filename or f"doc{ext}")
        with open(path, "wb") as out:
            content = await f.read()
            out.write(content)
        uploaded.append(f.filename)
    return {"session_id": session_id, "files": uploaded}


@router.post("/{session_id}/index")
async def index_documents(session_id: str, request: Request):
    """Build RAG index for uploaded docs. Call after upload for faster first query."""
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=400, detail="Invalid session_id.")
    persist = STORAGE_DIR / session_id
    try:
        vectorstore = build_rag_store(
            upload_dir=session_dir,
            chunk_size=DEFAULT_CHUNK_SIZE,
            persist_dir=persist,
        )
        retriever = get_retriever(vectorstore, top_k=DEFAULT_TOP_K)
        store = getattr(request.app.state, "rag_store", {}) or {}
        key = f"{session_id}_{DEFAULT_CHUNK_SIZE}"
        store[key] = (vectorstore, retriever)
        request.app.state.rag_store = store
        return {"status": "indexed", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

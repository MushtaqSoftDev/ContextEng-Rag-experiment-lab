import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # Disable ChromaDB telemetry

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import CORS_ORIGINS, OPENAI_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY
from app.routers import documents, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.rag_store = {}
    yield
    # Shutdown
    app.state.rag_store.clear()


app = FastAPI(
    title="RAG Context-Eng API",
    description="Document upload, RAG retrieval, multi-LLM chat with streaming",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/api/providers")
def get_providers():
    """Return which LLM providers have API keys configured. HuggingFace needs no key."""
    return {
        "openai": bool(OPENAI_API_KEY),
        "groq": bool(GROQ_API_KEY),
        "deepseek": bool(DEEPSEEK_API_KEY),
        "huggingface": True,  # No key needed, runs on CPU
    }


@app.get("/health")
def health():
    return {"status": "ok"}

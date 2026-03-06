"""
RAG service: document loading, chunking, embedding, retrieval.
Uses ChromaDB + sentence-transformers for local CPU embeddings.
"""
import os
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import uuid
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
try:
    from langchain_huggingface.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings


# Embedding model (CPU-friendly)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def load_document(path: Path) -> List[dict]:
    """Load document based on extension."""
    suffix = path.suffix.lower()
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".md": lambda p: TextLoader(str(p), encoding="utf-8"),
    }
    loader_class = loaders.get(suffix)
    if not loader_class:
        raise ValueError(f"Unsupported file type: {suffix}")
    loader = loader_class(str(path))
    docs = loader.load()
    return docs


def build_rag_store(
    upload_dir: Path,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    persist_dir: Optional[Path] = None,
) -> Chroma:
    """Build vector store from all documents in upload_dir."""
    all_docs = []
    for f in upload_dir.iterdir():
        if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".md"}:
            try:
                docs = load_document(f)
                all_docs.extend(docs)
            except Exception as e:
                raise RuntimeError(f"Failed to load {f.name}: {e}")

    if not all_docs:
        raise ValueError("No documents found in upload directory")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    splits = splitter.split_documents(all_docs)

    embeddings = _get_embeddings()
    collection_name = str(uuid.uuid4())

    if persist_dir:
        persist_dir.mkdir(parents=True, exist_ok=True)
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=str(persist_dir),
            collection_name=collection_name,
        )
    else:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            collection_name=collection_name,
        )

    return vectorstore


def get_retriever(vectorstore: Chroma, top_k: int = 4):
    """Get retriever from vector store."""
    return vectorstore.as_retriever(search_kwargs={"k": top_k})

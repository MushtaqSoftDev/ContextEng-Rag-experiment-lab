# RAG Context-Eng

An **LLM experiment lab** for document-based Q&A. Upload your documents, ask questions, and **control the output in real time** using context-engineering parameters.  
React (JavaScript) frontend + Python/FastAPI backend, fully Dockerized.

## What is this?

RAG Context-Eng is a playground to experiment with **Retrieval-Augmented Generation (RAG)** and LLM behavior. Unlike a fixed chat interface, you can tune **both RAG retrieval** and **LLM generation** parameters live—see how chunk size, top-K, temperature, and reasoning modes change answers.

- **Upload** PDF, TXT, or MD files
- **Index** them into a vector store (ChromaDB + sentence-transformers)
- **Ask questions** over your documents
- **Adjust sliders** and parameters; answers update immediately on the next query
- **Theory panel** explains each parameter with examples

## Features

### Document upload & RAG pipeline

- **Supported formats**: PDF, TXT, MD
- **Workflow**: Select files → Upload & Index → Ask questions
- **Embeddings**: Local CPU via `sentence-transformers/all-MiniLM-L6-v2` (no embedding API key)
- **Vector store**: ChromaDB with persistent storage per session

### Context-engineering parameters (output control)

| Parameter | Range | What it does |
|-----------|-------|--------------|
| **LLM Provider** | OpenAI, Groq, DeepSeek, HuggingFace | Switch between models; HuggingFace runs on CPU (free) |
| **Reasoning Mode** | Direct, Chain-of-Thought, Atom of Thought | How the model structures its answer: direct, step-by-step, or fine-grained reasoning |
| **Temperature** | 0 – 2 | Randomness: low = focused, high = creative |
| **Top-p (nucleus)** | 0 – 1 | Cumulative probability cutoff; lower = more focused |
| **Max tokens** | 64 – 4096 | Maximum response length |
| **Chunk size** | 128 – 1024 | Size of text chunks for embedding; smaller = finer retrieval, larger = more context per chunk |
| **Top-K retrieval** | 1 – 20 | Number of chunks passed to the LLM; more = more context, may add noise |

All parameters take effect on the **next question**—no page reload.

### How it works (RAG pipeline)

1. **Upload** → Files saved to a session folder; each session gets a unique `session_id`
2. **Index** → Documents are chunked (RecursiveCharacterTextSplitter), embedded (sentence-transformers), and stored in ChromaDB
3. **Query** → Your question is embedded; top-K most similar chunks are retrieved
4. **Generate** → Retrieved context + question are sent to the selected LLM; response streams back
5. Changing **chunk size** or **top-K** triggers re-indexing/re-retrieval; **LLM params** (temperature, top-p, reasoning mode) affect only generation

### Other

- **Real-time streaming** responses (NDJSON)
- **Theory panel**: collapsible sidebar with parameter descriptions and example values

## Quick Start

### 1. Clone & setup

```bash
cd ContextEng-Rag-experiment-lab
cp .env.example .env
```

### 2. Add API keys (optional)

Edit `.env` and add keys for the providers you want:

```env
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
DEEPSEEK_API_KEY=sk-...
```

HuggingFace BART needs **no key** and runs on CPU.

### 3. Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173  
- Backend: http://localhost:8000  
- Health: http://localhost:8000/health

### 4. Use the app

1. Click **+ Add files** and select one or more PDF/TXT/MD documents
2. Click **Upload & Index** (uploads files, chunks them, builds the vector index)
3. Tune **context-eng parameters** in the left panel (LLM provider, reasoning mode, sliders)
4. Ask questions in natural language; answers are grounded in your documents
5. Responses **stream in real time**; adjust parameters and ask again to compare
6. Use the **Theory** panel (▶) for parameter explanations and example values

## Local development (no Docker)

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend proxies `/api` to the backend.

## Project structure

```
ContextEng-Rag-experiment-lab/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── prompts.py
│       ├── routers/
│       │   ├── documents.py
│       │   └── chat.py
│       └── services/
│           ├── rag_service.py
│           └── llm_providers/
│               ├── openai_provider.py
│               ├── groq_provider.py
│               ├── deepseek_provider.py
│               └── huggingface_provider.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── App.jsx
        ├── api.js
        └── components/
            ├── DocumentUpload.jsx
            ├── ParameterControls.jsx
            ├── ChatInterface.jsx
            └── TheoryPanel.jsx
```

## Deploy to Railway / Render

A **root Dockerfile** runs everything in one container (frontend + backend). Both platforms can use it.

### Railway

1. Connect your repo to Railway
2. Railway detects the root `Dockerfile` automatically (or set in Settings → Dockerfile path: `Dockerfile`)
3. Add env vars in Variables: `GROQ_API_KEY`, `OPENAI_API_KEY`, etc.
4. Deploy

### Render

1. New → Web Service → Connect repo
2. **Environment**: Docker
3. **Dockerfile Path**: `./Dockerfile` (or leave blank if at root)
4. Add env vars in Environment
5. Deploy

Or use the Blueprint: add `render.yaml` to your repo, then Render will use it on connect.

### Files for platform deploy

| File | Purpose |
|------|---------|
| `Dockerfile` (root) | Single container: nginx + uvicorn |
| `render.yaml` | Render Blueprint |
| `railway.json` | Railway config |
| `scripts/start.sh` | Starts backend + nginx |

## API endpoints

- `POST /api/documents/upload` — Upload files, returns `session_id`
- `POST /api/documents/{session_id}/index` — Build RAG index for uploaded docs (called after upload)
- `POST /api/chat/stream` — Stream chat; accepts `session_id`, `question`, and all context-eng params (NDJSON)

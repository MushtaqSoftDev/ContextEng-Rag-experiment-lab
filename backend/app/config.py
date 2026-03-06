import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "storage")))

# API keys (optional - HuggingFace works without)
# .strip() removes accidental whitespace when pasting from Groq/OpenAI console
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()

# CORS
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

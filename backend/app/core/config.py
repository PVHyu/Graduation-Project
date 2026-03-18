import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {".txt", ".docx", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_CHUNK_CHARS = 1500

AI_MODEL = os.getenv("AI_MODEL", "qwen3:1.7b")
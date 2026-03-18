import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {".txt", ".docx", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024

MAX_CHUNK_CHARS = 1200
AI_MODEL = os.getenv("AI_MODEL", "qwen3:1.7b")

MINDMAP_SOURCE_PREVIEW_CHARS = 2500
MAX_MINDMAP_DEPTH = 3
MAX_MINDMAP_CHILDREN = 6
"""Application configuration values."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "SnapSum"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"

# SQLite veritabanı dosyası (JSON'dan taşındı)
DB_FILE = DATA_DIR / "snapsum.db"

# Gemini
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Chunking
CHUNK_SIZE = 12_000
CHUNK_OVERLAP = 500

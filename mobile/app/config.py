"""Application configuration values."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "SnapSum"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_FILE = DATA_DIR / "books.json"

# .env dosyasını proje kök dizininden yükle
load_dotenv(BASE_DIR / ".env")

# Gemini model can be changed later without touching business logic.
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Approximate character limit for one Gemini request input section.
CHUNK_SIZE = 12_000
CHUNK_OVERLAP = 500

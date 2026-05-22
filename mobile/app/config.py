"""Application configuration values."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "SnapSum"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_FILE = DATA_DIR / "snapsum.db"

# .env dosyasını proje kök dizininden yükle
load_dotenv(BASE_DIR / ".env")

# Mistral model can be changed later without touching business logic.
MISTRAL_MODEL = "mistral-medium-latest"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# Approximate character limit for one Mistral request input section.
CHUNK_SIZE = 12_000
CHUNK_OVERLAP = 500

SETTINGS_FILE = DATA_DIR / "settings.json"

import json

def load_settings() -> dict:
    """Load settings from JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(settings: dict) -> None:
    """Save settings to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        existing = load_settings()
        existing.update(settings)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def get_mistral_api_key() -> str:
    """Get Mistral API Key from settings or environment."""
    settings = load_settings()
    return settings.get("mistral_api_key", os.getenv("MISTRAL_API_KEY", MISTRAL_API_KEY))

def get_ui_language() -> str:
    """Get UI Language from settings (default is tr)."""
    settings = load_settings()
    return settings.get("language", "tr")


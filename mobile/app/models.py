"""Data models used by SnapSum."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class Book:
    """Represents one book/PDF item in the library.

    source  : 'general'  → admin/built-in kitaplar
              'personal' → kullanıcının yüklediği PDF'ler
    """

    title: str
    file_path: str
    source: str           # 'general' veya 'personal'  (DB: book_type)
    author: str = "Bilinmiyor"
    category: str = "Genel"
    summary: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize model for JSON/DB storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Book":
        """Deserialize model from JSON/DB row."""
        # Geriye dönük uyumluluk: eski kayıtlarda author/category olmayabilir.
        payload.setdefault("author", "Bilinmiyor")
        payload.setdefault("category", "Genel")
        payload.setdefault("summary", "")
        return cls(**{k: v for k, v in payload.items() if k in cls.__dataclass_fields__})

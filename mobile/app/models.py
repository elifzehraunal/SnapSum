"""Data models used by SnapSum."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class Book:
    """Represents one PDF item in the library."""

    title: str
    file_path: str
    source: str  # "general" or "personal"
    author: str = "Bilinmiyor"
    category: str = "Genel"
    summary: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize model for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Book":
        """Deserialize model from JSON payload."""
        return cls(**payload)

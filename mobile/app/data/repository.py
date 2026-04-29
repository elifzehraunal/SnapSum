"""Repository layer — thin wrapper over DatabaseManager.

UI kodu bu sınıfla konuşur; veritabanı detaylarını bilmez.
Arayüz değişmeden DatabaseManager farklı bir backend'e
(PostgreSQL, Firestore vb.) taşınabilir.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.models import Book
from app.data.database import DatabaseManager


class BookRepository:
    """High-level data access for Book objects."""

    def __init__(self, db_path: str | Path = "data/snapsum.db") -> None:
        self._db = DatabaseManager(db_path)

    # ------------------------------------------------------------------
    # Book operations
    # ------------------------------------------------------------------

    def add_book(self, book: Book) -> None:
        """Persist a new book to the database."""
        self._db.add_book(book)

    def get_book(self, book_id: str) -> Book | None:
        """Fetch one book by its UUID."""
        return self._db.get_book(book_id)

    def list_books(self, source: str | None = None) -> list[Book]:
        """List books, optionally filtered by source ('general'/'personal')."""
        return self._db.list_books(source)

    def seed_general_books(self, books: Iterable[Book]) -> None:
        """Seed built-in library once on first run."""
        self._db.seed_general_books(books)

    # ------------------------------------------------------------------
    # Summary operations (DB cache — replaces JSON summary_cache.json)
    # ------------------------------------------------------------------

    def get_summary(self, book_id: str, summary_type: str) -> str | None:
        """Return a cached summary if it exists, else None."""
        return self._db.get_summary(book_id, summary_type)

    def save_summary(self, book_id: str, summary_type: str, content: str) -> None:
        """Persist a newly generated summary to the database."""
        self._db.save_summary(book_id, summary_type, content)

    def update_summary(self, book_id: str, summary: str, summary_type: str = "Orta") -> None:
        """Convenience alias used by the UI (book_detail_view)."""
        self._db.save_summary(book_id, summary_type, summary)

    def list_summaries(self, book_id: str) -> list[dict]:
        """Return all summary records for a book."""
        return self._db.list_summaries(book_id)

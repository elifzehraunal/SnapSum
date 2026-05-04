"""JSON-based local database manager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.models import Book


class DatabaseManager:
    """Simple, swappable local persistence layer."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._write_payload({"books": []})

    def _read_payload(self) -> dict:
        with self.db_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_payload(self, payload: dict) -> None:
        with self.db_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def list_books(self, source: str | None = None) -> list[Book]:
        payload = self._read_payload()
        books = [Book.from_dict(item) for item in payload.get("books", [])]
        if source:
            return [book for book in books if book.source == source]
        return books

    def add_book(self, book: Book) -> None:
        payload = self._read_payload()
        payload.setdefault("books", []).append(book.to_dict())
        self._write_payload(payload)

    def get_book(self, book_id: str) -> Book | None:
        for book in self.list_books():
            if book.id == book_id:
                return book
        return None

    def update_summary(self, book_id: str, summary: str) -> None:
        payload = self._read_payload()
        for item in payload.get("books", []):
            if item["id"] == book_id:
                item["summary"] = summary
                break
        self._write_payload(payload)

    def delete_book(self, book_id: str) -> bool:
        """Delete a book by ID. Returns True if found and deleted."""
        payload = self._read_payload()
        books = payload.get("books", [])
        new_books = [b for b in books if b.get("id") != book_id]
        if len(new_books) == len(books):
            return False
        payload["books"] = new_books
        self._write_payload(payload)
        return True

    def seed_general_books(self, books: Iterable[Book]) -> None:
        """Populate default library only if empty."""
        if self.list_books(source="general"):
            return
        for book in books:
            self.add_book(book)

"""Forward-compatible repository abstractions.

Bu katman, bugün bellek içi çalışır; ileride SQLite/PostgreSQL gibi gerçek
veritabanlarına geçişte aynı arayüz korunabilir.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import Book


@dataclass
class BookRepository:
    """In-memory repository with DB-ready method signatures."""

    _books: list[Book] = field(default_factory=list)

    def seed_general_books(self, books: list[Book]) -> None:
        if self.list_books(source="general"):
            return
        self._books.extend(books)

    def list_books(self, source: str | None = None) -> list[Book]:
        if source is None:
            return list(self._books)
        return [book for book in self._books if book.source == source]

    def add_book(self, book: Book) -> None:
        # TODO(db): INSERT INTO books(title, file_path, source, summary, ...)
        self._books.append(book)

    def update_summary(self, book_id: str, summary: str) -> None:
        # TODO(db): UPDATE books SET summary=? WHERE id=?
        for book in self._books:
            if book.id == book_id:
                book.summary = summary
                return

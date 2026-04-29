"""SQLite-based database manager for SnapSum.

Şema:
  books     → kitap/PDF kayıtları (genel + kişisel)
  summaries → her kitap için üretilen özetler (tip bazlı cache)

Bu modül Ibrahim'in önerdiği şemayı temel alır; mevcut uygulama
arayüzüyle (source/general/personal, category) uyumlu hale getirilmiştir.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

from app.models import Book


class DatabaseManager:
    """SQLite persistence layer for SnapSum."""

    DDL = """
    -- ────────────────────────────────────────────────────────────────────
    -- books: Hem genel (admin) hem kullanıcı PDF'lerini saklar.
    --   book_type → 'general' (admin kitaplar) | 'personal' (kullanıcı)
    -- ────────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS books (
        id          TEXT        PRIMARY KEY,          -- UUID
        title       TEXT        NOT NULL,
        author      TEXT        NOT NULL DEFAULT 'Bilinmiyor',
        file_path   TEXT        NOT NULL,
        book_type   TEXT        NOT NULL DEFAULT 'general',  -- general | personal
        category    TEXT        NOT NULL DEFAULT 'Genel',
        upload_date DATETIME    NOT NULL DEFAULT (datetime('now'))
    );

    -- ────────────────────────────────────────────────────────────────────
    -- summaries: Kitap başına, özet tipine göre cache tablosu.
    --   summary_type → 'Kısa' | 'Orta' | 'Uzun'
    -- ────────────────────────────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS summaries (
        id              INTEGER     PRIMARY KEY AUTOINCREMENT,
        book_id         TEXT        NOT NULL,
        summary_type    TEXT        NOT NULL,   -- 'Kısa' | 'Orta' | 'Uzun'
        content         TEXT        NOT NULL,
        created_at      DATETIME    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        UNIQUE (book_id, summary_type)          -- aynı tip için tek özet
    );
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Yield an auto-commit connection with row_factory set."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create tables if they don't exist yet."""
        with self._conn() as conn:
            conn.executescript(self.DDL)

    # ------------------------------------------------------------------
    # books CRUD
    # ------------------------------------------------------------------

    def add_book(self, book: Book) -> None:
        """Insert a book record. Silently ignores duplicate IDs."""
        sql = """
            INSERT OR IGNORE INTO books
                (id, title, author, file_path, book_type, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._conn() as conn:
            conn.execute(sql, (
                book.id,
                book.title,
                book.author,
                book.file_path,
                book.source,   # model'deki 'source' → DB'de 'book_type'
                book.category,
            ))

    def get_book(self, book_id: str) -> Book | None:
        """Fetch a single book by UUID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = ?", (book_id,)
            ).fetchone()
        return self._row_to_book(row) if row else None

    def list_books(self, source: str | None = None) -> list[Book]:
        """Return all books, optionally filtered by source (book_type)."""
        with self._conn() as conn:
            if source:
                rows = conn.execute(
                    "SELECT * FROM books WHERE book_type = ? ORDER BY upload_date DESC",
                    (source,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM books ORDER BY upload_date DESC"
                ).fetchall()
        return [self._row_to_book(r) for r in rows]

    def seed_general_books(self, books: Iterable[Book]) -> None:
        """Populate general library only if the table is empty."""
        with self._conn() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM books WHERE book_type = 'general'"
            ).fetchone()[0]
        if count == 0:
            for book in books:
                self.add_book(book)

    # ------------------------------------------------------------------
    # summaries CRUD
    # ------------------------------------------------------------------

    def get_summary(self, book_id: str, summary_type: str) -> str | None:
        """Return cached summary content, or None if not found."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT content FROM summaries WHERE book_id = ? AND summary_type = ?",
                (book_id, summary_type),
            ).fetchone()
        return row["content"] if row else None

    def save_summary(self, book_id: str, summary_type: str, content: str) -> None:
        """Insert or replace a summary for the given book + type pair."""
        sql = """
            INSERT INTO summaries (book_id, summary_type, content)
            VALUES (?, ?, ?)
            ON CONFLICT(book_id, summary_type) DO UPDATE SET
                content    = excluded.content,
                created_at = datetime('now')
        """
        with self._conn() as conn:
            conn.execute(sql, (book_id, summary_type, content))

    def list_summaries(self, book_id: str) -> list[dict]:
        """Return all summaries for a book as plain dicts."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT summary_type, content, created_at FROM summaries WHERE book_id = ?",
                (book_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_book(row: sqlite3.Row) -> Book:
        """Convert a DB row to a Book dataclass instance."""
        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            file_path=row["file_path"],
            source=row["book_type"],    # DB'de 'book_type' → model'de 'source'
            category=row["category"],
            created_at=row["upload_date"],
        )

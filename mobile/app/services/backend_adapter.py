"""Bridge layer between mobile UI and backend manager.

UI tarafını backend implementasyonundan ayırır. Gelecekte OCR, HTTP API
eklendiğinde bu adapter güncellenerek aynı arayüz korunur.

DB entegrasyonu:
  - summarize_pdf / summarize_image çağrılmadan önce DB'de özet aranır.
  - Yeni özet üretilirse hem DB'ye hem de eski JSON cache'e yazılır.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Any


@dataclass
class SummaryResult:
    """UI-friendly summary result."""

    success: bool
    message: str
    summary: str = ""
    from_cache: bool = False


@dataclass
class UserProfile:
    """Kullanıcının okuma profili ve karakter bilgisi."""
    character_name: str
    description: str
    dominant_category: str
    category_counts: dict


class BackendAdapter:
    """Mobile-facing adapter for backend manager usage."""

    # Okuyucu karakterleri (kategori → karakter)
    _CHARACTERS: dict[str, tuple[str, str]] = {
        "Bilim":   ("Kaşif",      "Bilimi seven, meraklı bir okuyucu."),
        "Tarih":   ("Tarihçi",    "Geçmişten ders çıkaran bir okuyucu."),
        "Dram":    ("Empatist",   "Duyguları derinlemesine hisseden bir okuyucu."),
        "Macera":  ("Maceracı",   "Heyecanı seven, cesur bir okuyucu."),
        "Felsefe": ("Düşünür",    "Hayatın anlamını sorgulayan bir okuyucu."),
        "Genel":   ("Çok Yönlü",  "Her türden kitap okuyan dengeli bir okuyucu."),
    }

    def __init__(self) -> None:
        self._backend: Any | None = None
        self._load_backend_manager()

    def _load_backend_manager(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.append(str(repo_root))

        cache_path = repo_root / "backend" / "database" / "summary_cache.json"
        api_key = os.getenv("GEMINI_API_KEY", "")

        try:
            from backend.backend_manager import BackendManager
            self._backend = BackendManager(
                cache_path=cache_path,
                gemini_api_key=api_key,
            )
        except Exception:
            self._backend = None

    @property
    def available(self) -> bool:
        return self._backend is not None

    # ------------------------------------------------------------------
    # Summarization (DB-first cache check)
    # ------------------------------------------------------------------

    def summarize(
        self,
        file_path: str | Path,
        summary_type: str,
        book_id: str | None = None,
        repository=None,
    ) -> SummaryResult:
        """Özetle. Önce DB'de ara, yoksa Gemini'ye sor ve DB'ye kaydet."""

        # 1) DB cache kontrolü
        if book_id and repository:
            cached = repository.get_summary(book_id, summary_type)
            if cached:
                return SummaryResult(
                    success=True,
                    message="Özet veritabanından getirildi.",
                    summary=cached,
                    from_cache=True,
                )

        # 2) Backend mevcut değilse hata döndür
        if not self._backend:
            return SummaryResult(
                success=False,
                message=(
                    "Backend manager yüklenemedi. "
                    "backend/backend_manager.py dosyasını kontrol edin."
                ),
            )

        # 3) Gemini ile özetle
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in (".jpg", ".jpeg", ".png"):
            result = self._backend.summarize_image(path, summary_type)
        else:
            result = self._backend.summarize_pdf(path, summary_type)

        # 4) Başarılıysa DB'ye kaydet
        if result.success and result.summary and book_id and repository:
            repository.save_summary(book_id, summary_type, result.summary)

        return SummaryResult(
            success=result.success,
            message=result.message,
            summary=result.summary,
            from_cache=result.from_cache,
        )

    # Geriye dönük uyumluluk için eski arayüz
    def summarize_pdf(self, pdf_path: str | Path, summary_length: str) -> SummaryResult:
        return self.summarize(pdf_path, summary_length)

    # ------------------------------------------------------------------
    # Category & title classification
    # ------------------------------------------------------------------

    def categorize_title(self, title: str) -> str:
        """Gemini ile kitap başlığına göre kategori belirle."""
        if not self._backend:
            return "Genel"
        return self._backend.categorize_title(title)

    # ------------------------------------------------------------------
    # User profile & recommendations
    # ------------------------------------------------------------------

    def get_user_profile(self, personal_books: list) -> UserProfile | None:
        """Kişisel kütüphaneden okuyucu karakteri üret."""
        if not personal_books:
            return None

        counts: dict[str, int] = {}
        for book in personal_books:
            cat = getattr(book, "category", "Genel")
            counts[cat] = counts.get(cat, 0) + 1

        dominant = max(counts, key=counts.get)
        char_name, char_desc = self._CHARACTERS.get(dominant, ("Okuyucu", "Dengeli bir okuyucu."))
        return UserProfile(
            character_name=char_name,
            description=char_desc,
            dominant_category=dominant,
            category_counts=counts,
        )

    def get_recommendations(self, profile: UserProfile, general_books: list) -> list:
        """Profile göre genel kütüphaneden kitap öner."""
        same_cat = [b for b in general_books if getattr(b, "category", "") == profile.dominant_category]
        others   = [b for b in general_books if getattr(b, "category", "") != profile.dominant_category]
        return (same_cat + others)[:6]

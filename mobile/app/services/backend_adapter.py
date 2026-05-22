"""Bridge layer between mobile UI and backend manager.

UI tarafını backend implementasyonundan ayırır. Gelecekte OCR, gerçek DB veya
HTTP API eklendiğinde bu adapter güncellenerek aynı arayüz korunur.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

from app.config import MISTRAL_API_KEY


@dataclass
class SummaryResult:
    """UI-friendly summary result."""

    success: bool
    message: str
    summary: str = ""
    from_cache: bool = False


class BackendAdapter:
    """Mobile-facing adapter for backend manager usage."""

    def __init__(self) -> None:
        self._backend: Any | None = None
        self._load_backend_manager()

    def _load_backend_manager(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.append(str(repo_root))

        cache_path = repo_root / "backend" / "database" / "summary_cache.json"
        
        from app.config import get_mistral_api_key
        api_key = get_mistral_api_key()

        try:
            from backend.backend_manager import BackendManager
            from backend.recommendation.engine import RecommendationEngine

            self._backend = BackendManager(
                cache_path=cache_path,
                mistral_api_key=api_key,
            )
            self._recommendation_engine = RecommendationEngine()
        except Exception:
            self._backend = None
            self._recommendation_engine = None

    def reload(self) -> None:
        """Reload configuration and re-initialize backend manager."""
        self._load_backend_manager()

    @property
    def available(self) -> bool:
        return self._backend is not None


    def extract_text(self, pdf_path: str | Path) -> str:
        if not self._backend:
            return ""
        return self._backend.extract_plain_text(pdf_path)

    def summarize_pdf(self, pdf_path: str | Path, summary_length: str, text_coverage: str = "Full") -> SummaryResult:
        if not self._backend:
            return SummaryResult(
                success=False,
                message=(
                    "Backend manager could not be loaded. Check backend/backend_manager.py "
                    "and dependencies."
                ),
            )
        result = self._backend.summarize_pdf(pdf_path=pdf_path, summary_length=summary_length, text_coverage=text_coverage)
        return SummaryResult(
            success=result.success,
            message=result.message,
            summary=result.summary,
            from_cache=result.from_cache,
        )

    def summarize_image(self, image_path: str | Path, summary_length: str, text_coverage: str = "Full") -> SummaryResult:
        if not self._backend:
            return SummaryResult(success=False, message="Backend manager could not be loaded.")
        result = self._backend.summarize_image(image_path=image_path, summary_length=summary_length, text_coverage=text_coverage)
        return SummaryResult(
            success=result.success,
            message=result.message,
            summary=result.summary,
            from_cache=result.from_cache,
        )

    def get_user_profile(self, personal_books: List[Any]) -> Any:
        """Get the user profile from reading history."""
        if not self._recommendation_engine:
            return None
        return self._recommendation_engine.analyze_history(personal_books)

    def get_recommendations(self, profile: Any, general_library: List[Any]) -> List[Any]:
        """Get book recommendations based on user profile."""
        if not self._recommendation_engine or not profile:
            return []
        return self._recommendation_engine.get_recommendations(profile, general_library)

    def categorize_title(self, title: str) -> str:
        """Categorize a book title using Mistral."""
        if not self._backend:
            return "Genel"
        return self._backend.categorize_title(title)

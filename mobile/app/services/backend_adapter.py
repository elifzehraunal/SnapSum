"""Bridge layer between mobile UI and backend manager.

UI tarafını backend implementasyonundan ayırır. Gelecekte OCR, gerçek DB veya
HTTP API eklendiğinde bu adapter güncellenerek aynı arayüz korunur.
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

    def extract_text(self, pdf_path: str | Path) -> str:
        if not self._backend:
            return ""
        return self._backend.extract_plain_text(pdf_path)

    def summarize_pdf(self, pdf_path: str | Path, summary_length: str) -> SummaryResult:
        if not self._backend:
            return SummaryResult(
                success=False,
                message=(
                    "Backend manager yüklenemedi. backend/backend_manager.py "
                    "dosyasını ve bağımlılıkları kontrol edin."
                ),
            )
        result = self._backend.summarize_pdf(pdf_path=pdf_path, summary_length=summary_length)
        return SummaryResult(
            success=result.success,
            message=result.message,
            summary=result.summary,
            from_cache=result.from_cache,
        )

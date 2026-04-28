"""SnapSum backend logic manager.

Bu dosya Flet arayüzünden çağrılabilecek backend mantığını içerir:
- PDF metin ayıklama ve normalize etme
- Uzun metni anlamlı parçalara bölme (chunking)
- Gemini ile map-reduce özetleme
- Aynı istekler için yerel cache kontrolü (JSON tabanlı)
- Hata yönetimi ve kullanıcı dostu mesajlar
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal

import fitz

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional at runtime
    genai = None


SummaryLength = Literal["Kısa", "Orta", "Uzun"]


@dataclass
class BackendResponse:
    """Standard response structure for UI integration."""

    success: bool
    message: str
    summary: str = ""
    from_cache: bool = False


class BackendManager:
    """Main business logic class for PDF summarization flow."""

    def __init__(
        self,
        cache_path: str | Path = "backend/database/summary_cache.json",
        gemini_api_key: str | None = None,
        model_name: str = "gemini-1.5-flash",
        chunk_min: int = 5000,
        chunk_max: int = 8000,
    ) -> None:
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self.cache_path.write_text("{}", encoding="utf-8")

        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        self.chunk_min = chunk_min
        self.chunk_max = chunk_max

        self._model = None
        if genai and gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self._model = genai.GenerativeModel(model_name)
            except Exception:
                # Anahtar geçersiz/bağlantı hatası gibi durumlarda uygulama çökmesin.
                self._model = None

    # ----------------------------
    # PDF extraction & normalization
    # ----------------------------
    def extract_plain_text(self, pdf_path: str | Path) -> str:
        """
        Extract plain text from PDF and normalize it.

        Not:
        - `page.get_text("text")` sadece metin katmanını alır.
        - Görseller doğrudan alınmaz; tablo/grafik içeriği metin katmanındaysa
          heuristik temizleme uygulanır.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF bulunamadı: {path}")

        all_pages: list[str] = []
        with fitz.open(path) as doc:
            for page in doc:
                page_text = page.get_text("text") or ""
                if page_text.strip():
                    all_pages.append(page_text)

        raw_text = "\n".join(all_pages)
        return self._normalize_text(raw_text)

    def _normalize_text(self, text: str) -> str:
        """Remove page markers/noise and normalize whitespace."""
        if not text.strip():
            return ""

        cleaned_lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Sayfa numarası benzeri satırlar: "12", "Sayfa 12", "- 12 -"
            if re.fullmatch(r"[-–—\s]*\d{1,4}[-–—\s]*", stripped):
                continue
            if re.fullmatch(r"(?i)sayfa\s+\d{1,4}", stripped):
                continue

            # Çok yoğun separator karakterleri (tablo çizgileri vb.) filtrele
            if re.fullmatch(r"[\|\-_=~.]{4,}", stripped):
                continue

            cleaned_lines.append(stripped)

        normalized = "\n".join(cleaned_lines)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = re.sub(r"[ \t]{2,}", " ", normalized)
        return normalized.strip()

    # ----------------------------
    # Chunking
    # ----------------------------
    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into 5000-8000 char chunks with paragraph awareness.

        Önce paragraf bazlı parçalar oluşturur, tek paragraf aşırı uzunsa
        güvenli fallback olarak karakter bazlı böler.
        """
        content = text.strip()
        if not content:
            return []

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= self.chunk_max:
                current = candidate
                continue

            if current:
                chunks.append(current)
                current = ""

            # Aşırı uzun tek paragrafı fallback ile böl.
            if len(paragraph) > self.chunk_max:
                start = 0
                while start < len(paragraph):
                    end = start + self.chunk_max
                    chunks.append(paragraph[start:end].strip())
                    start = end
            else:
                current = paragraph

        if current:
            chunks.append(current)

        # Çok kısa son parçaları mümkünse bir öncekiyle birleştir.
        balanced: list[str] = []
        for chunk in chunks:
            if balanced and len(chunk) < self.chunk_min:
                merged = f"{balanced[-1]}\n\n{chunk}"
                if len(merged) <= self.chunk_max + 1200:
                    balanced[-1] = merged
                    continue
            balanced.append(chunk)
        return balanced

    # ----------------------------
    # Gemini prompts & summary
    # ----------------------------
    def _instruction_for(self, summary_length: SummaryLength) -> str:
        prompts = {
            "Kısa": (
                "Metni tek bir paragrafta, en can alici noktalarla, "
                "akici ve sade bir Turkce ile ozetle."
            ),
            "Orta": (
                "Metni ana basliklar halinde, 5-10 madde ile ozetle. "
                "Her maddede kritik fikirleri koru."
            ),
            "Uzun": (
                "Metnin tum bolumlerini kapsayan detayli bir analiz sun. "
                "Ana fikirler, argumanlar ve onemli detaylari sistematik anlat."
            ),
        }
        return prompts[summary_length]

    def _cache_key(self, pdf_path: str | Path, summary_length: SummaryLength) -> str:
        path = Path(pdf_path)
        payload = f"{path.resolve()}::{summary_length}::{self.model_name}".encode("utf-8")
        return sha256(payload).hexdigest()

    def _load_cache(self) -> dict[str, dict]:
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_cache(self, cache: dict[str, dict]) -> None:
        self.cache_path.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def summarize_pdf(
        self,
        pdf_path: str | Path,
        summary_length: SummaryLength,
    ) -> BackendResponse:
        """Complete flow: cache check -> extract -> chunk -> Gemini map-reduce."""
        try:
            if summary_length not in ("Kısa", "Orta", "Uzun"):
                return BackendResponse(False, "Geçersiz özet uzunluğu seçimi.")

            cache_key = self._cache_key(pdf_path, summary_length)
            cache = self._load_cache()
            if cache_key in cache and cache[cache_key].get("summary"):
                return BackendResponse(
                    success=True,
                    message="Özet cache üzerinden getirildi.",
                    summary=cache[cache_key]["summary"],
                    from_cache=True,
                )

            if not self.gemini_api_key:
                return BackendResponse(
                    success=False,
                    message=(
                        "Gemini API anahtarı tanımlı değil. "
                        "Lütfen backend manager oluştururken anahtar verin."
                    ),
                )
            if not self._model:
                return BackendResponse(
                    success=False,
                    message=(
                        "Gemini modeli başlatılamadı. API anahtarı geçersiz veya "
                        "bağlantı sorunu olabilir."
                    ),
                )

            text = self.extract_plain_text(pdf_path)
            if not text:
                return BackendResponse(
                    success=False,
                    message="PDF içinde okunabilir metin bulunamadı.",
                )

            chunks = self.chunk_text(text)
            instruction = self._instruction_for(summary_length)

            # MAP step: her chunk için özet
            partials: list[str] = []
            for idx, chunk in enumerate(chunks, start=1):
                prompt = (
                    "Sen profesyonel bir kitap ozetleyicisisin. Sadece Turkce yaz.\n"
                    f"Mod: {summary_length}\n"
                    f"Sistem Talimati: {instruction}\n"
                    f"Parca {idx}/{len(chunks)}:\n{chunk}"
                )
                response = self._model.generate_content(prompt)
                part = (response.text or "").strip()
                if part:
                    partials.append(part)

            if not partials:
                return BackendResponse(
                    success=False,
                    message="Gemini yanıtı boş döndü. Lütfen tekrar deneyin.",
                )

            # REDUCE step: parçaları master özete dönüştür
            if len(partials) == 1:
                master_summary = partials[0]
            else:
                reduce_prompt = (
                    "Aşağıdaki parça özetlerini tek bir MASTER OZET haline getir.\n"
                    "Tutarlı, tekrar etmeyen, kaliteli bir Türkçe üret.\n"
                    f"Mod: {summary_length}\n"
                    f"Sistem Talimati: {instruction}\n\n"
                    + "\n\n---\n\n".join(partials)
                )
                reduce_response = self._model.generate_content(reduce_prompt)
                master_summary = (reduce_response.text or "").strip()

            if not master_summary:
                return BackendResponse(
                    success=False,
                    message="Master özet üretilemedi. Lütfen tekrar deneyin.",
                )

            cache[cache_key] = {
                "pdf_path": str(Path(pdf_path)),
                "summary_length": summary_length,
                "model": self.model_name,
                "summary": master_summary,
            }
            self._save_cache(cache)

            return BackendResponse(
                success=True,
                message="Özet başarıyla oluşturuldu.",
                summary=master_summary,
                from_cache=False,
            )

        except FileNotFoundError as error:
            return BackendResponse(False, f"PDF okunamadı: {error}")
        except ConnectionError:
            return BackendResponse(
                False,
                "İnternet bağlantısı hatası. Lütfen bağlantınızı kontrol edin.",
            )
        except TimeoutError:
            return BackendResponse(
                False,
                "Gemini isteği zaman aşımına uğradı. Tekrar deneyin.",
            )
        except Exception as error:  # kapsamlı güvenlik ağı
            return BackendResponse(
                False,
                f"Beklenmeyen bir hata oluştu: {error}",
            )


"""SnapSum backend logic manager.

Bu dosya Flet arayüzünden çağrılabilecek backend mantığını içerir:
- PDF metin ayıklama ve normalize etme
- Uzun metni anlamlı parçalara bölme (chunking)
- Mistral AI ile map-reduce özetleme (HTTP API)
- Aynı istekler için yerel cache kontrolü (JSON tabanlı)
- Hata yönetimi ve kullanıcı dostu mesajlar
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal

import fitz
import httpx

try:
    import PIL.Image
except Exception:
    PIL = None


MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

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

    # Özet moduna göre metnin ne kadarını işleyeceğimizi belirle
    TEXT_LIMITS: dict[str, int] = {
        "Kısa": 50_000,    # ~50K karakter yeterli
        "Orta": 150_000,   # ~150K karakter
        "Uzun": 500_000,   # ~500K karakter
    }

    def __init__(
        self,
        cache_path: str | Path = "backend/database/summary_cache.json",
        mistral_api_key: str | None = None,
        model_name: str = "mistral-small-latest",
        chunk_min: int = 20_000,
        chunk_max: int = 30_000,
    ) -> None:
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self.cache_path.write_text("{}", encoding="utf-8")

        self.mistral_api_key = mistral_api_key
        self.model_name = model_name
        self.chunk_min = chunk_min
        self.chunk_max = chunk_max

        self._ready = False
        if mistral_api_key:
            self._ready = True

    # ----------------------------
    # Mistral HTTP chat helper
    # ----------------------------
    def _chat(self, prompt: str, model: str | None = None) -> str:
        """Send a single-turn chat message to Mistral via HTTP and return the text."""
        if not self._ready:
            return ""
        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or self.model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = httpx.post(MISTRAL_API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return (data["choices"][0]["message"]["content"] or "").strip()

    def _chat_vision(self, prompt_text: str, image_b64: str, mime_type: str) -> str:
        """Send a vision request to Mistral via HTTP."""
        if not self._ready:
            return ""
        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "pixtral-large-latest",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                        },
                        {
                            "type": "text",
                            "text": prompt_text,
                        },
                    ],
                }
            ],
        }
        resp = httpx.post(MISTRAL_API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return (data["choices"][0]["message"]["content"] or "").strip()

    # ----------------------------
    # PDF extraction & normalization
    # ----------------------------
    def extract_plain_text(self, pdf_path: str | Path) -> str:
        """
        Extract plain text from PDF or TXT and normalize it.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")

        if path.suffix.lower() == ".txt":
            raw_text = path.read_text(encoding="utf-8", errors="replace")
            return self._normalize_text(raw_text)

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
    # Classification
    # ----------------------------
    def categorize_title(self, title: str) -> str:
        """Mistral kullanarak başlığa göre kategori tahmini yapar."""
        if not self._ready:
            return "Genel"

        prompt = (
            f"Sen bir kütüphanecisin. Verilen kitap/dosya adını analiz et ve "
            f"sadece şu kategorilerden birini seçerek cevap ver: "
            f"Bilim, Tarih, Dram, Macera, Felsefe, Genel.\n\n"
            f"Kitap Adı: {title}\nKategori:"
        )
        try:
            cat = self._chat(prompt)
            valid_cats = ["Bilim", "Tarih", "Dram", "Macera", "Felsefe", "Genel"]
            for v in valid_cats:
                if v.lower() in cat.lower():
                    return v
            return "Genel"
        except Exception:
            return "Genel"

    # ----------------------------
    # Mistral prompts & summary
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
        """Complete flow: cache check -> extract -> chunk -> Mistral map-reduce."""
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

            if not self.mistral_api_key:
                return BackendResponse(
                    success=False,
                    message=(
                        "Mistral API anahtarı tanımlı değil. "
                        "Lütfen .env dosyasına MISTRAL_API_KEY ekleyin."
                    ),
                )
            if not self._ready:
                return BackendResponse(
                    success=False,
                    message=(
                        "Mistral istemcisi başlatılamadı. API anahtarı geçersiz veya "
                        "bağlantı sorunu olabilir."
                    ),
                )

            text = self.extract_plain_text(pdf_path)
            if not text:
                return BackendResponse(
                    success=False,
                    message="PDF içinde okunabilir metin bulunamadı.",
                )

            # Özet moduna göre metni sınırla (hız optimizasyonu)
            text_limit = self.TEXT_LIMITS.get(summary_length, 500_000)
            if len(text) > text_limit:
                text = text[:text_limit]

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
                part = self._chat(prompt)
                if part:
                    partials.append(part)

            if not partials:
                return BackendResponse(
                    success=False,
                    message="Mistral yanıtı boş döndü. Lütfen tekrar deneyin.",
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
                master_summary = self._chat(reduce_prompt)

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
                "Mistral isteği zaman aşımına uğradı. Tekrar deneyin.",
            )
        except Exception as error:  # kapsamlı güvenlik ağı
            return BackendResponse(
                False,
                f"Beklenmeyen bir hata oluştu: {error}",
            )

    def summarize_image(
        self,
        image_path: str | Path,
        summary_length: SummaryLength,
    ) -> BackendResponse:
        """Extract text from image and summarize using Mistral Vision (Pixtral)."""
        try:
            if summary_length not in ("Kısa", "Orta", "Uzun"):
                return BackendResponse(False, "Geçersiz özet uzunluğu seçimi.")

            cache_key = self._cache_key(image_path, summary_length)
            cache = self._load_cache()
            if cache_key in cache and cache[cache_key].get("summary"):
                return BackendResponse(
                    success=True,
                    message="Özet cache üzerinden getirildi.",
                    summary=cache[cache_key]["summary"],
                    from_cache=True,
                )

            if not self._ready:
                return BackendResponse(
                    success=False,
                    message="Mistral istemcisi yüklenemedi.",
                )

            path = Path(image_path)
            if not path.exists():
                return BackendResponse(False, f"Görsel bulunamadı: {path}")

            # Görseli base64 formatına çevir
            image_data = path.read_bytes()
            b64_image = base64.b64encode(image_data).decode("utf-8")

            # Uzantıdan MIME type belirle
            ext = path.suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
            }
            mime_type = mime_map.get(ext, "image/jpeg")

            instruction = self._instruction_for(summary_length)
            prompt_text = (
                "Bu görseldeki metni dikkatlice oku ve aşağıdaki talimata göre özetle.\n"
                f"Mod: {summary_length}\n"
                f"Sistem Talimatı: {instruction}"
            )

            master_summary = self._chat_vision(prompt_text, b64_image, mime_type)

            if not master_summary:
                return BackendResponse(
                    success=False,
                    message="Görselden özet üretilemedi.",
                )

            cache[cache_key] = {
                "file_path": str(path),
                "summary_length": summary_length,
                "model": self.model_name,
                "summary": master_summary,
            }
            self._save_cache(cache)

            return BackendResponse(
                success=True,
                message="Görsel başarıyla özetlendi.",
                summary=master_summary,
                from_cache=False,
            )

        except FileNotFoundError as error:
            return BackendResponse(False, f"Dosya okunamadı: {error}")
        except ConnectionError:
            return BackendResponse(False, "İnternet bağlantısı hatası.")
        except Exception as error:
            return BackendResponse(False, f"Beklenmeyen bir hata oluştu: {error}")

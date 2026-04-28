"""Google Gemini integration service."""

from __future__ import annotations

from dataclasses import dataclass

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.chunking import chunk_text


SUMMARY_STYLE_PROMPTS = {
    "Kısa": "Metni en fazla 5 madde ile, hızlı okunabilir ve öz bir şekilde Türkçe özetle.",
    "Orta": "Metni Türkçe olarak dengeli detay seviyesinde, bölüm yapısını koruyarak özetle.",
    "Uzun": "Metni Türkçe olarak kapsamlı özetle; ana fikirler, argümanlar ve önemli detayları koru.",
}


@dataclass
class GeminiService:
    """Wrapper service for text summarization."""

    api_key: str = GEMINI_API_KEY
    model_name: str = GEMINI_MODEL

    def __post_init__(self) -> None:
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name) if self.api_key else None

    @property
    def is_configured(self) -> bool:
        return self._model is not None

    def summarize(
        self,
        text: str,
        length: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> str:
        """Summarize long text by chunking then combining."""
        if not self._model:
            raise RuntimeError("GEMINI_API_KEY tanımlı değil.")
        if length not in SUMMARY_STYLE_PROMPTS:
            raise ValueError("length must be one of: Kısa, Orta, Uzun.")

        prompt = SUMMARY_STYLE_PROMPTS[length]
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        if not chunks:
            return "Özetlenecek metin bulunamadı."

        partial_summaries: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            response = self._model.generate_content(
                [
                    (
                        "Sen bir profesyonel kitap özetleyicisisin. "
                        "Yalnızca Türkçe cevap ver."
                    ),
                    f"Özet modu: {length}. Talimat: {prompt}",
                    f"Parça {index}/{len(chunks)}:\n{chunk}",
                ]
            )
            partial_summaries.append(response.text.strip())

        if len(partial_summaries) == 1:
            return partial_summaries[0]

        final_response = self._model.generate_content(
            [
                "Aşağıdaki parça özetlerini birleştirip tek bir tutarlı Türkçe özet yaz.",
                f"Özet modu: {length}. Talimat: {prompt}",
                "\n\n".join(partial_summaries),
            ]
        )
        return final_response.text.strip()

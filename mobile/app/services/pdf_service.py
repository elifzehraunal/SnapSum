"""PDF processing service layer."""

from __future__ import annotations

from pathlib import Path
import fitz


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF pages.

    Uses page.get_text("text"), which naturally ignores image-only regions.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text("text").strip()
            if text:
                output.append(text)
    return "\n\n".join(output)

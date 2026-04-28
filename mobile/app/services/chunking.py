"""Chunking utility for long text."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks by character count."""
    normalized = text.strip()
    if not normalized:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be larger than overlap.")

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end])
        if end >= len(normalized):
            break
        start = end - overlap
    return chunks

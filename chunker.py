"""Paragraph-aware document chunking; the original fixed-window fallback is retained."""

from dataclasses import dataclass
import re

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """Keep paragraphs intact and repeat short document headings for context.

    CHUNK_SIZE is a soft body target, not a hard character window. An
    unusually long paragraph is packed by whole sentences; a sentence longer
    than the target stays intact. No body text is overlapped or discarded.
    """
    if config.CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be positive")
    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", doc.text) if p.strip()]
        if not paragraphs:
            continue
        # The supplied corpus starts each file with a short, single-line title.
        heading = ""
        if len(paragraphs) > 1 and "\n" not in paragraphs[0] and len(paragraphs[0]) <= 120:
            heading = paragraphs.pop(0)
        pieces: list[str] = []
        for paragraph in paragraphs:
            if len(paragraph) <= config.CHUNK_SIZE:
                pieces.append(paragraph)
                continue
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", paragraph)
            current = ""
            for sentence in sentences:
                combined = f"{current} {sentence}".strip()
                if current and len(combined) > config.CHUNK_SIZE:
                    pieces.append(current)
                    current = sentence
                else:
                    current = combined
            if current:
                pieces.append(current)
        for index, piece in enumerate(pieces):
            text = f"{heading}\n\n{piece}" if heading else piece
            chunks.append(Chunk(text, doc.source, index, "chunker.py::split_documents"))
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))

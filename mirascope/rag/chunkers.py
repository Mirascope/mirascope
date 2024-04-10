"""Chunkers for the RAG module."""
import uuid
from typing import Callable, Concatenate

from pydantic import BaseModel

from .types import Document


def base_chunk_fn(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
) -> list[Document]:
    """Chunk the text into chunks of size `chunk_size`."""
    chunks: list[Document] = []
    start: int = 0
    while start < len(text):
        end: int = min(start + chunk_size, len(text))
        chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
        start += chunk_size - chunk_overlap
    return chunks


class BaseChunker(BaseModel):
    """"""

    chunk_fn: Callable[Concatenate[str, ...], list[Document]] = base_chunk_fn

    def chunk(self, text: str) -> list[Document]:
        return self.chunk_fn(text)

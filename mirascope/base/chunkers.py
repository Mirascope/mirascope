import uuid
from typing import Any, Callable, Optional

from pydantic import BaseModel


class Document(BaseModel):
    """A document to be added to the vectorstore."""

    id: str
    text: str
    metadata: Optional[dict[str, Any]] = None


def base_chunk_fn(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
) -> list[Document]:
    chunks: list[Document] = []
    start: int = 0
    while start < len(text):
        end: int = min(start + chunk_size, len(text))
        chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
        start += chunk_size - chunk_overlap
    return chunks


class BaseChunker(BaseModel):
    chunk_fn: Callable[[str], list[Document]] = base_chunk_fn

    def chunk(self, text: str) -> list[Document]:
        return self.chunk_fn(text)

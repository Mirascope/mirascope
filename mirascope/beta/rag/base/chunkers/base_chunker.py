"""Chunkers for the RAG module."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from ..document import Document


class BaseChunker(BaseModel, ABC):
    """Base class for chunkers.

    Example:

    ```python
    from mirascope.rag import BaseChunker, Document


    class TextChunker(BaseChunker):
        chunk_size: int
        chunk_overlap: int

        def chunk(self, text: str) -> list[Document]:
            chunks: list[Document] = []
            start: int = 0
            while start < len(text):
                end: int = min(start + self.chunk_size, len(text))
                chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
                start += self.chunk_size - self.chunk_overlap
            return chunks
    ```
    """

    @abstractmethod
    def chunk(self, text: str) -> list[Document]:
        """Returns a Document that contains an id, text, and optionally metadata."""
        ...

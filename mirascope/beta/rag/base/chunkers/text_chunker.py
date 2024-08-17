"""Text chunker for the RAG module"""

import uuid

from ..document import Document
from .base_chunker import BaseChunker


class TextChunker(BaseChunker):
    """A text chunker that splits a text into chunks of a certain size and overlaps.

    Example:

    ```python
    from mirascope.rag import TextChunker

    text_chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunks = text_chunker.chunk("This is a long text that I want to split into chunks.")
    print(chunks)
    ```
    """

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

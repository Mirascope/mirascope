import uuid
from typing import Callable, ClassVar

from pydantic import BaseModel

from mirascope.base.types import BaseChunkerParams, Document


def base_chunker(text: str, params: BaseChunkerParams) -> list[Document]:
    chunks: list[Document] = []
    chunk_size = params.chunk_size or 0
    chunk_overlap = params.chunk_overlap or 0
    start: int = 0
    while start < len(text):
        end: int = min(start + chunk_size, len(text))
        chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
        start += chunk_size - chunk_overlap
    return chunks


class BaseChunker(BaseModel):
    chunker_params: ClassVar[BaseChunkerParams] = BaseChunkerParams(
        chunk_size=1000, chunk_overlap=0
    )
    chunk_fn: Callable[[str, BaseChunkerParams], list[Document]] = base_chunker

    def chunk(self, text: str) -> list[Document]:
        return self.chunk_fn(text, self.chunker_params)

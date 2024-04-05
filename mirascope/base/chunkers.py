from typing import Any, Callable, ClassVar, Optional

from pydantic import BaseModel

from mirascope.base.types import BaseChunkerParams


class BaseChunker(BaseModel):
    chunker_params: ClassVar[BaseChunkerParams] = BaseChunkerParams(
        chunk_size=1000, chunk_overlap=0
    )
    chunk_fn: Optional[Callable[[str], list[str]]]

    def chunk(self, text: str) -> list[str]:
        if self.chunk_fn:
            return self.chunk_fn(text, **self.chunker_params.kwargs())
        else:
            chunks: list[str] = []
            start = 0
            while start < len(text):
                end = min(start + self.chunker_params.chunk_size, len(text))
                chunks.append(text[start:end])
                start += (
                    self.chunker_params.chunk_size - self.chunker_params.chunk_overlap
                )
            return chunks

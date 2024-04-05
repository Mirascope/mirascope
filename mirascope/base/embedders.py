from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel

from .types import BaseEmbeddingParams

BaseEmbeddingT = TypeVar("BaseEmbeddingT", bound=BaseModel)


class BaseEmbedder(BaseModel, Generic[BaseEmbeddingT], ABC):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    embedding_params: ClassVar[BaseEmbeddingParams] = BaseEmbeddingParams(
        model="text-embedding-ada-002"
    )

    @abstractmethod
    def create_embeddings(self, inputs: list[str]) -> list[BaseEmbeddingT]:
        """A call to the embedder with multiple inputs"""
        ...  # pragma: no cover

    @abstractmethod
    def embed(self, input: str) -> BaseEmbeddingT:
        """A call to the embedder with a single input"""
        ...  # pragma: no cover

    @abstractmethod
    def create_embeddings_async(self, inputs: list[str]) -> list[BaseEmbeddingT]:
        """Asynchronously call the embedder with multiple inputs"""
        ...  # pragma: no cover

    @abstractmethod
    def embed_async(self, input: str) -> BaseEmbeddingT:
        """Asynchronously call the embedder with a single input"""
        ...  # pragma: no cover

"""Embedders for the RAG module."""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel

from ..base.types import BaseConfig
from .types import BaseEmbeddingParams, BaseEmbeddingResponse

BaseEmbeddingT = TypeVar("BaseEmbeddingT", bound=BaseEmbeddingResponse)


class BaseEmbedder(BaseModel, Generic[BaseEmbeddingT], ABC):
    """The base class abstract interface for interacting with LLM embeddings."""

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    embedding_params: ClassVar[BaseEmbeddingParams] = BaseEmbeddingParams(
        model="text-embedding-ada-002"
    )
    dimensions: Optional[int] = None
    configuration: ClassVar[BaseConfig] = BaseConfig(llm_ops=[], client_wrappers=[])
    _provider: ClassVar[str] = "base"

    @abstractmethod
    def embed(self, input: list[str]) -> BaseEmbeddingT:
        """A call to the embedder with a single input"""
        ...  # pragma: no cover

    @abstractmethod
    async def embed_async(self, input: list[str]) -> BaseEmbeddingT:
        """Asynchronously call the embedder with a single input"""
        ...  # pragma: no cover

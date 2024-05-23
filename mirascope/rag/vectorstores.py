"""Vectorstores for the RAG module."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Optional, TypeVar, Union

from pydantic import BaseModel

from ..base.types import BaseConfig
from .chunkers import BaseChunker, TextChunker
from .embedders import BaseEmbedder
from .types import BaseQueryResults, BaseVectorStoreParams, Document

BaseQueryResultsT = TypeVar("BaseQueryResultsT", bound=BaseQueryResults)


class BaseVectorStore(BaseModel, Generic[BaseQueryResultsT], ABC):
    """The base class abstract interface for interacting with vectorstores."""

    api_key: ClassVar[Optional[str]] = None
    index_name: ClassVar[Optional[str]] = None
    chunker: ClassVar[BaseChunker] = TextChunker(chunk_size=1000, chunk_overlap=200)
    embedder: ClassVar[BaseEmbedder]
    vectorstore_params: ClassVar[BaseVectorStoreParams] = BaseVectorStoreParams()
    configuration: ClassVar[BaseConfig] = BaseConfig()
    _provider: ClassVar[str] = "base"

    @abstractmethod
    def retrieve(self, text: str, **kwargs: Any) -> BaseQueryResultsT:
        """Queries the vectorstore for closest match"""
        ...  # pragma: no cover

    @abstractmethod
    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        ...  # pragma: no cover

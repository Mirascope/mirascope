"""Vectorstores for the RAG module."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel

from .chunkers import BaseChunker, TextChunker
from .config import BaseConfig
from .document import Document
from .embedders import BaseEmbedder
from .query_results import BaseQueryResults
from .vectorstore_params import BaseVectorStoreParams

BaseQueryResultsT = TypeVar("BaseQueryResultsT", bound=BaseQueryResults)


class BaseVectorStore(BaseModel, Generic[BaseQueryResultsT], ABC):
    """The base class abstract interface for interacting with vectorstores."""

    api_key: ClassVar[str | None] = None
    index_name: ClassVar[str | None] = None
    chunker: ClassVar[BaseChunker] = TextChunker(chunk_size=1000, chunk_overlap=200)
    embedder: ClassVar[BaseEmbedder]
    vectorstore_params: ClassVar[BaseVectorStoreParams] = BaseVectorStoreParams()
    configuration: ClassVar[BaseConfig] = BaseConfig()
    _provider: ClassVar[str] = "base"

    @abstractmethod
    def retrieve(self, text: str, **kwargs: Any) -> BaseQueryResultsT:  # noqa: ANN401
        """Queries the vectorstore for closest match"""
        ...

    @abstractmethod
    def add(self, text: str | list[Document], **kwargs: Any) -> None:  # noqa: ANN401
        """Takes unstructured data and upserts into vectorstore"""
        ...

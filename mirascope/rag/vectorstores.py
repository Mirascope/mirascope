"""Vectorstores for the RAG module."""
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional, Union

from pydantic import BaseModel

from .chunkers import BaseChunker
from .embedders import BaseEmbedder
from .types import BaseVectorStoreParams, Document


class BaseVectorStore(BaseModel, ABC):
    api_key: ClassVar[Optional[str]] = None
    index_name: ClassVar[Optional[str]] = None
    chunker: ClassVar[BaseChunker] = BaseChunker()
    embedder: ClassVar[Optional[BaseEmbedder]] = BaseEmbedder
    vectorstore_params: ClassVar[BaseVectorStoreParams] = BaseVectorStoreParams()

    @abstractmethod
    def retrieve(
        self, text: Optional[str] = None, **kwargs: Any
    ) -> Optional[list[list[str]]]:
        """Queries the vectorstore for closest match"""
        ...  # pragma: no cover

    @abstractmethod
    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        ...  # pragma: no cover

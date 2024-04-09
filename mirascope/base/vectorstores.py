from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Optional, Union

from pydantic import BaseModel

from .chunkers import BaseChunker, Document
from .embedders import BaseEmbedder
from .types import BaseVectorStoreParams


class BaseVectorStore(BaseModel, ABC):
    api_key: ClassVar[Optional[str]] = None
    index_name: ClassVar[Optional[str]] = None
    chunker: Union[Callable, BaseChunker] = BaseChunker()
    embedder: ClassVar[Optional[BaseEmbedder]] = BaseEmbedder
    vectorstore_params: ClassVar[BaseVectorStoreParams] = BaseVectorStoreParams()

    @abstractmethod
    def get_documents(
        self, text: Optional[str] = None, **kwargs: Any
    ) -> Optional[list[list[str]]]:
        """Queries the vectorstore for closest match"""
        ...  # pragma: no cover

    @abstractmethod
    def add_documents(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        ...  # pragma: no cover

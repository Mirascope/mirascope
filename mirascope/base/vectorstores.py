from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel

from mirascope.base.chunkers import BaseChunker
from mirascope.base.embedders import BaseEmbedder
from mirascope.openai.embedders import OpenAIEmbedder

from .types import BaseVectorStoreParams

BaseQueryResultT = TypeVar("BaseQueryResultT", bound=BaseModel)


class BaseVectorStore(BaseModel, Generic[BaseQueryResultT], ABC):
    vectorstore_api_key: Optional[str] = None
    index_name: Optional[str] = None
    chunker: Optional[BaseChunker] = BaseChunker()
    embedder: Optional[BaseEmbedder] = OpenAIEmbedder()
    vectorstore_params: ClassVar[BaseVectorStoreParams] = BaseVectorStoreParams()

    @abstractmethod
    def get_documents(self, **kwargs: Any) -> list[BaseQueryResultT]:
        """Queries the vectorstore for closest match"""
        ...  # pragma: no cover

    @abstractmethod
    def add_documents(self, **kwargs: Any) -> dict:
        """Takes unstructured data and upserts into vectorstore"""
        ...  # pragma: no cover

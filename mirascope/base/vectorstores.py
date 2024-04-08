from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional, Union

from pydantic import BaseModel

from mirascope.base.chunkers import BaseChunker
from mirascope.base.embedders import BaseEmbedder
from mirascope.openai.embedders import OpenAIEmbedder

from .types import BaseVectorStoreParams, Document


class BaseVectorStore(BaseModel, ABC):
    vectorstore_api_key: Optional[str] = None
    index_name: ClassVar[Optional[str]] = None
    chunker: ClassVar[BaseChunker] = BaseChunker()
    embedder: ClassVar[Optional[BaseEmbedder]] = OpenAIEmbedder()
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

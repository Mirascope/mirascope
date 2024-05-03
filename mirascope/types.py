from typing import TypeVar

from .base import BaseCall, BaseExtractor
from .rag.chunkers import BaseChunker
from .rag.embedders import BaseEmbedder
from .rag.vectorstores import BaseVectorStore

BaseCallT = TypeVar("BaseCallT", bound=BaseCall)
BaseExtractorT = TypeVar("BaseExtractorT", bound=BaseExtractor)
BaseVectorStoreT = TypeVar("BaseVectorStoreT", bound=BaseVectorStore)
BaseChunkerT = TypeVar("BaseChunkerT", bound=BaseChunker)
BaseEmbedderT = TypeVar("BaseEmbedderT", bound=BaseEmbedder)

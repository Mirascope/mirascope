"""Base types and abstract interfaces for typing Mirascope RAG."""
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class BaseVectorStoreParams(BaseModel):
    """The parameters with which to make a vectorstore."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return kwargs


class BaseEmbeddingParams(BaseModel):
    """The parameters with which to make an embedding."""

    model: str
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the embedder as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return kwargs


class BaseQueryResults(BaseModel):
    """The results of a query."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class Document(BaseModel):
    """A document to be added to the vectorstore."""

    id: str
    text: str
    metadata: Optional[dict[str, Any]] = None

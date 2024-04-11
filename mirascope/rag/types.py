"""Base types and abstract interfaces for typing Mirascope RAG."""
from typing import Any, Callable, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseVectorStoreParams(BaseModel):
    """The parameters with which to make a vectorstore."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    weave: Optional[Callable[[T], T]] = None

    def kwargs(
        self,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        extra_exclude = {"weave"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        kwargs = {
            key: value
            for key, value in self.model_dump(exclude=exclude).items()
            if value is not None
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

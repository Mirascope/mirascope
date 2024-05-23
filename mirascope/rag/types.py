"""Base types and abstract interfaces for typing Mirascope RAG."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict

ResponseT = TypeVar("ResponseT", bound=Any)


class BaseEmbeddingResponse(BaseModel, Generic[ResponseT], ABC):
    """A base abstract interface for LLM embedding responses.

    Attributes:
        response: The original response from whichever model response this wraps.
    """

    response: ResponseT
    start_time: float  # The start time of the embedding in ms
    end_time: float  # The end time of the embedding in ms

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def embeddings(self) -> Optional[Union[list[list[float]], list[list[int]]]]:
        """Should return the embedding of the response.

        If there are multiple choices in a response, this method should select the 0th
        choice and return it's embedding.
        """
        ...  # pragma: no cover


T = TypeVar("T")


class BaseVectorStoreParams(BaseModel):
    """The parameters with which to make a vectorstore."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(
        self,
    ) -> dict[str, Any]:
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

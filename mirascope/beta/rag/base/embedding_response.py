from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

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
    def embeddings(self) -> list[list[float]] | list[list[int]] | None:
        """Should return the embedding of the response.

        If there are multiple choices in a response, this method should select the 0th
        choice and return it's embedding.
        """
        ...

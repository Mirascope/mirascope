"""This module contains the base classes for async structured streams from LLMs."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ._utils import BaseType

_ChunkT = TypeVar("_ChunkT", bound=Any)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BaseAsyncStructuredStream(Generic[_ChunkT, _ResponseModelT], ABC):
    """A base class for async streaming structured outputs from LLMs."""

    stream: AsyncGenerator[_ChunkT, None]
    response_model: type[_ResponseModelT]
    json_mode: bool

    def __init__(
        self,
        stream: AsyncGenerator[_ChunkT, None],
        response_model: type[_ResponseModelT],
        json_mode: bool = False,
    ):
        """Initializes an instance of `BaseAsyncStructuredStream`."""
        self.stream = stream
        self.response_model = response_model
        self.json_mode = json_mode

    @abstractmethod
    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

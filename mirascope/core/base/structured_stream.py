"""This module contains the base classes for structured streams from LLMs."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ._utils import BaseType

_ChunkT = TypeVar("_ChunkT", bound=Any)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BaseStructuredStream(Generic[_ChunkT, _ResponseModelT], ABC):
    """A base class for streaming structured outputs from LLMs."""

    stream: Generator[_ChunkT, None, None]
    response_model: type[_ResponseModelT]
    json_mode: bool

    def __init__(
        self,
        stream: Generator[_ChunkT, None, None],
        response_model: type[_ResponseModelT],
        json_mode: bool = False,
    ):
        """Initializes an instance of `BaseStructuredStream`."""
        self.stream = stream
        self.response_model = response_model
        self.json_mode = json_mode

    @abstractmethod
    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""

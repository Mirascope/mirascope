"""This module contains the base classes for structured streams from LLMs."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

_ChunkT = TypeVar("_ChunkT", bound=Any)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel)


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

"""A base module for convenience around streaming tools."""
from abc import ABC, abstractmethod
from typing import (
    AsyncGenerator,
    Generator,
    Generic,
    Literal,
    Optional,
    TypeVar,
    overload,
)

import pydantic
from pydantic import BaseModel

from .tools import BaseTool
from .types import BaseCallResponseChunk

BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)


class BaseToolStream(BaseModel, Generic[BaseCallResponseChunkT, BaseToolT], ABC):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: Literal[True],
    ) -> Generator[Optional[BaseToolT], None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: Literal[False],
    ) -> Generator[BaseToolT, None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: bool,
    ) -> Generator[Optional[BaseToolT], None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    def from_stream(cls, stream, allow_partial=False):
        """Yields tools from the given stream of chunks."""
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: Literal[True],
    ) -> AsyncGenerator[Optional[BaseToolT], None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: Literal[False],
    ) -> AsyncGenerator[BaseToolT, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: bool,
    ) -> AsyncGenerator[Optional[BaseToolT], None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    async def from_async_stream(cls, async_stream, allow_partial=False):
        """Yields tools asynchronously from the given async stream of chunks."""
        yield ...  # type: ignore # pragma: no cover

    ############################## PRIVATE METHODS ###################################

    @classmethod
    def _check_version_for_partial(cls, partial: bool) -> None:
        """Checks that the correct version of Pydantic is installed to use partial."""
        if partial and int(pydantic.__version__.split(".")[1]) < 7:
            raise ImportError(
                "You must have `pydantic==^2.7.0` to stream tools. "
                f"Current version: {pydantic.__version__}"
            )  # pragma: no cover

"""A base module for convenience around streaming tools."""
from abc import ABC, abstractmethod
from typing import (
    AsyncGenerator,
    Generator,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)

import pydantic
from pydantic import BaseModel

from ..partial import Partial
from .tools import BaseTool
from .types import BaseCallResponseChunk

# if int(pydantic.__version__.split(".")[1]) < 7:
#     raise ImportError(
#         "You must have `pydantic==^2.7.0` to stream tools. "
#         f"Current version: {pydantic.__version__}"
#     )


# BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
# BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)


class BaseToolStream(BaseModel, ABC):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunk, None, None],
        partial: Literal[True],
    ) -> Generator[Optional[Partial[BaseTool]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunk, None, None],
        partial: Literal[False],
    ) -> Generator[BaseTool, None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunk, None, None],
        partial: bool,
    ) -> Generator[Union[BaseTool, Optional[Partial[BaseTool]]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def from_stream(cls, stream, partial=False):
        """Yields tools from the given stream of chunks."""
        ...  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[BaseCallResponseChunk, None],
        partial: Literal[True],
    ) -> Generator[Optional[Partial[BaseTool]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[BaseCallResponseChunk, None],
        partial: Literal[False],
    ) -> Generator[BaseTool, None, None]:
        ...  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        async_stream: AsyncGenerator[BaseCallResponseChunk, None],
        partial: bool,
    ) -> Generator[Union[BaseTool, Optional[Partial[BaseTool]]], None, None]:
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    async def from_async_stream(cls, async_stream, partial=False):
        """Yields tools asynchronously from the given async stream of chunks."""
        ...  # pragma: no cover

    ############################## PRIVATE METHODS ###################################

    @classmethod
    def _check_version_for_partial(cls, partial: bool) -> None:
        """Checks that the correct version of Pydantic is installed to use partial."""
        # BUG: https://github.com/pydantic/pydantic/issues/9191
        # prevents using partial json parsing for now
        if partial and int(pydantic.__version__.split(".")[1]) < 7:
            raise ImportError(
                "You must have `pydantic==^2.7.0` to stream tools. "
                f"Current version: {pydantic.__version__}"
            )

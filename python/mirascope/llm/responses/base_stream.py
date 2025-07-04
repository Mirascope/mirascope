"""Base classes for streaming responses from LLMs."""

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Generic

from typing_extensions import TypeVar

from .finish_reason import FinishReason
from .response import Response
from .usage import Usage

T = TypeVar("T", bound=object | None, default=None)


class BaseStream(Generic[T]):
    """Base class for streaming responses from LLMs.

    Provides common metadata fields that are populated as the stream is consumed.
    """

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""


class BaseSyncStream(BaseStream[T]):
    """Base class for synchronous streaming responses from LLMs."""

    def __iter__(self) -> Iterator:
        """Iterate through the chunks of the stream.

        Returns:
            An iterator yielding StreamChunk objects.
        """
        raise NotImplementedError()

    def to_response(self) -> Response:
        """Convert the stream to a complete response.

        This method consumes the stream and aggregates all chunks into a single
        response object, providing access to metadata like usage statistics and
        the complete response content.

        Returns:
            A Response object containing the aggregated stream data.

        Note:
            This method will consume the stream if it hasn't been consumed yet.
            If the stream has already been iterated through, it will use the
            previously collected data.
        """
        raise NotImplementedError()


class BaseAsyncStream(BaseStream[T]):
    """Base class for asynchronous streaming responses from LLMs."""

    def __aiter__(self) -> AsyncIterator:
        """Iterate through the chunks of the stream asynchronously.

        Returns:
            An async iterator yielding StreamChunk objects.
        """
        raise NotImplementedError()

    async def to_response(self) -> Response:
        """Convert the stream to a complete response asynchronously.

        This method consumes the stream and aggregates all chunks into a single
        response object, providing access to metadata like usage statistics and
        the complete response content.

        Returns:
            A Response object containing the aggregated stream data.

        Note:
            This method will consume the stream if it hasn't been consumed yet.
            If the stream has already been iterated through, it will use the
            previously collected data.
        """
        raise NotImplementedError()

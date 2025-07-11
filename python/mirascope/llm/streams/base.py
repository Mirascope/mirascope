"""Base interface for streaming responses from LLMs."""

from decimal import Decimal
from typing import Generic

from typing_extensions import TypeVar

from ..context import Context
from ..responses import FinishReason, Response, Usage

DepsT = TypeVar("DepsT", default=None)
FormatT = TypeVar("FormatT", bound=object | None, default=None)


class BaseStream(Generic[DepsT, FormatT]):
    """Base class for streaming responses from LLMs.
    Provides common metadata fields that are populated as the stream is consumed.
    """

    context: Context[DepsT]
    """The context used to generate this stream."""

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""

    def to_response(self) -> Response[DepsT, FormatT]:
        """Convert the stream to a complete response.

        This method consumes the stream and aggregates all chunks into a single response
        object, providing access to metadata like usage statistics and the complete
        response content.

        The Response is reconstructed on a best-effort basis, but it may not exactly
        match the response that would have been generated if not using streaming.

        Returns:
            A Response object containing the aggregated stream data.

        Raises:
            ValueError: If the stream has not been fully exhausted before calling this method.
                The stream must be completely iterated through to ensure all data is
                collected.

        """
        raise NotImplementedError()

    def format(self) -> FormatT:
        """Format the already-streamed content using the response format parser.

        It will parse the response content according to the specified format (if present)
        and return a structured object. Returns None if there was no format.

        `stream.format()` is equivalent to calling `stream.to_response().format()`.

        Returns:
            The formatted response object of type T. May be a partial response
            if the stream has not been exhausted.

        Raises:
            ValueError: If the response cannot be formatted according to the
                specified format.
        """
        raise NotImplementedError()

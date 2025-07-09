"""Base interface for streaming responses from LLMs."""

from decimal import Decimal
from typing import Generic

from typing_extensions import TypeVar

from ..context import Context
from ..responses import FinishReason, Response, Usage
from ..types import DepsT

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

"""Base interface for streaming responses from LLMs."""

from decimal import Decimal
from typing import Generic, Literal, overload

from ..formatting import FormatT, Partial
from ..responses import FinishReason, Response, Usage


class BaseStream(Generic[FormatT]):
    """Base class for streaming responses from LLMs.
    Provides common metadata fields that are populated as the stream is consumed.
    """

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""

    def to_response(self) -> Response[FormatT]:
        """Convert the stream to a complete response.

        This method converts all the already-streamed content into a response object.
        Content that has not yet been iterated over will not be included, even if the
        stream is not exhausted.

        The Response is reconstructed on a best-effort basis, but it may not exactly
        match the response that would have been generated if not using streaming.

        Returns:
            A Response object containing the aggregated stream data.
        """
        raise NotImplementedError()

    @overload
    def format(self, partial: Literal[True]) -> Partial[FormatT]:
        """Format the response into a Partial[BaseModel] (with optional fields)."""
        ...

    @overload
    def format(self, partial: Literal[False] = False) -> FormatT:
        """Format the response into a Pydantic BaseModel."""
        ...

    def format(self, partial: bool = False) -> FormatT | Partial[FormatT]:
        """Format the already-streamed content using the response format parser.

        It will parse the response content according to the specified format (if present)
        and return a structured object. Returns None if there was no format.

        When called with `partial=True`, it will return a partial of the model, with all
        fields optional. This is most useful for generating partial structured outputs
        while the content is still streaming.

        Returns:
            The formatted response model.

        Raises:
            ValueError: If the response cannot be formatted according to the
                specified format.
        """
        raise NotImplementedError()

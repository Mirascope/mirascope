"""This module contains the `AnthropicCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from anthropic.types import (
    Message,
    MessageDeltaUsage,
    MessageStartEvent,
    MessageStreamEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    Usage,
)

from ..base import BaseCallResponseChunk, types
from ..base.types import CostMetadata
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)

FinishReason = Message.__annotations__["stop_reason"]


class AnthropicCallResponseChunk(
    BaseCallResponseChunk[MessageStreamEvent, FinishReason]
):
    """A convenience wrapper around the Anthropic `ChatCompletionChunk` streamed chunks.

    When calling the Anthropic API using a function decorated with `anthropic_call` and
    `stream` set to `True`, the stream will contain `AnthropicResponseChunk` instances
    with properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.anthropic import anthropic_call


    @anthropic_call("claude-3-5-sonnet-20240620", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # response is an `AnthropicStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        return (
            self.chunk.delta.text
            if self.chunk.type == "content_block_delta"
            and self.chunk.delta.type == "text_delta"
            else ""
        )

    @property
    def finish_reasons(self) -> list[FinishReason] | None:
        """Returns the finish reason of the response."""
        if (
            isinstance(self.chunk, RawMessageStartEvent)
            and self.chunk.message.stop_reason
        ):
            return [str(self.chunk.message.stop_reason)]
        return None

    @property
    def model(self) -> str | None:
        """Returns the name of the response model."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.model
        return None

    @property
    def id(self) -> str | None:
        """Returns the id of the response."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.id
        return None

    @property
    def usage(self) -> Usage | MessageDeltaUsage | None:
        """Returns the usage of the message."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.usage
        elif isinstance(self.chunk, RawMessageDeltaEvent):
            return self.chunk.usage
        return None

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if (usage := self.usage) and isinstance(usage, Usage):
            return usage.input_tokens
        return None

    @property
    def cached_tokens(self) -> int | None:
        """Returns the number of cached tokens."""
        if (usage := self.usage) and isinstance(usage, Usage):
            return getattr(usage, "cache_read_input_tokens", 0)
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return CostMetadata(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cached_tokens=self.cached_tokens,
        )

    @property
    def common_finish_reasons(self) -> list[types.FinishReason] | None:
        """Provider-agnostic finish reasons."""
        return _convert_finish_reasons_to_common_finish_reasons(
            cast(list[str], self.finish_reasons)
        )

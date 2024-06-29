"""This module contains the `AnthropicCallResponseChunk` class."""

from anthropic.types import (
    MessageStartEvent,
    MessageStreamEvent,
    RawMessageDeltaEvent,
    Usage,
)

from ..base import BaseCallResponseChunk


class AnthropicCallResponseChunk(BaseCallResponseChunk[MessageStreamEvent]):
    '''A convenience wrapper around the Anthropic `ChatCompletionChunk` streamed chunks.

    When calling the Anthropic API using a function decorated with `anthropic_call` and
    `stream` set to `True`, the stream will contain `AnthropicResponseChunk` instances
    with properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.anthropic import anthropic_call

    @anthropic_call(model="claude-3-5-sonnet-20240620", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `AnthropicStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        return (
            self.chunk.delta.text
            if self.chunk.type == "content_block_delta"
            and self.chunk.delta.type in ["text", "text_delta"]
            else ""
        )

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
    def finish_reasons(self) -> list[str] | None:
        """Returns the finish reason of the response."""
        return self.chunk.message.stop_reason

    @property
    def usage(self) -> Usage | None:
        """Returns the usage of the message."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.usage
        elif isinstance(self.chunk, RawMessageDeltaEvent):
            return self.chunk.usage
        return None

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if usage := self.usage:
            return usage.input_tokens if hasattr(usage, "input_tokens") else None
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None

    def __str__(self) -> str:
        """Returns the string content of the chunk."""
        return self.content

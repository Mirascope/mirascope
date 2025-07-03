"""Interface for streaming responses from LLMs."""

from collections.abc import Iterator
from decimal import Decimal
from typing import Generic

from typing_extensions import TypeVar

from .finish_reason import FinishReason
from .response import Response
from .stream_chunk import StreamChunk
from .usage import Usage

T = TypeVar("T", bound=object | None, default=None)


class Stream(Generic[T]):
    """A synchronous stream of response chunks from an LLM.

    This class supports iteration to process chunks as they arrive from the model.

    Example:
        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream = answer_question.stream("What is the capital of France?")
        for chunk in stream:
            print(chunk.content, end="", flush=True)
        ```
    """

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""

    def __iter__(self) -> Iterator[StreamChunk[T]]:
        """Iterate through the chunks of the stream.

        Returns:
            An iterator yielding StreamChunk objects.
        """
        raise NotImplementedError()

    def to_response(self) -> Response[T]:
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

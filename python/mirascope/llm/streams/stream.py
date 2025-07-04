"""Interface for streaming responses from LLMs."""

from collections.abc import Iterator
from decimal import Decimal

from ..content import ContentChunk
from ..responses import FinishReason, Response, Usage


class BaseStream:
    """Base class for streaming responses from LLMs.
    Provides common metadata fields that are populated as the stream is consumed.
    """

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""

    def to_response(self) -> Response:
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


class Stream(BaseStream):
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

    def __iter__(self) -> Iterator[ContentChunk]:
        """Iterate through the chunks of the stream.

        Returns:
            An iterator yielding ContentChunk objects.
        """
        raise NotImplementedError()

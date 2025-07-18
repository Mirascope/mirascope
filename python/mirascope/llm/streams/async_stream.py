"""Interface for streaming responses asynchronously from LLMs."""

from collections.abc import AsyncIterator

from ..content import ContentChunk
from ..context import DepsT
from ..formatting import FormatT
from .base import BaseStream
from .group_types import AsyncGroup


class AsyncStream(BaseStream[DepsT, FormatT]):
    """An asynchronous stream of response chunks from an LLM.

    This class supports async iteration to process chunks as they arrive from the model.

    Example:
        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream = await answer_question.stream_async("What is the capital of France?")
        async for chunk in stream:
            print(chunk.content, end="", flush=True)
        ```
    """

    def __aiter__(self) -> AsyncIterator[ContentChunk]:
        """Iterate through the chunks of the stream asynchronously.

        Returns:
            An async iterator yielding ContentChunk objects.
        """
        raise NotImplementedError()

    def groups(self) -> AsyncIterator[AsyncGroup]:
        """Iterate through grouped chunks of the stream asynchronously.

        Returns:
            An async iterator yielding AsyncGroup objects that contain related chunks.
        """
        raise NotImplementedError()

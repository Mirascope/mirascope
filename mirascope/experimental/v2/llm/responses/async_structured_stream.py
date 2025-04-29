"""Interfaces for asynchronous streaming structured responses from LLMs."""

from collections.abc import AsyncIterator
from typing import Generic

from typing_extensions import TypeVar

from ..types import Dataclass
from .stream_chunk import StreamChunk

T = TypeVar("T", bound=Dataclass | None, default=None)


class AsyncStructuredStream(Generic[T]):
    """An asynchronous stream of partial structured outputs from an LLM.

    This class supports async iteration to process structured outputs as they arrive
    from the model.

    Example:
        ```python
        from mirascope import llm

        @llm.response_format(parser="json")
        class Book:
            title: str
            author: str

        @llm.call("openai:gpt-4o-mini", response_format=Book)
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream = await answer_question.stream_async("What is the capital of France?")
        async for partial_book in stream:
            print(partial_book)
        ```
    """

    def __aiter__(self) -> AsyncIterator[StreamChunk[T]]:
        """Iterate through the structured outputs of the stream asynchronously.

        Returns:
            An async iterator yielding structured output objects.
        """
        raise NotImplementedError()

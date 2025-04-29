"""Interfaces for streaming structured responses from LLMs.

This module provides interfaces for both synchronous and asynchronous streaming
of responses from language models. Streaming allows for incremental processing of
responses as they are generated, rather than waiting for the complete response.

TODO: this interface is missing stuff from v1 like usage etc. that we collect during
the stream for convenience (e.g. calling stream.cost after the stream is done).
"""

from collections.abc import Iterator
from typing import Generic

from typing_extensions import TypeVar

from ..types import Dataclass
from .stream_chunk import StreamChunk

T = TypeVar("T", bound=Dataclass | None, default=None)


class StructuredStream(Generic[T]):
    """A synchronous stream of partial structured outputs from an LLM.

    This class supports iteration to process structured outputs as they arrive from the
    model.

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

        stream = answer_question.stream("What is the capital of France?")
        for partial_book in stream:
            print(partial_book)
        ```
    """

    def __iter__(self) -> Iterator[StreamChunk[T]]:
        """Iterate through the structured outputs of the stream.

        Returns:
            An iterator yielding structured output objects.
        """
        raise NotImplementedError()

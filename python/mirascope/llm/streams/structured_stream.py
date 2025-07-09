"""Interfaces for streaming structured responses from LLMs.

This module provides interfaces for both synchronous and asynchronous streaming
of responses from language models. Streaming allows for incremental processing of
responses as they are generated, rather than waiting for the complete response.
"""

from collections.abc import Iterator

from ..content import ContentChunk
from ..types import DepsT, FormatT
from .base import BaseStream


class StructuredStream(BaseStream[DepsT, FormatT]):
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

    def __iter__(self) -> Iterator[ContentChunk]:
        """Iterate through the structured outputs of the stream.

        Returns:
            An iterator yielding structured output objects.
        """
        raise NotImplementedError()

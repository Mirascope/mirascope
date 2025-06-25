"""Interface for streaming structured responses asynchronously with context from LLMs.

This module provides interfaces for asynchronous streaming of structured responses from
language models with context. Streaming allows for incremental processing of responses
as they are generated, rather than waiting for the complete response.

TODO: this interface is missing stuff from v1 like usage etc. that we collect during
the stream for convenience (e.g. calling stream.cost after the stream is done).
"""

from collections.abc import AsyncIterator
from typing import Generic

from typing_extensions import TypeVar

from ..types import Dataclass
from .context_stream_chunk import ContextStreamChunk

T = TypeVar("T", bound=Dataclass | None, default=None)
DepsT = TypeVar("DepsT", default=None)


class AsyncContextStructuredStream(Generic[DepsT, T]):
    """An asynchronous stream of partial structured outputs from an LLM with context.

    This class supports async iteration to process structured outputs as they arrive
    from the model. Each chunk includes access to the context dependencies.

    Example:
        ```python
        from mirascope import llm

        class BookData:
            isbn: str
            publisher: str

        @llm.response_format(parser="json")
        class Book:
            title: str
            author: str

        @llm.call("openai:gpt-4o-mini", response_format=Book, deps_type=BookData)
        def answer_question(ctx: llm.Context[BookData], question: str) -> str:
            return f"Answer this question based on the book data: {question}"

        with llm.context(deps=BookData(isbn="1234567890", publisher="Penguin")) as ctx:
            stream = await answer_question.astream(ctx, "What is the book about?")
            async for partial_book in stream:
                print(partial_book)
                # Access the context with partial_book.ctx
        ```
    """

    def __aiter__(self) -> AsyncIterator[ContextStreamChunk[DepsT, T]]:
        """Iterate through the structured outputs of the stream asynchronously.

        Returns:
            An async iterator yielding structured output objects with context.
        """
        raise NotImplementedError()

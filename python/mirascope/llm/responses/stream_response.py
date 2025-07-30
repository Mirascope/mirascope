"""Responses that stream content from LLMs."""

from collections.abc import AsyncIterator, Iterator, Sequence
from typing import Any

from ..content import AsyncStream, AsyncTextStream, Stream, TextStream
from ..formatting import FormatT
from .response import BR, Response


class BaseStreamResponse(BR[FormatT]):
    """Base class for streaming responses from LLMs.
    Provides common metadata fields that are populated as the stream is consumed.
    """

    chunks: Sequence[Any]
    """The raw, provider-specific chunks returned by the underlying LLM."""

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


class StreamResponse(BaseStreamResponse[FormatT]):
    """A synchronous stream of response chunks from an LLM.

    This class supports iteration to process chunks as they arrive from the model.

    Example:
        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4o-mini")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        stream_response = answer_question.stream("What is the capital of France?")
        for partial in stream_response.text():
            print(partial.delta, end="", flush=True)
        print() # Final flush
        ```
    """

    def text(self, delimiter: str = "\n") -> TextStream:
        """Provides a stream that iterates through all the text content of the StreamResponse.

        If the response contains multiple text parts, they will be combined into a single
        TextStream, with `delimiter` (which defaults to newline) separating the distinct
        text parts.

        If the response has no text parts, then the text stream will provide an single
        partial with an empty string.
        """
        raise NotImplementedError()

    def content(self) -> Iterator[Stream]:
        """Iterate through the response's content, one stream at a time.

        Each content part in the response will correspond to one stream, which will yield
        partials of that content as chunks come in from the underlying LLM.

        Subsequent calls to `content` will create new iterators that restart iteration
        from the beginning of the stream.
        """
        raise NotImplementedError()


class AsyncStreamResponse(BaseStreamResponse[FormatT]):
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

    def text(self, delimiter: str = "\n") -> AsyncTextStream:
        """Provides a stream that iterates through all the text content of the StreamResponse.

        If the response contains multiple text parts, they will be combined into a single
        TextStream, with `delimiter` (which defaults to newline) separating the distinct
        text parts.

        If the response has no text parts, then the text stream will provide an single
        partial with an empty string.
        """
        raise NotImplementedError()

    def content(self) -> AsyncIterator[AsyncStream]:
        """Asynchronously iterate through the response's content, one stream at a time.

        Each content part in the response will correspond to one async stream, which will yield
        partials of that content as chunks come in from the underlying LLM.

        Subsequent calls to `content` will create new iterators that restart iteration
        from the beginning of the stream.
        """
        raise NotImplementedError()

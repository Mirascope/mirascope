"""Responses that stream content from LLMs."""

from collections.abc import AsyncIterator, Iterator

from ..content import ContentChunk
from ..formatting import FormatT
from ..streams import AsyncGroup, Group
from .response import BR, Response


class BaseStreamResponse(BR[FormatT]):
    """Base class for streaming responses from LLMs.
    Provides common metadata fields that are populated as the stream is consumed.
    """

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

    def groups(self) -> Iterator[Group]:
        """Iterate through grouped chunks of the stream.

        Returns:
            An iterator yielding Group objects that contain related chunks.
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

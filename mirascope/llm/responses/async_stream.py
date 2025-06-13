"""Interface for streaming responses asynchronously from LLMs.

TODO: this interface is missing stuff from v1 like usage etc. that we collect during
the stream for convenience (e.g. calling stream.cost after the stream is done).
"""

from collections.abc import AsyncIterator

from .stream_chunk import StreamChunk


class AsyncStream:
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

    def __aiter__(self) -> AsyncIterator[StreamChunk]:
        """Iterate through the chunks of the stream asynchronously.

        Returns:
            An async iterator yielding StreamChunk objects.
        """
        raise NotImplementedError()

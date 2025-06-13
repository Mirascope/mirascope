"""Interface for streaming responses from LLMs.

TODO: this interface is missing stuff from v1 like usage etc. that we collect during
the stream for convenience (e.g. calling stream.cost after the stream is done).
"""

from collections.abc import Iterator

from .stream_chunk import StreamChunk


class Stream:
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

    def __iter__(self) -> Iterator[StreamChunk]:
        """Iterate through the chunks of the stream.

        Returns:
            An iterator yielding StreamChunk objects.
        """
        raise NotImplementedError()

"""Interface for streaming responses asynchronously from LLMs."""

from typing_extensions import TypeVar

from .base_stream import BaseAsyncStream

T = TypeVar("T", bound=object | None, default=None)


class AsyncStream(BaseAsyncStream[T]):
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


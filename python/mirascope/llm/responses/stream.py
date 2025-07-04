"""Interface for streaming responses from LLMs."""

from typing_extensions import TypeVar

from .base_stream import BaseSyncStream

T = TypeVar("T", bound=object | None, default=None)


class Stream(BaseSyncStream[T]):
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



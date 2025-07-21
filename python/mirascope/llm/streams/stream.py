"""Interface for streaming responses from LLMs."""

from collections.abc import Iterator

from ..content import ContentChunk
from ..formatting import FormatT
from .base import BaseStream
from .group_types import Group


class Stream(BaseStream[FormatT]):
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

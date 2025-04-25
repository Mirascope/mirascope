"""Context for LLM calls."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..messages import Message

NoneType = type(None)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class Context(Generic[DepsT]):
    """Context for LLM calls.

    This class provides a context for LLM calls, including the model,
    parameters, and any dependencies needed for the call.
    """

    messages: list[Message]
    """The array of messages that have been sent so far (i.e. history)."""

    deps: DepsT
    """The dependencies needed for a call."""


CONTEXT: ContextVar[Context | None] = ContextVar("CONTEXT", default=None)


@contextmanager
def context(
    *,
    messages: list[Message] | None = None,
    deps: DepsT = None,
) -> Iterator[Context[DepsT]]:
    """Set the context for LLM calls.

    Example:

        ```python
        from mirascope import llm

        class Book:
            ...

        @llm.call("openai:gpt-4o-mini", tools=[])
        def answer_question(ctx: Context[Book], question: str) -> str:
            return f"Answer this question: {question}"

        ctx = Context()
        with llm.context() as ctx:
            response = answer_question(ctx, "What is the capital of France?")
    """
    raise NotImplementedError()
    context = ...
    token = CONTEXT.set(context)  # need to construct context
    try:
        yield context
    finally:
        CONTEXT.reset(token)

"""Context for LLM generations."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from .messages import Message

NoneType = type(None)
DepsT = TypeVar("DepsT", default=None)


@dataclass
class Context(Generic[DepsT]):
    """Context for LLM generations.

    This class provides a context for LLM generations, including the model,
    parameters, and any dependencies needed for the generation.
    """

    messages: list[Message]
    """The array of messages that have been sent so far (i.e. history)."""

    deps: DepsT
    """The dependencies needed for a generation."""


CONTEXT: ContextVar[Context | None] = ContextVar("CONTEXT", default=None)


@contextmanager
def context(
    *,
    messages: list[Message] | None = None,
    deps: DepsT = None,
) -> Iterator[Context[DepsT]]:
    """Set the context for LLM generations."""
    raise NotImplementedError()
    context = ...
    token = CONTEXT.set(context)  # need to construct context
    try:
        yield context
    finally:
        CONTEXT.reset(token)

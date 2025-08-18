"""Context for LLM calls."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from ..messages import Message

DepsT = TypeVar("DepsT", default=None)
"""Type variable for dependency injection in `llm.Context`.

This TypeVar is used throughout the LLM module to represent the type of
dependencies that are present in `llm.Context`. 
It defaults to None when no dependencies are needed.
"""

RequiredDepsT = TypeVar("RequiredDepsT")
"""Type variable for dependency injection in `llm.Context`."""


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

    def __init__(
        self, *, messages: Sequence[Message] | None = None, deps: DepsT = None
    ) -> None:
        self.messages = list(messages or [])
        self.deps = deps

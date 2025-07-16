"""Context for LLM calls."""

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


@dataclass
class Context(Generic[DepsT]):
    """Context for LLM calls.

    This class provides a context for LLM calls, including the model,
    parameters, and any dependencies needed for the call.
    """

    def __init__(
        self, *, messages: list[Message] | None = None, deps: DepsT = None
    ) -> None:
        self.messages = messages or []
        self.deps = deps

    messages: list[Message]
    """The array of messages that have been sent so far (i.e. history)."""

    deps: DepsT
    """The dependencies needed for a call."""

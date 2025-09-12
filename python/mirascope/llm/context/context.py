"""Context for LLM calls."""

from dataclasses import dataclass
from typing import Generic
from typing_extensions import TypeVar

DepsT = TypeVar("DepsT")
"""Type variable for dependency injection in `llm.Context`.

This TypeVar is used throughout the LLM module to represent the type of
dependencies that are present in `llm.Context`. 
"""


@dataclass(kw_only=True)
class Context(Generic[DepsT]):
    """Context for LLM calls.

    This class provides a context for LLM calls, including the model,
    parameters, and any dependencies needed for the call.
    """

    deps: DepsT
    """The dependencies needed for a call."""

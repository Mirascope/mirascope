"""Common TypeVar definitions for the LLM module."""

from typing_extensions import TypeVar

DepsT = TypeVar("DepsT", default=None)
"""Type variable for dependency injection context types.

This TypeVar is used throughout the LLM module to represent the type of
dependencies that can be injected into various components like agents,
streams, and tools. It defaults to None when no dependencies are needed.
"""
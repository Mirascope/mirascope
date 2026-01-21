"""Utilities for tool type checking and validation."""

import inspect
from typing_extensions import TypeIs

from ..context import DepsT, _utils as _context_utils
from ..types import JsonableCovariantT, P
from .protocols import AsyncContextToolFn, AsyncToolFn, ContextToolFn, ToolFn


def is_context_tool_fn(
    fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    | ToolFn[P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT],
) -> TypeIs[
    ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
]:
    """Type guard to check if a function is a context tool function."""
    return _context_utils.first_param_is_context(fn)


def is_async_tool_fn(
    fn: ContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    | ToolFn[P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT],
) -> TypeIs[
    AsyncContextToolFn[DepsT, P, JsonableCovariantT]
    | AsyncToolFn[P, JsonableCovariantT]
]:
    """Type guard to check if a function is an async tool function."""
    return inspect.iscoroutinefunction(fn)

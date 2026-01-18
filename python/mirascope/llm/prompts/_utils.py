import inspect
from typing_extensions import TypeIs

from ..context import DepsT, _utils as _context_utils
from ..types import P
from .protocols import (
    AsyncContextMessageTemplate,
    AsyncMessageTemplate,
    ContextMessageTemplate,
    MessageTemplate,
)


def is_context_promptable(
    fn: ContextMessageTemplate[P, DepsT]
    | AsyncContextMessageTemplate[P, DepsT]
    | MessageTemplate[P]
    | AsyncMessageTemplate[P],
) -> TypeIs[ContextMessageTemplate[P, DepsT] | AsyncContextMessageTemplate[P, DepsT]]:
    """Type guard to check if a function is a context promptable function."""
    return _context_utils.first_param_is_context(fn)


def is_async_promptable(
    fn: ContextMessageTemplate[P, DepsT]
    | AsyncContextMessageTemplate[P, DepsT]
    | MessageTemplate[P]
    | AsyncMessageTemplate[P],
) -> TypeIs[AsyncMessageTemplate[P] | AsyncContextMessageTemplate[P, DepsT]]:
    """Type guard to check if a function is an async promptable function."""
    return inspect.iscoroutinefunction(fn)

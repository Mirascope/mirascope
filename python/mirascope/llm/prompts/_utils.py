import inspect
from collections.abc import Sequence
from typing_extensions import TypeIs

from ..context import DepsT, _utils as _context_utils
from ..messages import (
    AssistantMessage,
    Message,
    SystemMessage,
    UserContent,
    UserMessage,
    user,
)
from ..types import P
from .protocols import (
    AsyncContextPromptable,
    AsyncPromptable,
    ContextPromptable,
    Promptable,
)


def is_messages(
    messages_or_content: Sequence[Message] | UserContent,
) -> TypeIs[Sequence[Message]]:
    if not messages_or_content:
        raise ValueError("Prompt returned empty content")
    return isinstance(messages_or_content, list) and isinstance(
        messages_or_content[0], SystemMessage | UserMessage | AssistantMessage
    )


def promote_to_messages(result: Sequence[Message] | UserContent) -> Sequence[Message]:
    """Promote a prompt result to a list of messages.

    If the result is already a list of Messages, returns it as-is.
    If the result is UserContent, wraps it in a single user message.
    """
    if is_messages(result):
        return result
    return [user(result)]


def is_context_promptable(
    fn: ContextPromptable[P, DepsT]
    | AsyncContextPromptable[P, DepsT]
    | Promptable[P]
    | AsyncPromptable[P],
) -> TypeIs[ContextPromptable[P, DepsT] | AsyncContextPromptable[P, DepsT]]:
    """Type guard to check if a function is a context promptable function."""
    return _context_utils.first_param_is_context(fn)


def is_async_promptable(
    fn: ContextPromptable[P, DepsT]
    | AsyncContextPromptable[P, DepsT]
    | Promptable[P]
    | AsyncPromptable[P],
) -> TypeIs[AsyncPromptable[P] | AsyncContextPromptable[P, DepsT]]:
    """Type guard to check if a function is an async promptable function."""
    return inspect.iscoroutinefunction(fn)

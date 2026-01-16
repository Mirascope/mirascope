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
    AsyncContextMessageTemplate,
    AsyncMessageTemplate,
    ContextMessageTemplate,
    MessageTemplate,
)


def is_messages(
    messages_or_content: UserContent | Sequence[Message],
) -> TypeIs[Sequence[Message]]:
    if isinstance(messages_or_content, list):
        if not messages_or_content:
            raise ValueError("Empty array may not be used as message content")
        return isinstance(
            messages_or_content[0], SystemMessage | UserMessage | AssistantMessage
        )
    return False


def promote_to_messages(content: UserContent | Sequence[Message]) -> Sequence[Message]:
    """Promote a prompt result to a list of messages.

    If the result is already a list of Messages, returns it as-is.
    If the result is str/UserContentPart/Sequence of content parts, wraps it in a user message.
    """
    if is_messages(content):
        return content
    return [user(content)]


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

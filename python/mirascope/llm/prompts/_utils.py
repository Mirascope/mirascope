import inspect

from typing_extensions import TypeIs

from ..messages import (
    AssistantMessage,
    Message,
    SystemMessage,
    UserContent,
    UserMessage,
    user,
)
from .types import (
    AsyncPrompt,
    Prompt,
)


def is_messages(
    messages_or_content: list[Message] | UserContent,
) -> TypeIs[list[Message]]:
    if not messages_or_content:
        raise ValueError("Prompt returned empty content")
    return isinstance(messages_or_content, list) and isinstance(
        messages_or_content[0], SystemMessage | UserMessage | AssistantMessage
    )


def promote_to_messages(result: list[Message] | UserContent) -> list[Message]:
    """Promote a prompt result to a list of messages.

    If the result is already a list of Messages, returns it as-is.
    If the result is UserContent, wraps it in a single user message.
    """
    if is_messages(result):
        return result
    return [user(result)]


def is_async_prompt(fn: Prompt | AsyncPrompt) -> TypeIs[AsyncPrompt]:
    """Distinguish `Prompt` from `AsyncPrompt`, returning `TypeIs[AsyncPrompt]`"""
    return inspect.iscoroutinefunction(fn)

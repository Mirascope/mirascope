"""Typed dictionaries for prompt messages."""
from typing import Iterable, Literal, Optional, TypedDict, Union

from typing_extensions import Required


class SystemMessage(TypedDict, total=False):
    """A message with the `system` role.

    Attributes:
        content: The contents of the message.
        role: The role of the messages author, in this case `system`.
    """

    content: Required[str]
    role: Required[Literal["system"]]


class UserMessage(TypedDict, total=False):
    """A message with the `user` role.

    Attributes:
        content: The contents of the message.
        role: The role of the messages author, in this case `user`.
    """

    content: Required[Union[str, Iterable]]
    role: Required[Literal["user"]]


class AssistantMessage(TypedDict, total=False):
    """A message with the `assistant` role.

    Attributes:
        content: The contents of the message.
        role: The role of the messages author, in this case `assistant`.
    """

    content: Optional[str]
    role: Required[Literal["assistant"]]
    tool_calls: Iterable


class ToolMessage(TypedDict, total=False):
    """A message with the `tool` role.

    Attributes:
        content: The contents of the message.
        role: The role of the messages author, in this case `tool`.
    """

    content: Required[str]
    role: Required[Literal["system"]]
    tool_call_id: Required[str]


Message = Union[SystemMessage, UserMessage, AssistantMessage, ToolMessage]

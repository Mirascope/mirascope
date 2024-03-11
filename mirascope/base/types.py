"""Base types and abstract interfaces for typing LLM calls."""
from abc import ABC, abstractmethod
from typing import Any, Literal, TypedDict, Union

from pydantic import BaseModel, ConfigDict
from typing_extensions import Required

BaseType = Union[
    str,
    int,
    float,
    bool,
    list,
    set,
    tuple,
]


class SystemMessage(TypedDict, total=False):
    """A message with the `system` role.

    Attributes:
        role: The role of the message's author, in this case `system`.
        content: The contents of the message.
    """

    role: Required[Literal["system"]]
    content: Required[str]


class UserMessage(TypedDict, total=False):
    """A message with the `user` role.

    Attributes:
        role: The role of the message's author, in this case `user`.
        content: The contents of the message.
    """

    role: Required[Literal["user"]]
    content: Required[str]


class AssistantMessage(TypedDict, total=False):
    """A message with the `assistant` role.

    Attributes:
        role: The role of the message's author, in this case `assistant`.
        content: The contents of the message.
    """

    role: Required[Literal["assistant"]]
    content: Required[str]


class ModelMessage(TypedDict, total=False):
    """A message with the `model` role.

    Attributes:
        role: The role of the message's author, in this case `model`.
        content: The contents of the message.
    """

    role: Required[Literal["model"]]
    content: Required[str]


class ToolMessage(TypedDict, total=False):
    """A message with the `tool` role.

    Attributes:
        role: The role of the message's author, in this case `tool`.
        content: The contents of the message.
    """

    role: Required[Literal["tool"]]
    content: Required[str]


Message = Union[SystemMessage, UserMessage, AssistantMessage, ToolMessage, Any]


class BaseCallResponse(BaseModel, ABC):
    """A base abstract interface for LLM call responses.

    Attributes:
        response: The original response from whichever model response this wraps.
    """

    response: Any

    model_config = ConfigDict(extra="allow")

    @property
    @abstractmethod
    def content(self) -> str:
        """Should return the string content of the response.

        If there are multiple choices in a response, this method should select the 0th
        choice and return it's string content.

        If there is no string content (e.g. when using tools), this method must return
        the empty string.
        """
        ...  # pragma: no cover


class BaseCallResponseChunk(BaseModel, ABC):
    """A base abstract interface for LLM streaming response chunks.

    Attributes:
        response: The original response chunk from whichever model response this wraps.
    """

    chunk: Any

    model_config = ConfigDict(extra="allow")

    @property
    @abstractmethod
    def content(self) -> str:
        """Should return the string content of the response chunk.

        If there are multiple choices in a chunk, this method should select the 0th
        choice and return it's string content.

        If there is no string content (e.g. when using tools), this method must return
        the empty string.
        """
        ...  # pragma: no cover

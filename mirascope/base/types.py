"""Types for working with Mirascope prompts."""
from enum import Enum
from inspect import isclass
from typing import (
    Annotated,
    Any,
    Callable,
    Iterable,
    Literal,
    Optional,
    Type,
    TypedDict,
    Union,
    get_origin,
)

from pydantic import BaseModel
from typing_extensions import Required

from .tools import BaseTool

BaseType = Union[
    str,
    int,
    float,
    bool,
    list,
    set,
    tuple,
]


def is_base_type(type_: Any) -> bool:
    """Check if a type is a base type."""
    if isclass(type_) and issubclass(type_, Enum):
        return True
    base_types = {str, int, float, bool, list, set, tuple}
    if type_ in base_types or get_origin(type_) in base_types.union(
        {Literal, Union, Annotated}
    ):
        return True
    return False


class BaseCallParams(BaseModel):
    """The base parameters for calling a model with a prompt."""

    model: str
    tools: Optional[list[Union[Callable, Type[BaseTool]]]] = None

    @property
    def kwargs(self) -> dict[str, Any]:
        """Returns the keyword argument call parameters as a dictioanry."""
        return self.model_dump(exclude={"tools"})


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

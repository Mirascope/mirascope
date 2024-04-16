"""Base types and abstract interfaces for typing LLM calls."""

from abc import ABC, abstractmethod
from inspect import isclass
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, ConfigDict
from typing_extensions import Required, TypedDict

from .tools import BaseTool
from .utils import convert_function_to_tool


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


Message = Union[SystemMessage, UserMessage, AssistantMessage, ToolMessage]


ResponseT = TypeVar("ResponseT", bound=Any)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
T = TypeVar("T")


class BaseCallParams(BaseModel, Generic[BaseToolT]):
    """The parameters with which to make a call."""

    model: str
    tools: Optional[list[Union[Callable, Type[BaseToolT]]]] = None
    weave: Optional[Callable[[T], T]] = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[BaseToolT]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns all parameters for the call as a keyword arguments dictionary."""
        extra_exclude = {"tools", "weave"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        kwargs = {
            key: value
            for key, value in self.model_dump(exclude=exclude).items()
            if value is not None
        }
        if not self.tools or tool_type is None:
            return kwargs
        kwargs["tools"] = [
            tool if isclass(tool) else convert_function_to_tool(tool, tool_type)
            for tool in self.tools
        ]
        return kwargs


class BaseCallResponse(BaseModel, Generic[ResponseT, BaseToolT], ABC):
    """A base abstract interface for LLM call responses.

    Attributes:
        response: The original response from whichever model response this wraps.
    """

    response: ResponseT
    tool_types: Optional[list[Type[BaseToolT]]] = None
    start_time: float  # The start time of the completion in ms
    end_time: float  # The end time of the completion in ms

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def tools(self) -> Optional[list[BaseToolT]]:
        """Returns the tools for the 0th choice message."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def tool(self) -> Optional[BaseToolT]:
        """Returns the 0th tool for the 0th choice message."""
        ...  # pragma: no cover

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


ChunkT = TypeVar("ChunkT", bound=Any)


class BaseCallResponseChunk(BaseModel, Generic[ChunkT, BaseToolT], ABC):
    """A base abstract interface for LLM streaming response chunks.

    Attributes:
        response: The original response chunk from whichever model response this wraps.
    """

    chunk: ChunkT
    tool_types: Optional[list[Type[BaseToolT]]] = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

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

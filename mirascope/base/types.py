"""Base types and abstract interfaces for typing LLM calls."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
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
    overload,
)

import pydantic
from pydantic import BaseModel, ConfigDict
from typing_extensions import Required, TypedDict

from .tools import BaseTool, convert_function_to_tool


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


class BaseConfig(BaseModel):
    llm_ops: list[Union[Callable, str]] = []
    client_wrappers: list[Union[Callable, str]] = []


class BaseCallParams(BaseModel, Generic[BaseToolT]):
    """The parameters with which to make a call."""

    model: str
    tools: Optional[list[Union[Callable, Type[BaseToolT]]]] = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[BaseToolT]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns all parameters for the call as a keyword arguments dictionary."""
        extra_exclude = {"tools"}
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
    user_message_param: Optional[Any] = None
    tool_types: Optional[list[Type[BaseToolT]]] = None
    start_time: float  # The start time of the completion in ms
    end_time: float  # The end time of the completion in ms
    cost: Optional[float] = None  # The cost of the completion in dollars

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def message_param(self) -> Any:
        """Returns the assistant's response as a message parameter."""
        ...  # pragma: no cover

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

    @classmethod
    @abstractmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[BaseToolT, Any]]
    ) -> list[Any]:
        """Returns the tool message parameters for tool call results."""
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

    @property
    @abstractmethod
    def finish_reasons(self) -> Union[None, list[str]]:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def model(self) -> Optional[str]:
        """Should return the name of the response model."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def id(self) -> Optional[str]:
        """Should return the id of the response."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def usage(self) -> Any:
        """Should return the usage of the response.

        If there is no usage, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def input_tokens(self) -> Optional[Union[int, float]]:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def output_tokens(self) -> Optional[Union[int, float]]:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...  # pragma: no cover


ChunkT = TypeVar("ChunkT", bound=Any)


class BaseCallResponseChunk(BaseModel, Generic[ChunkT, BaseToolT], ABC):
    """A base abstract interface for LLM streaming response chunks.

    Attributes:
        response: The original response chunk from whichever model response this wraps.
    """

    chunk: ChunkT
    user_message_param: Optional[Any] = None
    tool_types: Optional[list[Type[BaseToolT]]] = None
    cost: Optional[float] = None  # The cost of the completion in dollars
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

    @property
    @abstractmethod
    def model(self) -> Optional[str]:
        """Should return the name of the response model."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def id(self) -> Optional[str]:
        """Should return the id of the response."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def finish_reasons(self) -> Union[None, list[str]]:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def usage(self) -> Any:
        """Should return the usage of the response.

        If there is no usage, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def input_tokens(self) -> Optional[Union[int, float]]:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def output_tokens(self) -> Optional[Union[int, float]]:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...  # pragma: no cover


BaseCallResponseT = TypeVar("BaseCallResponseT", bound=BaseCallResponse)
BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)


class BaseToolStream(BaseModel, Generic[BaseCallResponseChunkT, BaseToolT], ABC):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: Literal[True],
    ) -> Generator[Optional[BaseToolT], None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: Literal[False],
    ) -> Generator[BaseToolT, None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[BaseCallResponseChunkT, None, None],
        allow_partial: bool,
    ) -> Generator[Optional[BaseToolT], None, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    def from_stream(cls, stream, allow_partial=False):
        """Yields tools from the given stream of chunks."""
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: Literal[True],
    ) -> AsyncGenerator[Optional[BaseToolT], None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: Literal[False],
    ) -> AsyncGenerator[BaseToolT, None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        allow_partial: bool,
    ) -> AsyncGenerator[Optional[BaseToolT], None]:
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    @abstractmethod
    async def from_async_stream(cls, async_stream, allow_partial=False):
        """Yields tools asynchronously from the given async stream of chunks."""
        yield ...  # type: ignore # pragma: no cover

    ############################## PRIVATE METHODS ###################################

    @classmethod
    def _check_version_for_partial(cls, partial: bool) -> None:
        """Checks that the correct version of Pydantic is installed to use partial."""
        if partial and int(pydantic.__version__.split(".")[1]) < 7:
            raise ImportError(
                "You must have `pydantic==^2.7.0` to stream tools. "
                f"Current version: {pydantic.__version__}"
            )  # pragma: no cover


BaseToolStreamT = TypeVar("BaseToolStreamT", bound=BaseToolStream)
MessageParamT = TypeVar("MessageParamT", bound=Any)
UserMessageParamT = TypeVar("UserMessageParamT", bound=Any)
AssistantMessageParamT = TypeVar("AssistantMessageParamT", bound=Any)


class BaseStream(
    Generic[
        BaseCallResponseChunkT,
        UserMessageParamT,
        AssistantMessageParamT,
        BaseToolT,
    ],
    ABC,
):
    """A base class for streaming responses from LLMs."""

    stream: Generator[BaseCallResponseChunkT, None, None]
    message_param_type: type[AssistantMessageParamT]

    cost: Optional[float] = None
    user_message_param: Optional[UserMessageParamT] = None
    message_param: AssistantMessageParamT

    def __init__(
        self,
        stream: Generator[BaseCallResponseChunkT, None, None],
        message_param_type: type[AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __iter__(
        self,
    ) -> Generator[tuple[BaseCallResponseChunkT, Optional[BaseToolT]], None, None]:
        """Iterator over the stream and stores useful information."""
        content = ""
        for chunk in self.stream:
            content += chunk.content
            if chunk.cost is not None:
                self.cost = chunk.cost
            yield chunk, None
            self.user_message_param = chunk.user_message_param
        kwargs = {"role": "assistant"}
        if "message" in self.message_param_type.__annotations__:
            kwargs["message"] = content
        else:
            kwargs["content"] = content
        self.message_param = self.message_param_type(**kwargs)


class BaseAsyncStream(
    Generic[
        BaseCallResponseChunkT,
        UserMessageParamT,
        AssistantMessageParamT,
        BaseToolT,
    ],
    ABC,
):
    """A base class for async streaming responses from LLMs."""

    stream: AsyncGenerator[BaseCallResponseChunkT, None]
    message_param_type: type[AssistantMessageParamT]

    cost: Optional[float] = None
    user_message_param: Optional[UserMessageParamT] = None
    message_param: AssistantMessageParamT

    def __init__(
        self,
        stream: AsyncGenerator[BaseCallResponseChunkT, None],
        message_param_type: type[AssistantMessageParamT],
    ):
        """Initializes an instance of `BaseAsyncStream`."""
        self.stream = stream
        self.message_param_type = message_param_type

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[BaseCallResponseChunkT, Optional[BaseToolT]], None]:
        """Iterates over the stream and stores useful information."""

        async def generator():
            content = ""
            async for chunk in self.stream:
                content += chunk.content
                if chunk.cost is not None:
                    self.cost = chunk.cost
                yield chunk, None
                self.user_message_param = chunk.user_message_param
            kwargs = {"role": "assistant"}
            if "message" in self.message_param_type.__annotations__:
                kwargs["message"] = content
            else:
                kwargs["content"] = content
            self.message_param = self.message_param_type(**kwargs)

        return generator()

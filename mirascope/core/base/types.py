"""Mirascope Base Type Classes."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, computed_field
from typing_extensions import NotRequired, TypedDict

from .._internal import utils


class BaseContent(TypedDict):
    """A base class for message content."""


class BaseMessageParam(TypedDict):
    """A base class for message parameters.

    Available roles: `system`, `user`, `assistant`, `model`.
    """

    role: Literal["system", "user", "assistant", "model"]
    content: str | list[BaseContent]


class BaseTool(BaseModel):
    """A class for defining tools for LLM calls."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def name(cls) -> str:
        """Returns the name of the tool."""
        return cls.__name__

    @classmethod
    def description(cls) -> str:
        """Returns the description of the tool."""
        return (
            inspect.cleandoc(cls.__doc__)
            if cls.__doc__
            else utils.DEFAULT_TOOL_DOCSTRING
        )

    @abstractmethod
    def call(self) -> Any:
        """The method to call the tool."""
        ...  # pragma: no cover


class BaseCallParams(TypedDict, total=False): ...  # pragma: no cover


MessageParamT = TypeVar("MessageParamT", bound=Any)
CallParamsT = TypeVar("CallParamsT", bound=BaseCallParams)


class FunctionReturnBase(TypedDict):
    computed_fields: NotRequired[dict[str, str | list[str] | list[list[str]]]]
    tools: NotRequired[list[type[BaseTool]]]


class FunctionReturnMessages(FunctionReturnBase, Generic[MessageParamT]):
    messages: NotRequired[list[MessageParamT]]


class FunctionReturnCallParams(FunctionReturnBase, Generic[CallParamsT]):
    call_params: NotRequired[CallParamsT]


class FunctionReturnFull(FunctionReturnBase, Generic[MessageParamT, CallParamsT]):
    messages: NotRequired[list[MessageParamT]]
    call_params: NotRequired[CallParamsT]


BaseFunctionReturn = (
    FunctionReturnBase
    | FunctionReturnMessages[MessageParamT]
    | FunctionReturnCallParams[CallParamsT]
    | FunctionReturnFull[MessageParamT, CallParamsT]
    | None
)
"""The base function return type for functions as LLM calls."""


ResponseT = TypeVar("ResponseT", bound=Any)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
BaseFunctionReturnT = TypeVar("BaseFunctionReturnT", bound=BaseFunctionReturn)
UserMessageParamT = TypeVar("UserMessageParamT", bound=Any)


class BaseCallResponse(
    BaseModel,
    Generic[
        ResponseT,
        BaseToolT,
        BaseFunctionReturnT,
        MessageParamT,
        CallParamsT,
        UserMessageParamT,
    ],
    ABC,
):
    """A base abstract interface for LLM call responses.

    Attributes:
        response: The original response from whichever model response this wraps.
        user_message_param: The most recent message if it was a user message. Otherwise
            `None`.
        tool_types: The tool types sent in the LLM call.
        start_time: The start time of the completion in ms.
        end_time: The end time of the completion in ms.
        cost: The cost of the completion in dollars.
    """

    response: ResponseT
    tool_types: list[type[BaseToolT]] | None = None
    prompt_template: str | None
    fn_args: dict[str, Any]
    fn_return: BaseFunctionReturnT
    messages: list[MessageParamT]
    call_params: CallParamsT
    user_message_param: UserMessageParamT | None = None
    start_time: float
    end_time: float
    cost: float | None = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @computed_field
    @property
    @abstractmethod
    def message_param(self) -> Any:
        """Returns the assistant's response as a message parameter."""
        ...  # pragma: no cover

    @computed_field
    @property
    @abstractmethod
    def tools(self) -> list[BaseToolT] | None:
        """Returns the tools for the 0th choice message."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def tool(self) -> BaseToolT | None:
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
    def finish_reasons(self) -> list[str] | None:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def model(self) -> str | None:
        """Should return the name of the response model."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def id(self) -> str | None:
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
    def input_tokens(self) -> int | float | None:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...  # pragma: no cover

    @property
    @abstractmethod
    def output_tokens(self) -> int | float | None:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...  # pragma: no cover

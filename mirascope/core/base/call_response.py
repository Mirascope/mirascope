"""This module contains the base call response class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    SkipValidation,
    computed_field,
    field_serializer,
)

from .call_params import BaseCallParams
from .dynamic_config import BaseDynamicConfig
from .metadata import Metadata
from .tool import BaseTool

_ResponseT = TypeVar("_ResponseT", bound=Any)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)
_UserMessageParamT = TypeVar("_UserMessageParamT", bound=Any)


class BaseCallResponse(
    BaseModel,
    Generic[
        _ResponseT,
        _BaseToolT,
        _BaseDynamicConfigT,
        _MessageParamT,
        _CallParamsT,
        _UserMessageParamT,
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

    metadata: Metadata
    response: _ResponseT
    tool_types: list[type[_BaseToolT]] | None = None
    prompt_template: str | None
    fn_args: dict[str, Any]
    dynamic_config: _BaseDynamicConfigT
    messages: SkipValidation[list[_MessageParamT]]
    call_params: SkipValidation[_CallParamsT]
    call_kwargs: dict[str, Any]
    user_message_param: _UserMessageParamT | None = None
    start_time: float
    end_time: float

    _provider: ClassVar[str] = "NO PROVIDER"
    _model: str = "NO MODEL"

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @field_serializer("tool_types")
    def serialize_tool_types(self, tool_types: list[type[_BaseToolT]], _info):
        return [{"type": "function", "name": tool._name()} for tool in tool_types or []]

    def __str__(self) -> str:
        """Returns the string content of the response."""
        return self.content

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

    @property
    @abstractmethod
    def cost(self) -> float | None:
        """Should return the cost of the response in dollars.

        If there is no cost, this method must return None.
        """
        ...  # pragma: no cover

    @computed_field
    @property
    @abstractmethod
    def message_param(self) -> Any:
        """Returns the assistant's response as a message parameter."""
        ...  # pragma: no cover

    @computed_field
    @property
    @abstractmethod
    def tools(self) -> list[_BaseToolT] | None:
        """Returns the tools for the 0th choice message."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def tool(self) -> _BaseToolT | None:
        """Returns the 0th tool for the 0th choice message."""
        ...  # pragma: no cover

    @classmethod
    @abstractmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[_BaseToolT, Any]]
    ) -> list[Any]:
        """Returns the tool message parameters for tool call results."""
        ...  # pragma: no cover

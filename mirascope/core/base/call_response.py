"""This module contains the base call response class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    FieldSerializationInfo,
    SkipValidation,
    computed_field,
    field_serializer,
)

from .call_kwargs import BaseCallKwargs
from .call_params import BaseCallParams
from .dynamic_config import BaseDynamicConfig
from .metadata import Metadata
from .tool import BaseTool

_ResponseT = TypeVar("_ResponseT", bound=Any)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)
_UserMessageParamT = TypeVar("_UserMessageParamT", bound=Any)


class BaseCallResponse(
    BaseModel,
    Generic[
        _ResponseT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _MessageParamT,
        _CallParamsT,
        _UserMessageParamT,
    ],
    ABC,
):
    """A base abstract interface for LLM call responses.

    Attributes:
        metadata: The metadata pulled from the call that was made.
        response: The original response from whichever model response this wraps.
        tool_types: The list of tool types used, if any.
        prompt_template: The unformatted prompt template from the call that was made.
        fn_args: The input arguments used when making the call.
        dynamic_config: Dynamic configuration options, if any.
        messages: The list of provider-specific messages used to make the API call.
        call_params: The original call params set in the call decorator.
        call_kwargs: The keyword arguments used to make the API call.
        user_message_param: The most recent provider-specific message if it was a user
            message. Otherwise `None`.
        start_time: The start time of the completion in ms.
        end_time: The end time of the completion in ms.
    """

    metadata: Metadata
    response: _ResponseT
    tool_types: list[type[_BaseToolT]] | None = None
    prompt_template: str | None
    fn_args: dict[str, Any]
    dynamic_config: _BaseDynamicConfigT
    messages: SkipValidation[list[_MessageParamT]]
    call_params: SkipValidation[_CallParamsT]
    call_kwargs: BaseCallKwargs[_ToolSchemaT]
    user_message_param: _UserMessageParamT | None = None
    start_time: float
    end_time: float

    _provider: ClassVar[str] = "NO PROVIDER"
    _model: str = "NO MODEL"

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @field_serializer("tool_types", when_used="json")
    def serialize_tool_types(
        self, tool_types: list[type[_BaseToolT]] | None, info: FieldSerializationInfo
    ) -> list[dict[str, str]]:
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
        ...

    @property
    @abstractmethod
    def finish_reasons(self) -> list[str] | None:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def model(self) -> str | None:
        """Should return the name of the response model."""
        ...

    @property
    @abstractmethod
    def id(self) -> str | None:
        """Should return the id of the response."""
        ...

    @property
    @abstractmethod
    def usage(self) -> Any:  # noqa: ANN401
        """Should return the usage of the response.

        If there is no usage, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def input_tokens(self) -> int | float | None:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def output_tokens(self) -> int | float | None:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def cost(self) -> float | None:
        """Should return the cost of the response in dollars.

        If there is no cost, this method must return None.
        """
        ...

    @computed_field
    @property
    @abstractmethod
    def message_param(self) -> Any:  # noqa: ANN401
        """Returns the assistant's response as a message parameter."""
        ...

    @computed_field
    @property
    @abstractmethod
    def tools(self) -> list[_BaseToolT] | None:
        """Returns the tools for the 0th choice message."""
        ...

    @property
    @abstractmethod
    def tool(self) -> _BaseToolT | None:
        """Returns the 0th tool for the 0th choice message."""
        ...

    @classmethod
    @abstractmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[_BaseToolT, Any]]
    ) -> list[Any]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.
        """
        ...

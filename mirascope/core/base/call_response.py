"""This module contains the base call response class."""

from __future__ import annotations

import base64
import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from functools import cached_property, wraps
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    FieldSerializationInfo,
    SkipValidation,
    computed_field,
    field_serializer,
)

from ..costs import calculate_cost
from ._utils import BaseMessageParamConverter, BaseType, get_common_usage
from .call_kwargs import BaseCallKwargs
from .call_params import BaseCallParams
from .dynamic_config import BaseDynamicConfig
from .metadata import Metadata
from .tool import BaseTool
from .types import CostMetadata, FinishReason, JsonableType, Provider, Usage

if TYPE_CHECKING:
    from ...llm.tool import Tool
    from .. import BaseMessageParam

_ResponseT = TypeVar("_ResponseT", bound=Any)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_ToolMessageParamT = TypeVar("_ToolMessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)
_UserMessageParamT = TypeVar("_UserMessageParamT", bound=Any)
_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound="BaseCallResponse")
_BaseMessageParamConverterT = TypeVar(
    "_BaseMessageParamConverterT", bound=BaseMessageParamConverter
)


def transform_tool_outputs(
    fn: Callable[
        [type[_BaseCallResponseT], Sequence[tuple[_BaseToolT, str]]],
        list[_ToolMessageParamT],
    ],
) -> Callable[
    [type[_BaseCallResponseT], Sequence[tuple[_BaseToolT, JsonableType]]],
    list[_ToolMessageParamT],
]:
    @wraps(fn)
    def wrapper(
        cls: type[_BaseCallResponseT],
        tools_and_outputs: Sequence[tuple[_BaseToolT, JsonableType]],
    ) -> list[_ToolMessageParamT]:
        def recursive_serializer(value: JsonableType) -> BaseType:
            if isinstance(value, str):
                return value
            if isinstance(value, int | float | bool):
                return value  # Don't serialize primitives yet
            if isinstance(value, bytes):
                return base64.b64encode(value).decode("utf-8")
            if isinstance(value, BaseModel):
                return value.model_dump()
            if isinstance(value, list | set | tuple):
                return [recursive_serializer(item) for item in value]
            if isinstance(value, dict):
                return {k: recursive_serializer(v) for k, v in value.items()}
            raise TypeError(f"Unsupported type for serialization: {type(value)}")

        transformed_tools_and_outputs = [
            (
                tool,
                output.model_dump_json()
                if isinstance(output, BaseModel)
                else str(recursive_serializer(output))
                if isinstance(output, str | bytes)
                else json.dumps(recursive_serializer(output)),
            )
            for tool, output in tools_and_outputs
        ]
        return fn(cls, transformed_tools_and_outputs)

    return wrapper


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
        _BaseMessageParamConverterT,
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

    _message_converter: type[_BaseMessageParamConverterT]
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

    @computed_field
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

    @computed_field
    @property
    @abstractmethod
    def finish_reasons(self) -> list[str] | None:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...

    @computed_field
    @property
    @abstractmethod
    def model(self) -> str | None:
        """Should return the name of the response model."""
        ...

    @computed_field
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

    @computed_field
    @property
    @abstractmethod
    def input_tokens(self) -> int | float | None:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...

    @computed_field
    @property
    @abstractmethod
    def cached_tokens(self) -> int | float | None:
        """Should return the number of cached tokens.

        If there is no cached_tokens, this method must return None.
        """
        ...

    @computed_field
    @property
    @abstractmethod
    def output_tokens(self) -> int | float | None:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...

    @computed_field
    @property
    @abstractmethod
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation.

        Returns:
            Metadata relevant to cost calculation
        """

        return CostMetadata(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cached_tokens=self.cached_tokens,
        )

    @computed_field
    @property
    def cost(self) -> float | None:
        """Calculate the cost of this API call using the unified calculate_cost function."""

        model = self.model
        if not model:
            return None

        if self.input_tokens is None or self.output_tokens is None:
            return None

        return calculate_cost(
            provider=self.provider,
            model=model,
            metadata=self.cost_metadata,
        )

    @property
    def provider(self) -> Provider:
        """Get the provider used for this API call."""
        return cast(Provider, self._provider)

    @computed_field
    @cached_property
    @abstractmethod
    def message_param(self) -> Any:  # noqa: ANN401
        """Returns the assistant's response as a message parameter."""
        ...

    @cached_property
    @abstractmethod
    def tools(self) -> list[_BaseToolT] | None:
        """Returns the tools for the 0th choice message."""
        ...

    @cached_property
    @abstractmethod
    def tool(self) -> _BaseToolT | None:
        """Returns the 0th tool for the 0th choice message."""
        ...

    @classmethod
    @abstractmethod
    @transform_tool_outputs
    def tool_message_params(
        cls, tools_and_outputs: Sequence[tuple[_BaseToolT, str]]
    ) -> list[Any]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
                message parameters should be constructed.
        """
        ...

    @property
    @abstractmethod
    def common_finish_reasons(self) -> list[FinishReason] | None:
        """Provider-agnostic finish reasons."""
        ...

    @property
    @abstractmethod
    def common_message_param(self) -> BaseMessageParam:
        """Provider-agnostic assistant message param."""
        ...

    @property
    @abstractmethod
    def common_user_message_param(self) -> BaseMessageParam | None:
        """Provider-agnostic user message param."""
        ...

    @property
    def common_messages(self) -> list[BaseMessageParam]:
        """Provider-agnostic list of messages."""
        return self._message_converter.from_provider(self.messages)

    @property
    def common_tools(self) -> list[Tool] | None:
        """Provider-agnostic tools."""
        from ...llm.tool import Tool

        if not self.tools:
            return None
        return [Tool(tool=tool) for tool in self.tools]  # pyright: ignore [reportAbstractUsage]

    @property
    def common_usage(self) -> Usage | None:
        """Provider-agnostic usage info."""
        return get_common_usage(
            self.input_tokens, self.cached_tokens, self.output_tokens
        )

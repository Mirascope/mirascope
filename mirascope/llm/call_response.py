"""The CallResponse class for the LLM provider."""

from __future__ import annotations

from functools import cached_property
from typing import Any, TypeVar

from pydantic import computed_field

from mirascope.core import BaseDynamicConfig
from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseMessageParam,
    BaseTool,
    Usage,
    transform_tool_outputs,
)
from mirascope.core.base.message_param import ToolResultPart
from mirascope.core.base.types import FinishReason
from mirascope.llm._response_metaclass import _ResponseMetaclass
from mirascope.llm.tool import Tool

_ResponseT = TypeVar("_ResponseT")


class CallResponse(
    BaseCallResponse[
        _ResponseT,
        Tool,
        Any,
        BaseDynamicConfig[Any, Any, Any],
        BaseMessageParam,
        BaseCallParams,
        BaseMessageParam,
    ],
    metaclass=_ResponseMetaclass,
):
    """
    A provider-agnostic CallResponse class.

    We rely on _response having `common_` methods or properties for normalization.
    """

    _response: BaseCallResponse[_ResponseT, Tool, Any, Any, Any, Any, Any]

    def __init__(
        self,
        response: BaseCallResponse[_ResponseT, Tool, Any, Any, Any, Any, Any],
    ) -> None:
        super().__init__(
            **{
                field: getattr(response, field)
                for field in response.model_fields
                if field != "user_message_param"
            }
        )
        object.__setattr__(self, "_response", response)
        object.__setattr__(
            self, "user_message_param", response.common_user_message_param
        )

    def __getattribute__(self, name: str) -> Any:  # noqa: ANN401
        special_names = {
            "_response",
            "finish_reasons",
            "usage",
            "message_param",
            "user_message_param",
            "tools",
            "tool",
            "tool_message_params",
            "__dict__",
            "__class__",
            "model_fields",
            "__annotations__",
            "__pydantic_validator__",
            "__pydantic_fields_set__",
            "__pydantic_extra__",
            "__pydantic_private__",
            "__class_getitem__",
            "__repr__",
            "__str__",
            "_properties",
        } | set(object.__getattribute__(self, "_properties"))

        if name in special_names:
            return object.__getattribute__(self, name)

        try:
            response = object.__getattribute__(self, "_response")
            return getattr(response, name)
        except AttributeError:
            return object.__getattribute__(self, name)

    def __str__(self) -> str:
        return str(self._response)

    @computed_field
    @property
    def finish_reasons(self) -> list[FinishReason] | None:  # pyright: ignore [reportIncompatibleMethodOverride]
        return self._response.common_finish_reasons

    @property
    def usage(self) -> Usage | None:
        """Returns the usage of the chat completion."""
        return self._response.common_usage

    @computed_field
    @cached_property
    def message_param(self) -> BaseMessageParam:
        return self._response.common_message_param  # pyright: ignore [reportReturnType]

    @cached_property
    def tools(self) -> list[Tool] | None:  # pyright: ignore [reportIncompatibleVariableOverride]
        return self._response.common_tools

    @cached_property
    def tool(self) -> Tool | None:  # pyright: ignore [reportIncompatibleVariableOverride]
        tools = self._response.common_tools
        if tools:
            return tools[0]
        return None

    @classmethod
    @transform_tool_outputs
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[Tool, str]]
    ) -> list[BaseMessageParam]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.
        """

        def _get_tool_call_id(_tool: BaseTool) -> str | None:
            """Get the tool call ID."""
            if tool_call := getattr(_tool, "tool_call", None):
                # Expect tool_call has an id attribute.
                # If not, we should implement a method to get the id on the provider tool
                return getattr(tool_call, "id", None)
            return None

        return [
            BaseMessageParam(
                role="tool",
                content=[
                    ToolResultPart(
                        type="tool_result",
                        name=tool._name(),
                        content=output,
                        id=_get_tool_call_id(tool),
                    )
                ],
            )
            for tool, output in tools_and_outputs
        ]

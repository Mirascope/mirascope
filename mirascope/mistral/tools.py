"""Classes for using tools with Mistral Chat APIs"""
from __future__ import annotations

import json
from typing import Any, Callable, Type, TypeVar

from mistralai.models.chat_completion import ToolCall
from pydantic import BaseModel, ConfigDict

from ..base import BaseTool, BaseType
from ..base.tools import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)


class MistralTool(BaseTool):
    """Base class for Mistral tools."""

    tool_call: ToolCall

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        """Constructs a tool schema for use with the Mistral Chat client."""
        fn = super().tool_schema()
        return {"type": "function", "function": fn}

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> MistralTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ToolCall` from a Mistral chat completion response, takes its function
        arguments and creates a `MistralTool` instance from it.

        Args:
            tool_call: The Mistral `ToolCall` to extract the tool from.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValueError: if the tool call doesn't match the tool schema.
        """
        try:
            model_json = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError() from e

        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[MistralTool]:
        """Constructs a `OpenAITool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, MistralTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[MistralTool]:
        """Constructs a `OpenAITool` type from a function."""
        return convert_function_to_tool(fn, MistralTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseTypeT]) -> Type[MistralTool]:
        """Constructs a `GeminiTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, MistralTool)

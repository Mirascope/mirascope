"""The `GeminiTool` class for easy tool usage with Google's Gemini LLM calls."""

from __future__ import annotations

from typing import Any

from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class GeminiTool(BaseTool):
    """A class for defining tools for Gemini LLM calls."""

    tool_call: SkipJsonSchema[FunctionCall]

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_tool_schema()
        fn: dict[str, Any] = {"name": cls._name(), "description": cls._description()}
        if model_schema["properties"]:
            fn["parameters"] = model_schema  # type: ignore
        if model_schema["required"]:
            fn["parameters"]["required"] = model_schema["required"]
        if "parameters" in fn:
            if "$defs" in fn["parameters"]:
                raise ValueError(
                    "Unfortunately Google's Gemini API cannot handle nested structures "
                    "with $defs."
                )

            def handle_enum_schema(prop_schema):
                if "enum" in prop_schema:
                    prop_schema["format"] = "enum"
                return prop_schema

            fn["parameters"]["properties"] = {
                prop: {
                    key: value
                    for key, value in handle_enum_schema(prop_schema).items()
                    if key != "default"
                }
                for prop, prop_schema in fn["parameters"]["properties"].items()
            }
        return Tool(function_declarations=[FunctionDeclaration(**fn)])

    @classmethod
    def from_tool_call(cls, tool_call: FunctionCall) -> GeminiTool:
        """Constructs an `GeminiTool` instance from a `tool_call`."""
        if not tool_call.args:
            raise ValueError("Tool call doesn't have any arguments.")
        model_json: dict[str, Any] = {
            key: value for key, value in tool_call.args.items()
        }
        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

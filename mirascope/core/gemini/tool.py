"""Classes for using tools with Google's Gemini API."""

from __future__ import annotations

from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)

from ..base import BaseTool


class GeminiTool(BaseTool):
    """A class for defining tools for Gemini LLM calls."""

    tool_call: FunctionCall

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn = {"name": cls._name(), "description": cls._description()}
        if model_schema["properties"]:
            fn["parameters"] = model_schema  # type: ignore

        if "parameters" in model_schema:
            if "$defs" in model_schema["parameters"]:
                raise ValueError(
                    "Unfortunately Google's Gemini API cannot handle nested structures "
                    "with $defs."
                )
            model_schema["parameters"]["properties"] = {
                prop: {
                    key: value for key, value in prop_schema.items() if key != "title"
                }
                for prop, prop_schema in model_schema["parameters"][
                    "properties"
                ].items()
            }
        return Tool(function_declarations=[FunctionDeclaration(**model_schema)])

    @classmethod
    def from_tool_call(cls, tool_call: FunctionCall) -> GeminiTool:
        """Constructs an `GeminiTool` instance from a `tool_call`."""
        if not tool_call.args:
            raise ValueError("Tool call doesn't have any arguments.")
        model_json = {key: value for key, value in tool_call.args.items()}
        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

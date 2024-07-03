"""The `LiteLLMTool` class for easy tool usage with LiteLLM LLM calls."""

from __future__ import annotations

import jiter
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)
from openai.types.shared_params import FunctionDefinition

from ..base import BaseTool


class LiteLLMTool(BaseTool):
    """A class for defining tools for LiteLLM LLM calls."""

    tool_call: ChatCompletionMessageToolCall

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn = FunctionDefinition(name=cls._name(), description=cls._description())
        if model_schema["properties"]:
            fn["parameters"] = model_schema

        return ChatCompletionToolParam(function=fn, type="function")

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionMessageToolCall) -> LiteLLMTool:
        """Constructs an `LiteLLMTool` instance from a `tool_call`."""
        model_json = jiter.from_json(tool_call.function.arguments.encode())
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)

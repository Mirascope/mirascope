"""The `OpenAITool` class for easy tool usage with OpenAI LLM calls."""

from __future__ import annotations

import copy

from anthropic.types import ToolParam, ToolUseBlock

from ..base import BaseTool


class AnthropicTool(BaseTool):
    """A class for defining tools for Anthropic LLM calls."""

    tool_call: ToolUseBlock

    @classmethod
    def tool_schema(cls) -> ToolParam:
        """Constructs a `ToolParam` tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        return ToolParam(
            input_schema=model_schema,
            name=cls._name(),
            description=cls._description(),
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlock) -> AnthropicTool:
        """Constructs an `AnthropicTool` instance from a `tool_call`."""
        model_json = copy.deepcopy(tool_call.input)
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)

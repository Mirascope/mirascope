"""The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

import copy

from anthropic.types import ToolParam, ToolUseBlock
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import TypedDict

from ..base import BaseTool, ToolConfig


class _CacheControl(TypedDict):
    type: str


class AnthropicToolConfig(ToolConfig, total=False):
    """A tool configuration for Anthropic-specific features."""

    cache_control: _CacheControl


class AnthropicTool(BaseTool[ToolParam]):
    """A class for defining tools for Anthropic LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.anthropic import anthropic_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @anthropic_call("claude-3-5-sonnet-20240620", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `AnthropicTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "anthropic"
    __tool_config_type__ = AnthropicToolConfig

    tool_call: SkipJsonSchema[ToolUseBlock]

    @classmethod
    def tool_schema(cls) -> ToolParam:
        """Constructs a `ToolParam` tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.anthropic import AnthropicTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = AnthropicTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Anthropic-specific tool schema
        ```
        """
        kwargs = {
            "input_schema": cls.model_json_schema(),
            "name": cls._name(),
            "description": cls._description(),
        }
        if "cache_control" in cls.tool_config:
            kwargs["cache_control"] = cls.tool_config["cache_control"]
        return ToolParam(**kwargs)

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlock) -> AnthropicTool:
        """Constructs an `AnthropicTool` instance from a `tool_call`.

        Args:
            tool_call: The Anthropic tool call from which to construct this tool
                instance.
        """
        model_json = copy.deepcopy(tool_call.input)
        model_json["tool_call"] = tool_call.model_dump()  # pyright: ignore [reportIndexIssue]
        return cls.model_validate(model_json)

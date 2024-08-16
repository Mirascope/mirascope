"""The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

usage docs: learn/tools.md#using-tools-with-standard-calls
"""

from __future__ import annotations

import copy

from anthropic.types import ToolParam, ToolUseBlock
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class AnthropicTool(BaseTool):
    """A class for defining tools for Anthropic LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.anthropic import anthropic_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @anthropic_call("claude-3-5-sonnet-20240620", tools=[format_book])
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `AnthropicTool` instance
        print(tool.call())
    ```
    """

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
        return ToolParam(
            input_schema=cls.model_tool_schema(),
            name=cls._name(),
            description=cls._description(),
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlock) -> AnthropicTool:
        """Constructs an `AnthropicTool` instance from a `tool_call`.

        Args:
            tool_call: The Anthropic tool call from which to construct this tool
                instance.
        """
        model_json = copy.deepcopy(tool_call.input)
        model_json["tool_call"] = tool_call.model_dump()  # type: ignore
        return cls.model_validate(model_json)

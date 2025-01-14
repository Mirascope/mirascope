"""The `BedrockTool` class for easy tool usage with Bedrock LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

from mypy_boto3_bedrock_runtime.type_defs import (
    ToolSpecificationTypeDef,
    ToolTypeDef,
)
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool, GenerateJsonSchemaNoTitles, ToolConfig
from ._types import ToolUseBlockContentTypeDef


class GenerateBedrockStrictToolJsonSchema(GenerateJsonSchemaNoTitles):
    pass


class BedrockToolConfig(ToolConfig, total=False):
    """A tool configuration for Bedrock-specific features."""

    pass


class BedrockTool(BaseTool):
    """A class for defining tools for Bedrock LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.bedrock import bedrock_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @bedrock_call("anthropic.claude-3-haiku-20240307-v1:0", tools=[format_book])
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `BedrockTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "bedrock"
    __tool_config_type__ = BedrockToolConfig

    tool_call: SkipJsonSchema[ToolUseBlockContentTypeDef]

    @classmethod
    def tool_schema(cls) -> ToolTypeDef:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.bedrock import BedrockTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = BedrockTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Bedrock-specific tool schema
        ```
        """
        schema_generator = GenerateJsonSchemaNoTitles
        return ToolTypeDef(
            toolSpec=ToolSpecificationTypeDef(
                name=cls._name(),
                description=cls._description(),
                inputSchema={
                    "json": cls.model_json_schema(schema_generator=schema_generator)
                },
            )
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlockContentTypeDef) -> BedrockTool:
        """Constructs an `BedrockTool` instance from a `tool_call`.

        Args:
            tool_call: The Bedrock tool call from which to construct this tool instance.
        """
        return cls.model_validate(
            {"tool_call": tool_call, **tool_call["toolUse"]["input"]}
        )

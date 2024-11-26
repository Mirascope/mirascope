"""The `AzureTool` class for easy tool usage with Azure LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

import jiter
from azure.ai.inference.models import (
    ChatCompletionsToolCall,
    ChatCompletionsToolDefinition,
    FunctionDefinition,
)
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool, GenerateJsonSchemaNoTitles, ToolConfig


class GenerateAzureStrictToolJsonSchema(GenerateJsonSchemaNoTitles):
    _azure_strict = True


class AzureToolConfig(ToolConfig, total=False):
    """A tool configuration for Azure-specific features."""

    strict: bool


class AzureTool(BaseTool):
    """A class for defining tools for Azure LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.azure import azure_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @azure_call("gpt-4o-mini", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `AzureTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "azure"
    __tool_config_type__ = AzureToolConfig

    tool_call: SkipJsonSchema[ChatCompletionsToolCall]

    @classmethod
    def tool_schema(cls) -> ChatCompletionsToolDefinition:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.azure import AzureTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = AzureTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Azure-specific tool schema
        ```
        """
        fn = FunctionDefinition(name=cls._name(), description=cls._description())
        schema_generator = GenerateJsonSchemaNoTitles
        model_schema = cls.model_json_schema(schema_generator=schema_generator)
        if model_schema["properties"]:
            fn["parameters"] = model_schema
        return ChatCompletionsToolDefinition(function=fn)

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionsToolCall) -> AzureTool:
        """Constructs an `AzureTool` instance from a `tool_call`.

        Args:
            tool_call: The Azure tool call from which to construct this tool instance.
        """
        model_json = {"tool_call": tool_call}
        if args := tool_call.function.arguments:
            model_json |= jiter.from_json(args.encode())
        return cls.model_validate(model_json)

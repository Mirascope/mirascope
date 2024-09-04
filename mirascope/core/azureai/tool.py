"""The `AzureAITool` class for easy tool usage with AzureAI LLM calls.

usage docs: learn/tools.md#using-tools-with-standard-calls
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


class GenerateAzureAIStrictToolJsonSchema(GenerateJsonSchemaNoTitles):
    _azureai_strict = True


class AzureAIToolConfig(ToolConfig, total=False):
    """A tool configuration for AzureAI-specific features."""

    strict: bool


class AzureAITool(BaseTool[ChatCompletionsToolDefinition]):
    """A class for defining tools for AzureAI LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.azureai import azureai_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @azureai_call("gpt-4o-mini", tools=[format_book])
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `AzureAITool` instance
        print(tool.call())
    ```
    """

    __provider__ = "azureai"
    __tool_config_type__ = AzureAIToolConfig

    tool_call: SkipJsonSchema[ChatCompletionsToolCall]

    @classmethod
    def tool_schema(cls) -> ChatCompletionsToolDefinition:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.azureai import AzureAITool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = AzureAITool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the AzureAI-specific tool schema
        ```
        """
        fn = FunctionDefinition(name=cls._name(), description=cls._description())
        schema_generator = GenerateJsonSchemaNoTitles
        model_schema = cls.model_json_schema(schema_generator=schema_generator)
        if model_schema["properties"]:
            fn["parameters"] = model_schema
        return ChatCompletionsToolDefinition(function=fn)

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionsToolCall) -> AzureAITool:
        """Constructs an `AzureAITool` instance from a `tool_call`.

        Args:
            tool_call: The AzureAI tool call from which to construct this tool instance.
        """
        model_json = jiter.from_json(tool_call.function.arguments.encode())
        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

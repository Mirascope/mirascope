"""The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

import jiter
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)
from openai.types.shared_params import FunctionDefinition
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool, GenerateJsonSchemaNoTitles, ToolConfig


class GenerateOpenAIStrictToolJsonSchema(GenerateJsonSchemaNoTitles):
    _openai_strict = True


class OpenAIToolConfig(ToolConfig, total=False):
    """A tool configuration for OpenAI-specific features."""

    strict: bool


class OpenAITool(BaseTool[ChatCompletionToolParam]):
    """A class for defining tools for OpenAI LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.openai import openai_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @openai_call("gpt-4o-mini", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `OpenAITool` instance
        print(tool.call())
    ```
    """

    __provider__ = "openai"
    __tool_config_type__ = OpenAIToolConfig

    tool_call: SkipJsonSchema[ChatCompletionMessageToolCall]

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.openai import OpenAITool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = OpenAITool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the OpenAI-specific tool schema
        ```
        """
        fn = FunctionDefinition(name=cls._name(), description=cls._description())
        schema_generator = GenerateJsonSchemaNoTitles
        if cls.tool_config.get("strict", False):
            fn["strict"] = True
            schema_generator = GenerateOpenAIStrictToolJsonSchema
        model_schema = cls.model_json_schema(schema_generator=schema_generator)
        if model_schema["properties"]:
            fn["parameters"] = model_schema
        return ChatCompletionToolParam(function=fn, type="function")

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionMessageToolCall) -> OpenAITool:
        """Constructs an `OpenAITool` instance from a `tool_call`.

        Args:
            tool_call: The OpenAI tool call from which to construct this tool instance.
        """
        model_json = jiter.from_json(tool_call.function.arguments.encode())
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)

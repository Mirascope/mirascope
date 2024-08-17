"""The `OpenAITool` class for easy tool usage with OpenAI LLM calls.

usage docs: learn/tools.md#using-tools-with-standard-calls
"""

from __future__ import annotations

import jiter
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)
from openai.types.shared_params import FunctionDefinition
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class OpenAITool(BaseTool):
    """A class for defining tools for OpenAI LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.openai import openai_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @openai_call("gpt-4o-mini", tools=[format_book])
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `OpenAITool` instance
        print(tool.call())
    ```
    """

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
        model_schema = cls.model_tool_schema()
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

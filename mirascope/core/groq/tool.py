"""The `GroqTool` class for easy tool usage with Groq LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

import jiter
from groq.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)
from groq.types.shared_params import FunctionDefinition
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class GroqTool(BaseTool):
    """A class for defining tools for Groq LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.groq import groq_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @groq_call("llama-3.1-8b-instant", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `GroqTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "groq"

    tool_call: SkipJsonSchema[ChatCompletionMessageToolCall]

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.groq import GroqTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = GroqTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Groq-specific tool schema
        ```
        """
        fn = FunctionDefinition(name=cls._name(), description=cls._description())
        model_schema = cls.model_json_schema()
        if model_schema["properties"]:
            fn["parameters"] = model_schema
        return ChatCompletionToolParam(function=fn, type="function")

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionMessageToolCall) -> GroqTool:
        """Constructs an `GroqTool` instance from a `tool_call`.

        Args:
            tool_call: The Groq tool call from which to construct this tool instance.
        """
        model_json = {"tool_call": tool_call}
        if args := tool_call.function.arguments:
            model_json |= jiter.from_json(args.encode())
        return cls.model_validate(model_json)

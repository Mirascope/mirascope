"""The `MistralTool` class for easy tool usage with Mistral LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

from typing import Any

import jiter
from mistralai.models import ToolCall
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class MistralTool(BaseTool):
    """A class for defining tools for Mistral LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.mistral import mistral_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @mistral_call("mistral-large-latest", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    response = recommend_book("fantasy")
    if tool := response.tool:  # returns a `MistralTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "mistral"

    tool_call: SkipJsonSchema[ToolCall]

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.mistral import MistralTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = MistralTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Mistral-specific tool schema
        ```
        """
        fn: dict[str, Any] = {"name": cls._name(), "description": cls._description()}
        model_schema = cls.model_json_schema()
        fn["parameters"] = (
            model_schema if model_schema["properties"] else {"type": "object"}
        )
        return {"function": fn, "type": "function"}

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> MistralTool:
        """Constructs an `MistralTool` instance from a `tool_call`.

        Args:
            tool_call: The Mistral tool call from which to construct this tool instance.
        """
        model_json = {"tool_call": tool_call}
        if args := tool_call.function.arguments:
            model_json |= (
                jiter.from_json(args.encode()) if isinstance(args, str) else args
            )
        return cls.model_validate(model_json)

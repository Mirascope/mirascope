"""The `CohereTool` class for easy tool usage with Cohere LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

from cohere.types import Tool, ToolCall, ToolParameterDefinitionsValue
from pydantic import SkipValidation
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class CohereTool(BaseTool):
    """A class for defining tools for Cohere LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.cohere import cohere_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @cohere_call("command-r-plus", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `CohereTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "cohere"

    tool_call: SkipValidation[SkipJsonSchema[ToolCall]]

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.cohere import CohereTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = CohereTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Cohere-specific tool schema
        ```
        """
        model_schema = cls.model_json_schema()
        parameter_definitions = None
        if "properties" in model_schema:
            if "$defs" in model_schema["properties"]:
                raise ValueError(  # pragma: no cover
                    "Unfortunately Cohere's chat API cannot handle nested structures "
                    "with $defs."
                )
            parameter_definitions = {
                prop: ToolParameterDefinitionsValue(
                    description=prop_schema.get("description", None),
                    type=prop_schema["type"],
                    required="required" in model_schema
                    and prop in model_schema["required"],
                )
                for prop, prop_schema in model_schema["properties"].items()
            }
        return Tool(
            name=cls._name(),
            description=cls._description(),
            parameter_definitions=parameter_definitions,
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> CohereTool:
        """Constructs an `CohereTool` instance from a `tool_call`.

        Args:
            tool_call: The Cohere tool call from which to construct this tool instance.
        """
        model_json = {**tool_call.parameters}
        model_json["tool_call"] = tool_call.dict()
        return cls.model_validate(model_json)

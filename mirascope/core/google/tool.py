"""The `GoogleTool` class for easy tool usage with Google's Google LLM calls.

usage docs: learn/tools.md
"""

from __future__ import annotations

from typing import Any

from google.genai.types import (
    FunctionCall,
    FunctionDeclaration,
    Tool,
)
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class GoogleTool(BaseTool):
    """A class for defining tools for Google LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.google import google_call


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @google_call("google-1.5-flash", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")
    if tool := response.tool:  # returns an `GoogleTool` instance
        print(tool.call())
    ```
    """

    __provider__ = "google"

    tool_call: SkipJsonSchema[FunctionCall]

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.core.google import GoogleTool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = GoogleTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the Google-specific tool schema
        ```
        """
        model_schema = cls.model_json_schema()
        fn: dict[str, Any] = {"name": cls._name(), "description": cls._description()}

        if model_schema["properties"]:
            fn["parameters"] = model_schema

        if "parameters" in fn:
            # Resolve $defs and $ref
            if "$defs" in fn["parameters"]:
                defs = fn["parameters"].pop("$defs")

                def resolve_refs(schema: dict[str, Any]) -> dict[str, Any]:
                    """Recursively resolve $ref references using the $defs dictionary."""
                    # If this is a reference, resolve it
                    if "$ref" in schema:
                        ref = schema["$ref"]
                        if ref.startswith("#/$defs/"):
                            ref_key = ref.replace("#/$defs/", "")
                            if ref_key in defs:
                                # Merge the definition with the current schema (excluding $ref)
                                resolved = {
                                    **{k: v for k, v in schema.items() if k != "$ref"},
                                    **resolve_refs(defs[ref_key]),
                                }
                                return resolved

                    # Process all other keys recursively
                    result = {}
                    for key, value in schema.items():
                        if isinstance(value, dict):
                            result[key] = resolve_refs(value)
                        elif isinstance(value, list):
                            result[key] = [
                                resolve_refs(item) if isinstance(item, dict) else item
                                for item in value
                            ]
                        else:
                            result[key] = value
                    return result

                # Resolve all references in the parameters
                fn["parameters"] = resolve_refs(fn["parameters"])

            def handle_enum_schema(prop_schema: dict[str, Any]) -> dict[str, Any]:
                if "enum" in prop_schema:
                    prop_schema["format"] = "enum"
                return prop_schema

            # Process properties after resolving references
            fn["parameters"]["properties"] = {
                prop: {
                    key: value
                    for key, value in handle_enum_schema(prop_schema).items()
                    if key != "default"
                }
                for prop, prop_schema in fn["parameters"]["properties"].items()
            }
        return Tool(function_declarations=[FunctionDeclaration(**fn)])

    @classmethod
    def from_tool_call(cls, tool_call: FunctionCall) -> GoogleTool:
        """Constructs an `GoogleTool` instance from a `tool_call`.

        Args:
            tool_call: The Google tool call from which to construct this tool instance.
        """
        model_json = {"tool_call": tool_call}
        if tool_call.args:
            model_json |= dict(tool_call.args.items())
        return cls.model_validate(model_json)

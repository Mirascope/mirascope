"""Classes for using tools with Google's Gemini API."""
from __future__ import annotations

from typing import Any, Callable, Type, Union

from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)
from pydantic import BaseModel, ConfigDict

from ..base import (
    BaseTool,
    BaseType,
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)


class NoDefsFunctionDeclaration(FunctionDeclaration):
    def __init__(self, **kwargs):
        self._defs = kwargs.pop("$defs", None)  # Store $defs separately
        super().__init__(**kwargs)


def resolve_refs(
    schema: Union[dict[str, Any], list[Any]], defs: dict[str, Any]
) -> Union[dict[str, Any], list[Any]]:
    """Recursively resolves $ref references within a schema."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"].lstrip("#/")
            if ref_path.startswith("$defs/"):
                ref_name = ref_path.split("/")[1]
                ref_schema = defs.get(ref_name)
                if ref_schema is None:
                    raise ValueError(f"Invalid reference: {schema['$ref']}")
                return resolve_refs(ref_schema, defs)
        else:
            return {k: resolve_refs(v, defs) for k, v in schema.items() if k != "title"}
    elif isinstance(schema, list):
        return [resolve_refs(item, defs) for item in schema]
    else:
        return schema


class GeminiTool(BaseTool[FunctionCall]):
    '''A base class for easy use of tools with the Gemini API.

    `GeminiTool` internally handles the logic that allows you to use tools with simple
    calls such as `GeminiCompletion.tool` or `GeminiTool.fn`, as seen in the
    examples below.

    Example:

    ```python
    from mirascope.gemini import GeminiCall, GeminiCallParams, GeminiTool


    class CurrentWeather(GeminiTool):
        """A tool for getting the current weather in a location."""

        location: str


    class WeatherForecast(GeminiPrompt):
        prompt_template = "What is the current weather in {city}?"

        city: str

        call_params = GeminiCallParams(
            model="gemini-pro",
            tools=[CurrentWeather],
        )


    prompt = WeatherPrompt()
    forecast = WeatherForecast(city="Tokyo").call().tool
    print(forecast.location)
    #> Tokyo
    ```
    '''

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a tool schema for use with the Gemini API.

        A Mirascope `GeminiTool` is deconstructed into a `Tool` schema for use with the
        Gemini API.

        Returns:
            The constructed `Tool` schema.
        """
        tool_schema = super().tool_schema()
        if "parameters" in tool_schema:
            # Handle nested structures with $defs
            if "$defs" in tool_schema["parameters"]:
                defs = tool_schema["parameters"]["$defs"]
                # Resolve references in properties
                for key, prop_schema in tool_schema["parameters"]["properties"].items():
                    tool_schema["parameters"]["properties"][key] = resolve_refs(
                        prop_schema, defs
                    )

                # Remove $defs after resolving references
                del tool_schema["parameters"]["$defs"]

            # Remove title from properties
            tool_schema["parameters"]["properties"] = {
                prop: {
                    key: value for key, value in prop_schema.items() if key != "title"
                }
                for prop, prop_schema in tool_schema["parameters"]["properties"].items()
            }

        # Use CustomFunctionDeclaration to handle $defs
        return Tool(function_declarations=[NoDefsFunctionDeclaration(**tool_schema)])

    @classmethod
    def from_tool_call(cls, tool_call: FunctionCall) -> GeminiTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given a `GenerateContentResponse` from a Gemini chat completion response, this
        method extracts the tool call and constructs an instance of the tool.

        Args:
            tool_call: The `GenerateContentResponse` from which to extract the tool.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValueError: if the tool call doesn't have any arguments.
            ValidationError: if the tool call doesn't match the tool schema.
        """
        if not tool_call.args:
            raise ValueError("Tool call doesn't have any arguments.")
        model_json = {key: value for key, value in tool_call.args.items()}
        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[GeminiTool]:
        """Constructs a `GeminiTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, GeminiTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[GeminiTool]:
        """Constructs a `GeminiTool` type from a function."""
        return convert_function_to_tool(fn, GeminiTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseType]) -> Type[GeminiTool]:
        """Constructs a `GeminiTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, GeminiTool)

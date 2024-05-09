"""Classes for using tools with Google's Gemini API."""
from __future__ import annotations

import pprint
from typing import Any, Callable, Type

import jsonref
from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)
from pydantic import BaseModel, ConfigDict

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from mirascope.gemini.utils import remove_invalid_title_keys_from_parameters

from ..base import (
    BaseTool,
    BaseType,
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)


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
        super().tool_schema()
        model_schema: dict[str, Any] = cls.model_json_schema()
        pprint.pprint(model_schema)

        # Replace all references with their values
        without_refs: dict[str, Any] = jsonref.replace_refs(model_schema)  # type: ignore
        pprint.pprint(without_refs)

        # Remove all Defs
        without_refs.pop("$defs")
        pprint.pprint(without_refs)

        # Get the name and description, and remove them from the schema
        name: str = without_refs.pop("title")  # type: ignore
        description: str = (  # type: ignore
            without_refs.pop("description", None) or DEFAULT_TOOL_DOCSTRING
        )
        parameters: dict[str, Any] = without_refs

        # Remove all instances of title key in each param definition
        # This is careful not to delete keys that represent a field with the name title
        remove_invalid_title_keys_from_parameters(parameters)

        print(f"{name=}")
        print(f"{description=}")
        print(f"{parameters=}")

        return Tool(
            function_declarations=[
                FunctionDeclaration(
                    name=name,
                    description=description,
                    parameters=parameters,
                )
            ]
        )

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

"""Classes for using tools with Google's Gemini Chat APIs."""
from __future__ import annotations

from typing import Any, Callable, Type

from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)
from pydantic import BaseModel, ConfigDict

from ...prompts.tools import (
    BaseTool,
    convert_base_model_to_tool,
    convert_function_to_tool,
)


class GeminiTool(BaseTool):
    '''A base class for easy use of tools with the Gemini Chat client.

    `GeminiTool` internally handles the logic that allows you to use tools with simple
    calls such as `GeminiCompletion.tool` or `GeminiTool.fn`, as seen in the
    examples below.

    Example:

    ```python
    from mirascope.chat.gemini import GeminiCallParams, GeminiPrompt, GeminiTool


    class CurrentWeather(GeminiTool):
        """A tool for getting the current weather in a location."""

        location: str


    class WeatherPrompt(GeminiPrompt):
        """What is the current weather in Tokyo?"""

        call_params = GeminiCallParams(
            model="gemini-pro",
            tools=[CurrentWeather],
        )


    prompt = WeatherPrompt()
    current_weather = prompt.create().tool
    print(current_weather.location)
    #> Tokyo
    ```
    '''

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a tool schema for use with the OpenAI Chat client.

        A Mirascope `GeminiTool` is deconstructed into a `Tool` schema for use with the
        Gemini Chat client.

        Returns:
            The constructed `Tool` schema.

        Raises:
            ValueError: if the class doesn't have a docstring description.
        """
        model_schema = cls.model_json_schema()
        if "description" not in model_schema:
            raise ValueError("Tool must have a docstring description.")

        tool_schema = super().tool_schema()
        if "parameters" in tool_schema:
            tool_schema["parameters"].pop("$defs")
            tool_schema["parameters"]["properties"] = {
                prop: {
                    key: value for key, value in prop_schema.items() if key != "title"
                }
                for prop, prop_schema in tool_schema["parameters"]["properties"].items()
            }
        return Tool(function_declarations=[FunctionDeclaration(**tool_schema)])

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
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[GeminiTool]:
        """Constructs a `GeminiTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, GeminiTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[GeminiTool]:
        """Constructs a `GeminiTool` type from a function."""
        return convert_function_to_tool(fn, GeminiTool)

"""Classes for using tools with Cohere chat APIs."""

from __future__ import annotations

from typing import Callable, Type

from cohere.types import Tool, ToolCall, ToolParameterDefinitionsValue
from pydantic import BaseModel, SkipValidation
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool, BaseType
from ..base.tools import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)


class CohereTool(BaseTool[ToolCall]):
    '''A base class for easy use of tools with the Cohere chat client.

    `CohereTool` internally handles the logic that allows you to use tools with simple
    calls such as `CohereCallResponse.tool` or `CohereTool.fn`, as seen in the
    examples below.

    Example:

    ```python
    from mirascope.cohere import CohereCall, CohereCallParams


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(CohereCall):
        prompt_template = """
        Tell me my favorite animal if my favorite food is {food} and my
        favorite color is {color}.
        """

        food: str
        color: str

        call_params = CohereCallParams(tools=[animal_matcher])


    response = AnimalMatcher(food="pizza", color="red").call
    tool = response.tool
    print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    ```
    '''

    tool_call: SkipJsonSchema[SkipValidation[ToolCall]]

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a tool schema for use with the Cohere chat client.

        A Mirascope `CohereTool` is deconstructed into a JSON schema, and relevant keys
        are renamed to match the Cohere tool schema used to make function/tool calls in
        the Cohere chat API.

        Returns:
            The constructed tool schema.
        """
        tool_schema = super().tool_schema()
        parameter_definitions = None
        if "parameters" in tool_schema:
            if "$defs" in tool_schema["parameters"]:
                raise ValueError(
                    "Unfortunately Cohere's chat API cannot handle nested structures "
                    "with $defs."
                )
            parameter_definitions = {
                prop: ToolParameterDefinitionsValue(
                    description=prop_schema["description"]
                    if "description" in prop_schema
                    else None,
                    type=prop_schema["type"],
                    required="required" in tool_schema["parameters"]
                    and prop in tool_schema["parameters"]["required"],
                )
                for prop, prop_schema in tool_schema["parameters"]["properties"].items()
            }
        return Tool(
            name=tool_schema["name"],
            description=tool_schema["description"],
            parameter_definitions=parameter_definitions,
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> CohereTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ToolCall` from an Cohere chat completion response, takes its function
        arguments and creates an `CohereTool` instance from it.

        Args:
            tool_call: The `...` to extract the tool from.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """
        model_json = tool_call.parameters
        model_json["tool_call"] = tool_call  # type: ignore
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[CohereTool]:
        """Constructs a `CohereTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, CohereTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[CohereTool]:
        """Constructs a `CohereTool` type from a function."""
        return convert_function_to_tool(fn, CohereTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseType]) -> Type[CohereTool]:
        """Constructs a `CohereTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, CohereTool)

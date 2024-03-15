"""Classes for using tools with Anthropic's Claude API."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from textwrap import dedent
from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel

from ..base import BaseTool, BaseType
from ..base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)


class AnthropicTool(BaseTool[ET.Element]):
    '''

    Example:

    ```python
    from mirascope import AnthropicCall, AnthropicCallParams


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(AnthropicCall):
        prompt_template = """\\
        Tell me my favorite animal if my favorite food is {food} and my
        favorite color is {color}.
        """

        food: str
        color: str

        call_params = AnthropicCallParams(tools=[animal_matcher])


    response = AnimalMatcher(food="pizza", color="red").call
    tool = response.tool
    print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    ```
    '''

    @classmethod
    def tool_schema(cls) -> str:
        """Constructs XML tool schema string for use with Anthropic's Claude API."""
        json_schema = super().tool_schema()
        tool_schema = (
            dedent(
                """
                <tool_description>
                <tool_name>{name}</tool_name>
                <description>
                {description}
                </description>
                """
            )
            .strip()
            .format(name=cls.__name__, description=json_schema["description"])
        )
        if "parameters" in json_schema:
            tool_schema += "\n<parameters>\n"
            for prop, definition in json_schema["parameters"]["properties"].items():
                tool_schema += "<parameter>\n"
                tool_schema += f"<name>{prop}</name>\n"
                tool_schema += f"<type>{definition['type']}</type>\n"
                if "description" in definition:
                    tool_schema += (
                        f"<description>{definition['description']}</description>\n"
                    )
                if "default" in definition:
                    tool_schema += f"<default>{definition['default']}</default>\n"
                tool_schema += "</parameter>\n"
            tool_schema += "</parameters>\n"
        tool_schema += "</tool_description>"
        return tool_schema

    @classmethod
    def from_tool_call(cls, tool_call: ET.Element) -> AnthropicTool:
        """Extracts an instance of the tool constructed from a tool call repsonse.

        Given the `<invoke>...</invoke>` block in a `Message` from an Anthropic call
        response, this method parses out the XML defining the tool call and creates an
        `AnthropicTool` instance from it.

        Args:
            tool_call: The XML `str` from which to extract the tool.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """
        try:
            assert tool_call.tag == "invoke", "missing `<invoke>` root tag."
        except AssertionError as e:
            raise ValueError(f"Input `tool_call` XML had structure issues: {e}")

        parameters: dict[str, Any] = {"tool_call": tool_call}
        parameters_node = tool_call.find("parameters")
        if parameters_node is not None:
            parameters.update(
                {
                    parameter_node.tag: parameter_node.text
                    for parameter_node in parameters_node
                }
            )
        return cls.model_validate(parameters)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, AnthropicTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a function."""
        return convert_function_to_tool(fn, AnthropicTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseTypeT]) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, AnthropicTool)

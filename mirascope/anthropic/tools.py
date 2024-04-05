"""Classes for using tools with Anthropic's Claude API."""

from __future__ import annotations

from typing import Callable, Type, TypeVar

from anthropic.types.beta.tools import ToolParam, ToolUseBlock
from pydantic import BaseModel

from ..base import BaseTool, BaseType
from ..base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)


class AnthropicTool(BaseTool[ToolUseBlock]):
    '''A base class for easy use of tools with the Anthropic Claude client.

    `AnthropicTool` internally handles the logic that allows you to use tools with
    simple calls such as `AnthropicCallResponse.tool` or `AnthropicTool.fn`, as seen in
    the example below.

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
        prompt_template = """
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
    def tool_schema(cls) -> ToolParam:
        """Constructs JSON tool schema for use with Anthropic's Claude API."""
        schema = super().tool_schema()
        return ToolParam(
            input_schema=schema["parameters"],
            name=schema["name"],
            description=schema["description"],
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolUseBlock) -> AnthropicTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given the tool call contents in a `Message` from an Anthropic call response,
        this method parses out the arguments of the tool call and creates an
        `AnthropicTool` instance from them.

        Args:
            tool_call: The list of `TextBlock` contents.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """
        model_json = tool_call.input
        model_json["tool_call"] = tool_call.model_dump()  # type: ignore
        return cls.model_validate(model_json)

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

"""Classes for using tools with Mistral Chat APIs"""
from __future__ import annotations

import json
from typing import Any, Callable, Type, TypeVar

from mistralai.models.chat_completion import ToolCall
from pydantic import BaseModel

from ..base import BaseTool, BaseType
from ..base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)


class MistralTool(BaseTool[ToolCall]):
    '''A base class for easy use of tools with the Mistral client.

    `MistralTool` internally handles the logic that allows you to use tools with simple
    calls such as `MistralCallResponse.tool` or `MistralTool.fn`, as seen in the 
    examples below.
    
    Example:

    ```python
    import os

    from mirascope.mistral import MistralCall, MistralCallParams


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(MistralCall):
        prompt_template = """\\
            Tell me my favorite animal if my favorite food is {food} and my
            favorite color is {color}.
        """

        food: str
        color: str

        api_key = os.getenv("MISTRAL_API_KEY")
        call_params = MistralCallParams(
            model="mistral-large-latest", tools=[animal_matcher]
        )


    prompt = AnimalMatcher(food="pizza", color="green")
    response = prompt.call()

    if tools := response.tools:
        for tool in tools:
            print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    '''

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        """Constructs a tool schema for use with the Mistral Chat client.

        A Mirascope `MistralTool` is deconstructed into a JSON schema, and relevant keys
        are renamed to match the Mistral API schema used to make functional/tool calls
        in Mistral API.

        Returns:
            The constructed tool schema.
        """
        fn = super().tool_schema()
        return {"type": "function", "function": fn}

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> MistralTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ToolCall` from a Mistral chat completion response, takes its function
        arguments and creates a `MistralTool` instance from it.

        Args:
            tool_call: The Mistral `ToolCall` to extract the tool from.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValueError: if the tool call doesn't match the tool schema.
        """
        try:
            model_json = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError() from e

        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[MistralTool]:
        """Constructs a `OpenAITool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, MistralTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[MistralTool]:
        """Constructs a `OpenAITool` type from a function."""
        return convert_function_to_tool(fn, MistralTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseTypeT]) -> Type[MistralTool]:
        """Constructs a `MistralTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, MistralTool)

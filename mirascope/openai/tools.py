"""Classes for using tools with OpenAI Chat APIs."""

from __future__ import annotations

import json
from typing import Callable, Type, cast

from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolParam
from pydantic import BaseModel
from pydantic_core import from_json

from ..base import BaseTool, BaseType
from ..base.tools import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)


class OpenAITool(BaseTool[ChatCompletionMessageToolCall]):
    '''A base class for easy use of tools with the OpenAI Chat client.

    `OpenAITool` internally handles the logic that allows you to use tools with simple
    calls such as `OpenAICallResponse.tool` or `OpenAITool.fn`, as seen in the
    examples below.

    Example:

    ```python
    from mirascope.openai import OpenAICall, OpenAICallParams


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(OpenAICall):
        prompt_template = """
        Tell me my favorite animal if my favorite food is {food} and my
        favorite color is {color}.
        """

        food: str
        color: str

        call_params = OpenAICallParams(tools=[animal_matcher])


    response = AnimalMatcher(food="pizza", color="red").call
    tool = response.tool
    print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    ```
    '''

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a tool schema for use with the OpenAI Chat client.

        A Mirascope `OpenAITool` is deconstructed into a JSON schema, and relevant keys
        are renamed to match the OpenAI `ChatCompletionToolParam` schema used to make
        function/tool calls in OpenAI API.

        Returns:
            The constructed `ChatCompletionToolParam` schema.
        """
        fn = super().tool_schema()
        return cast(ChatCompletionToolParam, {"type": "function", "function": fn})

    @classmethod
    def from_tool_call(
        cls,
        tool_call: ChatCompletionMessageToolCall,
        allow_partial: bool = False,
    ) -> OpenAITool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ChatCompletionMessageToolCall` from an OpenAI chat completion response,
        takes its function arguments and creates an `OpenAITool` instance from it.

        Args:
            tool_call: The `ChatCompletionMessageToolCall` to extract the tool from.
            allow_partial: Whether to allow partial JSON schemas.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """
        if allow_partial:
            model_json = from_json(tool_call.function.arguments, allow_partial=True)
        else:
            try:
                model_json = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                raise ValueError() from e

        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[OpenAITool]:
        """Constructs a `OpenAITool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, OpenAITool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[OpenAITool]:
        """Constructs a `OpenAITool` type from a function."""
        return convert_function_to_tool(fn, OpenAITool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseType]) -> Type[OpenAITool]:
        """Constructs a `OpenAITool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, OpenAITool)

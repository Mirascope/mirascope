"""Classes for using tools with OpenAI Chat APIs."""
from __future__ import annotations

import json
from typing import cast

from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolParam
from pydantic import ConfigDict

from ..tools import BaseTool


class OpenAITool(BaseTool):
    '''A base class for easy use of tools with the OpenAI Chat client.

    `OpenAITool` internally handles the logic that allows you to use tools with simple
    calls such as `OpenAIChatCompletion.tool` or `OpenAITool.fn`, as seen in the
    examples below.

    Example:

    ```python
    from mirascope import OpenAICallParams, Prompt, OpenAIChat, OpenAIToolStreamParser


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalPrompt(Prompt):
        """
        Tell me my favorite animal if my favorite food is {food} and my
        favorite color is {color}.
        """

        food: str
        color: str

        call_params = OpenAICallParams(tools=[animal_matcher])


    prompt = AnimalPrompt(food="pizza", color="red")
    chat = OpenAIChat()

    response = chat.create(prompt)
    tool = response.tool

    print(tool.fn(**tool.model_dump(exclude={"tool_call"})))
    #> Your favorite animal is the best one, a frog.

    stream = chat.stream(prompt)
    parser = OpenAIToolStreamParser(tools=prompt.call_params.tools)

    for tool in parser.from_stream(stream):
        print(tool.fn(**tool.model_dump(exclude={"tool_call"})))
    #> Your favorite animal is the best one, a frog.
    ```
    '''

    tool_call: ChatCompletionMessageToolCall

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a tool schema for use with the OpenAI Chat client.

        A Mirascope `OpenAITool` is deconstructed into a JSON schema, and relevant keys
        are renamed to match the OpenAI `ChatCompletionToolParam` schema used to make
        function/tool calls in OpenAI API.

        Returns:
            The constructed `ChatCompletionToolParam` schema.

        Raises:
            ValueError: if the class doesn't have a docstring description.
        """
        fn = super().tool_schema()
        return cast(ChatCompletionToolParam, {"type": "function", "function": fn})

    @classmethod
    def from_tool_call(cls, tool_call: ChatCompletionMessageToolCall) -> OpenAITool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ChatCompletionMessageToolCall` from an OpenAI chat completion response,
        takes its function arguments and creates an `OpenAITool` instance from it.

        Args:
            tool_call: The `ChatCompletionMessageToolCall` to extract the tool from.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """
        try:
            model_json = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError() from e

        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

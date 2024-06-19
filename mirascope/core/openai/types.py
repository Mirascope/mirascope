"""Types for the Mirascope OpenAI module."""

from __future__ import annotations

import jiter
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionStreamOptionsParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.completion_usage import CompletionUsage
from openai.types.shared_params import FunctionDefinition
from pydantic import computed_field
from typing_extensions import NotRequired, Required

from ..base.types import BaseCallParams, BaseCallResponse, BaseFunctionReturn, BaseTool


class OpenAITool(BaseTool):
    """A class for defining tools for OpenAI LLM calls."""

    tool_call: ChatCompletionMessageToolCall

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn = FunctionDefinition(name=cls.name(), description=cls.description())
        if model_schema["properties"]:
            fn["parameters"] = model_schema

        return ChatCompletionToolParam(function=fn, type="function")

    @classmethod
    def from_tool_call(
        cls, tool_call: ChatCompletionMessageToolCall, allow_partial: bool = False
    ) -> OpenAITool:
        """Constructs an `OpenAITool` instance from a `tool_call`."""
        model_json = jiter.from_json(
            tool_call.function.arguments.encode(),
            partial_mode="trailing-strings" if allow_partial else "off",
        )
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API."""

    model: Required[str]
    frequency_penalty: NotRequired[float | None]
    logit_bias: NotRequired[dict[str, int] | None]
    logprobs: NotRequired[bool | None]
    max_tokens: NotRequired[int | None]
    n: NotRequired[int | None]
    parallel_tool_calls: NotRequired[bool]
    presence_penalty: NotRequired[float | None]
    response_format: NotRequired[ResponseFormat]
    seed: NotRequired[int | None]
    stop: NotRequired[str | list[str] | None]
    stream_options: NotRequired[ChatCompletionStreamOptionsParam | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
    top_logprobs: NotRequired[int | None]
    top_p: NotRequired[float | None]
    user: NotRequired[str]


OpenAICallFunctionReturn = BaseFunctionReturn[
    ChatCompletionMessageParam, OpenAICallParams
]
'''The function return type for functions wrapped with the `openai_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the OpenAI API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the OpenAI API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.openai import OpenAICallFunctionReturn, openai_call

@openai_call(model="gpt-4o")
def recommend_book(genre: str) -> OpenAICallFunctionReturn:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''


class OpenAICallResponse(
    BaseCallResponse[
        ChatCompletion,
        OpenAITool,
        OpenAICallFunctionReturn,
        ChatCompletionMessageParam,
        OpenAICallParams,
        ChatCompletionUserMessageParam,
    ]
):
    '''A convenience wrapper around the OpenAI `ChatCompletion` response.

    When calling the OpenAI API using a function decorated with `openai_call`, the
    response will be an `OpenAICallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `OpenAICallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    @computed_field
    @property
    def message_param(self) -> ChatCompletionAssistantMessageParam:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump(exclude={"function_call"})  # type: ignore

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChatCompletionMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.message.content if self.message.content is not None else ""

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.response.choices]

    @property
    def tool_calls(self) -> list[ChatCompletionMessageToolCall] | None:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @computed_field
    @property
    def tools(self) -> list[OpenAITool] | None:
        """Returns any available tool calls as their `OpenAITool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> OpenAITool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[OpenAITool, str]]
    ) -> list[ChatCompletionToolMessageParam]:
        return [
            ChatCompletionToolMessageParam(
                role="tool",
                content=output,
                tool_call_id=tool.tool_call.id,
                name=tool.name(),  # type: ignore
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens if self.usage else None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens if self.usage else None

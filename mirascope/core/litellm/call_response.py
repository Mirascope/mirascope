"""This module contains the `LiteLLMCallResponse` class."""

from typing import Any

from litellm.batches.main import ModelResponse
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from pydantic import computed_field

from ..base import BaseCallResponse
from .call_params import LiteLLMCallParams
from .dynamic_config import LiteLLMDynamicConfig
from .tool import LiteLLMTool


class LiteLLMCallResponse(
    BaseCallResponse[
        ModelResponse,
        LiteLLMTool,
        LiteLLMDynamicConfig,
        ChatCompletionMessageParam,
        LiteLLMCallParams,
        ChatCompletionUserMessageParam,
    ]
):
    '''A convenience wrapper around the LiteLLM `ChatCompletion` response.

    When calling the LiteLLM API using a function decorated with `openai_call`, the
    response will be an `LiteLLMCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `LiteLLMCallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    _provider = "openai"

    @computed_field
    @property
    def message_param(self) -> ChatCompletionAssistantMessageParam:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump(exclude={"function_call"})  # type: ignore

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.response.choices  # type: ignore

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
    def model(self) -> str | None:
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
    def tools(self) -> list[LiteLLMTool] | None:
        """Returns any available tool calls as their `LiteLLMTool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> LiteLLMTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[LiteLLMTool, str]]
    ) -> list[ChatCompletionToolMessageParam]:
        """Returns the tool message parameters for tool call results."""
        return [
            ChatCompletionToolMessageParam(
                role="tool",
                content=output,
                tool_call_id=tool.tool_call.id,
                name=tool._name(),  # type: ignore
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def usage(self) -> Any | None:
        """Returns the usage of the chat completion."""
        return self.response.usage  # type: ignore

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens if self.usage else None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens if self.usage else None

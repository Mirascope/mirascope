"""This module contains the `MistralCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from typing import Any

from mistralai.models.chat_completion import ChatCompletionResponse, ChatMessage
from mistralai.models.common import UsageInfo
from pydantic import computed_field

from ..base import BaseCallResponse
from ._utils import calculate_cost
from .call_params import MistralCallParams
from .dynamic_config import AsyncMistralDynamicConfig, MistralDynamicConfig
from .tool import MistralTool


class MistralCallResponse(
    BaseCallResponse[
        ChatCompletionResponse,
        MistralTool,
        dict[str, Any],
        AsyncMistralDynamicConfig | MistralDynamicConfig,
        ChatMessage,
        MistralCallParams,
        ChatMessage,
    ]
):
    """A convenience wrapper around the Mistral `ChatCompletion` response.

    When calling the Mistral API using a function decorated with `mistral_call`, the
    response will be an `MistralCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.mistral import mistral_call


    @mistral_call("mistral-largel-latest")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    response = recommend_book("fantasy")  # response is an `MistralCallResponse` instance
    print(response.content)
    ```
    """

    _provider = "mistral"

    @property
    def content(self) -> str:
        """The content of the chat completion for the 0th choice."""
        return self.response.choices[0].message.content

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self.response.choices
        ]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def usage(self) -> UsageInfo:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> ChatMessage:
        """Returns the assistants's response as a message parameter."""
        return self.response.choices[0].message

    @computed_field
    @property
    def tools(self) -> list[MistralTool] | None:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tool_calls = self.response.choices[0].message.tool_calls
        if not self.tool_types or not tool_calls:
            return None

        extracted_tools = []
        for tool_call in tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> MistralTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[MistralTool, str]]
    ) -> list[ChatMessage]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ChatMessage` parameters.
        """
        return [
            ChatMessage(
                role="tool",
                content=output,
                tool_call_id=tool.tool_call.id,
                name=tool._name(),
            )
            for tool, output in tools_and_outputs
        ]

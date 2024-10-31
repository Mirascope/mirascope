"""This module contains the `GroqCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from groq.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from groq.types.completion_usage import CompletionUsage
from pydantic import SerializeAsAny, computed_field

from ..base import BaseCallResponse
from ._utils import calculate_cost
from .call_params import GroqCallParams
from .dynamic_config import AsyncGroqDynamicConfig, GroqDynamicConfig
from .tool import GroqTool


class GroqCallResponse(
    BaseCallResponse[
        ChatCompletion,
        GroqTool,
        ChatCompletionToolParam,
        AsyncGroqDynamicConfig | GroqDynamicConfig,
        ChatCompletionMessageParam,
        GroqCallParams,
        ChatCompletionUserMessageParam,
    ]
):
    """A convenience wrapper around the Groq `ChatCompletion` response.

    When calling the Groq API using a function decorated with `groq_call`, the
    response will be an `GroqCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.groq import groq_call


    @groq_call("llama-3.1-8b-instant")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    response = recommend_book("fantasy")  # response is an `GroqCallResponse` instance
    print(response.content)
    ```
    """

    _provider = "groq"

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        message = self.response.choices[0].message
        return message.content if message.content is not None else ""

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.response.choices]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

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

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> SerializeAsAny[ChatCompletionAssistantMessageParam]:
        """Returns the assistants's response as a message parameter."""
        message_param = self.response.choices[0].message.model_dump(
            exclude={"function_call"}
        )
        return ChatCompletionAssistantMessageParam(**message_param)

    @computed_field
    @property
    def tools(self) -> list[GroqTool] | None:
        """Returns any available tool calls as their `GroqTool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
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
    def tool(self) -> GroqTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[GroqTool, str]]
    ) -> list[ChatCompletionToolMessageParam]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ChatCompletionToolMessageParam` parameters.
        """
        return [
            ChatCompletionToolMessageParam(
                role="tool",
                content=output,
                tool_call_id=tool.tool_call.id,
                name=tool._name(),  # pyright: ignore [reportCallIssue]
            )
            for tool, output in tools_and_outputs
        ]

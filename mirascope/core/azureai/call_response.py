"""This module contains the `AzureAICallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from azure.ai.inference.models import (
    AssistantMessage,
    ChatCompletions,
    ChatCompletionsToolDefinition,
    ChatRequestMessage,
    CompletionsUsage,
    ToolMessage,
    UserMessage,
)
from pydantic import SerializeAsAny, SkipValidation, computed_field

from ..base import BaseCallResponse
from ._utils import calculate_cost
from .call_params import AzureAICallParams
from .dynamic_config import AzureAIDynamicConfig
from .tool import AzureAITool


class AzureAICallResponse(
    BaseCallResponse[
        ChatCompletions,
        AzureAITool,
        ChatCompletionsToolDefinition,
        AzureAIDynamicConfig,
        ChatRequestMessage,
        AzureAICallParams,
        UserMessage,
    ]
):
    """A convenience wrapper around the AzureAI `ChatCompletion` response.

    When calling the AzureAI API using a function decorated with `azureai_call`, the
    response will be an `AzureAICallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.azureai import azureai_call


    @azureai_call("gpt-4o")
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")  # response is an `AzureAICallResponse` instance
    print(response.content)
    ```
    """

    response: SkipValidation[ChatCompletions]

    _provider = "azureai"

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
    def usage(self) -> CompletionsUsage | None:
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
    def message_param(self) -> SerializeAsAny[AssistantMessage]:
        """Returns the assistants's response as a message parameter."""
        message_param = self.response.choices[0].message
        return AssistantMessage(
            content=message_param.content, tool_calls=message_param.tool_calls
        )

    @computed_field
    @property
    def tools(self) -> list[AzureAITool] | None:
        """Returns any available tool calls as their `AzureAITool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
            ValueError: if the model refused to response, in which case the error
                message will be the refusal.
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
    def tool(self) -> AzureAITool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
            ValueError: if the model refused to response, in which case the error
                message will be the refusal.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def _get_tool_message(cls, tool: AzureAITool, output: str) -> ToolMessage:
        """Returns a tool message for the tool call."""
        tool_message = ToolMessage(
            content=output,
            tool_call_id=tool.tool_call.id,
        )
        tool_message.name = tool._name()  # pyright: ignore [reportCallIssue, reportAttributeAccessIssue]
        return tool_message

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[AzureAITool, str]]
    ) -> list[ToolMessage]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ChatCompletionToolMessageParam` parameters.
        """
        return [
            cls._get_tool_message(tool, output) for tool, output in tools_and_outputs
        ]

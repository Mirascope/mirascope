"""This module contains the `CohereCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from cohere.types import (
    ApiMetaBilledUnits,
    ChatMessage,
    NonStreamedChatResponse,
    Tool,
    ToolResult,
)
from pydantic import SkipValidation, computed_field

from ..base import BaseCallResponse
from ._utils import calculate_cost
from .call_params import CohereCallParams
from .dynamic_config import AsyncCohereDynamicConfig, CohereDynamicConfig
from .tool import CohereTool


class CohereCallResponse(
    BaseCallResponse[
        SkipValidation[NonStreamedChatResponse],
        CohereTool,
        SkipValidation[Tool],
        AsyncCohereDynamicConfig | CohereDynamicConfig,
        SkipValidation[ChatMessage],
        CohereCallParams,
        SkipValidation[ChatMessage],
    ]
):
    """A convenience wrapper around the Cohere `ChatCompletion` response.

    When calling the Cohere API using a function decorated with `cohere_call`, the
    response will be an `CohereCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.cohere import cohere_call


    @cohere_call("command-r-plus")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")  # response is an `CohereCallResponse` instance
    print(response.content)
    ```
    """

    _provider = "cohere"

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.response.text

    @property
    def finish_reasons(self) -> list[str] | None:
        """Returns the finish reasons of the response."""
        return [str(self.response.finish_reason)]

    @property
    def model(self) -> str:
        """Returns the name of the response model.

        Cohere does not return model, so we return the model provided by the user.
        """
        return self._model

    @property
    def id(self) -> str | None:
        """Returns the id of the response."""
        return self.response.generation_id

    @property
    def usage(self) -> ApiMetaBilledUnits | None:
        """Returns the usage of the response."""
        if self.response.meta:
            return self.response.meta.billed_units
        return None

    @property
    def input_tokens(self) -> float | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @property
    def output_tokens(self) -> float | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None

    @property
    def cost(self) -> float | None:
        """Returns the cost of the response."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> ChatMessage:
        """Returns the assistant's response as a message parameter."""
        return ChatMessage(
            message=self.response.text,
            tool_calls=self.response.tool_calls,
            role="assistant",  # pyright: ignore [reportCallIssue]
        )

    @computed_field
    @property
    def tools(self) -> list[CohereTool] | None:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.response.tool_calls:
            return None
        extracted_tools: list[CohereTool] = []
        for tool_call in self.response.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break
        return extracted_tools

    @computed_field
    @property
    def tool(self) -> CohereTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls,
        tools_and_outputs: list[tuple[CohereTool, str]],
    ) -> list[ToolResult]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ToolResult` parameters.
        """
        return [
            ToolResult(
                call=tool.tool_call,
                outputs=[{"output": output}],
            )
            for tool, output in tools_and_outputs
        ]

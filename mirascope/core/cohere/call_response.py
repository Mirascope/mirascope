"""This module contains the `CohereCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property

from cohere.types import (
    ApiMetaBilledUnits,
    ChatMessage,
    NonStreamedChatResponse,
    Tool,
    ToolResult,
)
from pydantic import SkipValidation, computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs
from ..base.types import CostMetadata, FinishReason
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import CohereMessageParamConverter
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
        CohereMessageParamConverter,
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

    _message_converter: type[CohereMessageParamConverter] = CohereMessageParamConverter

    _provider = "cohere"

    @computed_field
    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.response.text

    @computed_field
    @property
    def finish_reasons(self) -> list[str] | None:
        """Returns the finish reasons of the response."""
        return [str(self.response.finish_reason)]

    @computed_field
    @property
    def model(self) -> str:
        """Returns the name of the response model.

        Cohere does not return model, so we return the model provided by the user.
        """
        return self._model

    @computed_field
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

    @computed_field
    @property
    def input_tokens(self) -> float | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @computed_field
    @property
    def cached_tokens(self) -> float | None:
        """Returns the number of cached tokens."""
        return None

    @computed_field
    @property
    def output_tokens(self) -> float | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None

    @computed_field
    @cached_property
    def message_param(self) -> ChatMessage:
        """Returns the assistant's response as a message parameter."""
        return ChatMessage(
            message=self.response.text,
            tool_calls=self.response.tool_calls,
            role="assistant",  # pyright: ignore [reportCallIssue]
        )

    @cached_property
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

    @cached_property
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
    @transform_tool_outputs
    def tool_message_params(
        cls,
        tools_and_outputs: Sequence[tuple[CohereTool, str]],
    ) -> list[ToolResult]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ToolResult` parameters.
        """
        return [
            ToolResult(
                call=tool.tool_call,  # pyright: ignore [reportArgumentType]
                outputs=[{"output": output}],
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return CohereMessageParamConverter.from_provider([self.message_param])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return CohereMessageParamConverter.from_provider([self.user_message_param])[0]

    @computed_field
    @property
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation."""
        return super().cost_metadata

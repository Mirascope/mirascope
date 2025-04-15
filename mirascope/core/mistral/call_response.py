"""This module contains the `MistralCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property
from typing import Any, cast

from mistralai import ChatCompletionChoice
from mistralai.models import (
    AssistantMessage,
    ChatCompletionResponse,
    SystemMessage,
    ToolMessage,
    UsageInfo,
    UserMessage,
)
from pydantic import computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs
from ..base.types import CostMetadata, FinishReason
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import MistralMessageParamConverter
from .call_params import MistralCallParams
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralCallResponse(
    BaseCallResponse[
        ChatCompletionResponse,
        MistralTool,
        dict[str, Any],
        MistralDynamicConfig,
        AssistantMessage | SystemMessage | ToolMessage | UserMessage,
        MistralCallParams,
        UserMessage,
        MistralMessageParamConverter,
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

    _message_converter: type[MistralMessageParamConverter] = (
        MistralMessageParamConverter
    )

    _provider = "mistral"

    @property
    def _response_choices(self) -> list[ChatCompletionChoice]:
        return self.response.choices or []

    @computed_field
    @property
    def content(self) -> str:
        """The content of the chat completion for the 0th choice."""
        return cast(str, self._response_choices[0].message.content) or ""

    @computed_field
    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self._response_choices
        ]

    @computed_field
    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @computed_field
    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def usage(self) -> UsageInfo:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @computed_field
    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens

    @computed_field
    @property
    def cached_tokens(self) -> int:
        """Returns the number of cached tokens."""
        return 0

    @computed_field
    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens

    @computed_field
    @cached_property
    def message_param(self) -> AssistantMessage:
        """Returns the assistants's response as a message parameter."""
        return self._response_choices[0].message

    @cached_property
    def tools(self) -> list[MistralTool] | None:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tool_calls = self._response_choices[0].message.tool_calls
        if not self.tool_types or not tool_calls:
            return None

        extracted_tools = []
        for tool_call in tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @cached_property
    def tool(self) -> MistralTool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    @transform_tool_outputs
    def tool_message_params(
        cls, tools_and_outputs: Sequence[tuple[MistralTool, str]]
    ) -> list[ToolMessage]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ChatMessage` parameters.
        """
        return [
            ToolMessage(
                content=output,
                tool_call_id=tool.tool_call.id,  # pyright: ignore [reportOptionalMemberAccess]
                name=tool._name(),
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return MistralMessageParamConverter.from_provider([self.message_param])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return MistralMessageParamConverter.from_provider([self.user_message_param])[0]

    @computed_field
    @property
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation."""
        return super().cost_metadata

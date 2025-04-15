"""This module contains the `AnthropicCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property

from anthropic.types import (
    Message,
    MessageParam,
    ToolParam,
    ToolResultBlockParam,
    Usage,
)
from pydantic import SerializeAsAny, computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs, types
from ..base.types import CostMetadata
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import AnthropicMessageParamConverter
from .call_params import AnthropicCallParams
from .dynamic_config import AnthropicDynamicConfig, AsyncAnthropicDynamicConfig
from .tool import AnthropicTool


class AnthropicCallResponse(
    BaseCallResponse[
        Message,
        AnthropicTool,
        ToolParam,
        AsyncAnthropicDynamicConfig | AnthropicDynamicConfig,
        MessageParam,
        AnthropicCallParams,
        MessageParam,
        AnthropicMessageParamConverter,
    ]
):
    """A convenience wrapper around the Anthropic `Message` response.

    When calling the Anthropic API using a function decorated with `anthropic_call`, the
    response will be an `AnthropicCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.anthropic import anthropic_call


    @anthropic_call("claude-3-5-sonnet-20240620")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")  # response is an `AnthropicCallResponse` instance
    print(response.content)
    ```
    """

    _message_converter: type[AnthropicMessageParamConverter] = (
        AnthropicMessageParamConverter
    )

    _provider = "anthropic"

    @computed_field
    @property
    def content(self) -> str:
        """Returns the string text of the 0th text block."""
        block = self.response.content[0]
        return block.text if block.type == "text" else ""

    @computed_field
    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(self.response.stop_reason)]

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
    def usage(self) -> Usage:
        """Returns the usage of the message."""
        return self.response.usage

    @computed_field
    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.input_tokens

    @computed_field
    @property
    def cached_tokens(self) -> int:
        """Returns the number of cached tokens."""
        return getattr(self.usage, "cache_read_input_tokens", 0)

    @computed_field
    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.output_tokens

    @computed_field
    @cached_property
    def message_param(self) -> SerializeAsAny[MessageParam]:
        """Returns the assistants's response as a message parameter."""
        return MessageParam(**self.response.model_dump(include={"content", "role"}))

    @cached_property
    def tools(self) -> list[AnthropicTool] | None:
        """Returns any available tool calls as their `AnthropicTool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types:
            return None

        extracted_tools = []
        for content in self.response.content:
            if content.type != "tool_use":
                continue
            for tool_type in self.tool_types:
                if content.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(content))
                    break

        return extracted_tools

    @cached_property
    def tool(self) -> AnthropicTool | None:
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
        cls, tools_and_outputs: Sequence[tuple[AnthropicTool, str]]
    ) -> list[MessageParam]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `MessageParam` parameters.
        """
        return [
            {
                "role": "user",
                "content": [
                    ToolResultBlockParam(
                        tool_use_id=tool.tool_call.id,  # pyright: ignore [reportOptionalMemberAccess]
                        type="tool_result",
                        content=[{"text": output, "type": "text"}],
                    )
                    for tool, output in tools_and_outputs
                ],
            }
        ]

    @property
    def common_finish_reasons(self) -> list[types.FinishReason] | None:
        """Provider-agnostic finish reasons."""
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return AnthropicMessageParamConverter.from_provider([(self.message_param)])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return AnthropicMessageParamConverter.from_provider(
            [(self.user_message_param)]
        )[0]

    @computed_field
    @property
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation."""
        return super().cost_metadata

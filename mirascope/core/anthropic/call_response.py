"""This module contains the `AnthropicCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

import base64
from os import PathLike

from anthropic.types import (
    Message,
    MessageParam,
    ToolParam,
    ToolResultBlockParam,
    Usage,
)
from pydantic import SerializeAsAny, computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, ImagePart, TextPart, transform_tool_outputs, types
from ._utils import calculate_cost
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
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

    _provider = "anthropic"

    @property
    def content(self) -> str:
        """Returns the string text of the 0th text block."""
        block = self.response.content[0]
        return block.text if block.type == "text" else ""

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(self.response.stop_reason)]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def usage(self) -> Usage:
        """Returns the usage of the message."""
        return self.response.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.input_tokens

    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.output_tokens

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> SerializeAsAny[MessageParam]:
        """Returns the assistants's response as a message parameter."""
        return MessageParam(**self.response.model_dump(include={"content", "role"}))

    @computed_field
    @property
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

    @computed_field
    @property
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
        cls, tools_and_outputs: list[tuple[AnthropicTool, str]]
    ) -> list[MessageParam]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `MessageParam` parameters.
        """
        return [
            {
                "role": "user",
                "content": [
                    ToolResultBlockParam(
                        tool_use_id=tool.tool_call.id,
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
        role = self.message_param["role"]
        content = self.message_param["content"]

        if isinstance(content, str):
            return BaseMessageParam(role=role, content=content)

        converted_content = []

        for block in content:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")

            if block_type == "text":
                text = block.get("text")
                if not isinstance(text, str):
                    raise ValueError("TextBlockParam must have a string 'text' field.")
                converted_content.append(TextPart(type="text", text=text))

            elif block_type == "image":
                source = block.get("source")
                if not source or source.get("type") != "base64":
                    raise ValueError(
                        "ImageBlockParam must have a 'source' with type='base64'."
                    )
                image_data = source.get("data")
                media_type = source.get("media_type")
                if not image_data or not media_type:
                    raise ValueError(
                        "ImageBlockParam source must have 'data' and 'media_type'."
                    )
                if media_type not in [
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "image/webp",
                ]:
                    raise ValueError(
                        f"Unsupported image media type: {media_type}. "
                        "BaseMessageParam currently only supports JPEG, PNG, GIF, and WebP images."
                    )
                if isinstance(image_data, str):
                    decoded_image_data = base64.b64decode(image_data)
                elif isinstance(image_data, PathLike):
                    with open(image_data, "rb") as image_data:
                        decoded_image_data = image_data.read()
                else:
                    decoded_image_data = image_data.read()
                converted_content.append(
                    ImagePart(
                        type="image",
                        media_type=media_type,
                        image=decoded_image_data,
                        detail=None,
                    )
                )

            else:
                # Any other block type is not supported
                raise ValueError(
                    f"Unsupported block type '{block_type}'. "
                    "BaseMessageParam currently only supports text and image parts."
                )

        return BaseMessageParam(role=role, content=converted_content)

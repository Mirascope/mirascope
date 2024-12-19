"""This module contains the `BedrockCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from typing import cast

from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef as SyncConverseResponseTypeDef,
)
from pydantic import SerializeAsAny, SkipValidation, computed_field
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef as AsyncConverseResponseTypeDef,
)

from .. import BaseMessageParam
from ..base import (
    BaseCallResponse,
    DocumentPart,
    ImagePart,
    TextPart,
    transform_tool_outputs,
)
from ..base.types import FinishReason, Usage
from ._call_kwargs import BedrockCallKwargs
from ._types import (
    AssistantMessageTypeDef,
    AsyncMessageTypeDef,
    InternalBedrockMessageParam,
    SyncMessageTypeDef,
    TokenUsageTypeDef,
    ToolResultBlockContentTypeDef,
    ToolResultBlockMessageTypeDef,
    ToolTypeDef,
    ToolUseBlockContentTypeDef,
    UserMessageTypeDef,
)
from ._utils import calculate_cost
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from .call_params import BedrockCallParams
from .dynamic_config import AsyncBedrockDynamicConfig, BedrockDynamicConfig
from .tool import BedrockTool

IMAGE_FORMAT_MAP = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "GIF": "image/gif",
    "WEBP": "image/webp",
}


class BedrockCallResponse(
    BaseCallResponse[
        SyncConverseResponseTypeDef | AsyncConverseResponseTypeDef,
        BedrockTool,
        ToolTypeDef,
        AsyncBedrockDynamicConfig | BedrockDynamicConfig,
        InternalBedrockMessageParam,
        BedrockCallParams,
        UserMessageTypeDef,
    ]
):
    """A convenience wrapper around the Bedrock `ChatCompletion` response.

    When calling the Bedrock API using a function decorated with `bedrock_call`, the
    response will be an `BedrockCallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.bedrock import bedrock_call


    @bedrock_call("anthropic.claude-3-haiku-20240307-v1:0")
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")  # response is an `BedrockCallResponse` instance
    print(response.content)
    ```
    """

    response: SkipValidation[SyncConverseResponseTypeDef | AsyncConverseResponseTypeDef]

    _provider = "bedrock"

    @property
    def message(self) -> SyncMessageTypeDef | AsyncMessageTypeDef | None:
        """Returns the message of the response."""
        message = self.response.get("output", {}).get("message", {})
        if message:
            return cast(SyncMessageTypeDef | AsyncMessageTypeDef, message)
        return None

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        if not self.message:
            return ""
        if content := self.message.get("content", []):
            return content[0].get("text", "")
        return ""

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [self.response["stopReason"]]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return cast(BedrockCallKwargs, self.call_kwargs)["modelId"]

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response["ResponseMetadata"]["RequestId"]

    @property
    def usage(self) -> TokenUsageTypeDef:
        """Returns the usage of the chat completion."""
        return self.response["usage"]

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return self.usage["inputTokens"] if self.usage else None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage["outputTokens"] if self.usage else None

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> SerializeAsAny[AssistantMessageTypeDef]:
        """Returns the assistants's response as a message parameter."""
        message = self.message
        if not message:
            return AssistantMessageTypeDef(role="assistant", content=[])
        return AssistantMessageTypeDef(role="assistant", content=message["content"])

    @computed_field
    @property
    def tools(self) -> list[BedrockTool] | None:
        """Returns any available tool calls as their `BedrockTool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
            ValueError: if the model refused to response, in which case the error
                message will be the refusal.
        """
        if not self.message:
            return None
        content = self.message.get("content", [])
        tool_uses = [t for c in content if (t := c.get("toolUse"))]
        if not self.tool_types or not tool_uses:
            return None

        extracted_tools = []
        for tool_use in tool_uses:
            for tool_type in self.tool_types:
                if tool_use["name"] == tool_type._name():
                    extracted_tools.append(
                        tool_type.from_tool_call(
                            cast(ToolUseBlockContentTypeDef, {"toolUse": tool_use})
                        )
                    )
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> BedrockTool | None:
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
    @transform_tool_outputs
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[BedrockTool, str]]
    ) -> list[ToolResultBlockMessageTypeDef]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `ChatCompletionToolMessageParam` parameters.
        """
        return [
            ToolResultBlockMessageTypeDef(
                role="user",
                content=[
                    cast(
                        ToolResultBlockContentTypeDef,
                        {
                            "toolResult": {
                                "content": [{"text": output}],
                                "toolUseId": tool.tool_call["toolUse"]["toolUseId"],
                                "name": tool._name(),
                            }
                        },
                    )
                ],
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        message_param = self.message_param
        role = message_param["role"]
        content_blocks = message_param["content"]

        converted_content = []

        for block in content_blocks:
            if "text" in block:
                text = block["text"]
                if not isinstance(text, str):
                    raise ValueError("Text content must be a string.")
                converted_content.append(TextPart(type="text", text=text))

            elif "image" in block:
                image_block = block["image"]
                img_format = image_block["format"]  # e.g. "JPEG"
                source = image_block["source"]
                if "bytes" not in source or not isinstance(source["bytes"], bytes):
                    raise ValueError("Image block must have 'source.bytes' as bytes.")
                media_type = IMAGE_FORMAT_MAP.get(img_format.upper())
                if not media_type:
                    raise ValueError(f"Unsupported image format: {img_format}")
                converted_content.append(
                    ImagePart(
                        type="image",
                        media_type=media_type,
                        image=source["bytes"],
                        detail=None,
                    )
                )

            elif "document" in block:
                doc_block = block["document"]
                doc_format = doc_block["format"]  # e.g. "PDF"
                if doc_format.upper() != "PDF":
                    raise ValueError(
                        f"Unsupported document format: {doc_format}. Only PDF is supported."
                    )
                source = doc_block["source"]
                if "bytes" not in source or not isinstance(source["bytes"], bytes):
                    raise ValueError(
                        "Document block must have 'source.bytes' as bytes."
                    )
                converted_content.append(
                    DocumentPart(
                        type="document",
                        media_type="application/pdf",
                        document=source["bytes"],
                    )
                )

            else:
                raise ValueError("Content block does not contain supported content.")

        return BaseMessageParam(role=str(role), content=converted_content)

    @property
    def common_usage(self) -> Usage | None:
        if self.input_tokens is None and self.output_tokens is None:
            return None
        input_tokens = self.input_tokens or 0
        output_tokens = self.output_tokens or 0
        return Usage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

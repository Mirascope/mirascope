"""This module contains the OpenAIMessageParamConverter class."""

import json
from collections.abc import Iterable
from typing import cast

from openai.types.chat import ChatCompletionMessageParam

from mirascope.core import BaseMessageParam
from mirascope.core.base import (
    AudioPart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.openai._utils import convert_message_params


class OpenAIMessageParamConverter(BaseMessageParamConverter):
    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam],
    ) -> list[ChatCompletionMessageParam]:
        """Converts base message params to OpenAI message params."""
        return convert_message_params(
            cast(list[BaseMessageParam | ChatCompletionMessageParam], message_params)
        )

    @staticmethod
    def from_provider(
        message_params: list[ChatCompletionMessageParam],
    ) -> list[BaseMessageParam]:
        """Converts OpenAI message params to base message params."""
        converted = []
        for message_param in message_params:
            contents = []
            content = message_param.get("content")
            if (
                message_param["role"] == "tool"
                and "name" in message_param
                and "content" in message_param
            ):
                converted.append(
                    BaseMessageParam(
                        role="tool",
                        content=[
                            ToolResultPart(
                                type="tool_result",
                                name=message_param["name"],
                                content=message_param["content"],
                                id=message_param["tool_call_id"],
                                is_error=False,
                            )
                        ],
                    )
                )
                continue
            elif isinstance(content, str):
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=content)
                )
                continue
            elif isinstance(content, Iterable):
                for part in content:
                    if part["type"] == "text":
                        contents.append(TextPart(type="text", text=part["text"]))
                    elif part["type"] == "image_url":
                        image_url = part["image_url"]
                        contents.append(
                            ImageURLPart(
                                type="image_url",
                                url=image_url["url"],
                                detail=image_url.get("detail", None),
                            )
                        )
                    elif part["type"] == "input_audio":
                        input_audio = part["input_audio"]
                        contents.append(
                            AudioPart(
                                type="audio",
                                media_type=f"audio/{input_audio['format']}",
                                audio=input_audio["data"],
                            )
                        )
                    else:
                        raise ValueError(part["refusal"])  # pyright: ignore [reportGeneralTypeIssues]
            if tool_calls := message_param.get("tool_calls"):
                for tool_call in tool_calls:
                    contents.append(
                        ToolCallPart(
                            type="tool_call",
                            name=tool_call["function"]["name"],
                            id=tool_call["id"],
                            args=json.loads(tool_call["function"]["arguments"]),
                        )
                    )
            if contents:
                converted.append(
                    BaseMessageParam(role=message_param["role"], content=contents)
                )
        return converted

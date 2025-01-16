import base64
import json
import re
from typing import cast

from mistralai.models import (
    AssistantMessage,
    ImageURLChunk,
    ReferenceChunk,
    SystemMessage,
    TextChunk,
    ToolMessage,
    UserMessage,
)

from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.mistral._utils import convert_message_params

from ...base import BaseMessageParam, ImagePart, TextPart, ToolResultPart
from ...base.message_param import ToolCallPart


class MistralMessageParamConverter(BaseMessageParamConverter):
    """Converts between Mistral `AssistantMessage` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list:
        """
        Convert from Mirascope `BaseMessageParam` to Mistral messages (AssistantMessage, etc.).
        Mistral’s code snippet references convert_message_params returning a list of
        [AssistantMessage|SystemMessage|ToolMessage|UserMessage].
        """
        return convert_message_params(
            cast(
                list[
                    BaseMessageParam
                    | AssistantMessage
                    | SystemMessage
                    | ToolMessage
                    | UserMessage
                ],
                message_params,
            )
        )

    @staticmethod
    def from_provider(
        message_params: list[
            AssistantMessage | ToolMessage | SystemMessage | UserMessage
        ],
    ) -> list[BaseMessageParam]:
        """
        Convert from Mistral's `AssistantMessage` to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            content = message_param.content

            converted_parts = []

            if tool_calls := getattr(message_param, "tool_calls", None):
                for tool in tool_calls:
                    arguments = tool.function.arguments
                    converted.append(
                        BaseMessageParam(
                            role="tool",
                            content=[
                                ToolCallPart(
                                    type="tool_call",
                                    name=tool.function.name,
                                    id=tool.id,
                                    args=json.loads(arguments)
                                    if isinstance(arguments, str)
                                    else arguments,
                                )
                            ],
                        )
                    )
            elif isinstance(message_param, ToolMessage):
                converted.append(
                    BaseMessageParam(
                        role="tool",
                        content=[
                            ToolResultPart(
                                type="tool_result",
                                name=message_param.name,  # pyright: ignore [reportArgumentType]
                                content=message_param.content,  # pyright: ignore [reportArgumentType]
                                id=message_param.tool_call_id,  # pyright: ignore [reportArgumentType]
                            )
                        ],
                    )
                )
            elif isinstance(content, str):
                converted_parts.append(TextPart(type="text", text=content))
            elif isinstance(content, list):
                for chunk in content:
                    if isinstance(chunk, TextChunk):
                        converted_parts.append(TextPart(type="text", text=chunk.text))

                    elif isinstance(chunk, ImageURLChunk):
                        image_url = chunk.image_url
                        if isinstance(image_url, str):
                            # Extract data from the data URL
                            match = re.match(r"data:(image/\w+);base64,(.+)", image_url)
                            if not match:
                                raise ValueError(
                                    "ImageURLChunk image_url is not in a supported data URL format."
                                )
                            mime_type = match.group(1)
                            image_base64 = match.group(2)
                            image_data = base64.b64decode(image_base64)
                            converted_parts.append(
                                ImagePart(
                                    type="image",
                                    media_type=mime_type,
                                    image=image_data,
                                    detail=None,
                                )
                            )
                        else:
                            img_url_str = image_url.url  # type: ignore
                            match = re.match(
                                r"data:(image/\w+);base64,(.+)", img_url_str
                            )
                            if not match:
                                raise ValueError(
                                    "ImageURLChunk image_url is not in a supported data URL format."
                                )
                            mime_type = match.group(1)
                            image_base64 = match.group(2)
                            image_data = base64.b64decode(image_base64)
                            converted_parts.append(
                                ImagePart(
                                    type="image",
                                    media_type=mime_type,
                                    image=image_data,
                                    detail=None,
                                )
                            )

                    elif isinstance(chunk, ReferenceChunk):
                        raise ValueError(
                            "ReferenceChunk is not supported for conversion to BaseMessageParam."
                        )

                    else:
                        # Unknown chunk type
                        raise ValueError(
                            f"Unsupported ContentChunk type: {type(chunk).__name__}"
                        )

            if len(converted_parts) == 1 and isinstance(converted_parts[0], TextPart):
                converted.append(
                    BaseMessageParam(
                        role=message_param.role,  # pyright: ignore [reportArgumentType]
                        content=converted_parts[0].text,
                    )
                )
            else:
                if converted_parts:
                    converted.append(
                        BaseMessageParam(
                            role=message_param.role,  # pyright: ignore [reportArgumentType]
                            content=converted_parts,
                        )
                    )

        return converted

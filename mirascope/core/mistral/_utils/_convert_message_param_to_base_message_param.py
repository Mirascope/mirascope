import base64
import json
import re

from mistralai.models import (
    AssistantMessage,
    ImageURLChunk,
    ReferenceChunk,
    TextChunk,
)

from ...base import BaseMessageParam, ImagePart, TextPart
from ...base.message_param import ToolCallPart


def convert_message_param_to_base_message_param(
    message_param: AssistantMessage,
) -> BaseMessageParam:
    """
    Convert AssistantMessageContent (str or List[ContentChunk]) into BaseMessageParam.
    """

    content = message_param.content
    role: str = "assistant"
    converted_parts = []

    if isinstance(content, str):
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
                    match = re.match(r"data:(image/\w+);base64,(.+)", img_url_str)
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

    if tool_calls := message_param.tool_calls:
        for tool in tool_calls:
            arguments = tool.function.arguments
            converted_parts.append(
                ToolCallPart(
                    type="tool_call",
                    name=tool.function.name,
                    id=tool.id,
                    args=json.loads(arguments)
                    if isinstance(arguments, str)
                    else arguments,
                )
            )

    if len(converted_parts) == 1 and isinstance(converted_parts[0], TextPart):
        return BaseMessageParam(role=role, content=converted_parts[0].text)

    return BaseMessageParam(role=role, content=converted_parts)

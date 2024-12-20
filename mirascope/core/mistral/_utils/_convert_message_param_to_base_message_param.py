import base64
import re

from mistralai.models import (
    AssistantMessage,
    ImageURLChunk,
    ReferenceChunk,
    TextChunk,
)

from ...base import BaseMessageParam, ImagePart, TextPart


def convert_message_param_to_base_message_param(
    message_param: AssistantMessage,
) -> BaseMessageParam:
    """
    Convert AssistantMessageContent (str or List[ContentChunk]) into BaseMessageParam.
    """
    content = message_param.content
    if not content:
        return BaseMessageParam(role="assistant", content="")
    role: str = "assistant"
    if isinstance(content, str):
        return BaseMessageParam(role=role, content=content)

    converted_parts = []

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
            raise ValueError(f"Unsupported ContentChunk type: {type(chunk).__name__}")

    if len(converted_parts) == 1 and isinstance(converted_parts[0], TextPart):
        # Could simplify to just text
        return BaseMessageParam(role=role, content=converted_parts[0].text)
    else:
        return BaseMessageParam(role=role, content=converted_parts)

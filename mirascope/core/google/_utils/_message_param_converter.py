from typing import cast

from google.genai import Client
from google.genai.types import (
    Content,
    ContentDict,
    ContentOrDict,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base import DocumentPart, ImagePart, TextPart
from mirascope.core.base._utils._base_message_param_converter import (
    BaseMessageParamConverter,
)
from mirascope.core.base.message_param import (
    AudioPart,
    AudioURLPart,
    ImageURLPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.google._utils import convert_message_params

from ._validate_media_type import _check_audio_media_type, _check_image_media_type


class GoogleMessageParamConverter(BaseMessageParamConverter):
    """Converts between Google `ContentDict` and Mirascope `BaseMessageParam`."""

    @staticmethod
    def to_provider(
        message_params: list[BaseMessageParam], client: Client | None = None
    ) -> list[ContentDict]:
        """
        Convert from Mirascope `BaseMessageParam` to Google `ContentDict`.
        """
        return convert_message_params(
            cast(list[BaseMessageParam | ContentDict], message_params),
            client or Client(),
        )

    @staticmethod
    def from_provider(message_params: list[ContentOrDict]) -> list[BaseMessageParam]:
        """
        Convert from Google's `ContentDict` to Mirascope `BaseMessageParam`.
        """
        converted: list[BaseMessageParam] = []
        for message_param in message_params:
            if isinstance(message_param, dict):
                message_param = Content.model_validate(message_param)
            role = message_param.role
            if not role or role == "model":
                role = "assistant"
            content_list = []
            for part in message_param.parts or []:
                if part.text:
                    content_list.append(TextPart(type="text", text=part.text))

                elif blob := part.inline_data:
                    mime_type = blob.mime_type or ""
                    data = blob.data or b""
                    if mime_type.startswith("image/"):
                        _check_image_media_type(mime_type)
                        content_list.append(
                            ImagePart(
                                type="image",
                                media_type=mime_type,
                                image=data,
                                detail=None,
                            )
                        )
                    elif mime_type.startswith("audio/"):
                        _check_audio_media_type(mime_type)
                        content_list.append(
                            AudioPart(
                                type="audio",
                                media_type=mime_type,
                                audio=data,
                            )
                        )
                    elif mime_type == "application/pdf":
                        content_list.append(
                            DocumentPart(
                                type="document", media_type=mime_type, document=data
                            )
                        )
                    else:
                        raise ValueError(
                            f"Unsupported inline_data mime type: {mime_type}. Cannot convert to BaseMessageParam."
                        )

                elif file_data := part.file_data:
                    mime_type = file_data.mime_type or ""
                    if mime_type.startswith("image/"):
                        content_list.append(
                            ImageURLPart(
                                type="image_url",
                                url=cast(str, part.file_data.file_uri),
                                detail=None,
                            )
                        )
                    elif mime_type.startswith("audio/"):
                        content_list.append(
                            AudioURLPart(
                                type="audio_url",
                                url=cast(str, part.file_data.file_uri),
                            )
                        )
                    else:
                        # Since `FileDataDict` handles any file data, we use
                        # `ImageURLPart` for unknown mime types
                        content_list.append(
                            ImageURLPart(
                                type="image_url",
                                url=cast(str, part.file_data.file_uri),
                                detail=None,
                            )
                        )
                elif part.function_call:
                    converted.append(
                        BaseMessageParam(
                            role=role,
                            content=[
                                ToolCallPart(
                                    type="tool_call",
                                    name=part.function_call.name,  # pyright: ignore [reportArgumentType]
                                    args=part.function_call.args,
                                )
                            ],
                        )
                    )
                elif part.function_response:
                    converted.append(
                        BaseMessageParam(
                            role=role,
                            content=[
                                ToolResultPart(
                                    type="tool_result",
                                    name=part.function_response.name,  # pyright: ignore [reportArgumentType]
                                    content=part.function_response.response[  # pyright: ignore [reportArgumentType, reportOptionalSubscript]
                                        "content"
                                    ],
                                    id=None,
                                    is_error=False,
                                )
                            ],
                        )
                    )
                else:
                    raise ValueError(
                        "Part does not contain any supported content (text, image, or document)."
                    )

            if len(content_list) == 1 and isinstance(content_list[0], TextPart):
                converted.append(
                    BaseMessageParam(role=role, content=content_list[0].text)
                )
            else:
                if content_list:
                    converted.append(BaseMessageParam(role=role, content=content_list))

        return converted

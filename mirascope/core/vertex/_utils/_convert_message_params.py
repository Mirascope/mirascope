"""Utility for converting `BaseMessageParam` to `Content`"""

from vertexai.generative_models import Content, Image, Part

from ...base import BaseMessageParam


def convert_message_params(
    message_params: list[BaseMessageParam | Content],
) -> list[Content]:
    converted_message_params = []
    for message_param in message_params:
        if isinstance(message_param, Content):
            converted_message_params.append(message_param)
        elif (role := message_param.role) == "system":
            content = message_param.content
            if not isinstance(content, str):
                raise ValueError(
                    "System message content must be a single text string."
                )  # pragma: no cover
            converted_message_params += [
                Content(
                    role="user",
                    parts=[
                        Part.from_text(content) if isinstance(content, str) else content
                    ],
                ),
                Content(
                    role="model",
                    parts=[Part.from_text("Ok! I will adhere to this system message.")],
                ),
            ]
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(
                Content(role="user", parts=[Part.from_text(content)])
            )
        else:
            converted_content: list[Part] = []
            for part in content:
                if part.type == "text":
                    converted_content.append(Part.from_text(part.text))
                elif part.type == "image":
                    if part.media_type not in [
                        "image/jpeg",
                        "image/png",
                        "image/webp",
                        "image/heic",
                        "image/heif",
                    ]:
                        raise ValueError(
                            f"Unsupported image media type: {part.media_type}. "
                            "Vertex currently only supports JPEG, PNG, WebP, HEIC, "
                            "and HEIF images."
                        )
                    image = Image.from_bytes(part.image)
                    converted_content.append(Part.from_image(image))
                elif part.type == "audio":
                    if part.media_type not in [
                        "audio/wav",
                        "audio/mp3",
                        "audio/aiff",
                        "audio/aac",
                        "audio/ogg",
                        "audio/flac",
                    ]:
                        raise ValueError(
                            f"Unsupported audio media type: {part.media_type}. "
                            "Vertex currently only supports WAV, MP3, AIFF, AAC, OGG, "
                            "and FLAC audio file types."
                        )
                    converted_content.append(
                        Part.from_data(mime_type=part.media_type, data=part.audio)
                    )
                else:
                    raise ValueError(
                        "Vertex currently only supports text, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(Content(role=role, parts=converted_content))
    return converted_message_params

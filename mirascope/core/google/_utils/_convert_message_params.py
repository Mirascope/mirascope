"""Utility for converting `BaseMessageParam` to `ContentsType`"""

import base64
import io

import PIL.Image
from google.genai import Client
from google.genai.types import BlobDict, ContentDict, FileDataDict, PartDict

from ...base import BaseMessageParam
from ...base._utils import get_audio_type
from ...base._utils._parse_content_template import _load_media


def convert_message_params(
    message_params: list[BaseMessageParam | ContentDict], client: Client
) -> list[ContentDict]:
    converted_message_params = []
    for message_param in message_params:
        if not isinstance(message_param, BaseMessageParam):
            converted_message_params.append(message_param)
        elif (role := message_param.role) == "system":
            if not isinstance(message_param.content, str):
                raise ValueError(
                    "System message content must be a single text string."
                )  # pragma: no cover
            converted_message_params += [
                {
                    "role": "system",
                    "parts": [PartDict(text=message_param.content)],
                }
            ]
        elif isinstance((content := message_param.content), str):
            converted_message_params.append(
                {
                    "role": role if role == "user" else "model",
                    "parts": [PartDict(text=content)],
                }
            )
        else:
            converted_content = []
            for part in content:
                if part.type == "text":
                    converted_content.append(PartDict(text=part.text))
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
                            "Google currently only supports JPEG, PNG, WebP, HEIC, "
                            "and HEIF images."
                        )
                    converted_content.append(
                        PartDict(
                            inline_data=BlobDict(
                                data=part.image, mime_type=part.media_type
                            )
                        )
                    )
                elif part.type == "image_url":
                    if (
                        part.url.startswith(("https://", "http://"))
                        and "generativelanguage.googleapis.com" not in part.url
                    ):
                        downloaded_image = io.BytesIO(_load_media(part.url))
                        image = PIL.Image.open(downloaded_image)
                        media_type = (
                            PIL.Image.MIME[image.format]
                            if image.format
                            else "image/unknown"
                        )
                        if media_type not in [
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                            "image/heic",
                            "image/heif",
                        ]:
                            raise ValueError(
                                f"Unsupported image media type: {media_type}. "
                                "Google currently only supports JPEG, PNG, WebP, HEIC, "
                                "and HEIF images."
                            )
                        if client.vertexai:
                            uri = part.url
                        else:
                            downloaded_image.seek(0)
                            file_ref = client.files.upload(
                                file=downloaded_image, config={"mime_type": media_type}
                            )
                            uri = file_ref.uri
                            media_type = file_ref.mime_type
                    else:
                        uri = part.url
                        media_type = None

                    converted_content.append(
                        PartDict(
                            file_data=FileDataDict(file_uri=uri, mime_type=media_type)
                        )
                    )
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
                            "Google currently only supports WAV, MP3, AIFF, AAC, OGG, "
                            "and FLAC audio file types."
                        )
                    converted_content.append(
                        PartDict(
                            inline_data=BlobDict(
                                data=part.audio
                                if isinstance(part.audio, bytes)
                                else base64.b64decode(part.audio),
                                mime_type=part.media_type,
                            )
                        )
                    )
                elif part.type == "audio_url":
                    if (
                        part.url.startswith(("https://", "http://"))
                        and "generativelanguage.googleapis.com" not in part.url
                    ):
                        downloaded_audio = _load_media(part.url)
                        audio_type = get_audio_type(downloaded_audio)
                        if audio_type not in [
                            "audio/wav",
                            "audio/mp3",
                            "audio/aiff",
                            "audio/aac",
                            "audio/ogg",
                            "audio/flac",
                        ]:
                            raise ValueError(
                                f"Unsupported audio media type: {audio_type}. "
                                "Google currently only supports WAV, MP3, AIFF, AAC, OGG, "
                                "and FLAC audio file types."
                            )
                        if client.vertexai:
                            uri = part.url
                        else:
                            downloaded_audio = io.BytesIO(downloaded_audio)
                            downloaded_audio.seek(0)
                            file_ref = client.files.upload(
                                file=downloaded_audio, config={"mime_type": audio_type}
                            )
                            uri = file_ref.uri
                            media_type = file_ref.mime_type
                    else:
                        uri = part.url
                        audio_type = None

                    converted_content.append(
                        PartDict(
                            file_data=FileDataDict(file_uri=uri, mime_type=audio_type)
                        )
                    )
                else:
                    raise ValueError(
                        "Google currently only supports text, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )
            converted_message_params.append(
                {
                    "role": role if role == "user" else "model",
                    "parts": converted_content,
                }
            )
    return converted_message_params

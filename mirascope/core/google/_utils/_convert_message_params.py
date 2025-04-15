"""Utility for converting `BaseMessageParam` to `ContentsType`"""

import asyncio
import base64
import io
from concurrent.futures import ThreadPoolExecutor

from google.genai import Client
from google.genai.types import (
    BlobDict,
    ContentDict,
    FileDataDict,
    FunctionCallDict,
    FunctionResponseDict,
    PartDict,
)

from ...base import BaseMessageParam
from ...base._utils import get_audio_type, get_image_type
from ...base._utils._parse_content_template import _load_media
from ._validate_media_type import _check_audio_media_type, _check_image_media_type


def _over_file_size_limit(size: int) -> bool:
    """Check if the total file size exceeds the limit (10mb).

    Google limit is 20MB but base64 adds 33% to the size.
    """
    return size > 10 * 1024 * 1024  # 10MB


async def _convert_message_params_async(
    message_params: list[BaseMessageParam | ContentDict], client: Client
) -> list[ContentDict]:
    converted_message_params = []
    total_payload_size = 0
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
            must_upload: dict[int, BlobDict] = {}
            for index, part in enumerate(content):
                if part.type == "text":
                    converted_content.append(PartDict(text=part.text))
                elif part.type == "tool_call":
                    converted_content.append(
                        PartDict(
                            function_call=FunctionCallDict(
                                name=part.name, args=part.args, id=part.id
                            )
                        )
                    )
                elif part.type == "tool_result":
                    converted_content.append(
                        PartDict(
                            function_response=FunctionResponseDict(
                                name=part.name,
                                response={"content": part.content},
                                id=part.id,
                            )
                        )
                    )
                elif part.type == "image":
                    _check_image_media_type(part.media_type)
                    blob_dict = BlobDict(data=part.image, mime_type=part.media_type)
                    converted_content.append(PartDict(inline_data=blob_dict))
                    image_size = len(part.image)
                    total_payload_size += image_size
                    if _over_file_size_limit(total_payload_size):
                        must_upload[index] = blob_dict
                        total_payload_size -= image_size
                elif part.type == "image_url":
                    if (
                        client.vertexai
                        or not part.url.startswith(("https://", "http://"))
                        or "generativelanguage.googleapis.com" in part.url
                    ):
                        converted_content.append(
                            PartDict(
                                file_data=FileDataDict(
                                    file_uri=part.url, mime_type=None
                                )
                            )
                        )
                    else:
                        downloaded_image = _load_media(part.url)
                        media_type = f"image/{get_image_type(downloaded_image)}"
                        _check_image_media_type(media_type)
                        blob_dict = BlobDict(
                            data=downloaded_image, mime_type=media_type
                        )
                        converted_content.append(PartDict(inline_data=blob_dict))
                        image_size = len(downloaded_image)
                        total_payload_size += image_size
                        if _over_file_size_limit(total_payload_size):
                            must_upload[index] = blob_dict
                            total_payload_size -= image_size
                elif part.type == "audio":
                    _check_audio_media_type(part.media_type)
                    audio_data = (
                        part.audio
                        if isinstance(part.audio, bytes)
                        else base64.b64decode(part.audio)
                    )
                    blob_dict = BlobDict(data=audio_data, mime_type=part.media_type)
                    converted_content.append(PartDict(inline_data=blob_dict))
                    audio_size = len(audio_data)
                    total_payload_size += audio_size
                    if _over_file_size_limit(total_payload_size):
                        must_upload[index] = blob_dict
                        total_payload_size -= audio_size
                elif part.type == "audio_url":
                    if (
                        client.vertexai
                        or not part.url.startswith(("https://", "http://"))
                        or "generativelanguage.googleapis.com" in part.url
                    ):
                        converted_content.append(
                            PartDict(
                                file_data=FileDataDict(
                                    file_uri=part.url, mime_type=None
                                )
                            )
                        )
                    else:
                        downloaded_audio = _load_media(part.url)
                        media_type = f"audio/{get_audio_type(downloaded_audio)}"
                        _check_audio_media_type(media_type)
                        blob_dict = BlobDict(
                            data=downloaded_audio, mime_type=media_type
                        )
                        converted_content.append(PartDict(inline_data=blob_dict))
                        audio_size = len(downloaded_audio)
                        total_payload_size += audio_size
                        if _over_file_size_limit(total_payload_size):
                            must_upload[index] = blob_dict
                            total_payload_size -= audio_size
                else:
                    raise ValueError(
                        "Google currently only supports text, tool_call, tool_result, image, and audio parts. "
                        f"Part provided: {part.type}"
                    )

            if must_upload:
                indices, blob_dicts = zip(*must_upload.items(), strict=True)
                upload_tasks = [
                    client.aio.files.upload(
                        file=io.BytesIO(blob_dict["data"]),
                        config={"mime_type": blob_dict.get("mime_type", None)},
                    )
                    for blob_dict in blob_dicts
                ]
                file_refs = await asyncio.gather(*upload_tasks)
                for index, file_ref in zip(indices, file_refs, strict=True):
                    converted_content[index] = PartDict(
                        file_data=FileDataDict(
                            file_uri=file_ref.uri, mime_type=file_ref.mime_type
                        )
                    )

            converted_message_params.append(
                {
                    "role": role if role == "user" else "model",
                    "parts": converted_content,
                }
            )
    return converted_message_params


def convert_message_params(
    message_params: list[BaseMessageParam | ContentDict], client: Client
) -> list[ContentDict]:
    """Convert message params to Google's ContentDict format.

    If called from sync context, uses asyncio.run().
    If called from async context, uses the current event loop.
    """
    try:
        asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                asyncio.run, _convert_message_params_async(message_params, client)
            )
            return future.result()
    except RuntimeError:
        ...
    return asyncio.run(_convert_message_params_async(message_params, client))

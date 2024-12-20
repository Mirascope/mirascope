"""Tests the `openai._utils.convert_message_params` function."""

import pytest
from openai.types.chat import ChatCompletionMessageParam

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
)
from mirascope.core.openai._utils._convert_message_params import convert_message_params


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | ChatCompletionMessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail="auto"
                ),
                AudioPart(type="audio", media_type="audio/wav", audio=b"audio"),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "user", "content": "Hello"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,aW1hZ2U=",
                        "detail": "auto",
                    },
                },
                {
                    "input_audio": {
                        "data": "YXVkaW8=",
                        "format": "wav",
                    },
                    "type": "input_audio",
                },
            ],
        },
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. OpenAI currently only supports "
        "JPEG, PNG, GIF, and WebP images.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        ImagePart(
                            type="image",
                            media_type="image/svg",
                            image=b"image",
                            detail="auto",
                        )
                    ],
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/aac. OpenAI currently only supports WAV and MP3 audio file types.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(type="audio", media_type="audio/aac", audio=b"audio")
                    ],
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="OpenAI currently only supports text, image and audio parts. Part provided: cache_control",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        CacheControlPart(type="cache_control", cache_type="ephemeral")
                    ],
                )
            ]
        )

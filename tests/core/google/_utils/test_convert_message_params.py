"""Tests the `google._utils.convert_message_params` function."""

from unittest.mock import MagicMock, patch

import pytest
from google.genai.types import ContentDict

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
)
from mirascope.core.google._utils._convert_message_params import convert_message_params


@patch("PIL.Image.open", new_callable=MagicMock)
def test_convert_message_params(mock_image_open: MagicMock) -> None:
    """Tests the `convert_message_params` function."""
    mock_image_open.return_value = "test"
    message_params: list[BaseMessageParam | ContentDict] = [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Hello"),
        {"role": "user", "parts": ["Hello", {"type": "text", "text": "Hello"}]},  # pyright: ignore[reportAssignmentType]
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="test"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail=None
                ),
                AudioPart(type="audio", media_type="audio/wav", audio=b"audio"),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"parts": ["You are a helpful assistant."], "role": "user"},
        {"parts": ["Ok! I will adhere to this system message."], "role": "model"},
        {"parts": [{"text": "Hello"}], "role": "user"},
        {"parts": ["Hello", {"text": "Hello", "type": "text"}], "role": "user"},
        {
            "parts": [
                {"text": "test"},
                {"data": b"image", "mime_type": "image/jpeg"},
                {"data": b"audio", "mime_type": "audio/wav"},
            ],
            "role": "user",
        },
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Google currently only supports "
        "JPEG, PNG, WebP, HEIC, and HEIF images.",
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
                            detail=None,
                        )
                    ],
                ),
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. "
        "Google currently only supports WAV, MP3, AIFF, AAC, OGG, "
        "and FLAC audio file types.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(
                            type="audio", media_type="audio/unknown", audio=b"audio"
                        )
                    ],
                ),
            ]
        )

    with pytest.raises(
        ValueError,
        match="Google currently only supports text, image, and audio parts. Part provided: cache_control",
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

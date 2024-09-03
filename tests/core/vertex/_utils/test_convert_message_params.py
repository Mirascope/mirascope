"""Tests the `vertex._utils.convert_message_params` function."""

import io
from unittest.mock import MagicMock, patch

import pytest
from vertexai.generative_models import Content

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
)
from mirascope.core.vertex._utils._convert_message_params import convert_message_params


@patch("PIL.Image.open", new_callable=MagicMock)
def test_convert_message_params(mock_image_open: MagicMock) -> None:
    """Tests the `convert_message_params` function."""
    mock_image_open.return_value = "test"
    message_params: list[BaseMessageParam | Content] = [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Hello"),
        {"role": "user", "parts": ["Hello", {"type": "text", "text": "Hello"}]},
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
        {"role": "user", "parts": ["You are a helpful assistant."]},
        {"role": "model", "parts": ["Ok! I will adhere to this system message."]},
        {"role": "user", "parts": ["Hello"]},
        {"role": "user", "parts": ["Hello", {"type": "text", "text": "Hello"}]},
        {
            "role": "user",
            "parts": ["test", "test", {"mime_type": "audio/wav", "data": b"audio"}],
        },
    ]
    mock_image_open.assert_called_once()
    bytes_io: io.BytesIO = mock_image_open.call_args.args[0]
    assert bytes_io.getvalue() == b"image"

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Vertex currently only supports "
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
        "Vertex currently only supports WAV, MP3, AIFF, AAC, OGG, "
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
        match="Vertex currently only supports text, image, and audio parts. Part provided: cache_control",
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

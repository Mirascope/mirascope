"""Tests the `gemini._utils.convert_message_params` function."""

import io
from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base import BaseMessageParam
from mirascope.core.gemini._utils.convert_message_params import convert_message_params


@patch("PIL.Image.open", new_callable=MagicMock)
def test_convert_message_params(mock_image_open: MagicMock) -> None:
    """Tests the `convert_message_params` function."""
    mock_image_open.return_value = "test"
    message_params: list[BaseMessageParam] = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "media_type": "image/jpeg",
                    "image": b"image",
                    "detail": None,
                },
                {
                    "type": "audio",
                    "media_type": "audio/wav",
                    "audio": b"audio",
                },
            ],
        },
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"role": "user", "parts": ["You are a helpful assistant."]},
        {"role": "model", "parts": ["Ok! I will adhere to this system message."]},
        {"role": "user", "parts": ["Hello"]},
        {
            "role": "user",
            "parts": ["test", {"mime_type": "audio/wav", "data": b"audio"}],
        },
    ]
    mock_image_open.assert_called_once()
    bytes_io: io.BytesIO = mock_image_open.call_args.args[0]
    assert bytes_io.getvalue() == b"image"

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Gemini currently only supports "
        "JPEG, PNG, WebP, HEIC, and HEIF images.",
    ):
        convert_message_params(
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "media_type": "image/svg",
                            "image": b"image",
                            "detail": "auto",
                        }
                    ],
                }
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/unknown. "
        "Gemini currently only supports WAV, MP3, AIFF, AAC, OGG, "
        "and FLAC audio file types.",
    ):
        convert_message_params(
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "audio",
                            "media_type": "audio/unknown",
                            "audio": b"audio",
                        }
                    ],
                }
            ]
        )

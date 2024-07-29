"""Tests the `anthropic._utils.convert_message_params` function."""

import pytest

from mirascope.core.anthropic._utils.convert_message_params import (
    convert_message_params,
)
from mirascope.core.base import BaseMessageParam


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "media_type": "image/jpeg",
                    "image": b"image",
                    "detail": "auto",
                }
            ],
        },
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "data": "aW1hZ2U=",
                        "media_type": "image/jpeg",
                        "type": "base64",
                    },
                }
            ],
        },
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Anthropic currently only "
        "supports JPEG, PNG, GIF, and WebP images.",
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
        match="Anthropic currently only supports text and image modalities. "
        "Modality provided: audio",
    ):
        convert_message_params(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "audio", "media_type": "audio/mp3", "audio": b"audio"}
                    ],
                }
            ]
        )

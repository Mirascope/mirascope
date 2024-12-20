"""Tests the `anthropic._utils.convert_message_params` function."""

import pytest
from anthropic.types import MessageParam

from mirascope.core.anthropic._utils._convert_message_params import (
    convert_message_params,
)
from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    DocumentPart,
    ImagePart,
    TextPart,
)


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | MessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail="auto"
                ),
                CacheControlPart(type="cache_control", cache_type="ephemeral"),
                DocumentPart(
                    type="document", media_type="application/pdf", document=b"pdf"
                ),
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
                    "type": "image",
                    "source": {
                        "data": "aW1hZ2U=",
                        "media_type": "image/jpeg",
                        "type": "base64",
                    },
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "source": {
                        "data": "cGRm",
                        "media_type": "application/pdf",
                        "type": "base64",
                    },
                    "type": "document",
                },
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
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="Anthropic currently only supports text, image, and cache control parts. "
        "Part provided: audio",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(type="audio", media_type="audio/mp3", audio=b"audio")
                    ],
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="Unsupported document media type: application/docx. Anthropic currently only supports PDF document.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        DocumentPart(
                            type="document",
                            media_type="application/docx",
                            document=b"docx",
                        )
                    ],
                )
            ]
        )

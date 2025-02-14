"""Tests the `bedrock._utils.convert_message_params` function."""

from unittest.mock import patch

import pytest

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.bedrock import BedrockMessageParam
from mirascope.core.bedrock._utils._convert_message_params import (
    convert_message_params,
)


@patch(
    "mirascope.core.bedrock._utils._convert_message_params._load_media",
    return_value=b"imgdata",
)
@patch(
    "mirascope.core.bedrock._utils._convert_message_params.get_image_type",
    return_value="png",
)
def test_convert_message_params(mock_get_image_type, mock_load_media) -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | BedrockMessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},  # pyright: ignore [reportArgumentType, reportAssignmentType]
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail="auto"
                ),
                ToolResultPart(
                    name="tool_name", id="tool_id", content="result", type="tool_result"
                ),
                TextPart(type="text", text="Hello"),
                ToolCallPart(type="tool_call", name="tool_name", id="tool_id"),
                TextPart(type="text", text="Hello"),
                ImageURLPart(
                    type="image_url", url="http://example.com/image", detail="auto"
                ),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"content": [{"text": "Hello", "type": "text"}], "role": "user"},
        {"content": [{"text": "Hello"}], "role": "user"},
        {
            "content": [
                {"text": "Hello"},
                {"image": {"format": "jpeg", "source": {"bytes": b"image"}}},
            ],
            "role": "user",
        },
        {
            "content": [
                {
                    "toolResult": {
                        "toolUseId": "tool_id",
                        "content": [{"text": "result"}],
                    }
                }
            ],
            "role": "user",
        },
        {"content": [{"text": "Hello"}], "role": "user"},
        {
            "content": [
                {
                    "toolUse": {
                        "toolUseId": "tool_id",
                        "name": "tool_name",
                        "input": None,
                    }
                }
            ],
            "role": "assistant",
        },
        {
            "content": [
                {"text": "Hello"},
                {"image": {"format": "png", "source": {"bytes": b"imgdata"}}},
            ],
            "role": "user",
        },
    ]

    mock_load_media.assert_called_once_with("http://example.com/image")
    mock_get_image_type.assert_called_once_with(b"imgdata")

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Bedrock currently only "
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
        match="Bedrock currently only supports text and image parts. Part provided: audio",
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


@patch(
    "mirascope.core.bedrock._utils._convert_message_params._load_media",
    return_value=b"imgdata",
)
@patch(
    "mirascope.core.bedrock._utils._convert_message_params.get_image_type",
    return_value="png",
)
def test_image_url_conversion(mock_get_image_type, mock_load_media) -> None:
    """Tests conversion of an image_url part."""
    message = BaseMessageParam(
        role="user",
        content=[
            ImageURLPart(
                type="image_url", url="http://example.com/image", detail="auto"
            )
        ],
    )
    result = convert_message_params([message])
    expected = {
        "role": "user",
        "content": [{"image": {"format": "png", "source": {"bytes": b"imgdata"}}}],
    }
    assert result == [expected]
    mock_load_media.assert_called_once_with("http://example.com/image")
    mock_get_image_type.assert_called_once_with(b"imgdata")

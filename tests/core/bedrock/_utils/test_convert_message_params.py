"""Tests the `bedrock._utils.convert_message_params` function."""

import pytest

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.bedrock import BedrockMessageParam
from mirascope.core.bedrock._utils._convert_message_params import (
    convert_message_params,
)


def test_convert_message_params() -> None:
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
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"content": [{"text": "Hello", "type": "text"}], "role": "user"},
        {"content": [{"text": "Hello"}], "role": "user"},
        {
            "content": [{"text": "Hello"}, {"bytes": b"image", "format": "image/jpeg"}],
            "role": "user",
        },
        {
            "content": [
                {
                    "toolResult": {
                        "content": [{"text": "result"}],
                        "toolUseId": "tool_id",
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
                        "input": None,
                        "name": "tool_name",
                        "toolUseId": "tool_id",
                    }
                }
            ],
            "role": "assistant",
        },
        {"content": [{"text": "Hello"}], "role": "user"},
    ]

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

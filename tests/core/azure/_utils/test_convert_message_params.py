"""Tests the `azure._utils.convert_message_params` function."""

import json

import pytest
from azure.ai.inference.models import (
    ChatRequestMessage,
)

from mirascope.core.azure._utils._convert_message_params import convert_message_params
from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | ChatRequestMessage] = [
        ChatRequestMessage(
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]}
        ),
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
                ImagePart(
                    type="image", media_type="image/jpeg", image=b"image", detail="auto"
                ),
                ImageURLPart(
                    type="image_url", url="https://example.com/image.jpg", detail="auto"
                ),
                ToolResultPart(
                    type="tool_result", id="tool_id", content="result", name="tool_name"
                ),
                TextPart(type="text", text="Hello"),
            ],
        ),
        BaseMessageParam(
            role="assistant",
            content=[
                TextPart(type="text", text="Hello"),
                ToolCallPart(
                    type="tool_call", name="tool_name", args={"arg": "val"}, id="tc1"
                ),
            ],
        ),
        BaseMessageParam(
            role="assistant",
            content=[
                TextPart(type="text", text="Hello"),
                TextPart(type="text", text="Hello"),
                ToolCallPart(
                    type="tool_call", name="tool_name", args={"arg": "val"}, id="tc2"
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
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,aW1hZ2U=",
                        "detail": "auto",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg",
                        "detail": "auto",
                    },
                },
            ],
        },
        {"role": "tool", "content": "result", "tool_call_id": "tool_id"},
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tc1",
                    "function": {
                        "name": "tool_name",
                        "arguments": json.dumps({"arg": "val"}),
                    },
                    "type": "function",
                }
            ],
            "content": "Hello",
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "Hello"},
            ],
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tc2",
                    "function": {
                        "name": "tool_name",
                        "arguments": json.dumps({"arg": "val"}),
                    },
                    "type": "function",
                }
            ],
        },
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Azure currently only supports JPEG, PNG, GIF, and WebP images.",
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
        match="Azure currently only supports text and image parts. Part provided: audio",
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

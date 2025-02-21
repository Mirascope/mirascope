"""Tests the `groq._utils.convert_message_params` function."""

import pytest
from groq.types.chat import ChatCompletionMessageParam

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    ImagePart,
    ImageURLPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
)
from mirascope.core.groq._utils._convert_message_params import convert_message_params


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
                ToolResultPart(
                    name="tool_name", id="tool_id", content="result", type="tool_result"
                ),
                TextPart(type="text", text="Hello"),
                ImageURLPart(
                    type="image_url", url="http://example.com/image", detail="ignored"
                ),
            ],
        ),
        BaseMessageParam(
            role="assistant",
            content=[
                TextPart(type="text", text="Hello"),
                ToolCallPart(type="tool_call", name="tool_name", id="tool_id"),
                TextPart(type="text", text="Hello"),
            ],
        ),
        BaseMessageParam(
            role="assistant",
            content=[
                TextPart(type="text", text="Hello"),
                TextPart(type="text", text="Hello"),
                ToolCallPart(type="tool_call", name="tool_name", id="tool_id"),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"content": [{"text": "Hello", "type": "text"}], "role": "user"},
        {"content": "Hello", "role": "user"},
        {
            "content": [
                {"text": "Hello", "type": "text"},
                {
                    "image_url": {
                        "detail": "auto",
                        "url": "data:image/jpeg;base64,aW1hZ2U=",
                    },
                    "type": "image_url",
                },
            ],
            "role": "user",
        },
        {"content": "result", "role": "tool", "tool_call_id": "tool_id"},
        {
            "content": [
                {"text": "Hello", "type": "text"},
                {"image_url": {"url": "http://example.com/image"}, "type": "image_url"},
            ],
            "role": "user",
        },
        {
            "content": "Hello",
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {"arguments": "null", "name": "tool_name"},
                    "id": "tool_id",
                    "type": "function",
                }
            ],
        },
        {"content": [{"text": "Hello", "type": "text"}], "role": "assistant"},
        {
            "content": [
                {"text": "Hello", "type": "text"},
                {"text": "Hello", "type": "text"},
            ],
            "role": "assistant",
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {"arguments": "null", "name": "tool_name"},
                    "id": "tool_id",
                    "type": "function",
                }
            ],
        },
    ]
    with pytest.raises(
        ValueError,
        match="Unsupported image media type: image/svg. Groq currently only supports "
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
        match="Groq currently only supports text and image parts. Part provided: audio",
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

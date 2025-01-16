"""Tests the `openai._utils.convert_message_params` function."""

import pytest
from openai.types.chat import ChatCompletionMessageParam

from mirascope.core.base import (
    AudioPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
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
                ToolResultPart(
                    name="tool_name", id="tool_id", content="result", type="tool_result"
                ),
                ToolCallPart(type="tool_call", name="tool_name", id="tool_id"),
                TextPart(type="text", text="Hello"),
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
                {
                    "input_audio": {"data": "YXVkaW8=", "format": "wav"},
                    "type": "input_audio",
                },
            ],
            "role": "user",
        },
        {"content": "result", "role": "tool", "tool_call_id": "tool_id"},
        {
            "name": "tool_name",
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {"arguments": "null", "name": "tool_name"},
                    "id": "tool_id",
                    "type": "function",
                }
            ],
        },
        {"content": [{"text": "Hello", "type": "text"}], "role": "user"},
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

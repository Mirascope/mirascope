"""Tests the `openai._utils.convert_message_params` function."""

import base64
from unittest.mock import patch

import pytest
from openai.types.chat import ChatCompletionMessageParam

from mirascope.core.base import (
    AudioPart,
    AudioURLPart,
    BaseMessageParam,
    CacheControlPart,
    ImagePart,
    ImageURLPart,
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
                ImageURLPart(
                    type="image_url", url="http://example.com/image", detail="auto"
                ),
                AudioPart(type="audio", media_type="audio/wav", audio=b"audio"),
            ],
        ),
        BaseMessageParam(
            role="assistant",
            content=[
                ToolCallPart(type="tool_call", name="tool_name", id="tool_id"),
            ],
        ),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Here you go!"),
                ToolResultPart(
                    name="tool_name", id="tool_id", content="result", type="tool_result"
                ),
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
                    "image_url": {"detail": "auto", "url": "http://example.com/image"},
                    "type": "image_url",
                },
                {
                    "input_audio": {"data": "YXVkaW8=", "format": "wav"},
                    "type": "input_audio",
                },
            ],
            "role": "user",
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "function": {"arguments": "null", "name": "tool_name"},
                    "type": "function",
                    "id": "tool_id",
                }
            ],
        },
        {"content": [{"text": "Here you go!", "type": "text"}], "role": "user"},
        {"content": "result", "role": "tool", "tool_call_id": "tool_id"},
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


@patch(
    "mirascope.core.openai._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.openai._utils._convert_message_params.get_audio_type",
    return_value="wav",
)
def test_audio_url_valid(mock_get_audio_type, mock_load_media) -> None:
    """Tests conversion of a valid audio_url part."""
    message = BaseMessageParam(
        role="user",
        content=[
            AudioURLPart(
                type="audio_url",
                url="http://example.com/audio",
                detail="ignored",  # pyright: ignore [reportCallIssue]
            )
        ],
    )
    result = convert_message_params([message])
    expected = {
        "content": [
            {
                "input_audio": {
                    "format": "wav",
                    "data": base64.b64encode(b"audio_data").decode("utf-8"),
                },
                "type": "input_audio",
            }
        ],
        "role": "user",
    }
    assert result == [expected]
    mock_load_media.assert_called_once_with("http://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")


@patch(
    "mirascope.core.openai._utils._convert_message_params._load_media",
    return_value=b"audio_data",
)
@patch(
    "mirascope.core.openai._utils._convert_message_params.get_audio_type",
    return_value="aiff",
)
def test_audio_url_invalid(mock_get_audio_type, mock_load_media) -> None:
    """Tests conversion of an audio_url part with an unsupported audio type."""
    message = BaseMessageParam(
        role="user",
        content=[
            AudioURLPart(
                type="audio_url",
                url="http://example.com/audio",
                detail="ignored",  # pyright: ignore [reportCallIssue]
            )
        ],
    )
    with pytest.raises(
        ValueError,
        match="Unsupported audio media type: audio/aiff. OpenAI currently only supports WAV and MP3 audio file types.",
    ):
        convert_message_params([message])
    mock_load_media.assert_called_once_with("http://example.com/audio")
    mock_get_audio_type.assert_called_once_with(b"audio_data")

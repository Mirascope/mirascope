"""Tests the `groq._utils.convert_message_params` function."""

import pytest
from groq.types.chat import ChatCompletionMessageParam

from mirascope.core.base import AudioPart, BaseMessageParam, ImagePart, TextPart
from mirascope.core.groq._utils._convert_message_params import convert_message_params


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | ChatCompletionMessageParam] = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(role="user", content=[TextPart(type="text", text="Hello")]),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params == [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "user", "content": "Hello"},
        {"role": "user", "content": "Hello"},
    ]

    with pytest.raises(
        ValueError,
        match="Groq does not currently support multimodalities.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        ImagePart(
                            type="image",
                            media_type="image/jpeg",
                            image=b"image",
                            detail="auto",
                        )
                    ],
                )
            ]
        )

    with pytest.raises(
        ValueError,
        match="Groq does not currently support multimodalities.",
    ):
        convert_message_params(
            [
                BaseMessageParam(
                    role="user",
                    content=[
                        AudioPart(
                            type="audio",
                            media_type="audio/wav",
                            audio=b"audio",
                        )
                    ],
                ),
            ]
        )

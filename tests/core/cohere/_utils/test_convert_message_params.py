"""Tests the `cohere._utils.convert_message_params` function."""

import pytest
from cohere.types import ChatMessage

from mirascope.core.base import AudioPart, BaseMessageParam, ImagePart, TextPart
from mirascope.core.cohere._utils._convert_message_params import convert_message_params


def test_convert_message_params() -> None:
    """Tests the `convert_message_params` function."""

    message_params: list[BaseMessageParam | ChatMessage] = [
        ChatMessage(message="Hello"),
        BaseMessageParam(role="user", content="Hello"),
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Hello"),
            ],
        ),
    ]
    converted_message_params = convert_message_params(message_params)
    assert converted_message_params[0].dict() == ChatMessage(message="Hello").dict()
    assert (
        converted_message_params[1].dict()
        == ChatMessage(message="Hello", role="USER").dict()  # type: ignore
    )
    assert (
        converted_message_params[2].dict()
        == ChatMessage(message="Hello", role="USER").dict()  # type: ignore
    )

    with pytest.raises(
        ValueError,
        match="Cohere currently only supports text parts.",
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
        match="Cohere currently only supports text parts.",
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

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart, Messages, TextPart
from mirascope.core.base._utils._messages_decorator import messages_decorator
from mirascope.core.base.dynamic_config import DynamicConfigMessages


def test_messages_decorator_str_return():
    @messages_decorator()
    def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


def test_messages_decorator_dynamic_configuration_return():
    @messages_decorator()
    def recommend_book(genre: str) -> DynamicConfigMessages:
        return cast(DynamicConfigMessages, {"messages": f"recommend a {genre} book"})

    result = recommend_book("fantasy")
    assert isinstance(result, dict)
    assert "messages" in result
    assert result["messages"] == "recommend a fantasy book"


def test_messages_decorator_with_none_argument_str_return():
    @messages_decorator()
    def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


@pytest.mark.asyncio
async def test_messages_decorator_str_return_async():
    @messages_decorator()
    async def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = await recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


@pytest.mark.asyncio
async def test_prompt_messages_decorator_configuration_return_async():
    @messages_decorator()
    async def recommend_book(genre: str) -> DynamicConfigMessages:
        return cast(DynamicConfigMessages, {"messages": f"recommend a {genre} book"})

    result = cast(DynamicConfigMessages, await recommend_book("fantasy"))
    assert isinstance(result, dict)
    assert "messages" in result
    assert result["messages"] == "recommend a fantasy book"


def test_list_str_return():
    @messages_decorator()
    def recommend_book(genre: str) -> list[str]:
        return ["hello!", f"recommend a {genre} book"]

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result == [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="hello!"),
                TextPart(type="text", text="recommend a fantasy book"),
            ],
        )
    ]


def test_list_message_role_return():
    @messages_decorator()
    def recommend_book(genre: str) -> Messages.Type:
        return [
            Messages.System("You are a librarian"),
            Messages.Assistant("I can help you find a book"),
            Messages.User(
                content=[
                    TextPart(text="recommend a", type="text"),
                    TextPart(text=genre, type="text"),
                    TextPart(text="book", type="text"),
                ]
            ),
        ]

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 3
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "system"
    assert result[0].content == "You are a librarian"
    assert result[1].role == "assistant"
    assert result[1].content == "I can help you find a book"
    assert isinstance(result[2], BaseMessageParam)
    assert result[2].role == "user"
    assert result[2].content == [
        TextPart(type="text", text="recommend a"),
        TextPart(type="text", text="fantasy"),
        TextPart(type="text", text="book"),
    ]


def test_base_message_param_return():
    @messages_decorator()
    def recommend_book(genre: str) -> BaseMessageParam:
        return BaseMessageParam(role="user", content=f"hello! recommend a {genre} book")

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "hello! recommend a fantasy book"


@patch(
    "mirascope.core.base._utils._convert_messages_to_message_params.pil_image_to_bytes",
    new_callable=MagicMock,
)
def test_multimodal_return(mock_pil_image_to_bytes: MagicMock):
    mock_pil_image_to_bytes.return_value = b"image_bytes"
    mock_image = MagicMock(spec=Image.Image)
    mock_image.format = "PNG"

    @messages_decorator()
    def recommend_book(previous_book: Image.Image) -> list[Any]:
        return ["I just read this book:", previous_book, "What should I read next?"]

    result = recommend_book(mock_image)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert len(result[0].content) == 3
    assert result[0].content[0] == TextPart(type="text", text="I just read this book:")
    assert result[0].content[1] == ImagePart(
        type="image", media_type="image/png", image=b"image_bytes", detail=None
    )
    assert result[0].content[2] == TextPart(
        type="text", text="What should I read next?"
    )

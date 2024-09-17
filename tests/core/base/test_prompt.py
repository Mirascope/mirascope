"""Tests for the `base_prompt` module."""

import os
from typing import Any, ClassVar
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from PIL import Image
from pydantic import computed_field

from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart, TextPart
from mirascope.core.base.messages import Messages
from mirascope.core.base.prompt import BasePrompt, metadata, prompt_template


def test_base_prompt() -> None:
    """Tests the `BasePrompt` class."""

    @prompt_template("Recommend a {genre} book.")
    class BookRecommendationPrompt(BasePrompt):
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."
    assert prompt.dump() == {
        "metadata": {},
        "prompt": "Recommend a fantasy book.",
        "template": "Recommend a {genre} book.",
        "inputs": {"genre": "fantasy"},
    }

    @prompt_template(
        """
        SYSTEM: You are a helpful assistant.
        USER: Please help me.
        """
    )
    class MessagesPrompt(BasePrompt): ...

    prompt = MessagesPrompt()
    assert prompt.message_params() == [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Please help me."),
    ]


def test_base_prompt_with_computed_fields() -> None:
    """Tests the `BasePrompt` class with list and list[list] computed fields."""

    @prompt_template("Recommend a {genre} book.")
    class BookRecommendationPrompt(BasePrompt):
        @computed_field
        @property
        def genre(self) -> str:
            return "fantasy"

    prompt = BookRecommendationPrompt()
    assert str(prompt) == "Recommend a fantasy book."


def test_base_prompt_with_prompt_template() -> None:
    """Tests the `BasePrompt` class with prompt_template."""

    class BookRecommendationPrompt(BasePrompt):
        prompt_template: ClassVar[str] = "Recommend a {genre} book."
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."
    assert prompt.dump() == {
        "metadata": {},
        "prompt": "Recommend a fantasy book.",
        "template": "Recommend a {genre} book.",
        "inputs": {"genre": "fantasy"},
    }

    class BookRecommendationPromptWithoutClassVar(BasePrompt):
        prompt_template = "Recommend a {genre} book."
        genre: str

    prompt = BookRecommendationPromptWithoutClassVar(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."
    assert prompt.dump() == {
        "metadata": {},
        "prompt": "Recommend a fantasy book.",
        "template": "Recommend a {genre} book.",
        "inputs": {"genre": "fantasy"},
    }

    class MessagesPrompt(BasePrompt):
        prompt_template: ClassVar[str] = """
        SYSTEM: You are a helpful assistant.
        USER: Please help me.
        """

    prompt = MessagesPrompt()
    assert prompt.message_params() == [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Please help me."),
    ]

    class MessagesPromptWithoutClassVar(BasePrompt):
        prompt_template = """
        SYSTEM: You are a helpful assistant.
        USER: Please help me.
        """

    prompt = MessagesPromptWithoutClassVar()
    assert prompt.message_params() == [
        BaseMessageParam(role="system", content="You are a helpful assistant."),
        BaseMessageParam(role="user", content="Please help me."),
    ]


def test_base_prompt_run() -> None:
    """Tests the `BasePrompt.run` method."""
    mock_decorator = MagicMock()
    mock_call_fn = MagicMock()
    mock_decorator.return_value = mock_call_fn
    mock_call_fn.return_value = "response"

    @prompt_template("Recommend a {genre} book.")
    class BookRecommendationPrompt(BasePrompt):
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    response = prompt.run(mock_decorator)
    assert response == mock_call_fn.return_value

    # Ensure the decorator was called with the correct function
    mock_decorator.assert_called_once()
    decorator_arg = mock_decorator.call_args[0][0]
    assert callable(decorator_arg)
    assert hasattr(decorator_arg, "_prompt_template")
    assert decorator_arg._prompt_template == "Recommend a {genre} book."

    # Ensure the decorated function was called with the correct arguments
    mock_call_fn.assert_called_once_with(genre="fantasy")


@pytest.mark.asyncio
async def test_base_prompt_run_async() -> None:
    mock_decorator = MagicMock()
    mock_call_fn = AsyncMock()
    mock_decorator.return_value = mock_call_fn
    mock_call_fn.return_value = "response"

    @prompt_template("Recommend a {genre} book.")
    class BookRecommendationPrompt(BasePrompt):
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    response = await prompt.run_async(mock_decorator)
    assert response == mock_call_fn.return_value

    # Ensure the decorator was called with the correct function
    mock_decorator.assert_called_once()
    decorator_arg = mock_decorator.call_args[0][0]
    assert callable(decorator_arg)
    assert hasattr(decorator_arg, "_prompt_template")
    assert decorator_arg._prompt_template == "Recommend a {genre} book."

    # Ensure the decorated function was called with the correct arguments
    mock_call_fn.assert_called_once_with(genre="fantasy")


def test_prompt_template_docstring() -> None:
    """Tests the `prompt_template` decorator on a `BasePrompt`."""

    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "ENABLED"

    class BookRecommendationPrompt(BasePrompt):
        """Recommend a {genre} book."""

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."

    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "DISABLED"


def test_prompt_template_with_function() -> None:
    """Tests the `prompt_template` decorator on a function."""

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...

    assert (
        hasattr(fn, "_prompt_template")
        and fn._prompt_template == "Recommend a {genre} book."  # pyright: ignore [reportFunctionMemberAccess]
    )
    assert fn("fantasy") == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert fn(genre="fantasy") == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]


@pytest.mark.asyncio
async def test_prompt_template_with_async_function() -> None:
    """Tests the `prompt_template` decorator on a async function."""

    @prompt_template("Recommend a {genre} book.")
    async def fn(genre: str) -> None: ...

    assert (
        hasattr(fn, "_prompt_template")
        and fn._prompt_template == "Recommend a {genre} book."  # pyright: ignore [reportFunctionMemberAccess]
    )
    assert await fn("fantasy") == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert await fn(genre="fantasy") == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]


def test_metadata_decorator() -> None:
    """Tests the `metadata` decorator on a `BasePrompt`."""

    @metadata({"tags": {"version:0001"}})
    @prompt_template("Recommend a book.")
    class BookRecommendationPrompt(BasePrompt): ...

    prompt = BookRecommendationPrompt()
    assert prompt.dump()["metadata"] == {"tags": {"version:0001"}}

    @metadata({"tags": {"version:0001"}})
    def fn() -> None: ...

    assert hasattr(fn, "_metadata") and fn._metadata == {"tags": {"version:0001"}}  # pyright: ignore [reportFunctionMemberAccess]


def test_prompt_template_str_return():
    @prompt_template()
    def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


def test_prompt_template_with_none_argument_str_return():
    @prompt_template()
    def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


@pytest.mark.asyncio
async def test_prompt_template_str_return_async():
    @prompt_template()
    async def recommend_book(genre: str) -> str:
        return f"recommend a {genre} book"

    result = await recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "recommend a fantasy book"


def test_list_str_return():
    @prompt_template()
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
    @prompt_template()
    def recommend_book(genre: str) -> Messages.Type:
        return [
            Messages.System("You are a librarian"),
            Messages.User(f"recommend a {genre} book"),
        ]

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "system"
    assert result[0].content == "You are a librarian"
    assert isinstance(result[1], BaseMessageParam)
    assert result[1].role == "user"
    assert result[1].content == "recommend a fantasy book"


def test_base_message_param_return():
    @prompt_template()
    def recommend_book(genre: str) -> BaseMessageParam:
        return BaseMessageParam(role="user", content=f"hello! recommend a {genre} book")

    result = recommend_book("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].role == "user"
    assert result[0].content == "hello! recommend a fantasy book"


@pytest.fixture
def mock_image():
    return Mock(spec=Image.Image)


def test_multimodal_return(mock_image):
    mock_image.tobytes.return_value = b"\xff\xd8\xff"  # JPEG magic number

    @prompt_template()
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
        type="image", media_type="image/jpeg", image=b"\xff\xd8\xff", detail=None
    )
    assert result[0].content[2] == TextPart(
        type="text", text="What should I read next?"
    )

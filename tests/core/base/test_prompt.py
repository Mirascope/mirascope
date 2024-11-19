"""Tests for the `base_prompt` module."""

import os
from typing import ClassVar
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import computed_field

from mirascope.core import BaseMessageParam
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
    assert decorator_arg._prompt_template == "Recommend a {genre} book."  # pyright: ignore [reportFunctionMemberAccess]

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
    assert decorator_arg._prompt_template == "Recommend a {genre} book."  # pyright: ignore [reportFunctionMemberAccess]

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


def test_prompt_template_with_none() -> None:
    """Tests the `prompt_template` decorator with `None` arguments."""
    with mock.patch("mirascope.core.base.prompt.messages_decorator") as mock_decorator:
        mock_decorated_function = mock.MagicMock()
        mock_decorator.return_value.return_value = mock_decorated_function

        @prompt_template()
        def fn() -> None: ...

        assert fn == mock_decorated_function


def test_base_prompt_str_with_special_tags() -> None:
    """Tests the BasePrompt.__str__ method with special tags."""

    @prompt_template(
        """
        Process this: {content:text} and {image:image} and {audio:audio} and 
        these: {contents:texts} and {images:images} and {audios:audios}
        """
    )
    class MultiModalPrompt(BasePrompt):
        content: str
        image: bytes
        audio: bytes
        contents: list[str]
        images: list[bytes]
        audios: list[bytes]

    prompt = MultiModalPrompt(
        content="text",
        image=b"image",
        audio=b"audio",
        contents=["text1", "text2"],
        images=[b"image1", b"image2"],
        audios=[b"audio1", b"audio2"],
    )

    # Verify all special tags are removed in string representation
    expected = (
        "Process this: text and b'image' and b'audio' and \n"
        "these: ['text1', 'text2'] and [b'image1', b'image2'] and [b'audio1', b'audio2']"
    )
    assert str(prompt).strip() == expected.strip()

"""Tests for the `base_prompt` module."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import computed_field

from mirascope.core import BasePrompt, metadata, prompt_template


def test_base_prompt() -> None:
    """Tests the `BasePrompt` class."""

    class BookRecommendationPrompt(BasePrompt):
        """Recommend a {genre} book."""

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."
    assert prompt.dump() == {
        "metadata": {},
        "prompt": "Recommend a fantasy book.",
        "template": "Recommend a {genre} book.",
        "inputs": {"genre": "fantasy"},
    }


def test_base_prompt_with_computed_fields() -> None:
    """Tests the `BasePrompt` class with list and list[list] computed fields."""

    class BookRecommendationPrompt(BasePrompt):
        """Recommend a {genre} book."""

        @computed_field
        @property
        def genre(self) -> str:
            return "fantasy"

    prompt = BookRecommendationPrompt()
    assert str(prompt) == "Recommend a fantasy book."


def test_base_prompt_run() -> None:
    """Tests the `BasePrompt.run` method."""
    mock_decorator = MagicMock()
    mock_call_fn = MagicMock()
    mock_decorator.return_value = mock_call_fn
    mock_call_fn.return_value = "response"

    class BookRecommendationPrompt(BasePrompt):
        """Recommend a {genre} book."""

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    response = prompt.run(mock_decorator)
    assert response == mock_call_fn.return_value

    # Ensure the decorator was called with the correct function
    mock_decorator.assert_called_once()
    decorator_arg = mock_decorator.call_args[0][0]
    assert callable(decorator_arg)
    assert "prompt_template" in decorator_arg.__annotations__
    assert (
        decorator_arg.__annotations__["prompt_template"] == "Recommend a {genre} book."
    )

    # Ensure the decorated function was called with the correct arguments
    mock_call_fn.assert_called_once_with(genre="fantasy")


@pytest.mark.asyncio
async def test_base_prompt_run_async() -> None:
    mock_decorator = MagicMock()
    mock_call_fn = AsyncMock()
    mock_decorator.return_value = mock_call_fn
    mock_call_fn.return_value = "response"

    class BookRecommendationPrompt(BasePrompt):
        """Recommend a {genre} book."""

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    response = await prompt.run_async(mock_decorator)
    assert response == mock_call_fn.return_value

    # Ensure the decorator was called with the correct function
    mock_decorator.assert_called_once()
    decorator_arg = mock_decorator.call_args[0][0]
    assert callable(decorator_arg)
    assert "prompt_template" in decorator_arg.__annotations__
    assert (
        decorator_arg.__annotations__["prompt_template"] == "Recommend a {genre} book."
    )

    # Ensure the decorated function was called with the correct arguments
    mock_call_fn.assert_called_once_with(genre="fantasy")


def test_prompt_template_decorator() -> None:
    """Tests the `prompt_template` decorator on a `BasePrompt`."""

    @prompt_template("Recommend a {genre} book.")
    class BookRecommendationPrompt(BasePrompt):
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."


def test_metadata_decorator() -> None:
    """Tests the `metadata` decorator on a `BasePrompt`."""

    @metadata({"tags": {"version:0001"}})
    class BookRecommendationPrompt(BasePrompt):
        """Recommend a book."""

    prompt = BookRecommendationPrompt()
    assert prompt.dump()["metadata"] == {"tags": {"version:0001"}}

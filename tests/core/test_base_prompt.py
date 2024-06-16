"""Tests for the `base_prompt` module."""

from pydantic import computed_field

from mirascope.core import BasePrompt, tags
from mirascope.core.types import MessageParam


def test_base_prompt() -> None:
    """Tests the `BasePrompt` class."""

    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")
    assert str(prompt) == "Recommend a fantasy book."
    assert prompt.message_params() == [
        {"role": "user", "content": "Recommend a fantasy book."}
    ]
    assert prompt.dump() == {
        "tags": [],
        "prompt": "Recommend a fantasy book.",
        "template": "Recommend a {genre} book.",
        "inputs": {"genre": "fantasy"},
    }


def test_base_prompt_with_messages() -> None:
    """Tests the `BasePrompt` class with message keywords."""

    class BookRecommendationPrompt(BasePrompt):
        prompt_template = """
        SYSTEM: You are the world's greatest librarian.
        MESSAGES: {messages}
        USER: Recommend a book.
        """

        messages: list[MessageParam]

    messages = [
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
    ]
    prompt = BookRecommendationPrompt(messages=messages)
    assert prompt.message_params() == [
        {"role": "system", "content": "You are the world's greatest librarian."},
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Recommend a book."},
    ]


def test_base_prompt_with_list_computed_fields() -> None:
    """Tests the `BasePrompt` class with list and list[list] computed fields."""

    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        @computed_field
        @property
        def genre(self) -> str:
            return "fantasy"

    prompt = BookRecommendationPrompt()
    assert str(prompt) == "Recommend a fantasy book."


def test_tags() -> None:
    """Tests the `tags` decorator on a `BasePrompt`."""

    @tags(["version:0001"])
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a book."

    prompt = BookRecommendationPrompt()
    assert prompt.tags == ["version:0001"]
    assert prompt.dump()["tags"] == ["version:0001"]

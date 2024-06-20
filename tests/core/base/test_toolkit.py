"""Tests for the `toolkit` module."""
from typing import Literal

from mirascope.core.base import BaseToolKit, toolkit_tool


def test_toolkit() -> None:
    """Tests the `BaseToolKit` class and the `toolkit_tool` decorator."""

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        reading_level: Literal["beginner", "advanced"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            """Returns the title and author of a book nicely formatted.

            Reading level: {self.reading_level}
            """
            return f"{title} by {author}"

    toolkit = BookRecommendationToolKit(reading_level="beginner")
    tool = toolkit.create_tool()
    assert tool.__doc__ == "Returns the title and author of a book nicely formatted.\n\nReading level: beginner"

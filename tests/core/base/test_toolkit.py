"""Tests for the `toolkit` module."""
from typing import Literal, ClassVar

from mirascope.core.base import BaseToolKit, toolkit_tool


def test_toolkit() -> None:
    """Tests the `BaseToolKit` class and the `toolkit_tool` decorator."""

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        _namespace: ClassVar[str] = 'book_tools'
        reading_level: Literal["beginner", "advanced"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            """Returns the title and author of a book nicely formatted.

            Reading level: {self.reading_level}
            """
            return f"{title} by {author}"

    toolkit = BookRecommendationToolKit(reading_level="beginner")
    tools = toolkit.create_tools()
    assert len(tools) == 1
    tool = tools[0]
    assert tool._name() == "book_tools.format_book"
    assert (
            tool._description()
            == "Returns the title and author of a book nicely formatted.\n\nReading level: beginner"
    )
    assert (
            tool(title="The Name of the Wind", author="Rothfuss, Patrick").call()
            == "The Name of the Wind by Rothfuss, Patrick"
    )

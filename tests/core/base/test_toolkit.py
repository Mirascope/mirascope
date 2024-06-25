"""Tests for the `toolkit` module."""

from typing import ClassVar, Literal
from unittest import mock

import pytest

from mirascope.core.base import BaseToolKit, toolkit_tool


@pytest.fixture
def mock_namespaces():
    mock_namespaces = set()
    with mock.patch("mirascope.core.base.toolkit._namespaces", mock_namespaces):
        yield mock_namespaces


@pytest.mark.parametrize(
    "namespace, expected_name",
    [
        (None, "format_book"),
        ("book_tools", "book_tools_format_book"),
    ],
)
def test_toolkit(mock_namespaces, namespace: str | None, expected_name: str) -> None:
    """Tests the `BaseToolKit` class and the `toolkit_tool` decorator."""

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        __namespace__: ClassVar[str | None] = namespace
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
    assert tool._name() == expected_name
    assert (
        tool._description()
        == "Returns the title and author of a book nicely formatted.\n\nReading level: beginner"
    )
    assert (
        tool(title="The Name of the Wind", author="Rothfuss, Patrick").call()
        == "The Name of the Wind by Rothfuss, Patrick"
    )


def test_toolkit_multiple_method(mock_namespaces) -> None:
    """Toolkits with multiple toolkit_tool methods should be created correctly."""

    def dummy_decorator(func):
        return func

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        __namespace__: ClassVar[str | None] = "book_tools"
        reading_level: Literal["beginner", "advanced"]
        language: Literal["english", "spanish", "french"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            """Returns the title and author of a book nicely formatted.

            Reading level: {self.reading_level}
            """
            return f"{title} by {author}"

        @toolkit_tool
        def format_world_book(self, title: str, author: str, genre: str) -> str:
            """Returns the title, author, and genre of a book nicely formatted.

            Reading level: {self.reading_level}
            language: {self.language}
            """
            return f"{title} by {author} ({genre})"

        @dummy_decorator
        def dummy_method(self):
            """dummy method"""
            return "dummy"

    toolkit = BookRecommendationToolKit(reading_level="beginner", language="spanish")
    tools = toolkit.create_tools()
    assert len(tools) == 2

    assert tools[0]._name() == "book_tools_format_book"
    assert (
        tools[0]._description()
        == "Returns the title and author of a book nicely formatted.\n\nReading level: beginner"
    )
    assert (
        tools[0](title="The Name of the Wind", author="Rothfuss, Patrick").call()
        == "The Name of the Wind by Rothfuss, Patrick"
    )
    assert tools[1]._name() == "book_tools_format_world_book"
    assert (
        tools[1]._description()
        == "Returns the title, author, and genre of a book nicely formatted.\n\nReading level: beginner\n"
        "language: spanish"
    )
    assert (
        tools[1](
            title="The Name of the Wind", author="Rothfuss, Patrick", genre="fantasy"
        ).call()
        == "The Name of the Wind by Rothfuss, Patrick (fantasy)"
    )


def test_toolkit_tool_method_not_found() -> None:
    """When a toolkit_tool method is not found, a ValueError should be raised."""

    def dummy_decorator(func):
        return func

    with pytest.raises(ValueError, match="No toolkit_tool method found"):

        class BookRecommendationToolKit(BaseToolKit):
            """A toolkit for recommending books."""

            __namespace__: ClassVar[str | None] = "book_tools"
            reading_level: Literal["beginner", "advanced"]
            language: Literal["english", "spanish", "french"]

            def format_book(self, title: str, author: str) -> str:
                """Returns the title and author of a book nicely formatted.

                Reading level: {self.reading_level}
                """
                return f"{title} by {author}"

            @dummy_decorator
            def dummy_method(self):
                """dummy method"""
                return "dummy"


def test_toolkit_tool_method_has_non_self_var(mock_namespaces) -> None:
    """Check if toolkit_tool method has non-self variable, a ValueError should be raised."""

    with pytest.raises(
        ValueError,
        match="The toolkit_tool method must use self. prefix in template variables "
        "when creating tools dynamically",
    ):

        class BookRecommendationToolKit(BaseToolKit):
            """A toolkit for recommending books."""

            __namespace__: ClassVar[str | None] = "book_tools"
            reading_level: Literal["beginner", "advanced"]
            language: Literal["english", "spanish", "french"]

            @toolkit_tool
            def format_book(self, title: str, author: str) -> str:
                """Returns the title and author of a book nicely formatted.

                Reading level: {reading_level}
                """
                return f"{title} by {author}"


def test_toolkit_tool_method_has_no_exists_var(mock_namespaces) -> None:
    """Check if toolkit_tool method has no exists variable, a ValueError should be raised."""

    with pytest.raises(
        ValueError,
        match="The toolkit_tool method template variable self.not_exists is not found in the class",
    ):

        class BookRecommendationToolKit(BaseToolKit):
            """A toolkit for recommending books."""

            __namespace__: ClassVar[str | None] = "book_tools"
            reading_level: Literal["beginner", "advanced"]
            language: Literal["english", "spanish", "french"]

            @toolkit_tool
            def format_book(self, title: str, author: str) -> str:
                """Returns the title and author of a book nicely formatted.

                Reading level: {self.not_exists}
                """
                return f"{title} by {author}"


def test_toolkit_namespace_already_used(mock_namespaces) -> None:
    """Check if toolkit_tool namespace is already used, a ValueError should be raised."""

    mock_namespaces.add("book_tools")
    with pytest.raises(ValueError, match="The namespace book_tools is already used"):

        class BookRecommendationToolKit(BaseToolKit):
            """A toolkit for recommending books."""

            __namespace__: ClassVar[str | None] = "book_tools"

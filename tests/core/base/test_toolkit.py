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
            """Returns formatted title and author.

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
        == "Returns formatted title and author.\n\nReading level: beginner"
    )
    assert (
        tool(title="The Name of the Wind", author="Rothfuss, Patrick").call()  # type: ignore
        == "The Name of the Wind by Rothfuss, Patrick"
    )


def test_toolkit_multiple_method(mock_namespaces) -> None:
    """Tests that multiple `toolkit_tool` methods are created correctly."""

    def dummy_decorator(func):
        return func

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        __namespace__: ClassVar[str | None] = "book_tools"
        reading_level: Literal["beginner", "advanced"]
        language: Literal["english", "spanish", "french"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            """Returns formatted title and author.

            Reading level: {self.reading_level}
            """
            return f"{title} by {author}"

        @toolkit_tool
        def format_world_book(self, title: str, author: str, genre: str) -> str:
            """Returns formatted title, author, and genre.

            Reading level: {self.reading_level}
            language: {self.language}
            """
            return f"{title} by {author} ({genre})"

        @dummy_decorator
        def dummy_method(self) -> str:
            """dummy method"""
            return "dummy"  # pragma: no cover

    toolkit = BookRecommendationToolKit(reading_level="beginner", language="spanish")
    tools = toolkit.create_tools()
    assert len(tools) == 2

    assert tools[0]._name() == "book_tools_format_book"
    assert (
        tools[0]._description()
        == "Returns formatted title and author.\n\nReading level: beginner"
    )
    assert (
        tools[0](title="The Name of the Wind", author="Rothfuss, Patrick").call()  # type: ignore
        == "The Name of the Wind by Rothfuss, Patrick"
    )
    assert tools[1]._name() == "book_tools_format_world_book"
    assert (
        tools[1]._description()
        == "Returns formatted title, author, and genre.\n\nReading level: beginner\n"
        "language: spanish"
    )
    assert (
        tools[1](
            title="The Name of the Wind",  # type: ignore
            author="Rothfuss, Patrick",  # type: ignore
            genre="fantasy",  # type: ignore
        ).call()
        == "The Name of the Wind by Rothfuss, Patrick (fantasy)"
    )


def test_toolkit_tool_method_not_found() -> None:
    """Tests that a ValueError is raised when there's no `toolkit_tool` method."""

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
                return f"{title} by {author}"  # pragma: no cover

            @dummy_decorator
            def dummy_method(self) -> str:
                """dummy method"""
                return "dummy"  # pragma: no cover


def test_toolkit_tool_method_with_non_self_var(mock_namespaces) -> None:
    """Tests that non-self template variables are preserved through tool creation."""

    class BookRecommendationToolKit(BaseToolKit):
        """A toolkit for recommending books."""

        __namespace__: ClassVar[str | None] = "book_tools"
        reading_level: Literal["beginner", "advanced"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            """Reading Level: {self.reading_level}, Non-Self Template Var: {foo}"""
            return f"{title} by {author}"  # pragma: no cover

    tool = BookRecommendationToolKit(reading_level="beginner").create_tools()[0]
    assert (
        tool._description() == "Reading Level: beginner, Non-Self Template Var: {foo}"
    )


def test_toolkit_tool_method_has_no_exists_var(mock_namespaces) -> None:
    """Tests that a ValueError is raised when a template variable doesn't exist."""

    with pytest.raises(
        ValueError,
        match="The toolkit_tool method template variable self.not_exists is not found "
        "in the class",
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
                return f"{title} by {author}"  # pragma: no cover


def test_toolkit_namespace_already_used(mock_namespaces) -> None:
    """Tests that a ValueError is raised when the namespace is already used."""

    mock_namespaces.add("book_tools")
    with pytest.raises(ValueError, match="The namespace book_tools is already used"):

        class BookRecommendationToolKit(BaseToolKit):
            """A toolkit for recommending books."""

            __namespace__: ClassVar[str | None] = "book_tools"


def test_toolkit_tool_method_has_no_docstring(mock_namespaces) -> None:
    """Tests that a ValueError is raised when `toolkit_tool` method has no docstring."""

    with pytest.raises(
        ValueError, match="The toolkit_tool method must have a docstring"
    ):

        class BookRecommendationToolKit(BaseToolKit):
            @toolkit_tool
            def format_book(self, title: str, author: str) -> str:
                return f"{title} by {author}"  # pragma: no cover

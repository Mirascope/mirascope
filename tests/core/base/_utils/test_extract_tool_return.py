"""Tests the `_utils.extract_tool_return` module."""

from pydantic import BaseModel

from mirascope.core.base._utils._extract_tool_return import extract_tool_return


def test_extract_tool_return() -> None:
    """Tests the `extract_tool_return` function."""

    class Book(BaseModel):
        title: str
        author: str

    book = extract_tool_return(
        Book,
        '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        allow_partial=False,
    )
    assert isinstance(book, Book)
    book = extract_tool_return(Book, '{"title": "The Name', allow_partial=True)
    assert isinstance(book, Book)
    assert book.title == "The Name"
    assert book.author is None


def test_extract_tool_return_base_type() -> None:
    """Tests the `extract_tool_return` function with a base type."""

    title = extract_tool_return(
        str, '{"value": "The Name of the Wind"}', allow_partial=False
    )
    assert isinstance(title, str)
    assert title == "The Name of the Wind"
    title = extract_tool_return(str, '{"value": "The Name', allow_partial=True)
    assert isinstance(title, str)
    assert title == "The Name"

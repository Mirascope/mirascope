"""Tests the `_utils.extract_tool_return` module."""

from typing import Annotated

from pydantic import BaseModel, RootModel

from mirascope.core.base._utils._extract_tool_return import extract_tool_return
from mirascope.core.base.from_call_args import FromCallArgs


def test_extract_tool_return() -> None:
    """Tests the `extract_tool_return` function."""

    class Book(BaseModel):
        title: str
        author: str

    book = extract_tool_return(
        Book,
        '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        allow_partial=False,
        fields_from_call_args={},
    )
    assert isinstance(book, Book)
    book = extract_tool_return(
        Book, '{"title": "The Name', allow_partial=True, fields_from_call_args={}
    )
    assert isinstance(book, Book)
    assert book.title == "The Name"
    assert book.author is None


def test_extract_tool_return_base_type() -> None:
    """Tests the `extract_tool_return` function with a base type."""

    title = extract_tool_return(
        str,
        '{"value": "The Name of the Wind"}',
        allow_partial=False,
        fields_from_call_args={},
    )
    assert isinstance(title, str)
    assert title == "The Name of the Wind"
    title = extract_tool_return(
        str, '{"value": "The Name', allow_partial=True, fields_from_call_args={}
    )
    assert isinstance(title, str)
    assert title == "The Name"


def test_extract_tool_return_parse_obj_with_fields_from_call_args() -> None:
    """Tests the `extract_tool_return` function parsing obj and fields from call args."""

    class Book(BaseModel):
        title: Annotated[str, FromCallArgs()]
        author: str

    book = extract_tool_return(
        Book,
        '{"author": "Patrick Rothfuss"}',
        allow_partial=False,
        fields_from_call_args={"title": "The Name of the Wind"},
    )
    assert isinstance(book, Book)
    assert book.title == "The Name of the Wind"
    assert book.author == "Patrick Rothfuss"


def test_extract_tool_return_parse_array_with_fields_from_call_args() -> None:
    """Tests the `extract_tool_return` function parsing array and fields from call args."""

    class Book(BaseModel):
        title: Annotated[str, FromCallArgs()]
        author: str

    # Nested models are not supported in this
    class ListModel(RootModel):
        root: list[Book]

    list_model = extract_tool_return(
        ListModel,
        '[{"author": "Patrick Rothfuss", "title": "The Name of the Wind"}]',
        allow_partial=False,
        fields_from_call_args={"title": "Dummy Title"},
    )
    assert isinstance(list_model, ListModel)
    assert isinstance(list_model.root, list)
    assert len(list_model.root) == 1
    assert list_model.root[0].title == "The Name of the Wind"

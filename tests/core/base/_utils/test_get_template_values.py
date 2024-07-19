"""Tests the `_utils.get_template_values` module."""

from pydantic import BaseModel

from mirascope.core.base._utils.get_template_values import get_template_values


def test_get_template_values() -> None:
    """Test the get_template_values function."""

    class Book(BaseModel):
        title: str

    book = Book(title="book title")

    template_variables = [
        "self",
        "self.var0",
        "book.title",
        "var1",
        "var2",
        "var3",
        "var4",
    ]
    attrs = {
        "self": {"var0": "value0"},
        "book": book,
        "var1": "value1",
        "var2": ["value2", "value3"],
        "var3": [["value4", "value5"], ["value6", "value7"]],
        "var4": [],
    }
    expected = {
        "self": {"var0": "value0"},
        "book": book,
        "var1": "value1",
        "var2": "value2\nvalue3",
        "var3": "value4\nvalue5\n\nvalue6\nvalue7",
        "var4": "",
    }
    assert get_template_values(template_variables, attrs) == expected

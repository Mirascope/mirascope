"""Tests the `_utils.get_template_values` module."""

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils._get_template_values import get_template_values


def test_get_template_values() -> None:
    """Test the get_template_values function."""

    class Book(BaseModel):
        title: str

    book = Book(title="book title")

    template_variables: list[tuple[str, str | None]] = [
        ("self", ""),
        ("self.var0", ""),
        ("book.title", ""),
        ("var1", ""),
        ("var2", ""),
        ("var3", "list"),
        ("var4", "list"),
        ("var5", "lists"),
        ("var6", "lists"),
    ]
    attrs = {
        "self": {"var0": "value0"},
        "book": book,
        "var1": "value1",
        "var2": ["value2", "value3"],
        "var3": ["value2", "value3"],
        "var4": [],
        "var5": [["value4", "value5"], ["value6", "value7"]],
        "var6": [],
    }
    expected = {
        "self": {"var0": "value0"},
        "book": book,
        "var1": "value1",
        "var2": ["value2", "value3"],
        "var3": "value2\nvalue3",
        "var4": "",
        "var5": "value4\nvalue5\n\nvalue6\nvalue7",
        "var6": "",
    }
    assert get_template_values(template_variables, attrs) == expected

    with pytest.raises(
        ValueError,
        match="Template variable 'var3' must be a list when using the 'list' format "
        "spec.",
    ):
        get_template_values([("var3", "list")], {"var3": "value"})

    list_of_lists_match = "Template variable 'var5' must be a list of lists when using "
    "the 'lists' format spec."

    with pytest.raises(ValueError, match=list_of_lists_match):
        get_template_values([("var5", "lists")], {"var5": "value"})

    with pytest.raises(ValueError, match=list_of_lists_match):
        get_template_values([("var5", "lists")], {"var5": ["value"]})

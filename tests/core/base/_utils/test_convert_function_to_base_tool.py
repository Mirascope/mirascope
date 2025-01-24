"""Tests the `_utils.convert_function_to_base_tool` module."""

import pytest

from mirascope.core.base._utils._convert_function_to_base_tool import (
    convert_function_to_base_tool,
)
from mirascope.core.base.tool import BaseTool


def test_convert_function_to_base_tool() -> None:
    """Tests the `convert_function_to_base_tool` function."""

    def format_book(title: str, author: str) -> str:
        """Returns the title and author nicely formatted."""
        return f"{title} by {author}"

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    assert tool_type._name() == "format_book"
    assert tool_type._description() == "Returns the title and author nicely formatted."
    assert "title" in tool_type.model_fields
    assert "author" in tool_type.model_fields
    tool = tool_type(title="The Name of the Wind", author="Patrick Rothfuss")  # type: ignore
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"


@pytest.mark.asyncio
async def test_convert_async_function_to_base_tool() -> None:
    """Tests the `convert_function_to_base_tool` function with async functions."""

    async def format_book(title: str, author: str) -> str:
        """Returns the title and author nicely formatted."""
        return f"{title} by {author}"

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    tool = tool_type(title="The Name of the Wind", author="Patrick Rothfuss")  # type: ignore
    assert await tool.call() == "The Name of the Wind by Patrick Rothfuss"


def test_convert_class_function_to_base_tool_fully_documented() -> None:
    """Tests `convert_function_to_base_tool` with a fully documented class function."""

    def format_book(title: str = "default_title") -> None:
        """Returns the title and author nicely formatted.

        Examples:
            {"title": "The Name of the Wind"}

        Args:
            title: The title of the book.
        """

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    assert "title" in tool_type.model_fields
    title_field = tool_type.model_fields["title"]
    assert title_field.default == "default_title"
    assert title_field.description == "The title of the book."
    assert "json_schema_extra" in tool_type.model_config
    assert tool_type.model_config["json_schema_extra"]["examples"] == [  # type: ignore
        {"title": "The Name of the Wind"}
    ]


def test_convert_function_to_base_tool_with_protected_namespace_field() -> None:
    """Tests `convert_function_to_base_tool` with a protected namespace field."""

    def format_book(model_title: str) -> None:
        """Tool with protected name model_*"""

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    assert "aliased_model_title" in tool_type.model_fields


def test_convert_function_to_base_tool_with_self_argument() -> None:
    """Tests `convert_function_to_base_tool` with a function that takes `self`."""

    def format_book(self):
        return self.title

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    tool_type.title = "The Name of the Wind"  # pyright: ignore [reportAttributeAccessIssue]
    tool = tool_type()  # pyright: ignore [reportAbstractUsage]
    assert tool.call() == "The Name of the Wind"


def test_convert_function_to_base_tool_with_cls_argument() -> None:
    """Tests `convert_function_to_base_tool` with a function that takes `cls`."""

    def format_book(cls=None) -> str:
        return "The Name of the Wind"

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    tool = tool_type()  # pyright: ignore [reportAbstractUsage]
    assert tool.call() == "The Name of the Wind"


def test_convert_function_to_base_tool_missing_type_annotation() -> None:
    """Tests `convert_function_to_base_tool` with a missing a type annotation."""

    def format_book(title) -> None:
        """Tool with missing type annotation."""

    with pytest.raises(ValueError):
        convert_function_to_base_tool(format_book, BaseTool)


def test_convert_function_to_base_tool_incorrect_parameter_name() -> None:
    """Tests `convert_function_to_base_tool` with an incorrect parameter name."""

    def format_book(title: str) -> None:
        """Returns the title and author nicely formatted.

        Args:
            titles: The title of the book.
        """

    with pytest.raises(ValueError):
        convert_function_to_base_tool(format_book, BaseTool)


def test_convert_function_to_base_tool_missing_parameter_description() -> None:
    """Tests `convert_function_to_base_tool` with a missing parameter description."""

    def format_book(title: str) -> None:
        """Returns the title and author nicely formatted.

        Args:
            title:
        """

    with pytest.raises(ValueError):
        convert_function_to_base_tool(format_book, BaseTool)


def test_convert_function_to_base_tool_docstring_reconstruction() -> None:
    """Tests the docstring reconstruction in `convert_function_to_base_tool`."""

    def format_book(title: str) -> None:
        """Short description.

        Long description.

        Examples:
            {"title": "The Name of the Wind"}

        Args:
            title: The title of the book.

        Raises:
            ValueError: If the title is invalid.
        """

    tool_type = convert_function_to_base_tool(format_book, BaseTool)
    assert (
        tool_type._description()
        == """Short description.

Long description.

Raises:
    ValueError: If the title is invalid."""
    )

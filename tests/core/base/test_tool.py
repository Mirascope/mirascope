"""Tests for the `tool` module."""

from abc import update_abstractmethods

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils import DEFAULT_TOOL_DOCSTRING
from mirascope.core.base.response_model_config_dict import ResponseModelConfigDict
from mirascope.core.base.tool import BaseTool, ToolConfig


def test_base_tool() -> None:
    """Tests the `BaseTool` class."""

    class FormatBook(BaseTool):
        """Returns a formatted book title and author."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool = FormatBook(title="The Name of the Wind", author="Patrick Rothfuss")
    assert tool._name() == "FormatBook"
    assert tool._description() == "Returns a formatted book title and author."
    assert tool.args == {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"


def test_base_tool_additional_call_args() -> None:
    """Tests the `BaseTool` class with additional call arguments."""

    class FormatBook(BaseTool):
        title: str
        author: str

        def call(self, genre: str, *, topic: str) -> str:
            return f"{self.title} by {self.author} (genre: {genre}, topic: {topic})"

    tool = FormatBook(title="title", author="author")
    assert (
        tool.call("genre", topic="topic")
        == "title by author (genre: genre, topic: topic)"
    )


@pytest.mark.asyncio
async def test_base_tool_call_async() -> None:
    """Tests the `BaseTool.call` method with an async function."""

    class FormatBook(BaseTool):
        """Returns a formatted book title and author."""

        title: str
        author: str

        async def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool = FormatBook(title="The Name of the Wind", author="Patrick Rothfuss")
    assert await tool.call() == "The Name of the Wind by Patrick Rothfuss"


def test_base_tool_no_doc() -> None:
    """Tests the `BaseTool` class with no docstring."""
    from mirascope.core.base import BaseTool

    class FormatBook(BaseTool):
        title: str

    assert FormatBook._description() == DEFAULT_TOOL_DOCSTRING


def test_base_tool_custom_name() -> None:
    """Tests the `BaseTool` class with a custom name."""
    from mirascope.core.base import BaseTool

    class FormatBook(BaseTool):
        __custom_name__ = "format_book"

    assert FormatBook._name() == "format_book"


def test_base_tool_type_conversion() -> None:
    """Tests the `BaseTool.type_from...` class methods."""

    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"

    tool_type = BaseTool.type_from_fn(format_book)
    assert tool_type.__name__ == "format_book"
    tool = tool_type(title="The Name of the Wind", author="Patrick Rothfuss")  # type: ignore
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    class FormatBook(BaseModel):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_type = BaseTool.type_from_base_model_type(FormatBook)
    assert tool_type.__name__ == "FormatBook"
    tool = tool_type(title="The Name of the Wind", author="Patrick Rothfuss")  # type: ignore
    assert isinstance(tool, BaseTool)
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    tool_type = BaseTool.type_from_base_type(str)
    tool_type.call = lambda self: self.value  # pyright: ignore [reportAttributeAccessIssue]
    update_abstractmethods(tool_type)
    assert tool_type.__name__ == "str"
    tool = tool_type(value="The Name of the Wind")  # type: ignore
    assert tool.call() == "The Name of the Wind"
    assert isinstance(tool, BaseTool)


def test_base_tool_tool_schema_not_implemented() -> None:
    """Tests the `BaseTool` class when the `tool_schema` method is not implemented."""

    class FormatBook(BaseTool):
        title: str

    with pytest.raises(RuntimeError) as exc_info:
        FormatBook.tool_schema()
    assert "FormatBook.tool_schema() is not implemented." in str(exc_info.value)
    assert (
        "This method should be implemented in provider-specific tool classes."
        in str(exc_info.value)
    )


def test_base_tool_unsupported_configurations_warning() -> None:
    """Tests the `warn_for_unsupported_configurations` classmethod of `BaseTool`."""

    class Unsupported(ToolConfig, total=False):
        unsupported: str

    class FormatBook(BaseTool):
        title: str

        tool_config = Unsupported(unsupported="")

    with pytest.warns(
        UserWarning,
        match="NONE does not support the following tool configurations, so they will "
        "be ignored: {'unsupported'}",
    ):
        FormatBook.warn_for_unsupported_configurations()

    class Book(BaseTool):
        title: str

        model_config = ResponseModelConfigDict(strict=True)

    with pytest.warns(
        UserWarning,
        match="NONE does not support strict structured outputs, but you have "
        "configured `strict=True` in your `ResponseModelConfigDict`. Ignoring `strict` "
        "as this feature is only supported by OpenAI.",
    ):
        Book.warn_for_unsupported_configurations()

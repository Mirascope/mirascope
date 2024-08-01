"""Tests the `_utils.convert_base_model_to_base_tool` module."""

from pydantic import BaseModel

from mirascope.core.base._utils._convert_base_model_to_base_tool import (
    convert_base_model_to_base_tool,
)
from mirascope.core.base._utils._default_tool_docstring import DEFAULT_TOOL_DOCSTRING
from mirascope.core.base.tool import BaseTool


def test_convert_base_model_to_base_tool() -> None:
    """Tests the `convert_base_model_to_base_tool` function."""

    class Book(BaseModel):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool = convert_base_model_to_base_tool(Book, BaseTool)
    assert tool._name() == "Book"
    assert tool._description() == DEFAULT_TOOL_DOCSTRING
    assert (
        tool(title="The Name of the Wind", author="Patrick Rothfuss").call()  # type: ignore
        == "The Name of the Wind by Patrick Rothfuss"
    )

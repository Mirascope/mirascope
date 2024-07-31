"""Tests the `cohere.tool` module."""

from cohere.types import Tool, ToolCall, ToolParameterDefinitionsValue
from pydantic import Field

from mirascope.core.base.tool import BaseTool
from mirascope.core.cohere.tool import CohereTool


def test_cohere_tool() -> None:
    """Tests the `CohereTool` class."""

    class FormatBook(CohereTool):
        """Returns the title and author nicely formatted."""

        title: str = Field(..., description="Title")
        author: str = Field(..., description="Author")

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolCall(
        name="FormatBook",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, CohereTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"
    title = ToolParameterDefinitionsValue(
        description="Title", type="string", required=True
    )
    author = ToolParameterDefinitionsValue(
        description="Author", type="string", required=True
    )
    assert FormatBook.tool_schema() == Tool(
        name="FormatBook",
        description="Returns the title and author nicely formatted.",
        parameter_definitions={"title": title, "author": author},
    )

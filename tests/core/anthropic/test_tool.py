"""Tests the `anthropic.tool` module."""

from anthropic.types import (
    ToolParam,
    ToolUseBlock,
)

from mirascope.core.anthropic.tool import AnthropicTool
from mirascope.core.base.tool import BaseTool


def test_anthropic_tool() -> None:
    """Tests the `AnthropicTool` class."""

    class FormatBook(AnthropicTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolUseBlock(
        id="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
        type="tool_use",
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, FormatBook)
    assert isinstance(tool, BaseTool)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"
    assert FormatBook.tool_schema() == ToolParam(
        name="FormatBook",
        description="Returns the title and author nicely formatted.",
        input_schema={
            "$defs": {
                "ToolUseBlock": {
                    "additionalProperties": True,
                    "properties": {
                        "id": {"title": "Id", "type": "string"},
                        "input": {"title": "Input"},
                        "name": {"title": "Name", "type": "string"},
                        "type": {
                            "const": "tool_use",
                            "enum": ["tool_use"],
                            "title": "Type",
                            "type": "string",
                        },
                    },
                    "required": ["id", "input", "name", "type"],
                    "title": "ToolUseBlock",
                    "type": "object",
                }
            },
            "properties": {
                "tool_call": {"$ref": "#/$defs/ToolUseBlock"},
                "title": {"title": "Title", "type": "string"},
                "author": {"title": "Author", "type": "string"},
            },
            "required": ["tool_call", "title", "author"],
            "type": "object",
        },
    )

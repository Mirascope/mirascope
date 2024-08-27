"""Tests the `anthropic.tool` module."""

from anthropic.types import (
    ToolParam,
    ToolUseBlock,
)

from mirascope.core.anthropic.tool import AnthropicTool, AnthropicToolConfig
from mirascope.core.base.tool import BaseTool


def test_anthropic_tool() -> None:
    """Tests the `AnthropicTool` class."""

    class FormatBook(AnthropicTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        tool_config = AnthropicToolConfig(cache_control={"type": "ephemeral"})

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolUseBlock(
        id="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
        type="tool_use",
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, AnthropicTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"
    kwargs = {
        "name": "FormatBook",
        "description": "Returns the title and author nicely formatted.",
        "input_schema": {
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
            },
            "required": ["title", "author"],
            "type": "object",
        },
        "cache_control": {"type": "ephemeral"},
    }
    assert FormatBook.tool_schema() == ToolParam(**kwargs)

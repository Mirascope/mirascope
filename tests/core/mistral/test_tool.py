"""Tests the `mistral.tool` module."""

from mistralai.models.chat_completion import FunctionCall, ToolCall, ToolType

from mirascope.core.base.tool import BaseTool
from mirascope.core.mistral.tool import MistralTool


def test_mistral_tool() -> None:
    """Tests the `MistralTool` class."""

    class FormatBook(MistralTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type=ToolType.function,
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, MistralTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    assert FormatBook.tool_schema() == {
        "function": {
            "name": "FormatBook",
            "description": "Returns the title and author nicely formatted.",
            "parameters": {
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                },
                "required": ["title", "author"],
                "type": "object",
            },
        },
        "type": "function",
    }

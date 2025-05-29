"""Tests the `mistral.tool` module."""

from mistralai.models import FunctionCall, ToolCall

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
        type="function",
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


def test_mistral_tool_no_args() -> None:
    """Tests the `MistralTool` class with no arguments."""

    class FormatBook(MistralTool):
        """Returns the title and author nicely formatted."""

        def call(self) -> str: ...

    assert FormatBook.tool_schema() == {
        "function": {
            "name": "FormatBook",
            "description": "Returns the title and author nicely formatted.",
            "parameters": {"type": "object"},
        },
        "type": "function",
    }

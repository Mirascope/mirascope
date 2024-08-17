"""Tests the `groq.tool` module."""

from groq.types.chat import ChatCompletionToolParam
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.groq.tool import GroqTool


def test_groq_tool() -> None:
    """Tests the `GroqTool` class."""

    class FormatBook(GroqTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, GroqTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    assert FormatBook.tool_schema() == ChatCompletionToolParam(
        type="function",
        function={
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
    )

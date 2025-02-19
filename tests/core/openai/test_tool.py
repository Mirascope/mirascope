"""Tests the `openai.tool` module."""

from openai.types.chat import ChatCompletionToolParam
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.openai.tool import OpenAITool, OpenAIToolConfig


def test_openai_tool() -> None:
    """Tests the `OpenAITool` class."""

    class FormatBook(OpenAITool):
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
    assert isinstance(tool, OpenAITool)
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


def test_openai_tool_strict() -> None:
    """Tests the strict settings for the `OpenAITool` class."""

    class FormatBook(OpenAITool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        tool_config = OpenAIToolConfig(strict=True)

    assert FormatBook.tool_schema() == ChatCompletionToolParam(
        type="function",
        function={
            "name": "FormatBook",
            "description": "Returns the title and author nicely formatted.",
            "strict": True,
            "parameters": {
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                },
                "required": ["title", "author"],
                "type": "object",
                "additionalProperties": False,
            },
        },
    )

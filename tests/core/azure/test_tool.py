"""Tests the `azure.tool` module."""

from azure.ai.inference.models import (
    ChatCompletionsToolCall,
    ChatCompletionsToolDefinition,
    FunctionCall,
    FunctionDefinition,
)

from mirascope.core.azure.tool import AzureTool, AzureToolConfig

#
from mirascope.core.base.tool import BaseTool


def test_azure_tool() -> None:
    """Tests the `AzureTool` class."""

    class FormatBook(AzureTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ChatCompletionsToolCall(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, AzureTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    assert FormatBook.tool_schema() == ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            {
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
    )


def test_azure_tool_strict() -> None:
    """Tests the strict settings for the `AzureTool` class."""

    class FormatBook(AzureTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        tool_config = AzureToolConfig(strict=True)

    assert FormatBook.tool_schema() == ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            {
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
        ),
    )

"""Tests the `bedrock.tool` module."""

from mypy_boto3_bedrock_runtime.type_defs import (
    ToolSpecificationTypeDef,
    ToolTypeDef,
    ToolUseBlockOutputTypeDef,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.bedrock._types import ToolUseBlockContentTypeDef
from mirascope.core.bedrock.tool import BedrockTool, BedrockToolConfig


def test_bedrock_tool() -> None:
    """Tests the `BedrockTool` class."""

    class FormatBook(BedrockTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        tool_config = BedrockToolConfig()

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolUseBlockContentTypeDef(
        toolUse=ToolUseBlockOutputTypeDef(
            toolUseId="id",
            input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
            name="FormatBook",
        )
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, BedrockTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    expected_schema = ToolTypeDef(
        toolSpec=ToolSpecificationTypeDef(
            name="FormatBook",
            description="Returns the title and author nicely formatted.",
            inputSchema={
                "json": {
                    "properties": {
                        "title": {"type": "string"},
                        "author": {"type": "string"},
                    },
                    "required": ["title", "author"],
                    "type": "object",
                }
            },
        )
    )
    assert FormatBook.tool_schema() == expected_schema


def test_bedrock_tool_from_function() -> None:
    """Tests the `BedrockTool.type_from_fn` method."""

    def format_book(title: str, author: str) -> str:
        """Returns the title and author nicely formatted."""
        return f"{title} by {author}"

    ToolType = BedrockTool.type_from_fn(format_book)

    expected_schema = ToolTypeDef(
        toolSpec=ToolSpecificationTypeDef(
            name="format_book",
            description="Returns the title and author nicely formatted.",
            inputSchema={
                "json": {
                    "properties": {
                        "title": {"type": "string"},
                        "author": {"type": "string"},
                    },
                    "required": ["title", "author"],
                    "type": "object",
                }
            },
        )
    )
    assert ToolType.tool_schema() == expected_schema

    tool_call = ToolUseBlockContentTypeDef(
        toolUse={
            "toolUseId": "id",
            "input": {"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
            "name": "format_book",
        }
    )
    tool = ToolType.from_tool_call(tool_call)
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

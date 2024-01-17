"""Tests for mirascope chat API tool classes."""
import pytest
from pydantic import Field

from mirascope.chat.tools import OpenAITool


class MyTool(OpenAITool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


class EmptyTool(OpenAITool):
    """A test tool with no parameters."""


@pytest.mark.parametrize(
    "tool,expected_schema",
    [
        (
            MyTool,
            {
                "type": "function",
                "function": {
                    "name": "my_tool",
                    "description": "A test tool.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param": {
                                "type": "string",
                                "description": "A test parameter.",
                            },
                            "optional": {"type": "integer"},
                        },
                        "required": ["param"],
                    },
                },
            },
        ),
        (
            EmptyTool,
            {
                "type": "function",
                "function": {
                    "name": "empty_tool",
                    "description": "A test tool with no parameters.",
                },
            },
        ),
    ],
)
def test_openai_tool_tool_schema(tool, expected_schema):
    """Tests that `OpenAITool.tool_schema` returns the expected schema."""
    assert tool.tool_schema() == expected_schema


def test_openai_tool_no_description():
    """Tests that a tool without a description raises a ValueError."""
    with pytest.raises(ValueError):

        class NoDescriptionTool(OpenAITool):
            param: str = Field(..., description="A test parameter.")
            optional: int = 0

        NoDescriptionTool.tool_schema()

"""Tests for mirascope chat API tool classes."""
import pytest
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import Field, ValidationError

from mirascope.chat.tools import OpenAITool, openai_tool_fn


@pytest.mark.parametrize(
    "tool,expected_schema",
    [
        (
            "fixture_my_tool",
            {
                "type": "function",
                "function": {
                    "name": "MyTool",
                    "description": "A test tool.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param": {
                                "type": "string",
                                "description": "A test parameter.",
                            },
                            "optional": {"type": "integer"},
                            "tool_call": {
                                "$ref": "#/$defs/ChatCompletionMessageToolCall"
                            },
                        },
                        "required": ["tool_call", "param"],
                    },
                },
            },
        ),
        (
            "fixture_empty_tool",
            {
                "type": "function",
                "function": {
                    "name": "EmptyTool",
                    "description": "A test tool with no parameters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool_call": {
                                "$ref": "#/$defs/ChatCompletionMessageToolCall"
                            }
                        },
                        "required": ["tool_call"],
                    },
                },
            },
        ),
    ],
)
def test_openai_tool_tool_schema(tool, expected_schema, request):
    """Tests that `OpenAITool.tool_schema` returns the expected schema."""
    tool = request.getfixturevalue(tool)
    assert tool.tool_schema() == expected_schema


class NoDescriptionTool(OpenAITool):
    param: str = Field(..., description="A test parameter.")
    optional: int = 0


def test_openai_tool_no_description():
    """Tests that a tool without a description raises a ValueError."""
    with pytest.raises(ValueError):
        NoDescriptionTool.tool_schema()


def test_openai_tool_from_tool_call(fixture_my_tool):
    """Tests that `OpenAITool.from_tool_call` returns the expected tool instance."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": "param",\n  "optional": 0}', name="MyTool"
        ),
        type="function",
    )
    tool = fixture_my_tool.from_tool_call(tool_call)
    assert isinstance(tool, fixture_my_tool)
    assert tool.param == "param"
    assert tool.optional == 0
    assert tool.fn is None


def test_openai_tool_from_tool_call_validation_error(fixture_my_tool):
    """Tests that `OpenAITool.from_tool_call` raises a ValidationError for bad tool."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": 0,\n  "optional": 0}', name="MyTool"
        ),
        type="function",
    )
    with pytest.raises(ValidationError):
        fixture_my_tool.from_tool_call(tool_call)


def test_openai_tool_from_tool_call_json_decode_error(fixture_my_tool):
    """Tests that `OpenAITool.from_tool_call` raises a ValueError for bad JSON."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": "param",\n  "optional": 0', name="MyTool"
        ),
        type="function",
    )
    with pytest.raises(ValueError):
        fixture_my_tool.from_tool_call(tool_call)


def test_openai_tool_fn_decorator(fixture_my_tool):
    """Tests that the `fn` property returns the function that the tool describes."""

    def my_tool(param: str, optional: int = 0) -> None:
        """A test tool function."""

    assert (
        openai_tool_fn(my_tool)(fixture_my_tool)(
            param="param",
            optional=0,
            tool_call=ChatCompletionMessageToolCall(
                id="id",
                function=Function(
                    arguments='{\n  "param": "param",\n  "optional": 0}', name="MyTool"
                ),
                type="function",
            ),
        ).fn
        == my_tool
    )

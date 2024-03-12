"""Tests for the `OpenAITool` class."""
from typing import Any, Type

import pytest
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel, ValidationError
from pytest import FixtureRequest

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from mirascope.openai.tools import OpenAITool


@pytest.mark.parametrize(
    "tool_str,expected_schema",
    [
        (
            "fixture_my_openai_tool",
            {
                "type": "function",
                "function": {
                    "name": "MyOpenAITool",
                    "description": "A test tool.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param": {
                                "type": "string",
                                "description": "A test parameter.",
                                "title": "Param",
                            },
                            "optional": {
                                "type": "integer",
                                "title": "Optional",
                                "default": 0,
                            },
                        },
                        "required": ["param"],
                    },
                },
            },
        ),
        (
            "fixture_empty_openai_tool",
            {
                "type": "function",
                "function": {
                    "name": "EmptyOpenAITool",
                    "description": "A test tool with no parameters.",
                },
            },
        ),
    ],
)
def test_openai_tool_tool_schema(
    tool_str: str, expected_schema: dict[str, Any], request: FixtureRequest
):
    """Tests that `OpenAITool.tool_schema` returns the expected schema."""
    tool: Type[OpenAITool] = request.getfixturevalue(tool_str)
    assert tool.tool_schema() == expected_schema


def test_openai_tool_from_tool_call(fixture_my_openai_tool: Type[OpenAITool]):
    """Tests that `OpenAITool.from_tool_call` returns the expected tool instance."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": "param",\n  "optional": 0}', name="MyOpenAITool"
        ),
        type="function",
    )
    tool = fixture_my_openai_tool.from_tool_call(tool_call)
    assert isinstance(tool, fixture_my_openai_tool)
    assert tool.args == {"param": "param", "optional": 0}


def test_openai_tool_from_tool_call_validation_error(
    fixture_my_openai_tool: OpenAITool,
):
    """Tests that `OpenAITool.from_tool_call` raises a ValidationError for bad tool."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": 0,\n  "optional": 0}', name="MyOpenAITool"
        ),
        type="function",
    )
    with pytest.raises(ValidationError):
        fixture_my_openai_tool.from_tool_call(tool_call)


def test_openai_tool_from_tool_call_json_decode_error(
    fixture_my_openai_tool: OpenAITool,
):
    """Tests that `OpenAITool.from_tool_call` raises a ValueError for bad JSON."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": "param",\n  "optional": 0', name="MyOpenAITool"
        ),
        type="function",
    )
    with pytest.raises(ValueError):
        fixture_my_openai_tool.from_tool_call(tool_call)


def test_openai_tool_from_model(fixture_my_schema: Type[BaseModel]) -> None:
    """Tests that `OpenAITool.from_model` converts a `BaseModel` into `OpenAITool`."""
    tool_type = OpenAITool.from_model(fixture_my_schema)
    assert issubclass(tool_type, OpenAITool)
    assert tool_type.model_json_schema() == fixture_my_schema.model_json_schema()


def test_openai_tool_from_fn() -> None:
    """Tests that `OpenAITool.from_fn` converts a function into `OpenAITool`."""

    def fn(param: str):
        """Test fn"""

    class Fn(OpenAITool):
        """Test fn"""

        param: str

    tool_type = OpenAITool.from_fn(fn)
    assert issubclass(tool_type, OpenAITool)
    assert tool_type.model_json_schema() == Fn.model_json_schema()


def test_openai_tool_from_base_type() -> None:
    """Tests that `OpenAITool.from_base_type` converts a base type into `OpenAITool`."""

    class Float(OpenAITool):
        __doc__ = DEFAULT_TOOL_DOCSTRING
        value: float

    tool_type = OpenAITool.from_base_type(float)
    assert issubclass(tool_type, OpenAITool)
    assert tool_type.model_json_schema() == Float.model_json_schema()

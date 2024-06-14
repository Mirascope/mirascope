"""Tests for the `mirascope.groq.tools` module."""

import pytest
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel, Field

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from mirascope.groq.tools import GroqTool


class NoDescription(GroqTool):
    param: str


def test_from_tool_call_no_args() -> None:
    """Test the `from_tool_call` method with no args."""
    with pytest.raises(ValueError):
        NoDescription.from_tool_call(
            ChatCompletionMessageToolCall(
                id="id",
                function=Function(name="nodescription", arguments=""),
                type="function",
            )
        )


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param


class FakeTool(GroqTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")

    @classmethod
    def name(cls) -> str:
        return "fake_tool"


def test_tool_from_fn() -> None:
    """Tests converting a function into a `GroqTool`."""
    fake_tool("param")
    assert GroqTool.from_fn(fake_tool).tool_schema() == FakeTool.tool_schema()


def test_tool_from_model() -> None:
    """Tests creating a `GroqTool` type from a `BaseModel`."""

    class MyModel(BaseModel):
        """My model"""

        param: str

    tool_type = GroqTool.from_model(MyModel)
    assert tool_type.model_json_schema() == MyModel.model_json_schema()


def test_tool_from_base_type() -> None:
    """Tests creating a `GroqTool` type from a `BaseModel`."""

    class Str(BaseModel):
        __doc__ = DEFAULT_TOOL_DOCSTRING

        value: str

    assert GroqTool.from_base_type(str).model_json_schema() == Str.model_json_schema()


def test_groq_tool_from_tool_call_json_decode_error():
    """Tests that `GroqTool.from_tool_call` raises a ValueError for bad JSON."""
    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{\n  "param": "param",\n  "optional": 0', name="FakeTool"
        ),
        type="function",
    )
    with pytest.raises(ValueError):
        FakeTool.from_tool_call(tool_call)

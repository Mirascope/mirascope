"""Tests for the `mirascope.gemini.tools` module."""
import pytest
from google.ai.generativelanguage import FunctionCall
from pydantic import Field

from mirascope.gemini.tools import GeminiTool


class NoDescription(GeminiTool):
    param: str


def test_gemini_tool_no_description() -> None:
    """Test the `GeminiTool` class with no description."""
    with pytest.raises(ValueError):
        NoDescription.tool_schema()


def test_from_tool_call_no_args() -> None:
    """Test the `from_tool_call` method with no args."""
    with pytest.raises(ValueError):
        NoDescription.from_tool_call(FunctionCall(name="NoDescription"))


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param


class FakeTool(GeminiTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")


def test_tool_from_fn() -> None:
    """Tests converting a function into a `GeminiTool`."""
    fake_tool("param")
    assert (
        GeminiTool.from_fn(fake_tool).model_json_schema()
        == FakeTool.model_json_schema()
    )
